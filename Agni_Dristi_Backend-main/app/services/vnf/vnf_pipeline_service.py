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

from app.core.config import MODEL_PATH


# ============================================================
# MODEL
# ============================================================

classifier = SavedIndustrialClassifier(
    MODEL_PATH
)


# ============================================================
# EXISTING FULL PIPELINE
# ============================================================

def process_vnf_data(df: pd.DataFrame):
    """
    Existing behaviour.

    Input:
        Raw VNF dataframe

    Output:
        Classified persistent object dataframe
    """

    result = process_vnf_data_with_members(
        df
    )

    return result["objects"]


# ============================================================
# PIPELINE WITH MEMBER DETECTIONS
# ============================================================

def process_vnf_data_with_members(
    df: pd.DataFrame
):
    """
    Runs the VNF pipeline while preserving Stage-3
    member detections.

    Returns:

        {
            "objects": object-level classified dataframe,
            "detections": Stage-3 persistent detections,
            "temporal_detections": detections after temporal
                                   persistence classification
        }
    """

    if df.empty:
        return {
            "objects": pd.DataFrame(),
            "detections": pd.DataFrame(),
            "temporal_detections": pd.DataFrame()
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
            "temporal_detections": pd.DataFrame()
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
            "temporal_detections": pd.DataFrame()
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
        continuous_min_detections=10,
        random_state=42
    )

    temporal_df = temporal.fit_transform(
        grid_df
    )

    if temporal_df.empty:
        return {
            "objects": pd.DataFrame(),
            "detections": pd.DataFrame(),
            "temporal_detections": temporal_df
        }

    # ========================================================
    # 5. STAGE 3 — PERSISTENT RECLUSTERING
    # ========================================================

    recluster = PersistentReclusterer(
        eps=550.0,
        min_samples=5,
        persistent_col="temporal_class"
    )

    persistent_df = recluster.fit_transform(
        temporal_df
    )

    if persistent_df.empty:
        return {
            "objects": pd.DataFrame(),
            "detections": persistent_df,
            "temporal_detections": temporal_df
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
            "temporal_detections": temporal_df
        }

    # ========================================================
    # 7. CLASSIFICATION
    # ========================================================

    classified_objects = (
        classifier.predict(
            object_features
        )
    )

    return {
        "objects": classified_objects,

        # Only persistent detections surviving Stage 3.
        # Contains stage3_object_id.
        "detections": persistent_df,

        # Includes both persistent + transient temporal results.
        "temporal_detections": temporal_df
    }