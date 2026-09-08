from datetime import date
import unittest

import pandas as pd

from app.services.vnf.vnf_object_profile_service import (
    _calculate_profile_updates,
)


class ObjectProfileCalculationTests(unittest.TestCase):
    def test_calculates_profiles_for_multiple_objects(self):
        detections = pd.DataFrame([
            {
                "object_uid": "OBJECT_A",
                "temp_primary": 1000.0,
                "rh_primary": 2.0,
                "area_primary": 10.0,
                "mscan_date": date(2026, 1, 5),
            },
            {
                "object_uid": "OBJECT_A",
                "temp_primary": 1100.0,
                "rh_primary": 4.0,
                "area_primary": 20.0,
                "mscan_date": date(2026, 2, 5),
            },
            {
                "object_uid": "OBJECT_B",
                "temp_primary": 900.0,
                "rh_primary": 3.0,
                "area_primary": 15.0,
                "mscan_date": date(2026, 2, 10),
            },
        ])

        updates = _calculate_profile_updates(detections)

        self.assertEqual(set(updates), {"OBJECT_A", "OBJECT_B"})

        object_a = updates["OBJECT_A"]
        self.assertEqual(object_a["detection_count"], 2)
        self.assertEqual(object_a["active_months"], 2)
        self.assertEqual(object_a["temp_mean"], 1050.0)
        self.assertEqual(object_a["temp_median"], 1050.0)
        self.assertEqual(object_a["temp_min"], 1000.0)
        self.assertEqual(object_a["temp_max"], 1100.0)
        self.assertEqual(object_a["temp_range"], 100.0)
        self.assertAlmostEqual(
            sum(object_a["thermal_fingerprint"].values()),
            1.0
        )

        object_b = updates["OBJECT_B"]
        self.assertEqual(object_b["detection_count"], 1)
        self.assertEqual(object_b["active_months"], 1)
        self.assertIsNone(object_b["temp_std"])
        self.assertIsNone(object_b["temp_cv"])

    def test_ignores_invalid_values_without_dropping_detections(self):
        detections = pd.DataFrame([
            {
                "object_uid": "OBJECT_A",
                "temp_primary": "invalid",
                "rh_primary": None,
                "area_primary": None,
                "mscan_date": None,
            }
        ])

        profile = _calculate_profile_updates(detections)["OBJECT_A"]

        self.assertEqual(profile["detection_count"], 1)
        self.assertEqual(profile["active_months"], 0)
        self.assertIsNone(profile["temp_mean"])
        self.assertEqual(profile["thermal_fingerprint"], {})


if __name__ == "__main__":
    unittest.main()
