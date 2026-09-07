from pathlib import Path

import geopandas as gpd
import pandas as pd

from shapely.geometry import Point

from app.core.logger import get_logger


logger = get_logger(__name__)


INDIA_BOUNDARY_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "india_boundary.geojson"
)


_india_boundary = None


def _load_india_boundary():
    global _india_boundary

    if _india_boundary is not None:
        return _india_boundary

    if not INDIA_BOUNDARY_PATH.exists():
        raise FileNotFoundError(
            f"India boundary file not found: "
            f"{INDIA_BOUNDARY_PATH}"
        )

    india = gpd.read_file(
        INDIA_BOUNDARY_PATH
    )

    if india.empty:
        raise ValueError(
            "India boundary GeoJSON is empty."
        )

    india = india.to_crs(
        "EPSG:4326"
    )

    # Combine all parts into one geometry
    _india_boundary = india.geometry.union_all()

    logger.info(
        "India boundary loaded"
    )

    return _india_boundary


def filter_firms_to_india(
    df: pd.DataFrame
):
    """
    Keep only FIRMS detections physically inside
    the India polygon.

    Expected columns:
        latitude
        longitude
    """

    if df.empty:
        return df

    required = {
        "latitude",
        "longitude"
    }

    missing = required - set(
        df.columns
    )

    if missing:
        raise ValueError(
            f"Missing FIRMS coordinate columns: "
            f"{sorted(missing)}"
        )

    df = df.copy()

    df["latitude"] = pd.to_numeric(
        df["latitude"],
        errors="coerce"
    )

    df["longitude"] = pd.to_numeric(
        df["longitude"],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "latitude",
            "longitude"
        ]
    ).copy()

    before = len(df)

    india_boundary = (
        _load_india_boundary()
    )

    points = gpd.GeoSeries(
        [
            Point(
                lon,
                lat
            )
            for lon, lat in zip(
                df["longitude"],
                df["latitude"]
            )
        ],
        crs="EPSG:4326"
    )

    # covers() includes points exactly on boundary.
    mask = points.apply(
        india_boundary.covers
    )

    filtered = (
        df.loc[
            mask.values
        ]
        .copy()
        .reset_index(
            drop=True
        )
    )

    logger.info(
        "India FIRMS filter | "
        "%s -> %s detections | removed=%s",
        before,
        len(filtered),
        before - len(filtered)
    )

    return filtered