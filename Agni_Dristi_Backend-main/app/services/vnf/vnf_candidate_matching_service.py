from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.logger import get_logger


logger = get_logger(__name__)

MATCH_RADIUS_METERS = 550.0


def match_vnf_batch_to_known_objects(
    db: Session,
    batch_id: str
):
    if not batch_id:
        return {
            "total": 0,
            "matched_known": 0,
            "remaining_candidates": 0
        }

    logger.info(
        "Matching VNF batch %s "
        "against thermal objects",
        batch_id
    )

    # ========================================================
    # 1. MATCH + UPDATE IN ONE SQL STATEMENT
    # ========================================================

    db.execute(
        text("""
            WITH matches AS (

                SELECT
                    v.id,

                    nearest.object_uid

                FROM vnf_detections v

                JOIN LATERAL (

                    SELECT
                        t.object_uid

                    FROM thermal_objects t

                    WHERE
                        t.location IS NOT NULL

                        AND ST_DWithin(
                            t.location,
                            v.location,

                            COALESCE(
                                t.object_radius_m,
                                0
                            )
                            + :radius
                        )

                    ORDER BY
                        t.location
                        <-> v.location

                    LIMIT 1

                ) nearest
                ON TRUE

                WHERE
                    v.ingestion_batch_id =
                        :batch_id

                    AND v.processing_state =
                        'CANDIDATE'

                    AND v.location IS NOT NULL
            )

            UPDATE vnf_detections v

            SET
                processing_state =
                    'KNOWN_OBJECT',

                matched_object_uid =
                    m.object_uid

            FROM matches m

            WHERE
                v.id = m.id
        """),
        {
            "batch_id":
                batch_id,

            "radius":
                MATCH_RADIUS_METERS
        }
    )

    db.commit()

    # ========================================================
    # 2. COUNTS
    # ========================================================

    row = (
        db.execute(
            text("""
                SELECT

                    COUNT(*) AS total,

                    COUNT(*) FILTER (
                        WHERE processing_state =
                            'KNOWN_OBJECT'
                    ) AS matched,

                    COUNT(*) FILTER (
                        WHERE processing_state =
                            'CANDIDATE'
                    ) AS remaining

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

    result = {
        "total":
            int(row["total"] or 0),

        "matched_known":
            int(row["matched"] or 0),

        "remaining_candidates":
            int(row["remaining"] or 0)
    }

    logger.info(
        "VNF batch matching complete | "
        "matched=%s | remaining=%s",
        result["matched_known"],
        result["remaining_candidates"]
    )

    return result