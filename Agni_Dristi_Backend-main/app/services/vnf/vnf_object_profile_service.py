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

    # ========================================================
    # 1. FIND OBJECTS TOUCHED BY THIS BATCH
    # ========================================================

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

    updated_count = 0

    try:
        # ====================================================
        # 2. UPDATE ONE AFFECTED OBJECT AT A TIME
        # ====================================================

        for object_uid in affected_uids:

            detections = (
                db.query(
                    VNFDetection
                )
                .filter(
                    VNFDetection.matched_object_uid
                    == object_uid,

                    VNFDetection.processing_state
                    == "KNOWN_OBJECT"
                )
                .all()
            )

            if not detections:
                continue

            df = pd.DataFrame([
                {
                    "temp_primary":
                        d.temp_primary,

                    "rh_primary":
                        d.rh_primary,

                    "area_primary":
                        d.area_primary,

                    "mscan_date":
                        d.mscan_date
                }
                for d in detections
            ])

            obj = (
                db.query(
                    ThermalObject
                )
                .filter(
                    ThermalObject.object_uid
                    == object_uid
                )
                .first()
            )

            if obj is None:
                continue

            # ================================================
            # TEMPERATURE
            # ================================================

            temp = pd.to_numeric(
                df["temp_primary"],
                errors="coerce"
            )

            obj.temp_mean = _safe_float(
                temp.mean()
            )

            obj.temp_median = _safe_float(
                temp.median()
            )

            obj.temp_min = _safe_float(
                temp.min()
            )

            obj.temp_max = _safe_float(
                temp.max()
            )

            obj.temp_std = _safe_float(
                temp.std()
            )

            obj.temp_range = (
                _safe_float(
                    temp.max()
                    - temp.min()
                )
            )

            if (
                obj.temp_mean is not None
                and obj.temp_std is not None
                and abs(obj.temp_mean) > 1e-8
            ):
                obj.temp_cv = (
                    obj.temp_std
                    / abs(obj.temp_mean)
                )
            else:
                obj.temp_cv = None

            # ================================================
            # AREA
            # ================================================

            area = pd.to_numeric(
                df["area_primary"],
                errors="coerce"
            )

            obj.area_mean = _safe_float(
                area.mean()
            )

            obj.area_std = _safe_float(
                area.std()
            )

            if (
                obj.area_mean is not None
                and obj.area_std is not None
                and abs(obj.area_mean) > 1e-8
            ):
                obj.area_cv = (
                    obj.area_std
                    / abs(obj.area_mean)
                )
            else:
                obj.area_cv = None

            # ================================================
            # RADIANT HEAT
            # ================================================

            rh = pd.to_numeric(
                df["rh_primary"],
                errors="coerce"
            )

            obj.rh_mean = _safe_float(
                rh.mean()
            )

            obj.rh_std = _safe_float(
                rh.std()
            )

            if (
                obj.rh_mean is not None
                and obj.rh_std is not None
                and abs(obj.rh_mean) > 1e-8
            ):
                obj.rh_cv = (
                    obj.rh_std
                    / abs(obj.rh_mean)
                )
            else:
                obj.rh_cv = None

            # ================================================
            # DETECTION COUNT
            # ================================================

            obj.detection_count = int(
                len(df)
            )

            # ================================================
            # ACTIVE MONTHS
            # ================================================

            dates = pd.to_datetime(
                df["mscan_date"],
                errors="coerce"
            )

            months = (
                dates
                .dropna()
                .dt.to_period("M")
                .nunique()
            )

            obj.active_months = int(
                months
            )

            # ================================================
            # THERMAL FINGERPRINT
            # ================================================

            obj.thermal_fingerprint = (
                _build_thermal_fingerprint(
                    temp
                )
            )

            updated_count += 1

        db.commit()

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
        "affected_objects":
            len(affected_uids),

        "updated_objects":
            updated_count
    }