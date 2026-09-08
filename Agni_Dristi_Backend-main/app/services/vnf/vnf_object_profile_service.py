import numpy as np
import pandas as pd

from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.models.vnf_detection_model import VNFDetection
from app.models.thermal_object_model import ThermalObject


logger = get_logger(__name__)


TEMP_MIN = 400.0
TEMP_MAX = 3000.0
BIN_SIZE = 50.0


def _safe_float(value):
    if value is None:
        return None

    if pd.isna(value):
        return None

    value = float(value)

    if not np.isfinite(value):
        return None

    return value


def _build_thermal_fingerprint(
    temperatures: pd.Series
):
    bins = np.arange(
        TEMP_MIN,
        TEMP_MAX + BIN_SIZE,
        BIN_SIZE
    )

    labels = [
        f"FP_{int(bins[i])}_{int(bins[i + 1])}K"
        for i in range(len(bins) - 1)
    ]

    temps = pd.to_numeric(
        temperatures,
        errors="coerce"
    )

    temps = temps[
        temps.between(
            TEMP_MIN,
            TEMP_MAX,
            inclusive="both"
        )
    ].dropna()

    if temps.empty:
        return {}

    counts, _ = np.histogram(
        temps.to_numpy(),
        bins=bins
    )

    total = counts.sum()

    if total == 0:
        return {}

    return {
        label: float(count / total)
        for label, count in zip(
            labels,
            counts
        )
    }


def _calculate_profile_updates(
    detections: pd.DataFrame
):
    """Calculate object profiles from detections already loaded in bulk."""

    if detections.empty:
        return {}

    df = detections.copy()

    for column in (
        "temp_primary",
        "area_primary",
        "rh_primary"
    ):
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df["active_month"] = pd.to_datetime(
        df["mscan_date"],
        errors="coerce"
    ).dt.to_period("M")

    updates = {}

    for object_uid, group in df.groupby(
        "object_uid",
        sort=False
    ):
        temp = group["temp_primary"]
        area = group["area_primary"]
        rh = group["rh_primary"]

        temp_mean = _safe_float(temp.mean())
        temp_std = _safe_float(temp.std())
        area_mean = _safe_float(area.mean())
        area_std = _safe_float(area.std())
        rh_mean = _safe_float(rh.mean())
        rh_std = _safe_float(rh.std())

        updates[object_uid] = {
            "temp_mean": temp_mean,
            "temp_median": _safe_float(temp.median()),
            "temp_min": _safe_float(temp.min()),
            "temp_max": _safe_float(temp.max()),
            "temp_std": temp_std,
            "temp_range": _safe_float(
                temp.max() - temp.min()
            ),
            "temp_cv": (
                temp_std / abs(temp_mean)
                if (
                    temp_mean is not None
                    and temp_std is not None
                    and abs(temp_mean) > 1e-8
                )
                else None
            ),
            "area_mean": area_mean,
            "area_std": area_std,
            "area_cv": (
                area_std / abs(area_mean)
                if (
                    area_mean is not None
                    and area_std is not None
                    and abs(area_mean) > 1e-8
                )
                else None
            ),
            "rh_mean": rh_mean,
            "rh_std": rh_std,
            "rh_cv": (
                rh_std / abs(rh_mean)
                if (
                    rh_mean is not None
                    and rh_std is not None
                    and abs(rh_mean) > 1e-8
                )
                else None
            ),
            "detection_count": int(len(group)),
            "active_months": int(
                group["active_month"].nunique()
            ),
            "thermal_fingerprint": (
                _build_thermal_fingerprint(temp)
            )
        }

    return updates


def recalculate_object_profiles_for_batch(
    db: Session,
    batch_id: str
):
    """
    Recalculate profiles only for thermal objects
    touched by the current VNF ingestion batch.
    """

    if not batch_id:
        return {
            "affected_objects": 0,
            "updated_objects": 0
        }

    affected_uids = [
        row[0]
        for row in (
            db.query(
                VNFDetection.matched_object_uid
            )
            .filter(
                VNFDetection.ingestion_batch_id
                == batch_id,
                VNFDetection.processing_state
                == "KNOWN_OBJECT",
                VNFDetection.matched_object_uid
                .isnot(None)
            )
            .distinct()
            .all()
        )
    ]

    if not affected_uids:
        logger.info(
            "No thermal objects require profile recalculation "
            "for batch %s",
            batch_id
        )

        return {
            "affected_objects": 0,
            "updated_objects": 0
        }

    logger.info(
        "Recalculating profiles for %s affected thermal objects",
        len(affected_uids)
    )

    try:
        detection_rows = (
            db.query(
                VNFDetection.matched_object_uid,
                VNFDetection.temp_primary,
                VNFDetection.rh_primary,
                VNFDetection.area_primary,
                VNFDetection.mscan_date
            )
            .filter(
                VNFDetection.matched_object_uid
                .in_(affected_uids),
                VNFDetection.processing_state
                == "KNOWN_OBJECT"
            )
            .all()
        )

        detections = pd.DataFrame(
            detection_rows,
            columns=[
                "object_uid",
                "temp_primary",
                "rh_primary",
                "area_primary",
                "mscan_date"
            ]
        )

        profile_updates = _calculate_profile_updates(
            detections
        )

        object_rows = (
            db.query(
                ThermalObject.id,
                ThermalObject.object_uid
            )
            .filter(
                ThermalObject.object_uid
                .in_(list(profile_updates))
            )
            .all()
            if profile_updates
            else []
        )

        update_mappings = [
            {
                "id": object_id,
                **profile_updates[object_uid]
            }
            for object_id, object_uid in object_rows
        ]

        if update_mappings:
            db.bulk_update_mappings(
                ThermalObject,
                update_mappings
            )

        db.commit()
        updated_count = len(update_mappings)

    except Exception:
        db.rollback()

        logger.exception(
            "Failed recalculating thermal object profiles"
        )

        raise

    logger.info(
        "Thermal profile recalculation complete | "
        "affected=%s | updated=%s",
        len(affected_uids),
        updated_count
    )

    return {
        "affected_objects": len(affected_uids),
        "updated_objects": updated_count
    }
