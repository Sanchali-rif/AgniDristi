from sklearn.pipeline import Pipeline

from app.pipeline.vnf.preprocessing import CleanSentinelValues
from app.pipeline.vnf.spatial import SpatialClusterer, GridCellAssigner
from app.pipeline.vnf.temporal import TemporalPersistenceLabeler, PersistentReclusterer
from app.pipeline.vnf.features import ObjectFeatureBuilder


def build_vnf_pipeline():

    pipeline = Pipeline([
        (
            "clean",
            CleanSentinelValues(
                temp_col="Temp_primary",
                sentinel=999999,
                lat_col="Lat_GMTCO",
                lon_col="Lon_GMTCO",
                date_col="Mscan_date"
            )
        ),

        (
            "spatial_cluster",
            SpatialClusterer(
                eps=550.0,
                min_samples=5,
                lat_col="Lat_GMTCO",
                lon_col="Lon_GMTCO",
                drop_noise=True
            )
        ),

        (
            "grid_cells",
            GridCellAssigner(
                grid_size=750.0
            )
        ),

        (
            "temporal_labels",
            TemporalPersistenceLabeler(
                date_col="Mscan_date",
                max_k=6,
                recurring_min_active_months=6,
                recurring_max_gap=3,
                continuous_min_run=3,
                continuous_min_detections=10,
                random_state=42
            )
        ),

        (
            "recluster_persistent",
            PersistentReclusterer(
                eps=550.0,
                min_samples=5
            )
        ),

        (
            "object_features",
            ObjectFeatureBuilder(
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
        )
    ])

    return pipeline