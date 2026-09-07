from datetime import date, timedelta

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.models.alert_model import Alert
from app.models.firms_detection_model import FIRMSDetection


ABNORMAL_FRP_MULTIPLIER = 3.0
ABNORMAL_MIN_HISTORY = 5

REPEATED_RADIUS_METERS = 550
REPEATED_MIN_DATES = 3
REPEATED_LOOKBACK_DAYS = 7


# ============================================================
# UNMATCHED ANOMALY
# ============================================================

def build_unmatched_alert(detection: FIRMSDetection):

    if detection.is_known_persistent_source:
        return None

    return Alert(
        alert_type="UNMATCHED_ANOMALY",
        severity="medium",
        firms_uid=detection.firms_uid,
        object_uid=None,
        latitude=detection.latitude,
        longitude=detection.longitude,
        message=(
            "New FIRMS thermal anomaly detected outside "
            "known persistent thermal objects."
        ),
        resolved=False
    )


# ============================================================
# ABNORMAL KNOWN SOURCE
# ============================================================

def build_abnormal_known_source_alert(
    detection: FIRMSDetection,
    history_count: int,
    median_frp: float | None
):

    if not detection.is_known_persistent_source:
        return None

    if not detection.matched_object_uid:
        return None

    if detection.frp is None:
        return None

    if history_count < ABNORMAL_MIN_HISTORY:
        return None

    if median_frp is None or median_frp <= 0:
        return None

    current_frp = float(detection.frp)

    ratio = current_frp / median_frp

    if ratio < ABNORMAL_FRP_MULTIPLIER:
        return None

    return Alert(
        alert_type="ABNORMAL_KNOWN_SOURCE",
        severity="high",
        firms_uid=detection.firms_uid,
        object_uid=detection.matched_object_uid,
        latitude=detection.latitude,
        longitude=detection.longitude,
        message=(
            f"Abnormally high thermal activity detected at "
            f"{detection.matched_object_uid}. "
            f"Current FRP {current_frp:.2f} MW is "
            f"{ratio:.1f}x its historical median "
            f"({median_frp:.2f} MW)."
        ),
        resolved=False
    )


# ============================================================
# FRP HISTORY — BULK
# ============================================================

def get_known_source_frp_stats(
    db: Session,
    object_uids: list[str],
    current_batch_uids: list[str]
):

    if not object_uids:
        return {}

    query = (
        db.query(
            FIRMSDetection.matched_object_uid,

            func.count(
                FIRMSDetection.frp
            ).label("history_count"),

            func.percentile_cont(0.5)
            .within_group(
                FIRMSDetection.frp
            )
            .label("median_frp")
        )

        .filter(
            FIRMSDetection.matched_object_uid.in_(
                object_uids
            ),

            FIRMSDetection.frp.isnot(None)
        )
    )

    # Don't use current batch as historical baseline
    if current_batch_uids:
        query = query.filter(
            ~FIRMSDetection.firms_uid.in_(
                current_batch_uids
            )
        )

    rows = (
        query
        .group_by(
            FIRMSDetection.matched_object_uid
        )
        .all()
    )

    return {
        row.matched_object_uid: {
            "history_count": int(row.history_count),

            "median_frp": (
                float(row.median_frp)
                if row.median_frp is not None
                else None
            )
        }

        for row in rows
    }


# ============================================================
# REPEATED UNMATCHED COUNTS — BULK
# ============================================================

def get_repeated_unmatched_counts(
    db: Session,
    detections: list[FIRMSDetection]
):

    if not detections:
        return {}

    values = []
    params = {}

    for i, detection in enumerate(detections):

        values.append(
            f"(:uid_{i}, :lat_{i}, :lon_{i})"
        )

        params[f"uid_{i}"] = detection.firms_uid
        params[f"lat_{i}"] = float(detection.latitude)
        params[f"lon_{i}"] = float(detection.longitude)

    params["radius"] = REPEATED_RADIUS_METERS

    params["since_date"] = (
        date.today()
        - timedelta(
            days=REPEATED_LOOKBACK_DAYS - 1
        )
    )

    sql = text(
        f"""
        WITH incoming(
            firms_uid,
            latitude,
            longitude
        ) AS (

            VALUES
            {", ".join(values)}

        ),

        incoming_points AS (

            SELECT
                firms_uid,

                ST_SetSRID(
                    ST_MakePoint(
                        longitude,
                        latitude
                    ),
                    4326
                )::geography AS location

            FROM incoming
        )

        SELECT
            i.firms_uid,

            COUNT(
                DISTINCT f.acq_date
            ) AS active_dates

        FROM incoming_points i

        LEFT JOIN firms_detections f

            ON f.is_known_persistent_source = FALSE

            AND f.acq_date >= :since_date

            AND ST_DWithin(
                f.location,
                i.location,
                :radius
            )

        GROUP BY
            i.firms_uid
        """
    )

    rows = (
        db.execute(
            sql,
            params
        )
        .mappings()
        .all()
    )

    return {
        row["firms_uid"]:
            int(row["active_dates"] or 0)

        for row in rows
    }


# ============================================================
# CHECK IF REPEATED ALERT ALREADY EXISTS NEARBY
# ============================================================

def repeated_alert_already_exists(
    db: Session,
    latitude: float,
    longitude: float
):

    sql = text(
        """
        SELECT id

        FROM alerts

        WHERE
            alert_type = 'REPEATED_UNMATCHED'

            AND resolved = FALSE

            AND ST_DWithin(
                ST_SetSRID(
                    ST_MakePoint(
                        longitude,
                        latitude
                    ),
                    4326
                )::geography,

                ST_SetSRID(
                    ST_MakePoint(
                        :lon,
                        :lat
                    ),
                    4326
                )::geography,

                :radius
            )

        LIMIT 1
        """
    )

    row = db.execute(
        sql,
        {
            "lat": latitude,
            "lon": longitude,
            "radius": REPEATED_RADIUS_METERS
        }
    ).first()

    return row is not None


# ============================================================
# REPEATED UNMATCHED ALERT
# ============================================================

def build_repeated_unmatched_alert(
    db: Session,
    detection: FIRMSDetection,
    active_dates: int
):

    if detection.is_known_persistent_source:
        return None

    if active_dates < REPEATED_MIN_DATES:
        return None

    if repeated_alert_already_exists(
        db,
        detection.latitude,
        detection.longitude
    ):
        return None

    return Alert(
        alert_type="REPEATED_UNMATCHED",
        severity="high",
        firms_uid=detection.firms_uid,
        object_uid=None,
        latitude=detection.latitude,
        longitude=detection.longitude,
        message=(
            f"Repeated unidentified thermal activity detected "
            f"within approximately {REPEATED_RADIUS_METERS} m "
            f"on {active_dates} distinct dates during the "
            f"last {REPEATED_LOOKBACK_DAYS} days."
        ),
        resolved=False
    )