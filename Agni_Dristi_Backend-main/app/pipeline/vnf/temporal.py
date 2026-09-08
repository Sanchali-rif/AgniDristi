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


def _episode_metrics(datetimes, max_gap_days=14):
    """Return the number and maximum duration of detection episodes."""
    dates = (
        pd.Series(datetimes)
        .dropna()
        .dt.normalize()
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

    if not dates:
        return 0, 0

    episode_count = 1
    episode_start = dates[0]
    previous = dates[0]
    max_duration_days = 1

    for current in dates[1:]:
        if (current - previous).days > max_gap_days:
            max_duration_days = max(
                max_duration_days,
                (previous - episode_start).days + 1
            )
            episode_count += 1
            episode_start = current

        previous = current

    max_duration_days = max(
        max_duration_days,
        (previous - episode_start).days + 1
    )

    return episode_count, max_duration_days


def _temporal_behaviour_metrics(datetimes, analysis_start, analysis_end):
    """Calculate observation-window-normalized weekly behaviour metrics."""
    series = pd.Series(datetimes).dropna()

    if series.empty:
        return {
            "active_weeks": 0,
            "total_weeks": 0,
            "weekly_active_ratio": 0.0,
            "weekly_transition_rate": 0.0,
            "observation_span_ratio": 0.0,
            "weekly_continuity_ratio": 0.0,
            "seasonal_concentration": 0.0,
            "episode_count": 0,
            "max_episode_duration_days": 0,
            "unique_active_dates": 0,
            "tci": 0.0
        }

    start_week = pd.Timestamp(analysis_start).to_period("W-SUN")
    end_week = pd.Timestamp(analysis_end).to_period("W-SUN")
    weeks = pd.period_range(start_week, end_week, freq="W-SUN")

    weekly_counts = (
        series.dt.to_period("W-SUN")
        .value_counts()
        .reindex(weeks, fill_value=0)
        .sort_index()
    )
    active = weekly_counts.to_numpy() > 0
    active_weeks = int(active.sum())
    total_weeks = len(active)

    active_positions = np.flatnonzero(active)
    span_weeks = (
        int(active_positions[-1] - active_positions[0] + 1)
        if active_weeks
        else 0
    )
    transitions = (
        int(np.count_nonzero(active[1:] != active[:-1]))
        if total_weeks > 1
        else 0
    )

    weekly_active_ratio = active_weeks / total_weeks if total_weeks else 0.0
    weekly_transition_rate = transitions / (total_weeks - 1) if total_weeks > 1 else 0.0
    observation_span_ratio = span_weeks / total_weeks if total_weeks else 0.0
    weekly_continuity_ratio = (
        _longest_active_run(active.astype(int)) / active_weeks
        if active_weeks
        else 0.0
    )

    # Biomass burning is commonly concentrated into a short annual season.
    month_of_year_counts = series.dt.month.value_counts()
    seasonal_concentration = float(
        month_of_year_counts.nlargest(3).sum() / len(series)
    )

    episode_count, max_episode_duration_days = _episode_metrics(series)
    unique_active_dates = int(series.dt.normalize().nunique())

    # TCI combines duty cycle, lifespan across the analysis window, and
    # continuity. A short, dense fire episode therefore does not look like a
    # continuously operating heat source merely because it has many records.
    tci = float(np.clip(
        0.40 * weekly_active_ratio
        + 0.35 * observation_span_ratio
        + 0.25 * weekly_continuity_ratio,
        0.0,
        1.0
    ))

    return {
        "active_weeks": active_weeks,
        "total_weeks": total_weeks,
        "weekly_active_ratio": float(weekly_active_ratio),
        "weekly_transition_rate": float(weekly_transition_rate),
        "observation_span_ratio": float(observation_span_ratio),
        "weekly_continuity_ratio": float(weekly_continuity_ratio),
        "seasonal_concentration": seasonal_concentration,
        "episode_count": episode_count,
        "max_episode_duration_days": max_episode_duration_days,
        "unique_active_dates": unique_active_dates,
        "tci": tci
    }


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
    def __init__(self, cluster_col="cluster_id", cell_col="cell_id", date_col="Mscan_date", max_k=6, recurring_min_active_months=6, recurring_max_gap=3, continuous_min_run=3, continuous_min_active_dates=10, min_persistence_ratio=0.50, min_source_persistence_ratio=0.50, industrial_tci_threshold=0.40, industrial_max_seasonal_concentration=0.75, random_state=42):
        self.cluster_col = cluster_col
        self.cell_col = cell_col
        self.date_col = date_col
        self.max_k = max_k
        self.recurring_min_active_months = recurring_min_active_months
        self.recurring_max_gap = recurring_max_gap
        self.continuous_min_run = continuous_min_run
        self.continuous_min_active_dates = continuous_min_active_dates
        self.min_persistence_ratio = min_persistence_ratio
        self.min_source_persistence_ratio = min_source_persistence_ratio
        self.industrial_tci_threshold = industrial_tci_threshold
        self.industrial_max_seasonal_concentration = (
            industrial_max_seasonal_concentration
        )
        self.random_state = random_state

    def fit(self, X, y=None):
        return self

    @staticmethod
    def _classify(row, recurring_min_active_months, recurring_max_gap, continuous_min_run, continuous_min_active_dates, min_persistence_ratio, min_source_persistence_ratio):
        recurring = (
            row["source_span_months"] >= recurring_min_active_months
            and
            row["active_months"] >= recurring_min_active_months
            and
            row["max_internal_inactive_gap"] <= recurring_max_gap
            and
            row["unique_active_dates"] >= recurring_min_active_months
            and
            row["source_persistence_ratio"] >= min_source_persistence_ratio
            and
            row["persistence_ratio"] >= min_persistence_ratio
        )

        continuous = (
            row["longest_active_run"] >= continuous_min_run
            and
            row["unique_active_dates"] >= continuous_min_active_dates
            and
            row["max_internal_inactive_gap"] <= recurring_max_gap
            and
            row["source_persistence_ratio"] >= min_source_persistence_ratio
            and
            row["persistence_ratio"] >= min_persistence_ratio
        )

        return (
            "persistent"
            if recurring or continuous
            else "transient"
        )

    @staticmethod
    def _source_hint(
        row,
        industrial_tci_threshold,
        industrial_max_seasonal_concentration
    ):
        """Split persistent activity using continuity and seasonality."""
        if row["temporal_class"] != "persistent":
            return "not_assessed"

        ambiguous = (
            row["tci"] < industrial_tci_threshold
            and row["seasonal_concentration"]
            > industrial_max_seasonal_concentration
        )

        return "ambiguous" if ambiguous else "industrial"

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

        # The pivot only creates columns for months found in the input. Fill
        # the entire calendar range so Jan, Mar, May cannot be interpreted as
        # three consecutive months when Feb and Apr contain no detections.
        calendar_months = pd.period_range(
            df["_month"].min(),
            df["_month"].max(),
            freq="M"
        )
        cell_time_series = cell_time_series.reindex(
            columns=calendar_months,
            fill_value=0
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

        detections_with_groups = df.merge(
            temporal_clusters,
            on=[self.cluster_col, self.cell_col],
            how="left"
        )

        analysis_start = df["_datetime"].min()
        analysis_end = df["_datetime"].max()

        behaviour_records = []
        for (cluster_id, temporal_cluster), group in detections_with_groups.groupby(
            [self.cluster_col, "temporal_cluster"],
            observed=True
        ):
            behaviour_records.append({
                self.cluster_col: cluster_id,
                "temporal_cluster": temporal_cluster,
                **_temporal_behaviour_metrics(
                    group["_datetime"],
                    analysis_start,
                    analysis_end
                )
            })

        behaviour_metrics = pd.DataFrame(behaviour_records)

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

            active_positions = np.flatnonzero(active)

            if active_months:
                first_active = int(active_positions[0])
                last_active = int(active_positions[-1])
                source_span_months = last_active - first_active + 1
                leading_inactive_months = first_active
                trailing_inactive_months = len(values) - last_active - 1
                internal_values = values[first_active:last_active + 1]
                max_internal_inactive_gap = _longest_zero_gap(internal_values)
            else:
                source_span_months = 0
                leading_inactive_months = len(values)
                trailing_inactive_months = len(values)
                max_internal_inactive_gap = 0

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

                "source_span_months":
                    source_span_months,

                "leading_inactive_months":
                    leading_inactive_months,

                "trailing_inactive_months":
                    trailing_inactive_months,

                "persistence_ratio":
                    (
                        active_months
                        / len(values)
                        if len(values)
                        else 0.0
                    ),

                "source_persistence_ratio":
                    (
                        active_months
                        / source_span_months
                        if source_span_months
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

                # Retained for downstream compatibility, now correctly scoped
                # to gaps between the first and last detections.
                "max_inactive_gap":
                    max_internal_inactive_gap,

                "max_internal_inactive_gap":
                    max_internal_inactive_gap,

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

        temporal_metrics = temporal_metrics.merge(
            behaviour_metrics,
            on=[self.cluster_col, "temporal_cluster"],
            how="left"
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
            continuous_min_active_dates=
                self.continuous_min_active_dates,
            min_persistence_ratio=
                self.min_persistence_ratio,
            min_source_persistence_ratio=
                self.min_source_persistence_ratio
        )

        temporal_metrics["temporal_source_hint"] = temporal_metrics.apply(
            self._source_hint,
            axis=1,
            industrial_tci_threshold=self.industrial_tci_threshold,
            industrial_max_seasonal_concentration=(
                self.industrial_max_seasonal_concentration
            )
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
            f"{(out['temporal_class'] == 'transient').sum():,} transient | "
            f"{(out['temporal_source_hint'] == 'industrial').sum():,} industrial | "
            f"{(out['temporal_source_hint'] == 'ambiguous').sum():,} ambiguous"
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
