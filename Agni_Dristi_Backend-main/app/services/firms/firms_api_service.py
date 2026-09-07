from io import StringIO

import pandas as pd
import requests

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

FIRMS_BASE_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"

INDIA_BBOX = "68,6,98,38"

FIRMS_SOURCES = [
    "VIIRS_NOAA20_NRT",
    "VIIRS_NOAA21_NRT",
    "VIIRS_SNPP_NRT"
]


def fetch_firms_source(source: str, day_range: int = 1) -> pd.DataFrame:
    logger.info(f"Fetching FIRMS data from {source}")

    url = f"{FIRMS_BASE_URL}/{settings.FIRMS_MAP_KEY}/{source}/{INDIA_BBOX}/{day_range}"

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    if not response.text.strip():
        logger.info(f"No data returned from {source}")
        return pd.DataFrame()

    df = pd.read_csv(StringIO(response.text))

    logger.info(f"Fetched {len(df)} detections from {source}")

    df["source"] = source

    return df

def fetch_latest_firms(day_range: int = 1) -> pd.DataFrame:
    logger.info("Starting FIRMS API fetch")

    frames = []

    for source in FIRMS_SOURCES:
        try:
            df = fetch_firms_source(source, day_range)

            if not df.empty:
                frames.append(df)

        except Exception:
            logger.exception(f"FIRMS fetch failed for {source}")

    if not frames:
        logger.info("No FIRMS detections found")
        return pd.DataFrame()

    combined_df = pd.concat(frames, ignore_index=True)

    logger.info(f"Total FIRMS detections fetched: {len(combined_df)}")

    combined_df["acq_date"] = pd.to_datetime(
        combined_df["acq_date"],
        errors="coerce"
    ).dt.date

    return combined_df