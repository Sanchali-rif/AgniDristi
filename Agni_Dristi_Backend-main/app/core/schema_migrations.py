from sqlalchemy import inspect, text


THERMAL_OBJECT_TEMPORAL_COLUMNS = {
    "temporal_source_hint": "VARCHAR(30)",
    "tci": "DOUBLE PRECISION",
    "seasonal_concentration": "DOUBLE PRECISION",
    "source_persistence_ratio": "DOUBLE PRECISION",
    "gas_flare_candidate": "BOOLEAN",
    "gas_flare_likelihood": "VARCHAR(20)",
    "gas_flare_score": "DOUBLE PRECISION",
    "gas_flare_source": "VARCHAR(50)",
    "gas_flare_evidence": "JSONB"
}

VNF_DETECTION_GEM_COLUMNS = {
    "gem_industry_exact_type": "VARCHAR(100)",
    "gem_facility_name": "VARCHAR(255)"
}


def ensure_temporal_source_columns(engine):
    """Add temporal source columns for databases created before this feature."""
    inspector = inspect(engine)

    table_names = inspector.get_table_names()

    with engine.begin() as connection:
        if "thermal_objects" in table_names:
            existing = {
                column["name"]
                for column in inspector.get_columns("thermal_objects")
            }

            for column_name, column_type in THERMAL_OBJECT_TEMPORAL_COLUMNS.items():
                if column_name in existing:
                    continue

                connection.execute(text(
                    f"ALTER TABLE thermal_objects "
                    f"ADD COLUMN {column_name} {column_type}"
                ))

            connection.execute(text(
                "CREATE INDEX IF NOT EXISTS "
                "ix_thermal_objects_temporal_source_hint "
                "ON thermal_objects (temporal_source_hint)"
            ))

        if "vnf_detections" in table_names:
            existing = {
                column["name"]
                for column in inspector.get_columns("vnf_detections")
            }

            for column_name, column_type in VNF_DETECTION_GEM_COLUMNS.items():
                if column_name in existing:
                    continue

                connection.execute(text(
                    f"ALTER TABLE vnf_detections "
                    f"ADD COLUMN {column_name} {column_type}"
                ))
