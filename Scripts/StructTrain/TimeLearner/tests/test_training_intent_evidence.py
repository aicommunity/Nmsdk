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
                record = load(path)
                self.assertEqual(record["schema_version"], 2)
                result = audit_training_intent_lifecycle(record)
                self.assertEqual(result["requests"], 3)
                self.assertFalse(result["calibrated"])
                self.assertTrue(result["successful_import_recorded"])

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

    def test_resigned_boundary_controls_session_and_import_claim_reject(self):
        def sign(value):
            value["sha256"] = canonical_model_sha256({k: v for k, v in value.items() if k != "sha256"})

        for path in self.paths:
            record = load(path)
            for change in ("controls", "session", "import", "sources"):
                r = deepcopy(record)
                b = r["stopped_boundary"]
                if change == "controls":
                    b["controls"]["parameters"]["CalibrateLTZThresholdFraction"] += .1
                elif change == "session":
                    b["training_request"]["session_attempt"] += 1
                    sign(b["training_request"])
                elif change == "import":
                    r["import_adopted"] = False
                else:
                    binding = b["controls"]["bindings"]["IsNeedToTrain"]
                    binding["connected"] = not binding["connected"]
                sign(b)
                with self.subTest(case=path.name, mutation=change):
                    with self.assertRaises(EvidenceError):
                        audit_training_intent_lifecycle(r)
