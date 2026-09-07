import pandas as pd

from app.core.database import SessionLocal
from app.models.thermal_object_model import ThermalObject
from app.services.vnf.vnf_pipeline_service import process_vnf_data


CSV_PATH = "VNF_INDIA_2026.csv"


def main():

    print(
        "\n========== "
        "OBJECT RADIUS BACKFILL "
        "==========\n"
    )

    # ========================================================
    # 1. LOAD SAME HISTORICAL VNF DATASET
    # ========================================================

    df = pd.read_csv(
        CSV_PATH,
        low_memory=False
    )

    print(
        f"Input detections: "
        f"{len(df):,}"
    )

    # ========================================================
    # 2. REBUILD OBJECT FEATURES
    # ========================================================

    objects = process_vnf_data(
        df
    )

    print(
        f"Pipeline objects: "
        f"{len(objects):,}"
    )

    if objects.empty:
        print(
            "No objects produced."
        )

        return

    if (
        "object_radius_m"
        not in objects.columns
    ):
        raise ValueError(
            "object_radius_m is missing "
            "from pipeline output."
        )

    # ========================================================
    # 3. UPDATE EXISTING THERMAL OBJECTS
    # ========================================================

    db = SessionLocal()

    updated = 0
    missing = 0

    try:

        for _, row in objects.iterrows():

            stage3_id = str(
                row[
                    "stage3_object_id"
                ]
            )

            obj = (
                db.query(
                    ThermalObject
                )

                .filter(
                    ThermalObject
                    .stage3_object_id
                    == stage3_id
                )

                .first()
            )

            if obj is None:
                missing += 1
                continue

            radius = row[
                "object_radius_m"
            ]

            if pd.isna(radius):
                continue

            obj.object_radius_m = (
                float(radius)
            )

            updated += 1

        db.commit()

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()

    print(
        "\n========== RESULT =========="
    )

    print(
        f"Updated : {updated}"
    )

    print(
        f"Missing : {missing}"
    )


if __name__ == "__main__":
    main()