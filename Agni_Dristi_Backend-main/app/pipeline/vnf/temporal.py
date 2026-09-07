import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.cluster import DBSCAN


def longest_active_run(values):
    best = 0
    current = 0

    for value in values:
        if value > 0:
            current += 1
            best = max(best, current)
        else:
            current = 0

    return best


def longest_zero_gap(values):
    best = 0
    current = 0

    for value in values:
        if value == 0:
            current += 1
            best = max(best, current)
        else:
            current = 0

    return best

import numpy as np
import pandas as pd
import pymannkendall as mk

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.metrics import pairwise_distances, silhouette_score
from sklearn.cluster import DBSCAN

from app.pipeline.vnf.preprocessing import parse_date_series


def _longest_zero_gap(v):
    best = cur = 0

    for x in v:
        cur = cur + 1 if x == 0 else 0
        best = max(best, cur)

    return best


def _longest_active_run(v):
    best = cur = 0

    for x in v:
        cur = cur + 1 if x > 0 else 0
        best = max(best, cur)

    return best


def _kmedoids_precomputed(D, k, max_iter=100, random_state=42):
    rng = np.random.default_rng(random_state)
    n = D.shape[0]

    if k >= n:
        return np.arange(n), np.arange(n)

    medoids = np.sort(
        rng.choice(
            n,
            size=k,
            replace=False
        )
    )

    for _ in range(max_iter):
        labels = np.argmin(
            D[:, medoids],
            axis=1
        )

        new = medoids.copy()

        for j in range(k):
            members = np.where(
                labels == j
            )[0]

            if len(members):
                sub = D[
                    np.ix_(
                        members,
                        members
                    )
                ]

                new[j] = members[
                    np.argmin(
                        sub.sum(axis=1)
                    )
                ]

        new = np.sort(new)

        if np.array_equal(
            new,
            medoids
        ):
            break

        medoids = new

    return (
        np.argmin(
            D[:, medoids],
            axis=1
        ),
        medoids
    )


class TemporalPersistenceLabeler(BaseEstimator, TransformerMixin):
    def __init__(self, cluster_col="cluster_id", cell_col="cell_id", date_col="Mscan_date", max_k=6, recurring_min_active_months=6, recurring_max_gap=3, continuous_min_run=3, continuous_min_detections=10, random_state=42):
        self.cluster_col = cluster_col
        self.cell_col = cell_col
        self.date_col = date_col
        self.max_k = max_k
        self.recurring_min_active_months = recurring_min_active_months
        self.recurring_max_gap = recurring_max_gap
        self.continuous_min_run = continuous_min_run
        self.continuous_min_detections = continuous_min_detections
        self.random_state = random_state

    def fit(self, X, y=None):
        return self

    @staticmethod
    def _classify(row, recurring_min_active_months, recurring_max_gap, continuous_min_run, continuous_min_detections):
        recurring = (
            row["active_months"] >= recurring_min_active_months
            and
            row["max_inactive_gap"] <= recurring_max_gap
        )

        continuous = (
            row["longest_active_run"] >= continuous_min_run
            and
            row["total_detections"] >= continuous_min_detections
        )

        return (
            "persistent"
            if recurring or continuous
            else "transient"
        )

    def transform(self, X):
        df = X.copy()

        df["_datetime"] = parse_date_series(
            df[self.date_col]
        )

        df = df[
            df["_datetime"].notna()
        ].copy()

        df["_month"] = (
            df["_datetime"]
            .dt
            .to_period("M")
        )

        # ---------------------------------------------
        # 1. CELL × MONTH ACTIVITY
        # ---------------------------------------------

        cell_month_counts = (
            df
            .groupby(
                [
                    self.cluster_col,
                    self.cell_col,
                    "_month"
                ],
                observed=True
            )
            .size()
            .reset_index(
                name="detection_count"
            )
        )

        cell_time_series = (
            cell_month_counts
            .pivot_table(
                index=[
                    self.cluster_col,
                    self.cell_col
                ],
                columns="_month",
                values="detection_count",
                fill_value=0
            )
            .sort_index(axis=1)
            .astype(int)
        )

        # ---------------------------------------------
        # 2. TEMPORAL CLUSTERING
        # ---------------------------------------------

        temporal_results = []

        cluster_ids = (
            cell_time_series
            .index
            .get_level_values(
                self.cluster_col
            )
            .unique()
        )

        for cluster_id in cluster_ids:
            cluster_ts = (
                cell_time_series
                .loc[cluster_id]
            )

            n_cells = len(cluster_ts)

            if n_cells <= 2:
                labels = np.zeros(
                    n_cells,
                    dtype=int
                )

            else:
                D = pairwise_distances(
                    cluster_ts.to_numpy(),
                    metric="manhattan"
                )

                max_k = min(
                    self.max_k,
                    n_cells - 1
                )

                best_score = -np.inf
                best_labels = None

                for k in range(
                    2,
                    max_k + 1
                ):
                    try:
                        candidate_labels, _ = (
                            _kmedoids_precomputed(
                                D,
                                k=k,
                                random_state=self.random_state
                            )
                        )

                        if (
                            len(
                                np.unique(
                                    candidate_labels
                                )
                            )
                            < 2
                        ):
                            continue

                        score = silhouette_score(
                            D,
                            candidate_labels,
                            metric="precomputed"
                        )

                        if (
                            np.isfinite(score)
                            and score > best_score
                        ):
                            best_score = score
                            best_labels = (
                                candidate_labels
                            )

                    except Exception:
                        continue

                labels = (
                    best_labels
                    if best_labels is not None
                    else np.zeros(
                        n_cells,
                        dtype=int
                    )
                )

            temporal_results.append(
                pd.DataFrame({
                    self.cluster_col:
                        cluster_id,

                    self.cell_col:
                        cluster_ts.index,

                    "temporal_cluster":
                        labels
                })
            )

        if not temporal_results:
            raise ValueError(
                "No temporal groups could be generated."
            )

        temporal_clusters = pd.concat(
            temporal_results,
            ignore_index=True
        )

        # ---------------------------------------------
        # 3. AGGREGATE TEMPORAL GROUPS
        # ---------------------------------------------

        cell_ts = (
            cell_time_series
            .reset_index()
            .merge(
                temporal_clusters,
                on=[
                    self.cluster_col,
                    self.cell_col
                ],
                how="left"
            )
        )

        month_cols = [
            c
            for c in cell_ts.columns
            if c not in [
                self.cluster_col,
                self.cell_col,
                "temporal_cluster"
            ]
        ]

        temporal_group_ts = (
            cell_ts
            .groupby(
                [
                    self.cluster_col,
                    "temporal_cluster"
                ],
                observed=True
            )[month_cols]
            .sum()
        )

        # ---------------------------------------------
        # 4. PERSISTENCE + MANN-KENDALL
        # ---------------------------------------------

        records = []

        for (
            cluster_id,
            temporal_cluster
        ), row in temporal_group_ts.iterrows():

            values = row.to_numpy(
                dtype=float
            )

            active = values > 0

            active_months = int(
                active.sum()
            )

            trend = "no trend"
            tau = 0.0
            p_value = 1.0

            if (
                len(values) >= 3
                and len(
                    np.unique(values)
                ) > 1
            ):
                try:
                    res = mk.original_test(
                        values
                    )

                    trend = res.trend
                    tau = float(res.Tau)
                    p_value = float(res.p)

                except Exception:
                    pass

            records.append({
                self.cluster_col:
                    cluster_id,

                "temporal_cluster":
                    temporal_cluster,

                "active_months":
                    active_months,

                "total_months":
                    len(values),

                "persistence_ratio":
                    (
                        active_months
                        / len(values)
                        if len(values)
                        else 0.0
                    ),

                "total_detections":
                    float(
                        values.sum()
                    ),

                "mean_detections_per_month":
                    float(
                        values.mean()
                    ),

                "longest_active_run":
                    _longest_active_run(
                        values
                    ),

                "max_inactive_gap":
                    _longest_zero_gap(
                        values
                    ),

                "mk_trend":
                    trend,

                "mk_tau":
                    tau,

                "mk_p_value":
                    p_value
            })

        temporal_metrics = pd.DataFrame(
            records
        )

        temporal_metrics[
            "temporal_class"
        ] = temporal_metrics.apply(
            self._classify,
            axis=1,
            recurring_min_active_months=
                self.recurring_min_active_months,
            recurring_max_gap=
                self.recurring_max_gap,
            continuous_min_run=
                self.continuous_min_run,
            continuous_min_detections=
                self.continuous_min_detections
        )

        # ---------------------------------------------
        # 5. MERGE BACK TO DETECTIONS
        # ---------------------------------------------

        out = (
            df
            .merge(
                temporal_clusters,
                on=[
                    self.cluster_col,
                    self.cell_col
                ],
                how="left"
            )
            .merge(
                temporal_metrics,
                on=[
                    self.cluster_col,
                    "temporal_cluster"
                ],
                how="left"
            )
        )

        out = out[
            out["temporal_class"].notna()
        ].copy()

        out = out.drop(
            columns=[
                "_datetime",
                "_month"
            ]
        )

        print(
            "[Temporal] "
            f"{len(out):,} detections classified | "
            f"{(out['temporal_class'] == 'persistent').sum():,} persistent | "
            f"{(out['temporal_class'] == 'transient').sum():,} transient"
        )

        return out.reset_index(
            drop=True
        )


class PersistentReclusterer(BaseEstimator, TransformerMixin):
    def __init__(self, eps=550.0, min_samples=5, persistent_col="temporal_class"):
        self.eps = eps
        self.min_samples = min_samples
        self.persistent_col = persistent_col

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        persistent = X[
            X[self.persistent_col] == "persistent"
        ].copy()

        if persistent.empty:
            print("[Persistent DBSCAN] No persistent detections found")
            return persistent

        coords = persistent[
            ["X", "Y"]
        ].to_numpy()

        db = DBSCAN(
            eps=self.eps,
            min_samples=self.min_samples,
            metric="euclidean",
            n_jobs=-1
        )

        labels = db.fit_predict(coords)

        persistent["stage3_object_id"] = labels

        persistent = persistent[
            persistent["stage3_object_id"] != -1
        ].copy()

        self.dbscan_ = db

        n_noise = int((labels == -1).sum())

        n_objects = int(
            persistent.loc[
                persistent["stage3_object_id"] != -1,
                "stage3_object_id"
            ].nunique()
        )

        print(
            f"[Persistent DBSCAN] "
            f"{n_objects:,} objects | "
            f"{n_noise:,} noise detections"
        )

        return persistent.reset_index(drop=True)