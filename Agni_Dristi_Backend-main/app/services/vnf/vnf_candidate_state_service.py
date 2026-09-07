from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.logger import get_logger


logger = get_logger(__name__)


UPDATE_CHUNK_SIZE = 10000


def finalize_vnf_states(
    db: Session,
    batch_id: str,
    persistent_df,
    object_uid_map: dict
):
    persistent_updated = 0

    try:
        # ====================================================
        # 1. ALL REMAINING CURRENT-BATCH CANDIDATES
        #    -> TRANSIENT
        # ====================================================

        db.execute(
            text("""
                UPDATE vnf_detections

                SET
                    processing_state =
                        'TRANSIENT',

                    matched_object_uid =
                        NULL

                WHERE
                    ingestion_batch_id =
                        :batch_id

                    AND processing_state =
                        'CANDIDATE'
            """),
            {
                "batch_id":
                    batch_id
            }
        )

        # ====================================================
        # 2. PERSISTENT MEMBERS
        #    -> KNOWN_OBJECT
        # ====================================================

        if (
            persistent_df is not None
            and not persistent_df.empty
            and "db_detection_id"
                in persistent_df.columns
            and "stage3_object_id"
                in persistent_df.columns
        ):

            for stage3_id, group in (
                persistent_df.groupby(
                    "stage3_object_id"
                )
            ):

                object_uid = (
                    object_uid_map.get(
                        str(stage3_id)
                    )
                )

                if not object_uid:
                    continue

                member_ids = (
                    group[
                        "db_detection_id"
                    ]
                    .dropna()
                    .astype(int)
                    .unique()
                    .tolist()
                )

                for start in range(
                    0,
                    len(member_ids),
                    UPDATE_CHUNK_SIZE
                ):
                    chunk = (
                        member_ids[
                            start:
                            start
                            + UPDATE_CHUNK_SIZE
                        ]
                    )

                    db.execute(
                        text("""
                            UPDATE vnf_detections

                            SET
                                processing_state =
                                    'KNOWN_OBJECT',

                                matched_object_uid =
                                    :object_uid

                            WHERE
                                id = ANY(
                                    CAST(
                                        :ids
                                        AS bigint[]
                                    )
                                )
                        """),
                        {
                            "object_uid":
                                object_uid,

                            "ids":
                                chunk
                        }
                    )

                persistent_updated += (
                    len(member_ids)
                )

        db.commit()

    except Exception:
        db.rollback()

        logger.exception(
            "VNF state finalization failed"
        )

        raise

    # ========================================================
    # 3. FINAL BATCH COUNTS
    # ========================================================

    row = (
        db.execute(
            text("""
                SELECT

                    COUNT(*) FILTER (
                        WHERE processing_state =
                            'KNOWN_OBJECT'
                    ) AS known,

                    COUNT(*) FILTER (
                        WHERE processing_state =
                            'TRANSIENT'
                    ) AS transient,

                    COUNT(*) FILTER (
                        WHERE processing_state =
                            'CANDIDATE'
                    ) AS candidate

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
        .first()
    )

    return {
        "known_object":
            int(row["known"] or 0),

        "transient":
            int(row["transient"] or 0),

        "candidate":
            int(row["candidate"] or 0),

        "persistent_updated":
            persistent_updated
    }