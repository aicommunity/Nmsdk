"""Independent actual native formulas, clamps, stale sources and Solo confirmation."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError, load
from ..training_threshold_reference import audit_training_threshold_reference, audit_solo_threshold_confirmation


class TrainingThresholdReferenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = os.environ.get("TIMELEARNER_TRAINING_THRESHOLD_NATIVE")
        if not folder:
            raise unittest.SkipTest("requires actual native proposal and confirmation records")
        cls.folder = Path(folder)
        cls.sources = sorted((cls.folder/"threshold-references").glob("*-proposals.json"))
        if len(cls.sources) != 6:
            raise RuntimeError("requires both topologies, eligible/spiking/changed-model proposals")

    def test_actual_proposals_and_real_selected_threshold_bursts(self):
        proposals, confirmations = 0, 0
        for path in self.sources:
            name = path.name.removesuffix("-proposals.json")
            source = load(self.folder/(name+".json"))
            batch = load(path)
            self.assertEqual(batch["source_trace_sha256"], source["sha256"])
            for proposal in batch["proposals"]:
                result = audit_training_threshold_reference(proposal, source)
                self.assertFalse(result["calibrated"])
                proposals += 1
            if name.endswith("_0"):
                actual = load(path.with_name(name+"-confirmation.json"))
                result = audit_solo_threshold_confirmation(batch["proposals"][0], source, actual)
                self.assertGreater(result["spikes"], 0)
                self.assertTrue(result["recognition_confirmation_required"])
                self.assertFalse(result["calibrated"])
                confirmations += 1
        self.assertEqual((proposals, confirmations), (14, 2))

    def test_resigned_wrong_formula_clamp_source_and_acceptance_reject(self):
        for path in self.sources:
            name = path.name.removesuffix("-proposals.json")
            if not name.endswith("_0"):
                continue
            source = load(self.folder/(name+".json"))
            original = load(path)["proposals"][0]
            mutations = {"threshold": original["threshold"]*1.01, "positive_minimum": 0.,
                         "clipped": True, "source_model_revision": "wrong-source", "calibrated": True,
                         "sample_selection": "all_after_children", "reason": "calibrated",
                         "current_model_revision": "changed-model"}
            for key, value in mutations.items():
                proposal = deepcopy(original)
                proposal[key] = value
                proposal["sha256"] = canonical_model_sha256({k: v for k, v in proposal.items() if k != "sha256"})
                with self.subTest(case=name, field=key):
                    with self.assertRaises(EvidenceError):
                        audit_training_threshold_reference(proposal, source)
            actual = load(path.with_name(name+"-confirmation.json"))
            actual["source"]["threshold"] *= 1.01
            actual["sha256"] = canonical_model_sha256({k: v for k, v in actual.items() if k != "sha256"})
            with self.assertRaises(EvidenceError):
                audit_solo_threshold_confirmation(original, source, actual)
