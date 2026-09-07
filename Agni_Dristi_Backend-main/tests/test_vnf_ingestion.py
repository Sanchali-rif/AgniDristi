import pandas as pd

from app.core.database import SessionLocal
from app.services.vnf.vnf_ingestion_service import ingest_vnf_detections
from app.services.vnf.vnf_candidate_matching_service import (
    match_vnf_candidates_to_known_objects
)


CSV_PATH = "VNF_INDIA_2026.csv"


def main():
    df = pd.read_csv(
        CSV_PATH,
        low_memory=False
    )

    # Fresh test batch
    test_df = df.head(200).copy()

    db = SessionLocal()

    try:
        ingestion_result = ingest_vnf_detections(
            db,
            test_df
        )

        print("\nINGESTION:")
        print(ingestion_result)

        match_result = (
            match_vnf_candidates_to_known_objects(
                db,
                ingestion_result["inserted_ids"]
            )
        )

        print("\nKNOWN OBJECT MATCHING:")
        print(match_result)

    finally:
        db.close()


if __name__ == "__main__":
    main()