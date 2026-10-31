"""Actual native request declarations; re-signed identity/source/status controls."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError, load
from ..training_intent_evidence import audit_training_intent, audit_training_intent_lifecycle


class TrainingIntentEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = os.environ.get("TIMELEARNER_TRAINING_INTENT_NATIVE")
        if not folder:
            raise unittest.SkipTest("requires actual native request lifecycle records")
        cls.paths = sorted(Path(folder).glob("*_request_intent.json"))
        if len(cls.paths) != 8:
            raise RuntimeError("requires both topologies, modes and local/connected control")

    def test_actual_request_snapshots_and_session_invalidation(self):
        for path in self.paths:
            with self.subTest(case=path.name):
                result = audit_training_intent_lifecycle(load(path))
                self.assertEqual(result["requests"], 3)
                self.assertFalse(result["calibrated"])

    def test_resigned_missing_binding_and_checkpoint_claim_reject(self):
        for path in self.paths:
            first = load(path)["first"]
            for change in ("schema", "source", "checkpoint", "nonfinite"):
                r = deepcopy(first)
                if change == "schema":
                    r["extra"] = 1
                elif change == "source":
                    del r["controls"]["bindings"]["IsNeedToTrain"]
                elif change == "checkpoint":
                    r["dynamic_checkpoint"] = True
                else:
                    # Invalid numeric token, avoiding non-standard JSON NaN.
                    r["started_model_time"] = "nan"
                r["sha256"] = canonical_model_sha256({k: v for k, v in r.items() if k != "sha256"})
                with self.subTest(case=path.name, mutation=change):
                    with self.assertRaises(EvidenceError):
                        audit_training_intent(r)
