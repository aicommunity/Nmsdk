"""Recheck actual saved-model ownership controls, not process attestation.

The native assertions establish queue/lifecycle behaviour. These checks bind
their saved models and complete observations to the production proof readers.
Cancelled partial observations remain diagnostics, never calibration evidence.
"""
import os
from pathlib import Path
import unittest

from ..calibration_transaction_evidence import audit_native_calibration_transaction
from ..learned_evidence import load_case
from ..native_evidence import load
from ..recognition_trial_evidence import audit_recognition_trial
from ..threshold_candidate_evidence import audit_threshold_candidate


class NativeCalibrationOwnershipEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_CALIBRATION_OWNERSHIP_DIR")
        source = os.environ.get("TIMELEARNER_CALIBRATION_OWNERSHIP_SOURCE")
        if not directory or not source:
            raise unittest.SkipTest("requires actual eight native ownership controls and primary source")
        cls.records = {}
        for path in Path(directory).glob("*_ownership_*.json"):
            record = load(path)
            key = (record["topology"], record["scenario"])
            if key in cls.records:
                raise RuntimeError("duplicate ownership control")
            cls.records[key] = record
        if set(cls.records) != {(top, scenario) for top in ("Classic", "Branch") for scenario in range(4)}:
            raise RuntimeError("requires all eight actual ownership controls")
        cls.sources = {load(path)["sha256"]: load_case(path)
                       for path in Path(source).glob("*_learned_state.json")}
        if len(cls.sources) != 2:
            raise RuntimeError("requires both primary training sources")

    def test_every_record_binds_the_primary_model_and_transaction(self):
        fields = {"kind", "schema_version", "topology", "scenario", "transaction",
                  "candidate_before", "package_after", "foreign_result_preserved",
                  "external_observation", "evaluation_verdict"}
        for (top, scenario), record in self.records.items():
            self.assertEqual(set(record), fields)
            self.assertEqual(record["kind"], "native_calibration_ownership_control")
            self.assertIs(type(record["schema_version"]), int)
            self.assertEqual(record["schema_version"], 1)
            self.assertIs(type(record["scenario"]), int)
            self.assertIsNone(record["evaluation_verdict"])
            report = record["transaction"]
            source = self.sources[report["source_recognition"]["source_solo"]["sha256"]]
            audit = audit_native_calibration_transaction(report, source)
            self.assertTrue(audit["transaction_evidence_consistent"])
            self.assertFalse(audit["native_execution_verified"])
            self.assertEqual(report["attempt_id"], top+"/ownership/"+str(scenario))

    def test_interference_preserves_the_candidate_without_claiming_rollback(self):
        for (_, scenario), record in self.records.items():
            if scenario == 3:
                continue
            report = record["transaction"]
            self.assertEqual(report["status"], "recovery_required")
            self.assertFalse(report["source_restored"])
            self.assertFalse(report["calibrated"])
            self.assertEqual(record["candidate_before"], record["package_after"])
            candidate = record["candidate_before"]
            audit_threshold_candidate(candidate)
            self.assertEqual(candidate["source_recognition"], report["source_recognition"])
            self.assertEqual(report["candidates"], [])
            reason = ("recognition_context_replaced" if scenario == 2 else "trial_ownership_changed")
            self.assertIn(reason, report["reason"])
            self.assertIs(record["foreign_result_preserved"], True)

    def test_externally_consumed_result_is_a_complete_actual_candidate_probe(self):
        for (_, scenario), record in self.records.items():
            if scenario != 1:
                continue
            observation = record["external_observation"]
            audit_recognition_trial(observation, record["candidate_before"])
            self.assertIs(observation["complete"], True)
            self.assertIs(observation["valid"], True)
            request = record["transaction"]["active_matrix"]["requests"][0]
            for key, value in request.items():
                if key not in {"maximum_samples", "record_threshold_potential"}:
                    self.assertEqual(observation[key], value)
            self.assertEqual(record["transaction"]["active_matrix"]["observations"], [])

    def test_normal_flow_commits_only_the_freshly_confirmed_package(self):
        for (_, scenario), record in self.records.items():
            if scenario != 3:
                continue
            report = record["transaction"]
            self.assertEqual(report["status"], "calibrated")
            self.assertEqual(len(report["candidates"]), 2)
            self.assertEqual(report["selected_index"], 1)
            self.assertEqual(record["package_after"], report["calibrated_package"])
            self.assertIsNone(record["external_observation"])
            self.assertFalse(report["grid_selection_embedded_in_model_proof"])

