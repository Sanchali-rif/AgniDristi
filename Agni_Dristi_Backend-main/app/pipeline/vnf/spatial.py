import numpy as np
import pandas as pd
import geopandas as gpd

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.cluster import DBSCAN

class SpatialClusterer(BaseEstimator, TransformerMixin):
    def __init__(self, eps=550.0, min_samples=5, lat_col="Lat_GMTCO", lon_col="Lon_GMTCO", source_crs="EPSG:4326", projected_crs="EPSG:32645", drop_noise=True):
        self.eps = eps
        self.min_samples = min_samples
        self.lat_col = lat_col
        self.lon_col = lon_col
        self.source_crs = source_crs
        self.projected_crs = projected_crs
        self.drop_noise = drop_noise

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        df = X.copy().dropna(subset=[self.lat_col, self.lon_col])

        gdf = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(
                df[self.lon_col],
                df[self.lat_col]
            ),
            crs=self.source_crs
        ).to_crs(self.projected_crs)

        gdf["X"] = gdf.geometry.x
        gdf["Y"] = gdf.geometry.y

        coords = gdf[["X", "Y"]].to_numpy()

        db = DBSCAN(
            eps=self.eps,
            min_samples=self.min_samples,
            metric="euclidean",
            n_jobs=-1
        )

        labels = db.fit_predict(coords)

        gdf["cluster_id"] = labels

        core_mask = np.zeros(len(gdf), dtype=bool)
        core_mask[db.core_sample_indices_] = True

        gdf["dbscan_point_type"] = np.where(
            labels == -1,
            "noise",
            np.where(core_mask, "core", "border")
        )

        self.dbscan_ = db

        n_noise = int((labels == -1).sum())
        n_clusters = int(
            gdf.loc[
                gdf["cluster_id"] != -1,
                "cluster_id"
            ].nunique()
        )

        if self.drop_noise:
            gdf = gdf[
                gdf["cluster_id"] != -1
            ].copy()

        print(
            f"[Spatial DBSCAN] "
            f"eps={self.eps:.0f} m, "
            f"MinPts={self.min_samples} | "
            f"{n_clusters:,} clusters | "
            f"{n_noise:,} noise detections"
        )

        return gdf.reset_index(drop=True)


class GridCellAssigner(BaseEstimator, TransformerMixin):
    def __init__(self, grid_size=750.0, cluster_col="cluster_id"):
        self.grid_size = grid_size
        self.cluster_col = cluster_col

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        df = X.copy()

        x0 = df.groupby(
            self.cluster_col
        )["X"].transform("min")

        y0 = df.groupby(
            self.cluster_col
        )["Y"].transform("min")

        df["grid_col"] = np.floor(
            (df["X"] - x0) / self.grid_size
        ).astype(int)

        df["grid_row"] = np.floor(
            (df["Y"] - y0) / self.grid_size
        ).astype(int)

        df["cell_id"] = (
            df[self.cluster_col].astype(str)
            + "_"
            + df["grid_col"].astype(str)
            + "_"
            + df["grid_row"].astype(str)
        )

        print(
            f"[{self.grid_size:.0f} m grid] "
            f"{df['cell_id'].nunique():,} occupied cells "
            f"across "
            f"{df[self.cluster_col].nunique():,} candidate clusters"
        )

        return df