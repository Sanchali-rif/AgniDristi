from pathlib import Path

import pandas as pd

from app.pipeline.vnf.preprocessing import (
    preprocess_datetime_columns,
    CleanSentinelValues
)

from app.pipeline.vnf.spatial import (
    SpatialClusterer,
    GridCellAssigner
)

from app.pipeline.vnf.temporal import (
    TemporalPersistenceLabeler,
    PersistentReclusterer
)

from app.pipeline.vnf.features import (
    ObjectFeatureBuilder
)

from app.services.classification.classifier_service import (
    SavedIndustrialClassifier
)
from app.services.classification.gem_classifier_service import (
    classify_industrial_objects
)
from app.services.classification.flare_detection_service import (
    assess_gas_flare_candidates
)

from app.core.config import MODEL_PATH, settings


# ============================================================
# MODEL
# ============================================================

classifier = SavedIndustrialClassifier(
    MODEL_PATH
)


# ============================================================
# EXISTING FULL PIPELINE
# ============================================================

def process_vnf_data(df: pd.DataFrame, db=None):
    """
    Existing behaviour.

    Input:
        Raw VNF dataframe

    Output:
        Classified persistent object dataframe
    """

    result = process_vnf_data_with_members(
        df,
        db=db
    )

    return result["objects"]


# ============================================================
# PIPELINE WITH MEMBER DETECTIONS
# ============================================================

def process_vnf_data_with_members(
    df: pd.DataFrame,
    object_source_hints: tuple[str, ...] | None = None,
    db=None
):
    """
    Runs the VNF pipeline while preserving Stage-3
    member detections.

    Returns:

        {
            "objects": object-level classified dataframe,
            "detections": selected Stage-3 persistent detections,
            "temporal_detections": detections after temporal
                                   persistence classification,
            "industrial_detections": persistent industrial detections,
            "ambiguous_detections": persistent detections without a strong hint
        }

    By default, all persistent detections continue to object construction.
    Pass object_source_hints to selectively continue only named hints while
    retaining every annotated detection in temporal_detections and the
    source-specific outputs.
    """

    if df.empty:
        return {
            "objects": pd.DataFrame(),
            "detections": pd.DataFrame(),
            "temporal_detections": pd.DataFrame(),
            "industrial_detections": pd.DataFrame(),
            "ambiguous_detections": pd.DataFrame()
        }

    # ========================================================
    # 0. DATETIME PREPROCESSING
    # ========================================================

    prepared_df = preprocess_datetime_columns(
        df
    )

    # ========================================================
    # 1. CLEAN
    # ========================================================

    cleaner = CleanSentinelValues(
        temp_col="Temp_primary",
        sentinel=999999,
        lat_col="Lat_GMTCO",
        lon_col="Lon_GMTCO",
        date_col="Mscan_date"
    )

    clean_df = cleaner.fit_transform(
        prepared_df
    )

    if clean_df.empty:
        return {
            "objects": pd.DataFrame(),
            "detections": pd.DataFrame(),
            "temporal_detections": pd.DataFrame(),
            "industrial_detections": pd.DataFrame(),
            "ambiguous_detections": pd.DataFrame()
        }

    # ========================================================
    # 2. STAGE 1 — SPATIAL DBSCAN
    # ========================================================

    spatial = SpatialClusterer(
        eps=550.0,
        min_samples=5,
        lat_col="Lat_GMTCO",
        lon_col="Lon_GMTCO",
        source_crs="EPSG:4326",
        projected_crs="EPSG:32645",
        drop_noise=True
    )

    spatial_df = spatial.fit_transform(
        clean_df
    )

    if spatial_df.empty:
        return {
            "objects": pd.DataFrame(),
            "detections": pd.DataFrame(),
            "temporal_detections": pd.DataFrame(),
            "industrial_detections": pd.DataFrame(),
            "ambiguous_detections": pd.DataFrame()
        }

    # ========================================================
    # 3. 750 M GRID
    # ========================================================

    grid = GridCellAssigner(
        grid_size=750.0,
        cluster_col="cluster_id"
    )

    grid_df = grid.fit_transform(
        spatial_df
    )

    # ========================================================
    # 4. TEMPORAL PERSISTENCE
    # ========================================================

    temporal = TemporalPersistenceLabeler(
        cluster_col="cluster_id",
        cell_col="cell_id",
        date_col="Mscan_date",
        max_k=6,
        recurring_min_active_months=6,
        recurring_max_gap=3,
        continuous_min_run=3,
        continuous_min_active_dates=10,
        min_persistence_ratio=0.50,
        min_source_persistence_ratio=0.50,
        industrial_tci_threshold=0.40,
        industrial_max_seasonal_concentration=0.75,
        random_state=42
    )

    temporal_df = temporal.fit_transform(
        grid_df
    )

    if temporal_df.empty:
        return {
            "objects": pd.DataFrame(),
            "detections": pd.DataFrame(),
            "temporal_detections": temporal_df,
            "industrial_detections": pd.DataFrame(),
            "ambiguous_detections": pd.DataFrame()
        }

    persistent_temporal_df = temporal_df[
        temporal_df["temporal_class"] == "persistent"
    ].copy()

    industrial_df = persistent_temporal_df[
        persistent_temporal_df["temporal_source_hint"] == "industrial"
    ].copy()

    ambiguous_df = persistent_temporal_df[
        persistent_temporal_df["temporal_source_hint"] == "ambiguous"
    ].copy()

    recluster_input = temporal_df
    if object_source_hints is not None:
        recluster_input = temporal_df[
            temporal_df["temporal_source_hint"].isin(object_source_hints)
        ].copy()

    # ========================================================
    # 5. STAGE 3 — PERSISTENT RECLUSTERING
    # ========================================================

    recluster = PersistentReclusterer(
        eps=550.0,
        min_samples=5,
        persistent_col="temporal_class"
    )

    persistent_df = recluster.fit_transform(
        recluster_input
    )

    if persistent_df.empty:
        return {
            "objects": pd.DataFrame(),
            "detections": persistent_df,
            "temporal_detections": temporal_df,
            "industrial_detections": industrial_df,
            "ambiguous_detections": ambiguous_df
        }

    # ========================================================
    # 6. STAGE 4 — OBJECT FEATURES
    # ========================================================

    feature_builder = ObjectFeatureBuilder(
        object_col="stage3_object_id",
        temp_col="Temp_primary",
        rh_col="RH_primary",
        area_col="Area_primary",
        lat_col="Lat_GMTCO",
        lon_col="Lon_GMTCO",
        date_col="Mscan_date",
        temp_min=400.0,
        temp_max=3000.0,
        bin_size=50.0
    )

    object_features = (
        feature_builder.fit_transform(
            persistent_df
        )
    )

    if object_features.empty:
        return {
            "objects": pd.DataFrame(),
            "detections": persistent_df,
            "temporal_detections": temporal_df,
            "industrial_detections": industrial_df,
            "ambiguous_detections": ambiguous_df
        }

    # ========================================================
    # 7. CLASSIFICATION
    # ========================================================

    classified_objects = (
        classify_industrial_objects(
            db,
            object_features,
            classifier,
            settings.GEM_PRIMARY_RADIUS_METERS,
            settings.GEM_FALLBACK_RADIUS_METERS,
            settings.GEM_MAX_RADIUS_METERS,
            settings.GEM_EXTENDED_RADIUS_METERS
        )
    )

    classified_objects = assess_gas_flare_candidates(classified_objects)

    return {
        "objects": classified_objects,

        # Only persistent detections surviving Stage 3.
        # Contains stage3_object_id.
        "detections": persistent_df,

        # Includes both persistent + transient temporal results.
        "temporal_detections": temporal_df,

        # Source-hint partitions remain available for selective processing.
        "industrial_detections": industrial_df,
        "ambiguous_detections": ambiguous_df
    }
