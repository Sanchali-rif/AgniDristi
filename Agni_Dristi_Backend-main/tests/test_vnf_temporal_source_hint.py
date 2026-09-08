import pandas as pd

from app.pipeline.vnf.temporal import (
    PersistentReclusterer,
    TemporalPersistenceLabeler
)


def _row(cluster_id, cell_id, date):
    return {
        "cluster_id": cluster_id,
        "cell_id": cell_id,
        "Mscan_date": date
    }


def test_temporal_source_hint_requires_both_ambiguity_signals():
    persistent_low = pd.Series({
        "temporal_class": "persistent",
        "tci": 0.39,
        "seasonal_concentration": 0.70
    })
    persistent_seasonal = pd.Series({
        "temporal_class": "persistent",
        "tci": 0.70,
        "seasonal_concentration": 0.76
    })
    persistent_low_and_seasonal = pd.Series({
        "temporal_class": "persistent",
        "tci": 0.39,
        "seasonal_concentration": 0.76
    })

    assert TemporalPersistenceLabeler._source_hint(
        persistent_low,
        industrial_tci_threshold=0.40,
        industrial_max_seasonal_concentration=0.75
    ) == "industrial"
    assert TemporalPersistenceLabeler._source_hint(
        persistent_seasonal,
        industrial_tci_threshold=0.40,
        industrial_max_seasonal_concentration=0.75
    ) == "industrial"
    assert TemporalPersistenceLabeler._source_hint(
        persistent_low_and_seasonal,
        industrial_tci_threshold=0.40,
        industrial_max_seasonal_concentration=0.75
    ) == "ambiguous"


def test_temporal_source_hint_does_not_assess_transient_activity():
    dates = ["2025-01-10", "2025-04-10", "2025-08-10", "2025-12-10"]
    df = pd.DataFrame([_row(1, "1_0_0", date) for date in dates])

    result = TemporalPersistenceLabeler().fit_transform(df)

    assert set(result["temporal_source_hint"]) == {"not_assessed"}


def test_persistent_reclustering_retains_ambiguous_activity():
    df = pd.DataFrame({
        "temporal_class": ["persistent"] * 6,
        "temporal_source_hint": ["ambiguous"] * 6,
        "X": [0, 1, 2, 3, 4, 5],
        "Y": [0, 1, 2, 3, 4, 5]
    })

    result = PersistentReclusterer(eps=20, min_samples=2).fit_transform(df)

    assert len(result) == 6
    assert set(result["temporal_source_hint"]) == {"ambiguous"}
