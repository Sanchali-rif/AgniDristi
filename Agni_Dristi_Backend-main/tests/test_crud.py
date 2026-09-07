from app.core.database import SessionLocal
from app.models.thermal_object_model import ThermalObject


db = SessionLocal()

try:
    # ---------------------------------
    # CREATE
    # ---------------------------------
    obj = ThermalObject(
        object_uid="OBJ_TEST_001",
        stage3_object_id="S3_TEST",

        latitude=23.66754,
        longitude=86.92285,

        classification_label="Metallurgical",
        classification_source="test",

        predicted_label_confidence=0.91,

        detection_count=25,
        active_months=8,
        persistence_ratio=0.67,
        longest_active_run=5,
        max_inactive_gap=2,

        temp_mean=1080.5,
        temp_median=1055.2,
        temp_min=850.0,
        temp_max=1450.0,
        temp_std=120.4,
        temp_range=600.0,
        temp_cv=0.11,

        area_mean=0.42,
        area_std=0.08,
        area_cv=0.19,

        rh_mean=1.8,
        rh_std=0.3,
        rh_cv=0.17,

        thermal_fingerprint={
            "FP_900_950K": 0.15,
            "FP_950_1000K": 0.21,
            "FP_1000_1050K": 0.18
        },

        match_distance_km=0.12
    )

    db.add(obj)
    db.commit()

    # refresh gives us DB-generated fields like id
    db.refresh(obj)

    print("Inserted object ID:", obj.id)

    # ---------------------------------
    # READ
    # ---------------------------------
    fetched = (
        db.query(ThermalObject)
        .filter(
            ThermalObject.object_uid == "OBJ_TEST_001"
        )
        .first()
    )

    print("Object UID:", fetched.object_uid)
    print("Class:", fetched.classification_label)
    print("Latitude:", fetched.latitude)
    print("Longitude:", fetched.longitude)
    print("Fingerprint:", fetched.thermal_fingerprint)

except Exception as e:
    db.rollback()
    print("Error:", e)

finally:
    db.close()