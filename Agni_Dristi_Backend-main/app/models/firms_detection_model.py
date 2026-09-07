from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geography

from app.core.database import Base


class FIRMSDetection(Base):
    __tablename__ = "firms_detections"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Used to prevent the same FIRMS point being inserted twice
    firms_uid: Mapped[str] = mapped_column(String(200), unique=True, index=True)

    # Location
    latitude: Mapped[float] = mapped_column(Float, index=True)
    longitude: Mapped[float] = mapped_column(Float, index=True)
    location: Mapped[object | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=True)
    )

    # FIRMS thermal information
    bright_ti4: Mapped[float | None] = mapped_column(Float)
    bright_ti5: Mapped[float | None] = mapped_column(Float)
    frp: Mapped[float | None] = mapped_column(Float)

    # Pixel information
    scan: Mapped[float | None] = mapped_column(Float)
    track: Mapped[float | None] = mapped_column(Float)

    # Acquisition information
    acq_date: Mapped[date] = mapped_column(Date, index=True)
    acq_time: Mapped[str] = mapped_column(String(10))

    satellite: Mapped[str | None] = mapped_column(String(30))
    instrument: Mapped[str | None] = mapped_column(String(30))
    confidence: Mapped[str | None] = mapped_column(String(30))
    version: Mapped[str | None] = mapped_column(String(30))
    daynight: Mapped[str | None] = mapped_column(String(10))

    # Matching result
    matched_object_uid: Mapped[str | None] = mapped_column(String(50), index=True)
    match_distance_km: Mapped[float | None] = mapped_column(Float)

    is_known_persistent_source: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # Backend metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)