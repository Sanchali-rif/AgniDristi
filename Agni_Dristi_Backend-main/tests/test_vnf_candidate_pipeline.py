from app.core.database import (
    SessionLocal
)

from app.services.vnf.vnf_candidate_pipeline_service import (
    run_candidate_pipeline
)


def main():

    db = SessionLocal()

    try:

        result = (
            run_candidate_pipeline(
                db,
                months=12
            )
        )

        print(
            "\n========== "
            "CANDIDATE PIPELINE "
            "=========="
        )

        print(
            "Status:",
            result[
                "status"
            ]
        )

        print(
            "Pipeline input:",
            result[
                "pipeline_input"
            ]
        )

        print(
            "Objects found:",
            result[
                "objects_found"
            ]
        )

        print(
            "Existing objects:",
            result[
                "existing_objects"
            ]
        )

        print(
            "New objects:",
            result[
                "new_objects"
            ]
        )

        print(
            "Persistent → KNOWN_OBJECT:",
            result[
                "persistent_known"
            ]
        )

        print(
            "Transient:",
            result[
                "transient"
            ]
        )

        print(
            "\n========== "
            "TEST COMPLETED "
            "=========="
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()