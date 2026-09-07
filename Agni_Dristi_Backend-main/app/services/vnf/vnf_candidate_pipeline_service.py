from datetime import date

from dateutil.relativedelta import (
    relativedelta
)

import pandas as pd

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.logger import get_logger

from app.services.vnf.vnf_pipeline_service import (
    process_vnf_data_with_members
)

from app.services.vnf.vnf_object_sync_service import (
    sync_vnf_objects
)

from app.services.vnf.vnf_candidate_state_service import (
    finalize_vnf_states
)


logger = get_logger(__name__)


LOCAL_HISTORY_RADIUS_M = 2000


# ============================================================
# ATTACH DB IDS TO BOOTSTRAP DATAFRAME
# ============================================================

def attach_batch_database_ids(
    db: Session,
    df: pd.DataFrame,
    batch_id: str
):
    if "id_Key" not in df.columns:
        raise ValueError(
            "VNF bootstrap requires id_Key."
        )

    # Only fetch two tiny columns, not entire rows.
    rows = (
        db.execute(
            text("""
                SELECT
                    id,
                    id_key

                FROM vnf_detections

                WHERE
                    ingestion_batch_id =
                        :batch_id
            """),
            {
                "batch_id":
                    batch_id
            }
        )
        .mappings()
        .all()
    )

    key_map = {
        str(row["id_key"]):
            int(row["id"])

        for row in rows

        if row["id_key"] is not None
    }

    output = df.copy()

    output[
        "db_detection_id"
    ] = (
        output["id_Key"]
        .astype(str)
        .map(key_map)
    )

    output = output.dropna(
        subset=[
            "db_detection_id"
        ]
    ).copy()

    output[
        "db_detection_id"
    ] = (
        output[
            "db_detection_id"
        ]
        .astype(int)
    )

    return output


# ============================================================
# BOOTSTRAP
# ============================================================

def run_bootstrap_pipeline(
    db: Session,
    uploaded_df: pd.DataFrame,
    batch_id: str
):
    logger.info(
        "Running VNF bootstrap directly "
        "from uploaded dataframe"
    )

    working_df = (
        attach_batch_database_ids(
            db,
            uploaded_df,
            batch_id
        )
    )

    result = (
        process_vnf_data_with_members(
            working_df
        )
    )

    objects = result[
        "objects"
    ]

    persistent_df = result[
        "detections"
    ]

    if objects.empty:
        finalize_vnf_states(
            db,
            batch_id,
            persistent_df,
            {}
        )

        return {
            "pipeline_input":
                len(working_df),

            "objects_found":
                0,

            "existing_objects":
                0,

            "new_objects":
                0,

            "persistent_known":
                0,

            "transient":
                len(working_df)
        }

    sync_result = sync_vnf_objects(
        db,
        objects
    )

    states = finalize_vnf_states(
        db,
        batch_id,
        persistent_df,
        sync_result[
            "object_uid_map"
        ]
    )

    return {
        "pipeline_input":
            len(working_df),

        "objects_found":
            len(objects),

        "existing_objects":
            sync_result[
                "existing"
            ],

        "new_objects":
            sync_result[
                "inserted"
            ],

        "persistent_known":
            states[
                "known_object"
            ],

        "transient":
            states[
                "transient"
            ]
    }


# ============================================================
# LOAD AFFECTED MONTHLY REGION
# ============================================================

def load_affected_history(
    db: Session,
    batch_id: str,
    months: int = 12,
    radius_m: int = LOCAL_HISTORY_RADIUS_M
):
    start_date = (
        date.today()
        - relativedelta(
            months=months
        )
    )

    rows = (
        db.execute(
            text("""
                WITH new_candidates AS (

                    SELECT
                        id,
                        location

                    FROM vnf_detections

                    WHERE
                        ingestion_batch_id = :batch_id
                        AND processing_state = 'CANDIDATE'
                        AND location IS NOT NULL
                ),

                historical AS (

                    SELECT DISTINCT
                        old.id

                    FROM new_candidates n

                    JOIN vnf_detections old
                        ON old.processing_state = 'TRANSIENT'

                        AND old.mscan_date >= :start_date

                        AND old.location IS NOT NULL

                        AND ST_DWithin(
                            old.location,
                            n.location,
                            :radius
                        )
                ),

                working_ids AS (

                    SELECT id
                    FROM new_candidates

                    UNION

                    SELECT id
                    FROM historical
                )

                SELECT
                    v.id AS db_detection_id,
                    v.id_key AS "id_Key",

                    v.lat_gmtco AS "Lat_GMTCO",
                    v.lon_gmtco AS "Lon_GMTCO",

                    v.temp_primary AS "Temp_primary",
                    v.temp_background AS "Temp_background",

                    v.rh_primary AS "RH_primary",
                    v.area_primary AS "Area_primary",

                    v.cloud_mask_fixed AS "Cloud_Mask_Fixed",

                    v.sample_m10 AS "Sample_M10",
                    v.line_m10 AS "Line_M10",

                    v.sensor AS sensor,
                    v.vnf_version AS vnf_version,

                    v.mscan_date AS "Mscan_date",
                    v.mscan_time AS "Mscan_time",

                    v.ltz_date AS "LTZ_date",
                    v.ltz_time AS "LTZ_time"

                FROM vnf_detections v

                JOIN working_ids w
                    ON v.id = w.id
            """),
            {
                "batch_id": batch_id,
                "start_date": start_date,
                "radius": radius_m
            }
        )
        .mappings()
        .all()
    )

    df = pd.DataFrame(
        rows
    )

    if df.empty:
        logger.info(
            "Affected VNF working pool: 0"
        )

        return df

    logger.info(
        "Affected VNF working pool: %s",
        len(df)
    )

    return df

# ============================================================
# MONTHLY AFFECTED PIPELINE
# ============================================================

def run_affected_candidate_pipeline(
    db: Session,
    batch_id: str,
    months: int = 12,
    radius_m: int = LOCAL_HISTORY_RADIUS_M
):
    working_df = (
        load_affected_history(
            db,
            batch_id,
            months,
            radius_m
        )
    )

    if working_df.empty:

        states = finalize_vnf_states(
            db,
            batch_id,
            pd.DataFrame(),
            {}
        )

        return {
            "pipeline_input": 0,
            "objects_found": 0,
            "existing_objects": 0,
            "new_objects": 0,
            "persistent_known":
                states[
                    "known_object"
                ],
            "transient":
                states[
                    "transient"
                ]
        }

    result = (
        process_vnf_data_with_members(
            working_df
        )
    )

    objects = result[
        "objects"
    ]

    persistent_df = result[
        "detections"
    ]

    if objects.empty:

        states = finalize_vnf_states(
            db,
            batch_id,
            persistent_df,
            {}
        )

        return {
            "pipeline_input":
                len(working_df),

            "objects_found":
                0,

            "existing_objects":
                0,

            "new_objects":
                0,

            "persistent_known":
                states[
                    "known_object"
                ],

            "transient":
                states[
                    "transient"
                ]
        }

    sync_result = (
        sync_vnf_objects(
            db,
            objects
        )
    )

    states = finalize_vnf_states(
        db,
        batch_id,
        persistent_df,
        sync_result[
            "object_uid_map"
        ]
    )

    return {
        "pipeline_input":
            len(working_df),

        "objects_found":
            len(objects),

        "existing_objects":
            sync_result[
                "existing"
            ],

        "new_objects":
            sync_result[
                "inserted"
            ],

        "persistent_known":
            states[
                "known_object"
            ],

        "transient":
            states[
                "transient"
            ]
    }