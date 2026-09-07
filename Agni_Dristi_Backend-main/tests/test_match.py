from app.core.database import SessionLocal
from app.services.matching.matching_service import find_nearest_thermal_object


db = SessionLocal()

try:
    result = find_nearest_thermal_object(
        db,
        latitude=23.66800,
        longitude=86.92300
    )

    if result:
        print("Object:", result["object"].object_uid)
        print("Distance km:", result["distance_km"])
        print("Matched:", result["is_match"])
    else:
        print("No object within 550 metres")

finally:
    db.close()