import json

from sqlalchemy import text


def batch_match_firms_points(db, points: list[dict], threshold_m: int = 550):
    if not points:
        return {}

    sql = text("""
        WITH incoming AS (
            SELECT
                firms_uid,
                latitude,
                longitude,
                ST_SetSRID(
                    ST_MakePoint(longitude, latitude),
                    4326
                )::geography AS location
            FROM jsonb_to_recordset(
                CAST(:points AS jsonb)
            ) AS x(
                firms_uid text,
                latitude double precision,
                longitude double precision
            )
        )

        SELECT
            i.firms_uid,
            nearest.object_uid,
            nearest.distance_m

        FROM incoming i

        LEFT JOIN LATERAL (
            SELECT
                t.object_uid,
                ST_Distance(
                    t.location,
                    i.location
                ) AS distance_m

            FROM thermal_objects t

            WHERE
                t.location IS NOT NULL
                AND ST_DWithin(
                    t.location,
                    i.location,
                    :threshold_m
                )

            ORDER BY
                t.location <-> i.location

            LIMIT 1
        ) nearest ON TRUE
    """)

    rows = db.execute(
        sql,
        {
            "points": json.dumps(points),
            "threshold_m": threshold_m
        }
    ).mappings().all()

    return {
        row["firms_uid"]: {
            "matched_object_uid": row["object_uid"],
            "match_distance_km": (
                float(row["distance_m"]) / 1000
                if row["distance_m"] is not None
                else None
            ),
            "is_known_persistent_source": row["object_uid"] is not None
        }
        for row in rows
    }