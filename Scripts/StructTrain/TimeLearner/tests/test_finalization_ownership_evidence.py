"""Actual managed native transactions retain source evidence and full responses."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..finalization_ownership_evidence import audit_managed_finalization
from ..learned_evidence import load_case
from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError, load


class FinalizationOwnershipEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_FINALIZATION_OWNERSHIP_NATIVE")
        fixtures = os.environ.get("TIMELEARNER_FINALIZATION_ORIGINAL_FIXTURES")
        if not directory or not fixtures:
            raise unittest.SkipTest("requires complete actual native managed transactions and original source primaries")
        cls.records = sorted(Path(directory).glob("*_managed_finalization_*.json"))
        if len(cls.records) != 4:
            raise RuntimeError("requires Classic/Branch CalculateMode 0/1 native transactions")
        cls.sources = {}
        for topology, source in (("Classic", "Classic-auto_metric"), ("Branch", "Branch-synthetic")):
            paths = list((Path(fixtures)/source/"input/source").glob("*_learned_state.json"))
            if len(paths) != 1:
                raise RuntimeError("requires exactly one original learned source with summary and CSV primaries")
            cls.sources[topology] = load_case(paths[0])

    def test_all_actual_managed_transactions(self):
        for path in self.records:
            with self.subTest(case=path.name):
                result = audit_managed_finalization(load(path), self.sources[path.name.split("_")[0]])
                self.assertTrue(result["external_stop_record_consistent"])
                self.assertFalse(result["native_control_execution_attested"])
                self.assertIsNone(result["scientific_verdict"])

    def test_corrupt_controls_lineage_and_incomplete_matrix_reject(self):
        for path in self.records:
            record = load(path)
            source = self.sources[path.name.split("_")[0]]
            controls = deepcopy(record)
            controls["calculate_mode"] = 1-record["calculate_mode"]
            provider = deepcopy(record)
            provider["provider_after_stop"] = True
            missing = deepcopy(record)
            missing["transaction"]["final_model_matrix"]["observations"].pop()
            report = missing["transaction"]
            report["sha256"] = canonical_model_sha256({k: v for k, v in report.items() if k != "sha256"})
            changed = deepcopy(source[0])
            changed["model_revision"] = "different-model"
            changed["sha256"] = canonical_model_sha256({k: v for k, v in changed.items() if k != "sha256"})
            for name, data, original in (("controls", controls, source), ("provider", provider, source),
                                         ("missing_final_trial", missing, source),
                                         ("source_model", record, (changed, *source[1:]))):
                with self.subTest(case=path.name, corruption=name):
                    with self.assertRaises(EvidenceError):
                        audit_managed_finalization(data, original)
