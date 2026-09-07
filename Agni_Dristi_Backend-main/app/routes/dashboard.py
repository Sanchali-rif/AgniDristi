from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.models.thermal_object_model import ThermalObject
from app.models.firms_detection_model import FIRMSDetection
from app.models.monitoring_run_model import MonitoringRun
from app.models.alert_model import Alert


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# ============================================================
# 1. OVERALL SUMMARY
# ============================================================

@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db)
):
    total_objects = (
        db.query(
            func.count(
                ThermalObject.id
            )
        )
        .scalar()
        or 0
    )

    total_firms = (
        db.query(
            func.count(
                FIRMSDetection.id
            )
        )
        .scalar()
        or 0
    )

    matched_firms = (
        db.query(
            func.count(
                FIRMSDetection.id
            )
        )
        .filter(
            FIRMSDetection.is_known_persistent_source
            == True
        )
        .scalar()
        or 0
    )

    unmatched_firms = (
        db.query(
            func.count(
                FIRMSDetection.id
            )
        )
        .filter(
            FIRMSDetection.is_known_persistent_source
            == False
        )
        .scalar()
        or 0
    )

    total_alerts = (
        db.query(
            func.count(
                Alert.id
            )
        )
        .scalar()
        or 0
    )

    latest_run = (
        db.query(
            MonitoringRun
        )
        .order_by(
            MonitoringRun.id.desc()
        )
        .first()
    )

    latest_monitoring = None

    if latest_run:
        latest_monitoring = {
            "run_uid":
                latest_run.run_uid,

            "status":
                latest_run.status,

            "trigger_type":
                latest_run.trigger_type,

            "started_at":
                latest_run.started_at,

            "finished_at":
                latest_run.finished_at,

            "duration_seconds":
                latest_run.duration_seconds,

            "fetched":
                latest_run.fetched,

            "inserted":
                latest_run.inserted,

            "matched":
                latest_run.matched,

            "unmatched":
                latest_run.unmatched,

            "alerts_created":
                latest_run.alerts_created
        }

    return {
        "thermal_objects":
            int(total_objects),

        "firms_detections":
            int(total_firms),

        "matched_firms":
            int(matched_firms),

        "unmatched_firms":
            int(unmatched_firms),

        "alerts":
            int(total_alerts),

        "latest_monitoring":
            latest_monitoring
    }


# ============================================================
# 2. CLASS DISTRIBUTION
# ============================================================

@router.get("/classes")
def get_class_distribution(
    db: Session = Depends(get_db)
):
    rows = (
        db.query(
            ThermalObject.classification_label,
            func.count(
                ThermalObject.id
            )
        )
        .group_by(
            ThermalObject.classification_label
        )
        .order_by(
            func.count(
                ThermalObject.id
            ).desc()
        )
        .all()
    )

    classes = []

    for label, count in rows:
        classes.append({
            "label":
                label or "Unknown",

            "count":
                int(count)
        })

    return {
        "count":
            len(classes),

        "classes":
            classes
    }


# ============================================================
# 3. THERMAL OBJECT MAP / LIST
# ============================================================

@router.get("/objects")
def get_thermal_objects(
    limit: int = Query(
        500,
        ge=1,
        le=5000
    ),

    offset: int = Query(
        0,
        ge=0
    ),

    classification: str | None = Query(
        None
    ),

    db: Session = Depends(get_db)
):
    query = db.query(
        ThermalObject
    )

    if classification:
        query = query.filter(
            ThermalObject.classification_label
            == classification
        )

    total = (
        query.count()
    )

    objects = (
        query
        .order_by(
            ThermalObject.id.asc()
        )
        .offset(
            offset
        )
        .limit(
            limit
        )
        .all()
    )

    return {
        "total":
            total,

        "limit":
            limit,

        "offset":
            offset,

        "objects": [
            {
                "object_uid":
                    obj.object_uid,

                "latitude":
                    obj.latitude,

                "longitude":
                    obj.longitude,

                "classification_label":
                    obj.classification_label,

                "classification_source":
                    obj.classification_source,

                "confidence":
                    obj.predicted_label_confidence,

                "detection_count":
                    obj.detection_count,

                "active_months":
                    obj.active_months,

                "persistence_ratio":
                    obj.persistence_ratio,

                "temp_mean":
                    obj.temp_mean,

                "temp_max":
                    obj.temp_max,

                "object_radius_m":
                    getattr(
                        obj,
                        "object_radius_m",
                        None
                    )
            }

            for obj in objects
        ]
    }


# ============================================================
# 4. SINGLE THERMAL OBJECT DETAILS
# ============================================================

@router.get("/objects/{object_uid}")
def get_thermal_object_details(
    object_uid: str,
    db: Session = Depends(get_db)
):
    obj = (
        db.query(
            ThermalObject
        )
        .filter(
            ThermalObject.object_uid
            == object_uid
        )
        .first()
    )

    if obj is None:
        raise HTTPException(
            status_code=404,
            detail="Thermal object not found."
        )

    recent_firms = (
        db.query(
            FIRMSDetection
        )
        .filter(
            FIRMSDetection.matched_object_uid
            == object_uid
        )
        .order_by(
            FIRMSDetection.id.desc()
        )
        .limit(
            20
        )
        .all()
    )

    return {
        "object_uid":
            obj.object_uid,

        "stage3_object_id":
            obj.stage3_object_id,

        "location": {
            "latitude":
                obj.latitude,

            "longitude":
                obj.longitude
        },

        "classification": {
            "label":
                obj.classification_label,

            "source":
                obj.classification_source,

            "confidence":
                obj.predicted_label_confidence
        },

        "temporal": {
            "detection_count":
                obj.detection_count,

            "active_months":
                obj.active_months,

            "persistence_ratio":
                obj.persistence_ratio,

            "longest_active_run":
                obj.longest_active_run,

            "max_inactive_gap":
                obj.max_inactive_gap
        },

        "temperature": {
            "mean":
                obj.temp_mean,

            "median":
                obj.temp_median,

            "min":
                obj.temp_min,

            "max":
                obj.temp_max,

            "std":
                obj.temp_std,

            "range":
                obj.temp_range,

            "cv":
                obj.temp_cv
        },

        "area": {
            "mean":
                obj.area_mean,

            "std":
                obj.area_std,

            "cv":
                obj.area_cv
        },

        "radiant_heat": {
            "mean":
                obj.rh_mean,

            "std":
                obj.rh_std,

            "cv":
                obj.rh_cv
        },

        "thermal_fingerprint":
            obj.thermal_fingerprint,

        "object_radius_m":
            getattr(
                obj,
                "object_radius_m",
                None
            ),

        "recent_firms": [
            {
                "firms_uid":
                    detection.firms_uid,

                "latitude":
                    detection.latitude,

                "longitude":
                    detection.longitude,

                "bright_ti4":
                    detection.bright_ti4,

                "bright_ti5":
                    detection.bright_ti5,

                "frp":
                    detection.frp,

                "acq_date":
                    detection.acq_date,

                "acq_time":
                    detection.acq_time,

                "satellite":
                    detection.satellite,

                "confidence":
                    detection.confidence,

                "match_distance_km":
                    detection.match_distance_km
            }

            for detection in recent_firms
        ]
    }


# ============================================================
# 5. RECENT FIRMS DETECTIONS
# ============================================================

@router.get("/firms/recent")
def get_recent_firms(
    limit: int = Query(
        200,
        ge=1,
        le=2000
    ),

    matched_only: bool | None = Query(
        None
    ),

    db: Session = Depends(get_db)
):
    query = db.query(
        FIRMSDetection
    )

    if matched_only is True:
        query = query.filter(
            FIRMSDetection.is_known_persistent_source
            == True
        )

    elif matched_only is False:
        query = query.filter(
            FIRMSDetection.is_known_persistent_source
            == False
        )

    detections = (
        query
        .order_by(
            FIRMSDetection.id.desc()
        )
        .limit(
            limit
        )
        .all()
    )

    return {
        "count":
            len(detections),

        "detections": [
            {
                "firms_uid":
                    d.firms_uid,

                "latitude":
                    d.latitude,

                "longitude":
                    d.longitude,

                "frp":
                    d.frp,

                "bright_ti4":
                    d.bright_ti4,

                "bright_ti5":
                    d.bright_ti5,

                "acq_date":
                    d.acq_date,

                "acq_time":
                    d.acq_time,

                "satellite":
                    d.satellite,

                "confidence":
                    d.confidence,

                "daynight":
                    d.daynight,

                "known_source":
                    d.is_known_persistent_source,

                "matched_object_uid":
                    d.matched_object_uid,

                "match_distance_km":
                    d.match_distance_km
            }

            for d in detections
        ]
    }


# ============================================================
# 6. ALERTS
# ============================================================

@router.get("/alerts")
def get_dashboard_alerts(
    limit: int = Query(
        100,
        ge=1,
        le=1000
    ),

    alert_type: str | None = Query(
        None
    ),

    db: Session = Depends(get_db)
):
    query = db.query(
        Alert
    )

    if alert_type:
        query = query.filter(
            Alert.alert_type
            == alert_type
        )

    alerts = (
        query
        .order_by(
            Alert.id.desc()
        )
        .limit(
            limit
        )
        .all()
    )

    result = []

    for alert in alerts:
        result.append({
            "id":
                alert.id,

            "alert_type":
                alert.alert_type,

            "firms_uid":
                getattr(
                    alert,
                    "firms_uid",
                    None
                ),

            "object_uid":
                getattr(
                    alert,
                    "object_uid",
                    None
                ),

            "latitude":
                getattr(
                    alert,
                    "latitude",
                    None
                ),

            "longitude":
                getattr(
                    alert,
                    "longitude",
                    None
                ),

            "severity":
                getattr(
                    alert,
                    "severity",
                    None
                ),

            "message":
                getattr(
                    alert,
                    "message",
                    None
                ),

            "created_at":
                getattr(
                    alert,
                    "created_at",
                    None
                )
        })

    return {
        "count":
            len(result),

        "alerts":
            result
    }


# ============================================================
# 7. MONITORING STATUS
# ============================================================

@router.get("/monitoring")
def get_dashboard_monitoring(
    db: Session = Depends(get_db)
):
    latest = (
        db.query(
            MonitoringRun
        )
        .order_by(
            MonitoringRun.id.desc()
        )
        .first()
    )

    total_runs = (
        db.query(
            func.count(
                MonitoringRun.id
            )
        )
        .scalar()
        or 0
    )

    failed_runs = (
        db.query(
            func.count(
                MonitoringRun.id
            )
        )
        .filter(
            MonitoringRun.status
            == "FAILED"
        )
        .scalar()
        or 0
    )

    completed_runs = (
        db.query(
            func.count(
                MonitoringRun.id
            )
        )
        .filter(
            MonitoringRun.status
            == "COMPLETED"
        )
        .scalar()
        or 0
    )

    latest_data = None

    if latest:
        latest_data = {
            "run_uid":
                latest.run_uid,

            "trigger_type":
                latest.trigger_type,

            "status":
                latest.status,

            "attempt":
                latest.attempt,

            "started_at":
                latest.started_at,

            "finished_at":
                latest.finished_at,

            "duration_seconds":
                latest.duration_seconds,

            "fetched":
                latest.fetched,

            "inserted":
                latest.inserted,

            "duplicates":
                latest.duplicates,

            "matched":
                latest.matched,

            "unmatched":
                latest.unmatched,

            "alerts_created":
                latest.alerts_created,

            "error_message":
                latest.error_message
        }

    return {
        "total_runs":
            int(total_runs),

        "completed_runs":
            int(completed_runs),

        "failed_runs":
            int(failed_runs),

        "latest":
            latest_data
    }