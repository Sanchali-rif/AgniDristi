from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.firms_detection_model import FIRMSDetection


router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


@router.get("/summary")
def get_monitoring_summary(db: Session = Depends(get_db)):
    total = db.query(func.count(FIRMSDetection.id)).scalar()

    matched = (
        db.query(func.count(FIRMSDetection.id))
        .filter(FIRMSDetection.is_known_persistent_source.is_(True))
        .scalar()
    )

    unmatched = (
        db.query(func.count(FIRMSDetection.id))
        .filter(FIRMSDetection.is_known_persistent_source.is_(False))
        .scalar()
    )

    latest_date = db.query(func.max(FIRMSDetection.acq_date)).scalar()

    return {
        "total_detections": total,
        "matched_persistent": matched,
        "unmatched": unmatched,
        "latest_acquisition_date": latest_date
    }



@router.get("/recent")
def get_recent_detections(limit: int = 100, db: Session = Depends(get_db)):
    detections = (
        db.query(FIRMSDetection)
        .order_by(FIRMSDetection.acq_date.desc(), FIRMSDetection.acq_time.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "firms_uid": d.firms_uid,
            "latitude": d.latitude,
            "longitude": d.longitude,
            "acq_date": d.acq_date,
            "acq_time": d.acq_time,
            "frp": d.frp,
            "matched_object_uid": d.matched_object_uid,
            "match_distance_km": d.match_distance_km,
            "is_known_persistent_source": d.is_known_persistent_source
        }
        for d in detections
    ]



@router.get("/unmatched")
def get_unmatched_detections(limit: int = 100, db: Session = Depends(get_db)):
    detections = (
        db.query(FIRMSDetection)
        .filter(FIRMSDetection.is_known_persistent_source.is_(False))
        .order_by(FIRMSDetection.acq_date.desc(), FIRMSDetection.acq_time.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "firms_uid": d.firms_uid,
            "latitude": d.latitude,
            "longitude": d.longitude,
            "acq_date": d.acq_date,
            "acq_time": d.acq_time,
            "frp": d.frp
        }
        for d in detections
    ]