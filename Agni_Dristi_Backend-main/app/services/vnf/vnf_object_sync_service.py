import uuid
import json
import logging

import numpy as np
import pandas as pd

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.thermal_object_model import ThermalObject


logger = logging.getLogger(__name__)

MATCH_RADIUS_METERS = 550.0


# ============================================================
# HELPERS
# ============================================================

def _safe_float(value):
    if value is None:
        return None

    if pd.isna(value):
        return None

    value = float(value)

    if not np.isfinite(value):
        return None

    return value


def _safe_int(value):
    if value is None:
        return None

    if pd.isna(value):
        return None

    return int(value)


def _generate_object_uid():
    return (
        f"THERM_"
        f"{uuid.uuid4().hex[:12].upper()}"
    )


def _build_fingerprint(row):
    fingerprint = {}

    for col in row.index:
        if not col.startswith("FP_"):
            continue

        value = _safe_float(
            row[col]
        )

        if value is not None:
            fingerprint[col] = value

    return fingerprint


# ============================================================
# BULK MATCH AGAINST EXISTING THERMAL OBJECTS
# ============================================================

def _bulk_find_existing_objects(
    db: Session,
    objects: pd.DataFrame
):
    if objects.empty:
        return {}

    payload = []

    for idx, row in objects.iterrows():
        latitude = _safe_float(
            row.get("latitude")
        )

        longitude = _safe_float(
            row.get("longitude")
        )

        if latitude is None or longitude is None:
            continue

        payload.append({
            "idx": int(idx),
            "latitude": latitude,
            "longitude": longitude
        })

    if not payload:
        return {}

    sql = text("""
        WITH incoming AS (

            SELECT
                idx,
                latitude,
                longitude,

                ST_SetSRID(
                    ST_MakePoint(
                        longitude,
                        latitude
                    ),
                    4326
                )::geography AS location

            FROM jsonb_to_recordset(
                CAST(:payload AS jsonb)
            ) AS x(
                idx integer,
                latitude double precision,
                longitude double precision
            )
        )

        SELECT
            i.idx,
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

                    COALESCE(
                        t.object_radius_m,
                        0
                    )
                    + :radius
                )

            ORDER BY
                t.location <-> i.location

            LIMIT 1

        ) nearest ON TRUE
    """)

    rows = (
        db.execute(
            sql,
            {
                "payload": json.dumps(payload),
                "radius": MATCH_RADIUS_METERS
            }
        )
        .mappings()
        .all()
    )

    matches = {}

    for row in rows:
        if row["object_uid"] is None:
            continue

        matches[
            int(row["idx"])
        ] = {
            "object_uid": row["object_uid"],
            "distance_m": float(
                row["distance_m"]
            )
        }

    return matches


# ============================================================
# MAIN SYNC
# ============================================================

def sync_vnf_objects(
    db: Session,
    objects: pd.DataFrame
):
    if objects.empty:
        return {
            "total": 0,
            "existing": 0,
            "inserted": 0,
            "invalid": 0,
            "object_uid_map": {}
        }

    objects = (
        objects
        .reset_index(
            drop=True
        )
    )

    logger.info(
        "Starting VNF object sync for %s objects",
        len(objects)
    )

    # --------------------------------------------------------
    # 1. BULK MATCH EXISTING OBJECTS
    # --------------------------------------------------------

    matches = (
        _bulk_find_existing_objects(
            db,
            objects
        )
    )

    logger.info(
        "Existing thermal objects matched: %s",
        len(matches)
    )

    existing_count = 0
    invalid_count = 0

    new_objects = []

    # Stage3 ID -> permanent THERM UID
    object_uid_map = {}

    # --------------------------------------------------------
    # 2. PROCESS OBJECTS
    # --------------------------------------------------------

    for idx, row in objects.iterrows():

        latitude = _safe_float(
            row.get("latitude")
        )

        longitude = _safe_float(
            row.get("longitude")
        )

        if latitude is None or longitude is None:
            invalid_count += 1
            continue

        stage3_id = str(
            row.get("stage3_object_id")
        )

        # ====================================================
        # EXISTING OBJECT
        # ====================================================

        if idx in matches:
            existing_count += 1

            object_uid_map[
                stage3_id
            ] = matches[idx][
                "object_uid"
            ]

            # Existing object remains unchanged
            continue

        # ====================================================
        # NEW OBJECT
        # ====================================================

        new_object_uid = (
            _generate_object_uid()
        )

        object_uid_map[
            stage3_id
        ] = new_object_uid

        thermal_object = ThermalObject(

            object_uid=
                new_object_uid,

            stage3_object_id=
                stage3_id,

            latitude=
                latitude,

            longitude=
                longitude,

            location=(
                f"SRID=4326;"
                f"POINT({longitude} {latitude})"
            ),

            object_radius_m=
                _safe_float(
                    row.get(
                        "object_radius_m"
                    )
                ),

            classification_label=
                row.get(
                    "predicted_label"
                ),

            classification_source=
                "VNF_XGBOOST",

            predicted_label_confidence=
                _safe_float(
                    row.get(
                        "predicted_label_confidence"
                    )
                ),

            detection_count=
                _safe_int(
                    row.get(
                        "detection_count"
                    )
                ),

            active_months=
                _safe_int(
                    row.get(
                        "active_months"
                    )
                ),

            persistence_ratio=
                _safe_float(
                    row.get(
                        "persistence_ratio"
                    )
                ),

            longest_active_run=
                _safe_int(
                    row.get(
                        "longest_active_run"
                    )
                ),

            max_inactive_gap=
                _safe_int(
                    row.get(
                        "max_inactive_gap"
                    )
                ),

            temp_mean=
                _safe_float(
                    row.get(
                        "temp_mean"
                    )
                ),

            temp_median=
                _safe_float(
                    row.get(
                        "temp_median"
                    )
                ),

            temp_min=
                _safe_float(
                    row.get(
                        "temp_min"
                    )
                ),

            temp_max=
                _safe_float(
                    row.get(
                        "temp_max"
                    )
                ),

            temp_std=
                _safe_float(
                    row.get(
                        "temp_std"
                    )
                ),

            temp_range=
                _safe_float(
                    row.get(
                        "temp_range"
                    )
                ),

            temp_cv=
                _safe_float(
                    row.get(
                        "temp_cv"
                    )
                ),

            area_mean=
                _safe_float(
                    row.get(
                        "area_mean"
                    )
                ),

            area_std=
                _safe_float(
                    row.get(
                        "area_std"
                    )
                ),

            area_cv=
                _safe_float(
                    row.get(
                        "area_cv"
                    )
                ),

            rh_mean=
                _safe_float(
                    row.get(
                        "rh_mean"
                    )
                ),

            rh_std=
                _safe_float(
                    row.get(
                        "rh_std"
                    )
                ),

            rh_cv=
                _safe_float(
                    row.get(
                        "rh_cv"
                    )
                ),

            thermal_fingerprint=
                _build_fingerprint(
                    row
                ),

            match_distance_km=
                None
        )

        new_objects.append(
            thermal_object
        )

    # --------------------------------------------------------
    # 3. INSERT NEW OBJECTS
    # --------------------------------------------------------

    try:

        if new_objects:
            db.add_all(
                new_objects
            )

        db.commit()

    except Exception:
        db.rollback()

        logger.exception(
            "VNF object sync failed"
        )

        raise

    inserted_count = len(
        new_objects
    )

    logger.info(
        "VNF object sync completed | "
        "total=%s | existing=%s | "
        "inserted=%s | invalid=%s",
        len(objects),
        existing_count,
        inserted_count,
        invalid_count
    )

    return {
        "total": len(objects),
        "existing": existing_count,
        "inserted": inserted_count,
        "invalid": invalid_count,
        "object_uid_map": object_uid_map
    }