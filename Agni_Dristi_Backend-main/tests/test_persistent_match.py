from app.core.database import SessionLocal
from app.models.thermal_object_model import ThermalObject
from app.services.matching.batch_matching_service import batch_match_firms_points


db = SessionLocal()

try:
    # Pick one real persistent thermal object from Neon
    obj = (
        db.query(ThermalObject)
        .filter(ThermalObject.location.isnot(None))
        .first()
    )

    if not obj:
        print("No thermal objects found")
        exit()

    print("\nREFERENCE THERMAL OBJECT")
    print("------------------------")
    print("Object UID :", obj.object_uid)
    print("Latitude   :", obj.latitude)
    print("Longitude  :", obj.longitude)
    print("Class      :", obj.classification_label)

    # Create a FIRMS point extremely close to this object
    test_point = {
        "firms_uid": "TEST_PERSISTENT_POINT",
        "latitude": obj.latitude + 0.0002,
        "longitude": obj.longitude + 0.0002
    }

    print("\nTEST FIRMS POINT")
    print("----------------")
    print("Latitude  :", test_point["latitude"])
    print("Longitude :", test_point["longitude"])

    matches = batch_match_firms_points(
        db,
        [test_point],
        threshold_m=550
    )

    result = matches["TEST_PERSISTENT_POINT"]

    print("\nMATCH RESULT")
    print("------------")
    print("Matched Object :", result["matched_object_uid"])
    print("Distance (km)  :", result["match_distance_km"])
    print(
        "Known Persistent:",
        result["is_known_persistent_source"]
    )

finally:
    db.close()

