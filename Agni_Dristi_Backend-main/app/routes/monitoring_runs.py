from fastapi import (
    APIRouter,
    Depends,
    Query,
    HTTPException
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.monitoring_run_model import MonitoringRun

from app.services.firms.firms_runner_service import (
    run_firms_monitoring
)


router = APIRouter(
    prefix="/monitoring/runs",
    tags=["Monitoring Runs"]
)


# ============================================================
# MANUAL FIRMS MONITORING TRIGGER
# ============================================================

@router.post("/trigger")
def trigger_firms_monitoring(
    day_range: int = Query(
        1,
        ge=1,
        le=10,
        description="Number of FIRMS days to fetch"
    )
):
    try:
        return run_firms_monitoring(
            day_range=day_range,
            trigger_type="MANUAL"
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"FIRMS monitoring failed: "
                f"{str(exc)}"
            )
        )


# ============================================================
# LATEST MONITORING RUN
# ============================================================

@router.get("/latest")
def get_latest_monitoring_run(
    db: Session = Depends(get_db)
):
    run = (
        db.query(MonitoringRun)
        .order_by(
            MonitoringRun.id.desc()
        )
        .first()
    )

    if not run:
        return {
            "status": "no_runs",
            "message": (
                "No FIRMS monitoring runs "
                "recorded yet."
            )
        }

    return {
        "id": run.id,

        "run_uid":
            run.run_uid,

        "trigger_type":
            run.trigger_type,

        "attempt":
            run.attempt,

        "retry_of_run_uid":
            run.retry_of_run_uid,

        "status":
            run.status,

        "started_at":
            run.started_at,

        "finished_at":
            run.finished_at,

        "duration_seconds":
            run.duration_seconds,

        "fetched":
            run.fetched,

        "inserted":
            run.inserted,

        "duplicates":
            run.duplicates,

        "matched":
            run.matched,

        "unmatched":
            run.unmatched,

        "alerts_created":
            run.alerts_created,

        "error_message":
            run.error_message
    }


# ============================================================
# MONITORING RUN HISTORY
# ============================================================

@router.get("")
def get_monitoring_runs(
    limit: int = Query(
        20,
        ge=1,
        le=100
    ),
    db: Session = Depends(get_db)
):
    runs = (
        db.query(
            MonitoringRun
        )
        .order_by(
            MonitoringRun.id.desc()
        )
        .limit(
            limit
        )
        .all()
    )

    return {
        "count": len(runs),

        "runs": [
            {
                "id":
                    run.id,

                "run_uid":
                    run.run_uid,

                "trigger_type":
                    run.trigger_type,

                "attempt":
                    run.attempt,

                "retry_of_run_uid":
                    run.retry_of_run_uid,

                "status":
                    run.status,

                "started_at":
                    run.started_at,

                "finished_at":
                    run.finished_at,

                "duration_seconds":
                    run.duration_seconds,

                "fetched":
                    run.fetched,

                "inserted":
                    run.inserted,

                "duplicates":
                    run.duplicates,

                "matched":
                    run.matched,

                "unmatched":
                    run.unmatched,

                "alerts_created":
                    run.alerts_created,

                "error_message":
                    run.error_message
            }

            for run in runs
        ]
    }