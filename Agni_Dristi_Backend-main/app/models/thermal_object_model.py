from sqlalchemy import (
    BigInteger,
    Float,
    Integer,
    String
)

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geography

from app.core.database import Base


class ThermalObject(Base):
    __tablename__ = "thermal_objects"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    object_uid: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True
    )

    stage3_object_id: Mapped[str | None] = mapped_column(
        String(50)
    )

    # -------------------------
    # LOCATION
    # -------------------------

    object_radius_m: Mapped[float | None] = mapped_column(
        Float
    )

    latitude: Mapped[float] = mapped_column(
        Float,
        index=True
    )

    longitude: Mapped[float] = mapped_column(
        Float,
        index=True
    )

    location: Mapped[object | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=True)
    )

    # -------------------------
    # CLASSIFICATION
    # -------------------------

    classification_label: Mapped[str | None] = mapped_column(
        String(100),
        index=True
    )

    classification_source: Mapped[str | None] = mapped_column(
        String(100)
    )

    predicted_label_confidence: Mapped[float | None] = mapped_column(
        Float
    )

    # -------------------------
    # TEMPORAL FEATURES
    # -------------------------

    detection_count: Mapped[int | None] = mapped_column(
        Integer
    )

    active_months: Mapped[int | None] = mapped_column(
        Integer
    )

    persistence_ratio: Mapped[float | None] = mapped_column(
        Float
    )

    longest_active_run: Mapped[int | None] = mapped_column(
        Integer
    )

    max_inactive_gap: Mapped[int | None] = mapped_column(
        Integer
    )

    # -------------------------
    # TEMPERATURE FEATURES
    # -------------------------

    temp_mean: Mapped[float | None] = mapped_column(Float)
    temp_median: Mapped[float | None] = mapped_column(Float)
    temp_min: Mapped[float | None] = mapped_column(Float)
    temp_max: Mapped[float | None] = mapped_column(Float)
    temp_std: Mapped[float | None] = mapped_column(Float)

    temp_range: Mapped[float | None] = mapped_column(Float)
    temp_cv: Mapped[float | None] = mapped_column(Float)

    # -------------------------
    # AREA FEATURES
    # -------------------------

    area_mean: Mapped[float | None] = mapped_column(Float)
    area_std: Mapped[float | None] = mapped_column(Float)
    area_cv: Mapped[float | None] = mapped_column(Float)

    # -------------------------
    # RADIANT HEAT FEATURES
    # -------------------------

    rh_mean: Mapped[float | None] = mapped_column(Float)
    rh_std: Mapped[float | None] = mapped_column(Float)
    rh_cv: Mapped[float | None] = mapped_column(Float)

    # -------------------------
    # THERMAL FINGERPRINT
    # -------------------------

    thermal_fingerprint: Mapped[dict | None] = mapped_column(
        JSONB
    )

    # -------------------------
    # OBJECT MATCHING
    # -------------------------

    match_distance_km: Mapped[float | None] = mapped_column(
        Float
    )