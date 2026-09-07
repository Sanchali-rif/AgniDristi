import time

import pandas as pd

from geoalchemy2.elements import WKTElement
from sqlalchemy import insert

from app.core.logger import get_logger
from app.models.firms_detection_model import FIRMSDetection

from app.services.matching.batch_matching_service import (
    batch_match_firms_points
)

from app.services.firms.firms_monitor_service import (
    generate_firms_uid
)

from app.services.alerts.alert_service import (
    build_unmatched_alert,
    build_abnormal_known_source_alert,
    build_repeated_unmatched_alert,
    get_known_source_frp_stats,
    get_repeated_unmatched_counts
)


logger = get_logger(__name__)


def process_firms_dataframe(db, df: pd.DataFrame):

    start = time.perf_counter()

    logger.info(
        f"Starting FIRMS processing for {len(df)} rows"
    )

    if df.empty:

        return {
            "total_rows": 0,
            "inserted": 0,
            "duplicates": 0,
            "matched_persistent": 0,
            "unmatched": 0,
            "alerts_created": 0
        }

    df = df.copy()

    # ========================================================
    # 1. GENERATE UID
    # ========================================================

    t = time.perf_counter()

    df["firms_uid"] = df.apply(
        lambda row:
            generate_firms_uid(
                row.to_dict()
            ),
        axis=1
    )

    logger.info(
        f"UID generation completed in "
        f"{time.perf_counter() - t:.2f}s"
    )

    # ========================================================
    # 2. REMOVE SAME-BATCH DUPLICATES
    # ========================================================

    before = len(df)

    df = (
        df
        .drop_duplicates(
            subset=["firms_uid"]
        )
        .copy()
    )

    in_batch_duplicates = (
        before - len(df)
    )

    # ========================================================
    # 3. DATABASE DUPLICATE CHECK
    # ========================================================

    t = time.perf_counter()

    incoming_uids = (
        df["firms_uid"]
        .tolist()
    )

    existing_uids = {
        row[0]

        for row in (

            db.query(
                FIRMSDetection.firms_uid
            )

            .filter(
                FIRMSDetection.firms_uid.in_(
                    incoming_uids
                )
            )

            .all()
        )
    }

    logger.info(
        f"Database duplicate lookup completed in "
        f"{time.perf_counter() - t:.2f}s"
    )

    new_df = df[
        ~df["firms_uid"].isin(
            existing_uids
        )
    ].copy()

    logger.info(
        f"New FIRMS detections to process: "
        f"{len(new_df)}"
    )

    if new_df.empty:

        return {
            "total_rows": len(df),

            "inserted": 0,

            "duplicates": (
                len(existing_uids)
                + in_batch_duplicates
            ),

            "matched_persistent": 0,
            "unmatched": 0,

            "alerts_created": 0
        }

    # ========================================================
    # 4. BATCH POSTGIS OBJECT MATCHING
    # ========================================================

    t = time.perf_counter()

    points = (
        new_df[
            [
                "firms_uid",
                "latitude",
                "longitude"
            ]
        ]
        .to_dict("records")
    )

    matches = batch_match_firms_points(
        db,
        points,
        threshold_m=550
    )

    logger.info(
        f"Batch spatial matching completed in "
        f"{time.perf_counter() - t:.2f}s"
    )

    # ========================================================
    # 5. PREPARE FIRMS ROWS
    # ========================================================

    rows_to_insert = []

    matched_count = 0
    unmatched_count = 0

    for _, row in new_df.iterrows():

        match = matches.get(
            row["firms_uid"],

            {
                "matched_object_uid": None,
                "match_distance_km": None,
                "is_known_persistent_source": False
            }
        )

        is_known = (
            match[
                "is_known_persistent_source"
            ]
        )

        if is_known:
            matched_count += 1

        else:
            unmatched_count += 1

        latitude = float(
            row["latitude"]
        )

        longitude = float(
            row["longitude"]
        )

        rows_to_insert.append({

            "firms_uid":
                row["firms_uid"],

            "latitude":
                latitude,

            "longitude":
                longitude,

            "location":
                WKTElement(
                    f"POINT({longitude} {latitude})",
                    srid=4326
                ),

            "bright_ti4":
                clean_value(
                    row.get("bright_ti4")
                ),

            "bright_ti5":
                clean_value(
                    row.get("bright_ti5")
                ),

            "frp":
                clean_value(
                    row.get("frp")
                ),

            "scan":
                clean_value(
                    row.get("scan")
                ),

            "track":
                clean_value(
                    row.get("track")
                ),

            "acq_date":
                row["acq_date"],

            "acq_time":
                str(
                    row["acq_time"]
                ),

            "satellite":
                clean_string(
                    row.get("satellite")
                ),

            "instrument":
                clean_string(
                    row.get("instrument")
                ),

            "confidence":
                clean_string(
                    row.get("confidence")
                ),

            "version":
                clean_string(
                    row.get("version")
                ),

            "daynight":
                clean_string(
                    row.get("daynight")
                ),

            "matched_object_uid":
                match[
                    "matched_object_uid"
                ],

            "match_distance_km":
                match[
                    "match_distance_km"
                ],

            "is_known_persistent_source":
                is_known
        })

    # ========================================================
    # 6. BULK INSERT FIRMS
    # ========================================================

    try:

        db.execute(
            insert(FIRMSDetection),
            rows_to_insert
        )

        db.commit()

    except Exception:

        db.rollback()

        logger.exception(
            "Bulk FIRMS insert failed"
        )

        raise

    # ========================================================
    # 7. LOAD ONLY NEW FIRMS ROWS
    # ========================================================

    new_uids = [
        row["firms_uid"]
        for row in rows_to_insert
    ]

    detections = (

        db.query(
            FIRMSDetection
        )

        .filter(
            FIRMSDetection.firms_uid.in_(
                new_uids
            )
        )

        .all()
    )

    unmatched = [
        d
        for d in detections
        if not d.is_known_persistent_source
    ]

    matched = [
        d
        for d in detections
        if d.is_known_persistent_source
    ]

    # ========================================================
    # 8. BULK ALERT CONTEXT
    # ========================================================

    matched_object_uids = list({

        d.matched_object_uid

        for d in matched

        if d.matched_object_uid
    })

    frp_stats = get_known_source_frp_stats(
        db,
        matched_object_uids,
        new_uids
    )

    repeated_counts = (
        get_repeated_unmatched_counts(
            db,
            unmatched
        )
    )

    # ========================================================
    # 9. CREATE ALERTS
    # ========================================================

    alerts_to_insert = []

    unmatched_count_alert = 0
    repeated_count_alert = 0
    abnormal_count_alert = 0

    # --------------------------------------------------------
    # UNMATCHED + REPEATED
    # --------------------------------------------------------

    for detection in unmatched:

        active_dates = (
            repeated_counts.get(
                detection.firms_uid,
                0
            )
        )

        # Repeated gets priority
        repeated_alert = (
            build_repeated_unmatched_alert(
                db,
                detection,
                active_dates
            )
        )

        if repeated_alert:

            alerts_to_insert.append(
                repeated_alert
            )

            repeated_count_alert += 1

            # Do NOT create medium unmatched alert as well
            continue

        unmatched_alert = (
            build_unmatched_alert(
                detection
            )
        )

        if unmatched_alert:

            alerts_to_insert.append(
                unmatched_alert
            )

            unmatched_count_alert += 1

    # --------------------------------------------------------
    # ABNORMAL KNOWN SOURCE
    # --------------------------------------------------------

    for detection in matched:

        stats = frp_stats.get(
            detection.matched_object_uid,

            {
                "history_count": 0,
                "median_frp": None
            }
        )

        alert = (
            build_abnormal_known_source_alert(
                detection,

                history_count=
                    stats[
                        "history_count"
                    ],

                median_frp=
                    stats[
                        "median_frp"
                    ]
            )
        )

        if alert:

            alerts_to_insert.append(
                alert
            )

            abnormal_count_alert += 1

    # ========================================================
    # 10. INSERT ALERTS
    # ========================================================

    try:

        if alerts_to_insert:

            db.add_all(
                alerts_to_insert
            )

            db.commit()

    except Exception:

        db.rollback()

        logger.exception(
            "Alert insert failed"
        )

        raise

    total_alerts = len(
        alerts_to_insert
    )

    total_time = (
        time.perf_counter()
        - start
    )

    logger.info(
        f"Alerts created: {total_alerts} | "
        f"Unmatched: {unmatched_count_alert} | "
        f"Repeated: {repeated_count_alert} | "
        f"Abnormal: {abnormal_count_alert}"
    )

    logger.info(
        f"Total FIRMS processing time: "
        f"{total_time:.2f}s"
    )

    return {

        "total_rows":
            len(df),

        "inserted":
            len(rows_to_insert),

        "duplicates":
            (
                len(existing_uids)
                + in_batch_duplicates
            ),

        "matched_persistent":
            matched_count,

        "unmatched":
            unmatched_count,

        "alerts_created":
            total_alerts,

        "alerts": {

            "unmatched_anomaly":
                unmatched_count_alert,

            "repeated_unmatched":
                repeated_count_alert,

            "abnormal_known_source":
                abnormal_count_alert
        }
    }


def clean_value(value):

    if value is None:
        return None

    if pd.isna(value):
        return None

    return value


def clean_string(value):

    if value is None:
        return None

    if pd.isna(value):
        return None

    return str(value)