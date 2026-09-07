from app.core.database import SessionLocal
from app.services.vnf.vnf_candidate_matching_service import (
    match_vnf_candidates_to_known_objects
)


def main():
    db = SessionLocal()

    try:
        detection_ids = list(
            range(101, 201)
        )

        result = (
            match_vnf_candidates_to_known_objects(
                db,
                detection_ids
            )
        )

        print(result)

    finally:
        db.close()


if __name__ == "__main__":
    main()