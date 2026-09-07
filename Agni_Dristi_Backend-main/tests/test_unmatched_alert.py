from datetime import date

from app.core.database import SessionLocal
from app.models.firms_detection_model import FIRMSDetection
from app.services.alerts.alert_service import create_unmatched_alert


def main():
    db = SessionLocal()

    try:
        detection = FIRMSDetection(
            firms_uid="TEST_UNMATCHED_ALERT_001",
            latitude=22.5000,
            longitude=88.3000,
            acq_date=date.today(),
            acq_time="1200",
            satellite="TEST",
            instrument="VIIRS",
            confidence="n",
            version="TEST",
            daynight="D",
            matched_object_uid=None,
            match_distance_km=None,
            is_known_persistent_source=False
        )

        db.add(detection)
        db.commit()
        db.refresh(detection)

        alert = create_unmatched_alert(
            db,
            detection
        )

        db.commit()

        if alert:
            print("ALERT CREATED")
            print("Type     :", alert.alert_type)
            print("Severity :", alert.severity)
            print("FIRMS UID:", alert.firms_uid)
            print("Message  :", alert.message)

        else:
            print("Alert already existed")

    finally:
        db.close()


if __name__ == "__main__":
    main()