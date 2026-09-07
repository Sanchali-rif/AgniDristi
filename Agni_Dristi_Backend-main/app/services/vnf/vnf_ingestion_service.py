import time
import uuid

import pandas as pd

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.logger import get_logger


logger = get_logger(__name__)


COLUMN_MAP = {
    "id_Key": "id_key",
    "Lat_GMTCO": "lat_gmtco",
    "Lon_GMTCO": "lon_gmtco",
    "Temp_primary": "temp_primary",
    "Temp_background": "temp_background",
    "RH_primary": "rh_primary",
    "Area_primary": "area_primary",
    "Cloud_Mask_Fixed": "cloud_mask_fixed",
    "Sample_M10": "sample_m10",
    "Line_M10": "line_m10",
    "sensor": "sensor",
    "vnf_version": "vnf_version"
}


def ingest_vnf_detections(
    db: Session,
    df: pd.DataFrame
):
    start = time.perf_counter()

    if df.empty:
        return {
            "input": 0,
            "inserted": 0,
            "duplicates": 0,
            "batch_id": None
        }

    batch_id = (
        "VNF_"
        + uuid.uuid4().hex.upper()
    )

    df = df.copy()

    original_count = len(df)

    # ========================================================
    # 1. RENAME
    # ========================================================

    df = df.rename(
        columns={
            old: new
            for old, new in COLUMN_MAP.items()
            if old in df.columns
        }
    )

    # ========================================================
    # 2. DATETIME
    # ========================================================

    if "Date_Mscan" in df.columns:
        parsed = pd.to_datetime(
            df["Date_Mscan"],
            errors="coerce",
            utc=True
        )

        df["mscan_date"] = parsed.dt.date

        df["mscan_time"] = (
            parsed.dt.strftime(
                "%H:%M:%S.%f"
            )
        )

    elif "Mscan_date" in df.columns:
        parsed = pd.to_datetime(
            df["Mscan_date"],
            errors="coerce"
        )

        df["mscan_date"] = (
            parsed.dt.date
        )

        if "Mscan_time" in df.columns:
            df["mscan_time"] = (
                df["Mscan_time"]
                .astype(str)
            )
        else:
            df["mscan_time"] = None

    else:
        df["mscan_date"] = None
        df["mscan_time"] = None

    if "Date_LTZ" in df.columns:
        parsed = pd.to_datetime(
            df["Date_LTZ"],
            errors="coerce",
            utc=True
        )

        df["ltz_date"] = parsed.dt.date

        df["ltz_time"] = (
            parsed.dt.strftime(
                "%H:%M:%S.%f"
            )
        )

    elif "LTZ_date" in df.columns:
        parsed = pd.to_datetime(
            df["LTZ_date"],
            errors="coerce"
        )

        df["ltz_date"] = (
            parsed.dt.date
        )

        if "LTZ_time" in df.columns:
            df["ltz_time"] = (
                df["LTZ_time"]
                .astype(str)
            )
        else:
            df["ltz_time"] = None

    else:
        df["ltz_date"] = None
        df["ltz_time"] = None

    # ========================================================
    # 3. COORDINATES
    # ========================================================

    if (
        "lat_gmtco" not in df.columns
        or "lon_gmtco" not in df.columns
    ):
        raise ValueError(
            "Lat_GMTCO / Lon_GMTCO missing."
        )

    df["lat_gmtco"] = pd.to_numeric(
        df["lat_gmtco"],
        errors="coerce"
    )

    df["lon_gmtco"] = pd.to_numeric(
        df["lon_gmtco"],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "lat_gmtco",
            "lon_gmtco"
        ]
    ).copy()

    # ========================================================
    # 4. SAME-FILE DUPLICATES
    # ========================================================

    before = len(df)

    if "id_key" in df.columns:
        keyed = (
            df[
                df["id_key"].notna()
            ]
            .drop_duplicates(
                subset=["id_key"]
            )
        )

        unkeyed = df[
            df["id_key"].isna()
        ]

        df = pd.concat(
            [
                keyed,
                unkeyed
            ],
            ignore_index=True
        )

    internal_duplicates = (
        before - len(df)
    )

    # ========================================================
    # 5. REQUIRED STAGING COLUMNS
    # ========================================================

    columns = [
        "id_key",
        "lat_gmtco",
        "lon_gmtco",
        "temp_primary",
        "temp_background",
        "rh_primary",
        "area_primary",
        "cloud_mask_fixed",
        "sample_m10",
        "line_m10",
        "sensor",
        "vnf_version",
        "mscan_date",
        "mscan_time",
        "ltz_date",
        "ltz_time"
    ]

    for column in columns:
        if column not in df.columns:
            df[column] = None

    df = df[
        columns
    ].copy()

    # Pandas NaN -> Python None
    df = df.astype(object).where(
        pd.notna(df),
        None
    )

    # ========================================================
    # 6. POSTGRES COPY
    # ========================================================

    stage_table = (
        "tmp_vnf_"
        + uuid.uuid4().hex[:12]
    )

    try:
        # Same physical PostgreSQL connection used by Session
        connection = db.connection()

        raw_connection = (
            connection.connection
            .driver_connection
        )

        with raw_connection.cursor() as cur:

            cur.execute(
                f"""
                CREATE TEMP TABLE {stage_table} (
                    id_key VARCHAR(150),
                    lat_gmtco DOUBLE PRECISION,
                    lon_gmtco DOUBLE PRECISION,
                    temp_primary DOUBLE PRECISION,
                    temp_background DOUBLE PRECISION,
                    rh_primary DOUBLE PRECISION,
                    area_primary DOUBLE PRECISION,
                    cloud_mask_fixed VARCHAR(50),
                    sample_m10 DOUBLE PRECISION,
                    line_m10 DOUBLE PRECISION,
                    sensor VARCHAR(20),
                    vnf_version VARCHAR(20),
                    mscan_date DATE,
                    mscan_time VARCHAR(50),
                    ltz_date DATE,
                    ltz_time VARCHAR(50)
                )
                ON COMMIT DROP
                """
            )

            copy_sql = f"""
                COPY {stage_table} (
                    id_key,
                    lat_gmtco,
                    lon_gmtco,
                    temp_primary,
                    temp_background,
                    rh_primary,
                    area_primary,
                    cloud_mask_fixed,
                    sample_m10,
                    line_m10,
                    sensor,
                    vnf_version,
                    mscan_date,
                    mscan_time,
                    ltz_date,
                    ltz_time
                )
                FROM STDIN
            """

            with cur.copy(
                copy_sql
            ) as copy:

                for row in df.itertuples(
                    index=False,
                    name=None
                ):
                    copy.write_row(
                        row
                    )

            # =================================================
            # TEMP TABLE -> REAL TABLE
            # =================================================

            cur.execute(
                f"""
                INSERT INTO vnf_detections (
                    id_key,
                    lat_gmtco,
                    lon_gmtco,
                    location,
                    temp_primary,
                    temp_background,
                    rh_primary,
                    area_primary,
                    cloud_mask_fixed,
                    sample_m10,
                    line_m10,
                    sensor,
                    vnf_version,
                    mscan_date,
                    mscan_time,
                    ltz_date,
                    ltz_time,
                    processing_state,
                    matched_object_uid,
                    ingestion_batch_id
                )

                SELECT
                    id_key,
                    lat_gmtco,
                    lon_gmtco,

                    ST_SetSRID(
                        ST_MakePoint(
                            lon_gmtco,
                            lat_gmtco
                        ),
                        4326
                    )::geography,

                    temp_primary,
                    temp_background,
                    rh_primary,
                    area_primary,
                    cloud_mask_fixed,
                    sample_m10,
                    line_m10,
                    sensor,
                    vnf_version,
                    mscan_date,
                    mscan_time,
                    ltz_date,
                    ltz_time,

                    'CANDIDATE',
                    NULL,
                    %s

                FROM {stage_table}

                ON CONFLICT (id_key)
                DO NOTHING
                """,
                (
                    batch_id,
                )
            )

        db.commit()

    except Exception:
        db.rollback()

        logger.exception(
            "VNF COPY ingestion failed"
        )

        raise

    # ========================================================
    # 7. COUNT INSERTED
    # ========================================================

    inserted_count = (
        db.execute(
            text("""
                SELECT COUNT(*)
                FROM vnf_detections
                WHERE ingestion_batch_id = :batch_id
            """),
            {
                "batch_id":
                    batch_id
            }
        )
        .scalar()
    )

    inserted_count = int(
        inserted_count or 0
    )

    duplicates = (
        original_count
        - inserted_count
    )

    elapsed = (
        time.perf_counter()
        - start
    )

    logger.info(
        "VNF COPY ingestion | "
        "input=%s | inserted=%s | "
        "duplicates=%s | %.2fs",
        original_count,
        inserted_count,
        duplicates,
        elapsed
    )

    return {
        "input":
            original_count,

        "inserted":
            inserted_count,

        "duplicates":
            duplicates,

        "batch_id":
            batch_id
    }