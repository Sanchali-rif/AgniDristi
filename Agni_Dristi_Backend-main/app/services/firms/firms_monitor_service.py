from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.firms_detection_model import FIRMSDetection
from app.services.matching.matching_service import find_nearest_thermal_object


def generate_firms_uid(row: dict) -> str:
    return (
        f"{row.get('satellite')}_"
        f"{row.get('acq_date')}_"
        f"{row.get('acq_time')}_"
        f"{row.get('latitude')}_"
        f"{row.get('longitude')}"
    )


def process_firms_detection(db: Session, row: dict):
    firms_uid = generate_firms_uid(row)

    existing = (
        db.query(FIRMSDetection)
        .filter(FIRMSDetection.firms_uid == firms_uid)
        .first()
    )

    if existing:
        return {
            "status": "duplicate",
            "firms_uid": firms_uid
        }

    match = find_nearest_thermal_object(
        db,
        latitude=float(row["latitude"]),
        longitude=float(row["longitude"])
    )

    matched_object_uid = None
    match_distance_km = None
    is_known_persistent_source = False

    if match:
        match_distance_km = match["distance_km"]

        if match["is_match"]:
            matched_object_uid = match["object"].object_uid
            is_known_persistent_source = True

    detection = FIRMSDetection(
        firms_uid=firms_uid,
        latitude=float(row["latitude"]),
        longitude=float(row["longitude"]),

        location=func.ST_SetSRID(
            func.ST_MakePoint(
                float(row["longitude"]),
                float(row["latitude"])
            ),
            4326
        ),

        bright_ti4=row.get("bright_ti4"),
        bright_ti5=row.get("bright_ti5"),
        frp=row.get("frp"),
        scan=row.get("scan"),
        track=row.get("track"),

        acq_date=row["acq_date"],
        acq_time=str(row["acq_time"]),

        satellite=row.get("satellite"),
        instrument=row.get("instrument"),
        confidence=str(row.get("confidence")) if row.get("confidence") is not None else None,
        version=row.get("version"),
        daynight=row.get("daynight"),

        matched_object_uid=matched_object_uid,
        match_distance_km=match_distance_km,
        is_known_persistent_source=is_known_persistent_source
    )

    db.add(detection)
    db.commit()
    db.refresh(detection)

    return {
        "status": "inserted",
        "firms_uid": detection.firms_uid,
        "matched_object_uid": detection.matched_object_uid,
        "match_distance_km": detection.match_distance_km,
        "is_known_persistent_source": detection.is_known_persistent_source
    }