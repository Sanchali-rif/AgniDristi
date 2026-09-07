from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    alert_type: Mapped[str] = mapped_column(
        String(100),
        index=True
    )

    severity: Mapped[str] = mapped_column(
        String(30),
        index=True
    )

    firms_uid: Mapped[str | None] = mapped_column(
        String(200),
        index=True
    )

    object_uid: Mapped[str | None] = mapped_column(
        String(50),
        index=True
    )

    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    message: Mapped[str] = mapped_column(
        String(500)
    )

    resolved: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now
    )