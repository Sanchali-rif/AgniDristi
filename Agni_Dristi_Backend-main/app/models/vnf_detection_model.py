from datetime import date

from sqlalchemy import (
    BigInteger,
    Float,
    String,
    Date
)

from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geography

from app.core.database import Base


class VNFDetection(Base):
    __tablename__ = "vnf_detections"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    id_key: Mapped[str | None] = mapped_column(
        String(150),
        index=True
    )

    lat_gmtco: Mapped[float] = mapped_column(
        Float,
        index=True
    )

    lon_gmtco: Mapped[float] = mapped_column(
        Float,
        index=True
    )

    location: Mapped[object | None] = mapped_column(
        Geography(
            geometry_type="POINT",
            srid=4326,
            spatial_index=True
        )
    )

    temp_primary: Mapped[float | None] = mapped_column(
        Float
    )

    temp_background: Mapped[float | None] = mapped_column(
        Float
    )

    rh_primary: Mapped[float | None] = mapped_column(
        Float
    )

    area_primary: Mapped[float | None] = mapped_column(
        Float
    )

    cloud_mask_fixed: Mapped[str | None] = mapped_column(
        String(50)
    )

    sample_m10: Mapped[float | None] = mapped_column(
        Float
    )

    line_m10: Mapped[float | None] = mapped_column(
        Float
    )

    sensor: Mapped[str | None] = mapped_column(
        String(20)
    )

    vnf_version: Mapped[str | None] = mapped_column(
        String(20)
    )

    mscan_date: Mapped[date | None] = mapped_column(
        Date,
        index=True
    )

    mscan_time: Mapped[str | None] = mapped_column(
        String(50)
    )

    ltz_date: Mapped[date | None] = mapped_column(
        Date
    )

    ltz_time: Mapped[str | None] = mapped_column(
        String(50)
    )

    # -------------------------------------------------
    # INCREMENTAL PROCESSING
    # -------------------------------------------------

    processing_state: Mapped[str | None] = mapped_column(
        String(30),
        index=True,
        default="CANDIDATE"
    )

    matched_object_uid: Mapped[str | None] = mapped_column(
        String(50),
        index=True
    )

    ingestion_batch_id: Mapped[str | None] = mapped_column(
        String(50),
        index=True
    )