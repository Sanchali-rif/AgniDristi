import pandas as pd

from app.pipeline.vnf.temporal import TemporalPersistenceLabeler


def _rows(cluster_id, dates):
    return [
        {
            "cluster_id": cluster_id,
            "cell_id": f"{cluster_id}_0_0",
            "Mscan_date": date
        }
        for date in dates
    ]


def test_missing_calendar_months_are_not_consecutive():
    dates = (
        ["2025-01-05"] * 4
        + ["2025-03-05"] * 3
        + ["2025-05-05"] * 3
    )

    result = TemporalPersistenceLabeler().fit_transform(
        pd.DataFrame(_rows(1, dates))
    )
    record = result.iloc[0]

    assert record["total_months"] == 5
    assert record["longest_active_run"] == 1
    assert record["max_internal_inactive_gap"] == 1
    assert record["temporal_class"] == "transient"


def test_leading_inactivity_does_not_break_a_recurring_source():
    analysis_context = _rows(
        1,
        pd.date_range("2025-01-01", "2025-12-01", freq="MS")
    )
    recent_source = _rows(
        2,
        pd.date_range("2025-07-01", "2025-12-01", freq="MS")
    )

    result = TemporalPersistenceLabeler().fit_transform(
        pd.DataFrame(analysis_context + recent_source)
    )
    record = result[result["cluster_id"] == 2].iloc[0]

    assert record["leading_inactive_months"] == 6
    assert record["max_internal_inactive_gap"] == 0
    assert record["source_span_months"] == 6
    assert record["temporal_class"] == "persistent"


def test_many_pixels_on_too_few_dates_are_transient():
    dates = (
        ["2025-01-05"] * 5
        + ["2025-02-05"] * 5
        + ["2025-03-05"] * 5
    )

    result = TemporalPersistenceLabeler().fit_transform(
        pd.DataFrame(_rows(1, dates))
    )
    record = result.iloc[0]

    assert record["total_detections"] == 15
    assert record["unique_active_dates"] == 3
    assert record["temporal_class"] == "transient"


def test_three_month_run_with_later_long_gap_is_transient():
    dates = list(pd.date_range("2025-12-01", "2026-02-28", freq="7D"))
    dates.append(pd.Timestamp("2026-08-10"))

    result = TemporalPersistenceLabeler().fit_transform(
        pd.DataFrame(_rows(1, dates))
    )
    record = result.iloc[0]

    assert record["active_months"] == 4
    assert record["longest_active_run"] == 3
    assert record["max_internal_inactive_gap"] == 5
    assert record["unique_active_dates"] >= 10
    assert record["temporal_class"] == "transient"


def test_sparse_source_lifespan_fails_source_persistence_ratio():
    dates = list(pd.date_range("2025-01-01", "2025-03-31", freq="7D"))
    dates.extend([
        pd.Timestamp("2025-07-10"),
        pd.Timestamp("2025-11-10")
    ])

    result = TemporalPersistenceLabeler().fit_transform(
        pd.DataFrame(_rows(1, dates))
    )
    record = result.iloc[0]

    assert record["longest_active_run"] == 3
    assert record["max_internal_inactive_gap"] == 3
    assert record["source_span_months"] == 11
    assert record["source_persistence_ratio"] < 0.50
    assert record["temporal_class"] == "transient"


def test_low_full_window_persistence_ratio_is_transient():
    analysis_context = _rows(
        1,
        pd.date_range("2025-01-01", "2025-09-01", freq="MS")
    )
    three_month_source = _rows(
        2,
        pd.date_range("2025-01-01", "2025-03-31", freq="7D")
    )

    result = TemporalPersistenceLabeler().fit_transform(
        pd.DataFrame(analysis_context + three_month_source)
    )
    record = result[result["cluster_id"] == 2].iloc[0]

    assert record["active_months"] == 3
    assert record["persistence_ratio"] < 0.50
    assert record["source_persistence_ratio"] == 1.0
    assert record["temporal_class"] == "transient"
    assert record["temporal_source_hint"] == "not_assessed"
