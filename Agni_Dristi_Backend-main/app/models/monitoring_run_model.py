import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Float,
    Integer,
    String,
    DateTime
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MonitoringRun(Base):
    __tablename__ = "monitoring_runs"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    # --------------------------------------------------------
    # RUN IDENTITY
    # --------------------------------------------------------

    run_uid: Mapped[str] = mapped_column(
        String(60),
        unique=True,
        index=True,
        default=lambda: (
            "FIRMS_"
            + uuid.uuid4().hex.upper()
        )
    )

    # MANUAL / SCHEDULED / RETRY
    trigger_type: Mapped[str] = mapped_column(
        String(20),
        default="MANUAL",
        index=True
    )

    # RUNNING / COMPLETED / FAILED
    status: Mapped[str] = mapped_column(
        String(20),
        default="RUNNING",
        index=True
    )

    # --------------------------------------------------------
    # RETRY INFORMATION
    # --------------------------------------------------------

    attempt: Mapped[int] = mapped_column(
        Integer,
        default=1
    )

    retry_of_run_uid: Mapped[str | None] = mapped_column(
        String(60),
        nullable=True,
        index=True
    )

    # --------------------------------------------------------
    # TIMING
    # --------------------------------------------------------

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    duration_seconds: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    # --------------------------------------------------------
    # FIRMS COUNTS
    # --------------------------------------------------------

    fetched: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    inserted: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    duplicates: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    matched: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    unmatched: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    alerts_created: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    # --------------------------------------------------------
    # ERROR
    # --------------------------------------------------------

    error_message: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True
    )