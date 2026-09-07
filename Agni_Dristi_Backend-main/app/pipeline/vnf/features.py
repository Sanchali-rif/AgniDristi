import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin


class ObjectFeatureBuilder(BaseEstimator, TransformerMixin):
    def __init__(
        self,
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
    ):
        self.object_col = object_col
        self.temp_col = temp_col
        self.rh_col = rh_col
        self.area_col = area_col
        self.lat_col = lat_col
        self.lon_col = lon_col
        self.date_col = date_col
        self.temp_min = temp_min
        self.temp_max = temp_max
        self.bin_size = bin_size

    def fit(self, X, y=None):
        return self

    # ========================================================
    # TEMPERATURE BIN DEFINITION
    # ========================================================

    def _bin_definition(self):
        bins = np.arange(
            self.temp_min,
            self.temp_max + self.bin_size,
            self.bin_size
        )

        labels = [
            f"FP_{int(bins[i])}_{int(bins[i + 1])}K"
            for i in range(len(bins) - 1)
        ]

        return bins, labels

    # ========================================================
    # THERMAL FINGERPRINT
    # ========================================================

    def _thermal_fingerprint(self, df):
        bins, labels = self._bin_definition()

        valid = df[
            df[self.temp_col].between(
                self.temp_min,
                self.temp_max,
                inclusive="both"
            )
        ].copy()

        rows = []

        for object_id, group in valid.groupby(
            self.object_col,
            observed=True
        ):
            temps = pd.to_numeric(
                group[self.temp_col],
                errors="coerce"
            ).dropna().to_numpy()

            counts, _ = np.histogram(
                temps,
                bins=bins
            )

            total = int(
                counts.sum()
            )

            if total == 0:
                continue

            row = {
                self.object_col: object_id,
                "valid_temperature_count": total
            }

            row.update({
                label: float(
                    count / total
                )
                for label, count in zip(
                    labels,
                    counts
                )
            })

            rows.append(row)

        return pd.DataFrame(rows)

    # ========================================================
    # TRANSFORM
    # ========================================================

    def transform(self, X):
        df = X.copy()

        # ----------------------------------------------------
        # OBJECT LEVEL STATISTICS
        # ----------------------------------------------------

        agg = (
            df.groupby(
                self.object_col,
                observed=True
            )
            .agg(
                temp_mean=(
                    self.temp_col,
                    "mean"
                ),

                temp_median=(
                    self.temp_col,
                    "median"
                ),

                temp_min=(
                    self.temp_col,
                    "min"
                ),

                temp_max=(
                    self.temp_col,
                    "max"
                ),

                temp_std=(
                    self.temp_col,
                    "std"
                ),

                temp_p10=(
                    self.temp_col,
                    lambda s:
                        s.quantile(0.10)
                ),

                temp_p25=(
                    self.temp_col,
                    lambda s:
                        s.quantile(0.25)
                ),

                temp_p75=(
                    self.temp_col,
                    lambda s:
                        s.quantile(0.75)
                ),

                temp_p90=(
                    self.temp_col,
                    lambda s:
                        s.quantile(0.90)
                ),

                temp_p95=(
                    self.temp_col,
                    lambda s:
                        s.quantile(0.95)
                ),

                rh_mean=(
                    self.rh_col,
                    "mean"
                ),

                rh_max=(
                    self.rh_col,
                    "max"
                ),

                rh_std=(
                    self.rh_col,
                    "std"
                ),

                area_mean=(
                    self.area_col,
                    "mean"
                ),

                area_max=(
                    self.area_col,
                    "max"
                ),

                area_std=(
                    self.area_col,
                    "std"
                ),

                detection_count=(
                    self.temp_col,
                    "size"
                ),

                latitude=(
                    self.lat_col,
                    "mean"
                ),

                longitude=(
                    self.lon_col,
                    "mean"
                ),

                active_months=(
                    "active_months",
                    "first"
                ),

                persistence_ratio=(
                    "persistence_ratio",
                    "first"
                ),

                longest_active_run=(
                    "longest_active_run",
                    "first"
                ),

                max_inactive_gap=(
                    "max_inactive_gap",
                    "first"
                ),

                mk_trend=(
                    "mk_trend",
                    "first"
                ),

                mk_tau=(
                    "mk_tau",
                    "first"
                ),

                mk_p_value=(
                    "mk_p_value",
                    "first"
                ),

                first_seen=(
                    self.date_col,
                    "min"
                ),

                last_seen=(
                    self.date_col,
                    "max"
                )
            )
            .reset_index()
        )

        # ----------------------------------------------------
        # DERIVED MODEL FEATURES
        # ----------------------------------------------------

        EPS = 1e-8

        agg["temp_range"] = (
            agg["temp_max"]
            - agg["temp_min"]
        )

        agg["temp_cv"] = (
            agg["temp_std"]
            / (
                np.abs(
                    agg["temp_mean"]
                )
                + EPS
            )
        )

        agg["area_cv"] = (
            agg["area_std"]
            / (
                np.abs(
                    agg["area_mean"]
                )
                + EPS
            )
        )

        agg["rh_cv"] = (
            agg["rh_std"]
            / (
                np.abs(
                    agg["rh_mean"]
                )
                + EPS
            )
        )

        agg["temp_iqr"] = (
            agg["temp_p75"]
            - agg["temp_p25"]
        )

        agg["temp_p95_p10_range"] = (
            agg["temp_p95"]
            - agg["temp_p10"]
        )

        agg = agg.replace(
            [np.inf, -np.inf],
            np.nan
        )

        # ----------------------------------------------------
        # THERMAL FINGERPRINT
        # ----------------------------------------------------

        fingerprint = (
            self._thermal_fingerprint(
                df
            )
        )

        object_features = agg.merge(
            fingerprint,
            on=self.object_col,
            how="left"
        )

        fp_cols = [
            col
            for col
            in object_features.columns
            if col.startswith("FP_")
        ]

        object_features[
            fp_cols
        ] = (
            object_features[
                fp_cols
            ]
            .fillna(0.0)
        )

        object_features[
            "thermal_fingerprint_sum"
        ] = (
            object_features[
                fp_cols
            ]
            .sum(axis=1)
        )

        # ----------------------------------------------------
        # PROJECTED CENTROID
        # ----------------------------------------------------

        projected_centroids = (
            df.groupby(
                self.object_col,
                observed=True
            )[["X", "Y"]]
            .mean()
            .rename(
                columns={
                    "X": "centroid_X",
                    "Y": "centroid_Y"
                }
            )
            .reset_index()
        )

        # ----------------------------------------------------
        # OBJECT SPATIAL RADIUS
        # ----------------------------------------------------

        centroid_lookup = (
            projected_centroids
            .set_index(
                self.object_col
            )
        )

        radius_rows = []

        for object_id, group in df.groupby(
            self.object_col,
            observed=True
        ):
            cx = centroid_lookup.loc[
                object_id,
                "centroid_X"
            ]

            cy = centroid_lookup.loc[
                object_id,
                "centroid_Y"
            ]

            distances = np.sqrt(
                (
                    group["X"]
                    - cx
                ) ** 2
                +
                (
                    group["Y"]
                    - cy
                ) ** 2
            )

            object_radius_m = float(
                distances.max()
            )

            radius_rows.append({
                self.object_col:
                    object_id,

                "object_radius_m":
                    object_radius_m
            })

        object_radii = pd.DataFrame(
            radius_rows
        )

        # ----------------------------------------------------
        # MERGE CENTROID + RADIUS
        # ----------------------------------------------------

        object_features = (
            object_features
            .merge(
                projected_centroids,
                on=self.object_col,
                how="left"
            )
        )

        object_features = (
            object_features
            .merge(
                object_radii,
                on=self.object_col,
                how="left"
            )
        )

        print(
            f"[Stage 4] "
            f"{len(object_features):,} "
            f"persistent objects | "
            f"{len(fp_cols)} fingerprint bins"
        )

        return object_features