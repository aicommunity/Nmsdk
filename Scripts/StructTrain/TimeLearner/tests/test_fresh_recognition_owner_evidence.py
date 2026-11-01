import copy
import os
from pathlib import Path
import unittest

from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError, load
from Scripts.StructTrain.TimeLearner.recognition_owner_evidence import load_case
from Scripts.StructTrain.TimeLearner.fresh_recognition_owner_evidence import audit_fresh_destination, audit_fresh_owner_process


class FreshRecognitionOwnerEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = os.environ.get("TIMELEARNER_FRESH_OWNER_EVIDENCE_DIR")
        replay = os.environ.get("TIMELEARNER_FRESH_OWNER_REPLAY_DIR")
        if not source or not replay:
            raise unittest.SkipTest("requires actual distinct-owner and fresh-process native outputs")
        cls.paths = sorted(Path(source).glob("*_owner_recognition_state.json"))
        expected = {"Classic_2000_N0_learned_boundary_configured_recognition_7_owner_recognition_state.json",
                    "Branch_2000_N1_learned_boundary_configured_recognition_8_owner_recognition_state.json"}
        if {path.name for path in cls.paths} != expected:
            raise RuntimeError("requires both configured fresh destination cases")
        cls.cases = [load_case(path) for path in cls.paths]
        cls.transfers = [load(path.with_name(path.name.removesuffix("_state.json") + "_transfer.json")) for path in cls.paths]
        cls.replays = [(load(Path(replay) / f"replay-{i}.json"), Path(replay) / f"replay-{i}.json.csv") for i in range(2)]

    def test_distinct_owner_and_source_graph_preserved(self):
        for case, transfer in zip(self.cases, self.transfers):
            result = audit_fresh_destination(case, transfer)
            self.assertTrue(result["source_model_preserved"])
            self.assertTrue(result["distinct_destination_verified"])

    def test_fresh_process_waveform_byte_exact(self):
        for case, (observation, trace) in zip(self.cases, self.replays):
            result = audit_fresh_owner_process(case, observation, trace)
            self.assertTrue(result["waveform_bytes_exact"])
            self.assertFalse(result["process_provenance_verified"])
            self.assertIsNone(result["evaluation_verdict"])

    def test_same_owner_modified_source_and_defaults_rejected(self):
        for case, original in zip(self.cases, self.transfers):
            for key, value in (("distinct_owners", False), ("source_model_after", "0" * 64),
                               ("target_controller_version_before", 2), ("target_model", "0" * 64)):
                record = copy.deepcopy(original)
                record[key] = value
                with self.subTest(field=key), self.assertRaises(EvidenceError):
                    audit_fresh_destination(case, record)

    def test_fresh_process_wrong_hash_and_controller_rejected(self):
        for case, (original, trace) in zip(self.cases, self.replays):
            for key, value in (("frozen_before", "0" * 64), ("controller_version_after", 1), ("sample_count", 1)):
                record = copy.deepcopy(original)
                record[key] = value
                with self.subTest(field=key), self.assertRaises(EvidenceError):
                    audit_fresh_owner_process(case, record, trace)
