import pandas as pd

from app.core.database import SessionLocal
from app.models.thermal_object_model import ThermalObject
from app.services.vnf.vnf_object_sync_service import sync_vnf_objects


def main():
    db = SessionLocal()

    try:
        print("\n========== VNF OBJECT SYNC TEST ==========\n")

        # Get one object already stored in Neon
        existing = (
            db.query(ThermalObject)
            .first()
        )

        if existing is None:
            print("No existing thermal object found in database.")
            return

        print("Existing object:")
        print("UID       :", existing.object_uid)
        print("Latitude  :", existing.latitude)
        print("Longitude :", existing.longitude)
        print("Label     :", existing.classification_label)

        original_uid = existing.object_uid
        original_label = existing.classification_label
        original_confidence = existing.predicted_label_confidence

        # Fake VNF result at EXACTLY the same location.
        # Intentionally give it a different label/confidence.
        # These values MUST NOT overwrite the DB object.
        test_df = pd.DataFrame([
            {
                "stage3_object_id": "TEST_001",
                "latitude": existing.latitude,
                "longitude": existing.longitude,

                "predicted_label": "SHOULD_NOT_REPLACE",
                "predicted_label_confidence": 0.999,

                "detection_count": 999,
                "active_months": 12,
                "persistence_ratio": 1.0,

                "temp_mean": 999.0
            }
        ])

        print("\nRunning sync...")

        result = sync_vnf_objects(
            db,
            test_df
        )

        print("\nSync result:")
        print(result)

        # Reload object from database
        db.expire_all()

        after = (
            db.query(ThermalObject)
            .filter(
                ThermalObject.object_uid
                == original_uid
            )
            .first()
        )

        print("\nChecking existing object...")

        assert after is not None
        assert after.object_uid == original_uid
        assert after.classification_label == original_label
        assert (
            after.predicted_label_confidence
            == original_confidence
        )

        assert result["existing"] == 1
        assert result["inserted"] == 0

        print("\nPASS")
        print("Existing object detected.")
        print("No new object inserted.")
        print("Existing classification unchanged.")

    finally:
        db.close()


if __name__ == "__main__":
    main()