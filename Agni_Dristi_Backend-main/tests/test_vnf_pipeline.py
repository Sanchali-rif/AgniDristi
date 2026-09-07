import pandas as pd

from app.core.database import SessionLocal
from app.services.vnf.vnf_pipeline_service import process_vnf_data
from app.services.vnf.vnf_object_sync_service import sync_vnf_objects


CSV_PATH = "VNF_INDIA_2026.csv"  # put your actual CSV path here


def main():

    print("\n========== VNF PIPELINE TEST ==========\n")

    # Load historical VNF data
    df = pd.read_csv(
        CSV_PATH,
        low_memory=False
    )

    print(f"Input detections: {len(df):,}")
    print(f"Input columns   : {len(df.columns)}")

    # Run complete VNF pipeline
    result = process_vnf_data(df)

    print(
        f"\nPersistent objects produced: "
        f"{len(result):,}"
    )

    if result.empty:
        print("No persistent objects produced.")
        return

    # --------------------------------------------------
    # DATABASE TEST
    # ONLY FIRST OBJECT
    # --------------------------------------------------

    db = SessionLocal()

    try:
        sync_result = sync_vnf_objects(
            db,
            result.head(1)
        )

        print("\n========== DATABASE SYNC ==========")
        print(sync_result)

    finally:
        db.close()

    print("\n========== TEST COMPLETED ==========")


if __name__ == "__main__":
    main()