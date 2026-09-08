import unittest
from unittest.mock import Mock

import pandas as pd

from app.services.vnf.vnf_candidate_state_service import finalize_vnf_states


class _CountResult:
    def mappings(self):
        return self

    def first(self):
        return {"known": 1, "transient": 0, "candidate": 0}


class VnfCandidateStateServiceTests(unittest.TestCase):
    def test_gem_metadata_is_written_to_member_detections(self):
        db = Mock()
        db.execute.side_effect = [Mock(), Mock(), _CountResult()]
        persistent = pd.DataFrame([{
            "stage3_object_id": "OBJ-1",
            "db_detection_id": 42
        }])
        classified = pd.DataFrame([{
            "stage3_object_id": "OBJ-1",
            "classification_source": "GEM_DATABASE",
            "gem_industry_exact_type": "Steel Plant",
            "gem_facility_name": "Example Steel Works"
        }])

        result = finalize_vnf_states(
            db,
            "BATCH-1",
            persistent,
            {"OBJ-1": "THERM-1"},
            classified_objects=classified
        )

        member_update_params = db.execute.call_args_list[1].args[1]
        self.assertEqual(member_update_params["ids"], [42])
        self.assertEqual(member_update_params["object_uid"], "THERM-1")
        self.assertEqual(
            member_update_params["gem_industry_exact_type"],
            "Steel Plant"
        )
        self.assertEqual(
            member_update_params["gem_facility_name"],
            "Example Steel Works"
        )
        self.assertEqual(result["persistent_updated"], 1)


if __name__ == "__main__":
    unittest.main()
