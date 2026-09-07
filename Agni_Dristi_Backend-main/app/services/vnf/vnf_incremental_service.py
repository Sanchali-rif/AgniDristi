import time

import pandas as pd

from sqlalchemy.orm import Session

from app.core.logger import get_logger

from app.models.thermal_object_model import (
    ThermalObject
)

from app.services.vnf.vnf_ingestion_service import (
    ingest_vnf_detections
)

from app.services.vnf.vnf_candidate_matching_service import (
    match_vnf_batch_to_known_objects
)

from app.services.vnf.vnf_candidate_pipeline_service import (
    run_bootstrap_pipeline,
    run_affected_candidate_pipeline
)

from app.services.vnf.vnf_object_profile_service import (
    recalculate_object_profiles_for_batch
)


logger = get_logger(__name__)


def process_incremental_vnf_upload(
    db: Session,
    df: pd.DataFrame,
    rolling_months: int = 12
):
    start = time.perf_counter()

    # ========================================================
    # 1. DETERMINE MODE
    # ========================================================

    existing_objects = (
        db.query(
            ThermalObject
        )
        .count()
    )

    bootstrap = (
        existing_objects == 0
    )

    mode = (
        "bootstrap"
        if bootstrap
        else "incremental"
    )

    logger.info(
        "VNF processing mode: %s",
        mode
    )

    # ========================================================
    # 2. INGEST RAW VNF DATA
    # ========================================================

    ingestion = (
        ingest_vnf_detections(
            db,
            df
        )
    )

    batch_id = ingestion[
        "batch_id"
    ]

    # ========================================================
    # 3. BOOTSTRAP MODE
    # ========================================================

    if bootstrap:

        logger.info(
            "Running VNF bootstrap directly "
            "from uploaded dataframe"
        )

        pipeline = (
            run_bootstrap_pipeline(
                db,
                uploaded_df=df,
                batch_id=batch_id
            )
        )

        elapsed = (
            time.perf_counter()
            - start
        )

        return {
            "status":
                "completed",

            "mode":
                "bootstrap",

            "batch_id":
                batch_id,

            "input_detections":
                ingestion[
                    "input"
                ],

            "inserted_detections":
                ingestion[
                    "inserted"
                ],

            "duplicates":
                ingestion[
                    "duplicates"
                ],

            "matched_existing":
                0,

            "new_candidates":
                ingestion[
                    "inserted"
                ],

            "candidate_pipeline_input":
                pipeline[
                    "pipeline_input"
                ],

            "objects_found":
                pipeline[
                    "objects_found"
                ],

            "existing_objects":
                pipeline[
                    "existing_objects"
                ],

            "new_objects":
                pipeline[
                    "new_objects"
                ],

            "persistent_known":
                pipeline[
                    "persistent_known"
                ],

            "transient":
                pipeline[
                    "transient"
                ],

            "affected_profiles":
                0,

            "updated_profiles":
                0,

            "processing_time_seconds":
                round(
                    elapsed,
                    2
                )
        }

    # ========================================================
    # 4. INCREMENTAL MODE
    #    MATCH NEW DETECTIONS AGAINST KNOWN OBJECTS
    # ========================================================

    matching = (
        match_vnf_batch_to_known_objects(
            db,
            batch_id
        )
    )

    logger.info(
        "Known-object matching finished | "
        "matched=%s | remaining=%s",
        matching[
            "matched_known"
        ],
        matching[
            "remaining_candidates"
        ]
    )

    # ========================================================
    # 5. AFFECTED-REGION PIPELINE
    # ========================================================

    pipeline = (
        run_affected_candidate_pipeline(
            db,
            batch_id=batch_id,
            months=rolling_months,
            radius_m=2000
        )
    )

    logger.info(
        "Affected candidate pipeline finished | "
        "input=%s | objects=%s | new=%s",
        pipeline[
            "pipeline_input"
        ],
        pipeline[
            "objects_found"
        ],
        pipeline[
            "new_objects"
        ]
    )

    # ========================================================
    # 6. RECALCULATE AFFECTED THERMAL PROFILES
    #
    # This happens AFTER:
    #   - existing matches are assigned
    #   - newly persistent detections are assigned
    #
    # Therefore all KNOWN_OBJECT detections from this batch
    # can contribute to their thermal object's updated profile.
    # ========================================================

    profile_update = (
        recalculate_object_profiles_for_batch(
            db,
            batch_id
        )
    )

    logger.info(
        "Thermal object profile update finished | "
        "affected=%s | updated=%s",
        profile_update[
            "affected_objects"
        ],
        profile_update[
            "updated_objects"
        ]
    )

    # ========================================================
    # 7. FINAL RESPONSE
    # ========================================================

    elapsed = (
        time.perf_counter()
        - start
    )

    return {
        "status":
            "completed",

        "mode":
            "incremental",

        "batch_id":
            batch_id,

        "input_detections":
            ingestion[
                "input"
            ],

        "inserted_detections":
            ingestion[
                "inserted"
            ],

        "duplicates":
            ingestion[
                "duplicates"
            ],

        "matched_existing":
            matching[
                "matched_known"
            ],

        "new_candidates":
            matching[
                "remaining_candidates"
            ],

        "candidate_pipeline_input":
            pipeline[
                "pipeline_input"
            ],

        "objects_found":
            pipeline[
                "objects_found"
            ],

        "existing_objects":
            pipeline[
                "existing_objects"
            ],

        "new_objects":
            pipeline[
                "new_objects"
            ],

        "persistent_known":
            pipeline[
                "persistent_known"
            ],

        "transient":
            pipeline[
                "transient"
            ],

        "affected_profiles":
            profile_update[
                "affected_objects"
            ],

        "updated_profiles":
            profile_update[
                "updated_objects"
            ],

        "processing_time_seconds":
            round(
                elapsed,
                2
            )
    }