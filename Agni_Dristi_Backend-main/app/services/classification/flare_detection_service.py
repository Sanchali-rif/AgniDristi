import logging

import numpy as np
import pandas as pd


logger = logging.getLogger(__name__)

LIKELY_THRESHOLD = 0.70
POSSIBLE_THRESHOLD = 0.50


def _number(value):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None

    return result if np.isfinite(result) else None


def _ramp(value, low, high):
    value = _number(value)
    if value is None:
        return 0.0
    return float(np.clip((value - low) / (high - low), 0.0, 1.0))


def _inverse_ramp(value, low, high):
    value = _number(value)
    if value is None:
        return 0.0
    return float(np.clip((high - value) / (high - low), 0.0, 1.0))


def _assess_row(row):
    signals = {
        "high_mean_temperature": 0.20 * _ramp(row.get("temp_mean"), 900, 1700),
        "high_peak_temperature": 0.15 * _ramp(row.get("temp_max"), 1300, 2300),
        "compact_emitting_area": 0.15 * _inverse_ramp(row.get("area_mean"), 5, 100),
        "radiant_heat": 0.05 * _ramp(row.get("rh_mean"), 0.5, 4.0),
        "temporal_persistence": 0.08 * _ramp(
            row.get("persistence_ratio"), 0.50, 1.0
        ),
        "source_persistence": 0.05 * _ramp(
            row.get("source_persistence_ratio"), 0.50, 1.0
        ),
        "active_months": 0.04 * _ramp(row.get("active_months"), 3, 9),
        "low_seasonality": 0.03 * _inverse_ramp(
            row.get("seasonal_concentration"), 0.40, 0.90
        )
    }

    score = sum(signals.values())
    reasons = [name for name, contribution in signals.items() if contribution > 0]

    gem_available = row.get("classification_source") == "GEM_DATABASE"
    gem_category = str(row.get("predicted_label") or "")
    exact_type = str(row.get("gem_industry_exact_type") or "").lower()

    if gem_available and gem_category == "Oil_Gas":
        context_score = 0.30 if "field" in exact_type else 0.20
        score += context_score
        source = "GEM_OIL_GAS_AND_VNF"
        reasons.append("nearby_gem_oil_gas_facility")
        if "field" in exact_type:
            reasons.append("gem_oil_or_gas_field")
    elif gem_available:
        score -= 0.25
        source = "GEM_NON_OIL_GAS_AND_VNF"
        reasons.append("nearby_gem_non_oil_gas_facility")
    else:
        source = "VNF_HEURISTIC"
        reasons.append("no_decisive_gem_context")

    score = round(float(np.clip(score, 0.0, 1.0)), 4)

    if score >= LIKELY_THRESHOLD:
        likelihood = "LIKELY"
    elif score >= POSSIBLE_THRESHOLD:
        likelihood = "POSSIBLE"
    else:
        likelihood = "UNLIKELY"

    return {
        "gas_flare_candidate": likelihood == "LIKELY",
        "gas_flare_likelihood": likelihood,
        "gas_flare_score": score,
        "gas_flare_source": source,
        "gas_flare_evidence": {
            "reasons": reasons,
            "signal_contributions": {
                name: round(contribution, 4)
                for name, contribution in signals.items()
            },
            "gem_facility_name": row.get("gem_facility_name"),
            "gem_industry_exact_type": row.get("gem_industry_exact_type")
        }
    }


def assess_gas_flare_candidates(objects: pd.DataFrame):
    """Add an explainable gas-flare likelihood assessment to each object."""
    output = objects.copy()

    if output.empty:
        output["gas_flare_candidate"] = pd.Series(dtype="bool")
        output["gas_flare_likelihood"] = pd.Series(dtype="object")
        output["gas_flare_score"] = pd.Series(dtype="float")
        output["gas_flare_source"] = pd.Series(dtype="object")
        output["gas_flare_evidence"] = pd.Series(dtype="object")
        return output

    assessments = pd.DataFrame(
        [_assess_row(row) for _, row in output.iterrows()],
        index=output.index
    )

    for column in assessments.columns:
        output[column] = assessments[column]

    logger.info(
        "Gas flare assessment completed | total=%s | likely=%s | possible=%s | "
        "unlikely=%s | gem_context=%s | vnf_only=%s",
        len(output),
        int((output["gas_flare_likelihood"] == "LIKELY").sum()),
        int((output["gas_flare_likelihood"] == "POSSIBLE").sum()),
        int((output["gas_flare_likelihood"] == "UNLIKELY").sum()),
        int(output["gas_flare_source"].str.startswith("GEM_").sum()),
        int((output["gas_flare_source"] == "VNF_HEURISTIC").sum())
    )

    return output
