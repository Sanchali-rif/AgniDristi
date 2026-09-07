import time
import uuid
from datetime import datetime, timezone

from app.core.database import SessionLocal
from app.core.logger import get_logger

from app.models.monitoring_run_model import MonitoringRun

from app.services.firms.firms_api_service import (
    fetch_latest_firms
)

from app.services.firms.firms_batch_service import (
    process_firms_dataframe
)


logger = get_logger(__name__)


def _generate_run_uid():
    return (
        "FIRMS_"
        + uuid.uuid4().hex.upper()
    )


def run_firms_monitoring(
    day_range: int = 1,
    trigger_type: str = "MANUAL",
    retry_of_run_uid: str | None = None,
    attempt: int = 1
):
    start = time.perf_counter()

    run_uid = _generate_run_uid()

    db = SessionLocal()
    

    monitoring_run = MonitoringRun(
        run_uid=run_uid,
        trigger_type=trigger_type,
        status="RUNNING",
        attempt=attempt,
        retry_of_run_uid=retry_of_run_uid,
        started_at=datetime.now(
            timezone.utc
        ),
        fetched=0,
        inserted=0,
        duplicates=0,
        matched=0,
        unmatched=0,
        alerts_created=0
    )

    try:
        # ====================================================
        # 1. CREATE RUN RECORD
        # ====================================================

        db.add(
            monitoring_run
        )

        db.commit()

        db.refresh(
            monitoring_run
        )

        logger.info(
            "========== FIRMS MONITORING STARTED =========="
        )

        logger.info(
            "run_uid=%s | trigger=%s | attempt=%s",
            run_uid,
            trigger_type,
            attempt
        )

        # ====================================================
        # 2. FETCH NASA FIRMS
        # ====================================================

        logger.info(
            "Fetching latest FIRMS detections"
        )

        df = fetch_latest_firms(
            day_range=day_range
        )

        fetched = len(df)

        monitoring_run.fetched = fetched

        db.commit()

        logger.info(
            "FIRMS fetch finished | fetched=%s",
            fetched
        )

        # ====================================================
        # 3. NO DATA
        # ====================================================

        if df.empty:

            elapsed = (
                time.perf_counter()
                - start
            )

            monitoring_run.status = (
                "COMPLETED"
            )

            monitoring_run.finished_at = (
                datetime.now(
                    timezone.utc
                )
            )

            monitoring_run.duration_seconds = (
                round(
                    elapsed,
                    2
                )
            )

            db.commit()

            return {
                "run_uid":
                    run_uid,

                "trigger_type":
                    trigger_type,

                "status":
                    "completed",

                "fetched":
                    0,

                "total_rows":
                    0,

                "inserted":
                    0,

                "duplicates":
                    0,

                "matched_persistent":
                    0,

                "unmatched":
                    0,

                "alerts_created":
                    0,

                "alerts": {
                    "unmatched_anomaly": 0,
                    "repeated_unmatched": 0,
                    "abnormal_known_source": 0
                },

                "duration_seconds":
                    round(
                        elapsed,
                        2
                    )
            }

        # ====================================================
        # 4. PROCESS FIRMS
        # ====================================================

        result = (
            process_firms_dataframe(
                db,
                df
            )
        )

        # ====================================================
        # 5. UPDATE MONITORING RUN
        # ====================================================

        elapsed = (
            time.perf_counter()
            - start
        )

        monitoring_run.status = (
            "COMPLETED"
        )

        monitoring_run.finished_at = (
            datetime.now(
                timezone.utc
            )
        )

        monitoring_run.duration_seconds = (
            round(
                elapsed,
                2
            )
        )

        monitoring_run.inserted = int(
            result.get(
                "inserted",
                0
            )
        )

        monitoring_run.duplicates = int(
            result.get(
                "duplicates",
                0
            )
        )

        monitoring_run.matched = int(
            result.get(
                "matched_persistent",
                0
            )
        )

        monitoring_run.unmatched = int(
            result.get(
                "unmatched",
                0
            )
        )

        monitoring_run.alerts_created = int(
            result.get(
                "alerts_created",
                0
            )
        )

        monitoring_run.error_message = None

        db.commit()

        logger.info(
            "========== FIRMS MONITORING FINISHED =========="
        )

        logger.info(
            "run_uid=%s | duration=%.2fs",
            run_uid,
            elapsed
        )

        return {
            "run_uid":
                run_uid,

            "trigger_type":
                trigger_type,

            "status":
                "completed",

            "fetched":
                fetched,

            **result,

            "duration_seconds":
                round(
                    elapsed,
                    2
                )
        }

    except Exception as exc:

        db.rollback()

        elapsed = (
            time.perf_counter()
            - start
        )

        logger.exception(
            "FIRMS monitoring failed | run_uid=%s",
            run_uid
        )

        # ----------------------------------------------------
        # Separate DB transaction for failure logging
        # ----------------------------------------------------

        try:
            failed_run = (
                db.query(
                    MonitoringRun
                )
                .filter(
                    MonitoringRun.run_uid
                    == run_uid
                )
                .first()
            )

            if failed_run:

                failed_run.status = (
                    "FAILED"
                )

                failed_run.finished_at = (
                    datetime.now(
                        timezone.utc
                    )
                )

                failed_run.duration_seconds = (
                    round(
                        elapsed,
                        2
                    )
                )

                failed_run.error_message = (
                    str(exc)[:2000]
                )

                db.commit()

        except Exception:
            db.rollback()

            logger.exception(
                "Could not save FIRMS failure state"
            )

        raise

    finally:
        db.close()