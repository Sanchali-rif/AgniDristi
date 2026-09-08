import unittest
from unittest.mock import Mock

import numpy as np
import pandas as pd

from app.services.classification.gem_classifier_service import (
    GEM_SOURCE,
    MODEL_SOURCE,
    classify_industrial_objects
)


class _MappingsResult:
    def __init__(self, rows):
        self._rows = rows

    def mappings(self):
        return self

    def all(self):
        return self._rows


class _FakeModelClassifier:
    def __init__(self):
        self.predict = Mock(side_effect=self._predict)
        self.label_encoder = Mock()
        self.label_encoder.classes_ = np.array([
            "Metallurgical",
            "Mining_Extraction",
            "Oil_Gas",
            "Other_Industrial"
        ])

    @staticmethod
    def _predict(df):
        output = df.copy()
        output["predicted_label"] = "MODEL_RESULT"
        output["predicted_label_confidence"] = 0.75
        output["prob_Metallurgical"] = 0.10
        output["prob_Mining_Extraction"] = 0.15
        output["prob_Oil_Gas"] = 0.75
        output["prob_Other_Industrial"] = 0.00
        return output


class GemClassifierServiceTests(unittest.TestCase):
    def test_unique_database_majority_skips_model(self):
        db = Mock()
        db.execute.return_value = _MappingsResult([
            {
                "row_id": 0,
                "category": "Metallurgical",
                "match_radius_m": 1000,
                "category_count": 3,
                "nearest_facility_name": "Primary Steel Works",
                "nearest_exact_type": "Steel Plant"
            },
            {
                "row_id": 0,
                "category": "Mining_Extraction",
                "match_radius_m": 1000,
                "category_count": 1,
                "nearest_facility_name": "Primary Mine",
                "nearest_exact_type": "Coal Mine"
            },
            {
                "row_id": 0,
                "category": "Oil_Gas",
                "match_radius_m": 3000,
                "category_count": 10,
                "nearest_facility_name": "Outer Terminal",
                "nearest_exact_type": "LNG Terminal"
            }
        ])
        classifier = _FakeModelClassifier()
        objects = pd.DataFrame([{"latitude": 23.5, "longitude": 87.3}])

        result = classify_industrial_objects(
            db,
            objects,
            classifier,
            1000,
            3000,
            5000,
            10000
        )

        classifier.predict.assert_not_called()
        self.assertEqual(result.loc[0, "predicted_label"], "Metallurgical")
        self.assertEqual(result.loc[0, "classification_source"], GEM_SOURCE)
        self.assertEqual(result.loc[0, "gem_match_count"], 4)
        self.assertEqual(result.loc[0, "gem_match_radius_m"], 1000)
        self.assertEqual(result.loc[0, "gem_facility_name"], "Primary Steel Works")
        self.assertEqual(result.loc[0, "gem_industry_exact_type"], "Steel Plant")
        self.assertAlmostEqual(result.loc[0, "predicted_label_confidence"], 0.75)

    def test_tie_and_no_match_use_model_only_for_unresolved_rows(self):
        db = Mock()
        db.execute.return_value = _MappingsResult([
            {
                "row_id": 0,
                "category": "Metallurgical",
                "match_radius_m": 1000,
                "category_count": 2,
                "nearest_facility_name": "Steel A",
                "nearest_exact_type": "Steel Plant"
            },
            {
                "row_id": 0,
                "category": "Oil_Gas",
                "match_radius_m": 1000,
                "category_count": 2,
                "nearest_facility_name": "Terminal A",
                "nearest_exact_type": "LNG Terminal"
            },
            {
                "row_id": 2,
                "category": "Mining_Extraction",
                "match_radius_m": 10000,
                "category_count": 1,
                "nearest_facility_name": "Fallback Mine",
                "nearest_exact_type": "Coal Mine"
            }
        ])
        classifier = _FakeModelClassifier()
        objects = pd.DataFrame([
            {"latitude": 20.0, "longitude": 75.0},
            {"latitude": 21.0, "longitude": 76.0},
            {"latitude": 22.0, "longitude": 77.0}
        ])

        with self.assertLogs(
            "app.services.classification.gem_classifier_service",
            level="INFO"
        ) as logs:
            result = classify_industrial_objects(
                db,
                objects,
                classifier,
                1000,
                3000,
                5000,
                10000
            )

        model_input = classifier.predict.call_args.args[0]
        self.assertEqual(list(model_input.index), [0, 1])
        self.assertEqual(result.loc[0, "classification_source"], MODEL_SOURCE)
        self.assertEqual(result.loc[1, "classification_source"], MODEL_SOURCE)
        self.assertEqual(result.loc[2, "classification_source"], GEM_SOURCE)
        self.assertEqual(result.loc[2, "predicted_label"], "Mining_Extraction")
        self.assertEqual(result.loc[2, "gem_match_radius_m"], 10000)
        self.assertEqual(result.loc[2, "gem_facility_name"], "Fallback Mine")
        self.assertIn("gem=1", logs.output[0])
        self.assertIn("gem_primary=0", logs.output[0])
        self.assertIn("gem_fallback=0", logs.output[0])
        self.assertIn("gem_max=0", logs.output[0])
        self.assertIn("gem_extended=1", logs.output[0])
        self.assertIn("model=2", logs.output[0])


if __name__ == "__main__":
    unittest.main()
