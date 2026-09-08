import unittest

import pandas as pd

from app.services.classification.flare_detection_service import (
    assess_gas_flare_candidates
)


def _strong_thermal_object(**overrides):
    row = {
        "temp_mean": 1700.0,
        "temp_max": 2300.0,
        "area_mean": 5.0,
        "rh_mean": 4.0,
        "persistence_ratio": 1.0,
        "source_persistence_ratio": 1.0,
        "active_months": 9,
        "seasonal_concentration": 0.4,
        "classification_source": "VNF_XGBOOST",
        "predicted_label": "Other_Industrial",
        "gem_facility_name": None,
        "gem_industry_exact_type": None
    }
    row.update(overrides)
    return row


class FlareDetectionServiceTests(unittest.TestCase):
    def test_gem_oil_gas_context_strengthens_flare_evidence(self):
        objects = pd.DataFrame([_strong_thermal_object(
            classification_source="GEM_DATABASE",
            predicted_label="Oil_Gas",
            gem_facility_name="Example Gas Field",
            gem_industry_exact_type="Gas Field"
        )])

        result = assess_gas_flare_candidates(objects).iloc[0]

        self.assertTrue(result["gas_flare_candidate"])
        self.assertEqual(result["gas_flare_likelihood"], "LIKELY")
        self.assertEqual(result["gas_flare_source"], "GEM_OIL_GAS_AND_VNF")
        self.assertIn(
            "nearby_gem_oil_gas_facility",
            result["gas_flare_evidence"]["reasons"]
        )

    def test_strong_vnf_evidence_can_identify_candidate_without_gem(self):
        result = assess_gas_flare_candidates(
            pd.DataFrame([_strong_thermal_object()])
        ).iloc[0]

        self.assertTrue(result["gas_flare_candidate"])
        self.assertEqual(result["gas_flare_source"], "VNF_HEURISTIC")

    def test_weak_vnf_evidence_is_unlikely(self):
        objects = pd.DataFrame([_strong_thermal_object(
            temp_mean=850.0,
            temp_max=1100.0,
            area_mean=200.0,
            rh_mean=0.1,
            persistence_ratio=0.5,
            source_persistence_ratio=0.5,
            active_months=2,
            seasonal_concentration=0.95
        )])

        result = assess_gas_flare_candidates(objects).iloc[0]

        self.assertFalse(result["gas_flare_candidate"])
        self.assertEqual(result["gas_flare_likelihood"], "UNLIKELY")


if __name__ == "__main__":
    unittest.main()
