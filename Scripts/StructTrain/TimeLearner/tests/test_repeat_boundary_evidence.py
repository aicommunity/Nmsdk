"""Read actual repeated-N0 Train/Test and stopped boundary artifacts."""
import copy
import os
from pathlib import Path
import unittest

from ..learned_evidence import audit_learned_state, load_case as load_learned
from ..stopped_evidence import audit_stopped_state, load_case as load_stopped
from ..native_evidence import EvidenceError, audit_training_summary, load
from ..model_identity import canonical_model_sha256


class RepeatBoundaryEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_REPEAT_BOUNDARY_DIR")
        if not directory:
            raise unittest.SkipTest("requires actual repeated-N0 boundary runs")
        cls.root = Path(directory)
        cls.completed = sorted(cls.root.glob("*repeat2_learned_state.json"))
        cls.stopped = sorted(cls.root.glob("*stopped_N0Repeated*_stopped_state.json"))
        if len(cls.completed) != 4 or len(cls.stopped) != 6:
            raise RuntimeError("requires four completed and six stopped native cases")

    def test_completed_original_and_restored_proofs_use_primary_traces(self):
        for path in self.completed:
            package, summary, packets, traces = load_learned(path)
            original = audit_learned_state(package, summary, packets, traces)
            self.assertEqual(original["n0_candidate_repeats"], 2)
            self.assertIs(original["search_history_retained"], True)
            restored = load(path.with_name(path.name.removesuffix("_learned_state.json")+"_imported_summary.json"))
            result = audit_learned_state(package, restored, packets, traces)
            self.assertIs(result["search_history_retained"], False)
            self.assertEqual(result["exact"], original["exact"])
            self.assertIsNone(result["evaluation_verdict"])
            self.assertEqual(restored["candidate_repeat_groups"], [])

    def test_stopped_original_and_restored_remain_diagnostic(self):
        for path in self.stopped:
            package, summary, packets, traces = load_stopped(path)
            for value in (summary, load(path.with_name(path.name.removesuffix("_stopped_state.json")+"_imported_summary.json"))):
                result = audit_stopped_state(package, value, packets, traces)
                self.assertEqual(result["n0_candidate_repeats"], 2)
                self.assertFalse(result["certificate_present"])
                self.assertIsNone(result["evaluation_verdict"])
            if "HalfCandidate" in path.name:
                self.assertEqual(len(summary["candidates"]), 1)
                group, = summary["candidate_repeat_groups"]
                self.assertFalse(group["complete"])
                trial, = group["trial_ids"]
                candidate, = summary["candidates"]
                self.assertEqual(candidate["trial_id"], trial)
                packet = packets[trial]
                input_id = packet["prepared"]["input_id"]
                peak, = [p for p in packet["observation"]["peaks"] if p["input_id"] == input_id]
                self.assertEqual(group["raw_potentials"], [peak["raw_potential"]])

    def test_missing_history_cannot_be_relabelled_as_measured_search(self):
        path = self.completed[0]
        package, summary, packets, traces = load_learned(path)
        restored = load(path.with_name(path.name.removesuffix("_learned_state.json")+"_imported_summary.json"))
        for marker in (None, True, 0, "false"):
            value = copy.deepcopy(restored)
            if marker is None:
                del value["search_history_retained"]
            else:
                value["search_history_retained"] = marker
            with self.assertRaises(EvidenceError):
                audit_training_summary(value, packets, package["protocol"]["origin_stimulus_id"])
        value = copy.deepcopy(summary);value["search_history_retained"] = False
        self.assertTrue(value["candidates"])
        with self.assertRaises(EvidenceError):
            audit_training_summary(value, packets, package["protocol"]["origin_stimulus_id"])

    def test_changed_repeat_factor_is_not_hidden_by_a_resigned_package(self):
        for path, loader, audit in [(self.completed[0], load_learned, audit_learned_state),
                                    (self.stopped[0], load_stopped, audit_stopped_state)]:
            package, summary, packets, traces = loader(path)
            for factor in (3, True, 1):
                value = copy.deepcopy(package)
                value["configuration"]["search"]["n0_candidate_repeats"] = factor
                value["sha256"] = canonical_model_sha256({k: v for k, v in value.items() if k != "sha256"})
                with self.assertRaises(EvidenceError):
                    audit(value, summary, packets, traces)
