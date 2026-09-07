from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.thermal_object_model import ThermalObject


MATCH_THRESHOLD_METERS = 550


def find_nearest_thermal_object(db: Session, latitude: float, longitude: float):
    firms_point = func.ST_SetSRID(
        func.ST_MakePoint(longitude, latitude),
        4326
    ).cast(ThermalObject.location.type)

    result = (
        db.query(
            ThermalObject,
            func.ST_Distance(
                ThermalObject.location,
                firms_point
            ).label("distance_m")
        )
        .filter(
            ThermalObject.location.isnot(None),
            func.ST_DWithin(
                ThermalObject.location,
                firms_point,
                MATCH_THRESHOLD_METERS
            )
        )
        .order_by("distance_m")
        .first()
    )

    if not result:
        return None

    obj, distance_m = result

    return {
        "object": obj,
        "distance_km": distance_m / 1000,
        "is_match": True
    }