"""Actual native Solo LTZ data and strict corrupted-data controls."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError, load
from ..solo_threshold_evidence import audit_solo_threshold_trace


class SoloThresholdEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_SOLO_THRESHOLD_NATIVE")
        if not directory:
            raise unittest.SkipTest("requires eight actual native LTZ characterization controls")
        cls.paths = sorted(Path(directory).glob("*_solo_threshold_*.json"))
        if len(cls.paths) != 8:
            raise RuntimeError("requires both topologies and all four native scenarios")

    def test_actual_complete_spiking_reset_and_changed_model(self):
        for path in self.paths:
            with self.subTest(case=path.name):
                report = load(path)
                result = audit_solo_threshold_trace(report)
                scenario = int(path.stem.rsplit("_", 1)[1])
                self.assertIsNone(result["evaluation_verdict"])
                self.assertFalse(result["calibrated"])
                if scenario == 0:
                    self.assertTrue(result["complete"])
                    self.assertTrue(result["valid"])
                    self.assertTrue(result["proposal_eligible"])
                    self.assertEqual(result["spikes"], 0)
                    self.assertIsNotNone(result["native_peak_audit"])
                elif scenario == 1:
                    self.assertGreater(result["spikes"], 0)
                    self.assertFalse(result["proposal_eligible"])
                else:
                    self.assertFalse(result["valid"])
                    self.assertFalse(result["proposal_eligible"])

    def test_signed_corrupt_samples_extrema_spikes_and_status_reject(self):
        for path in self.paths:
            if not path.stem.endswith("_0"):
                continue
            original = load(path)
            versions = []
            r = deepcopy(original);r["maximum_after_children"] += .001;versions.append(r)
            r = deepcopy(original);r["spike_times"].append(r["samples"][0]["time"]);versions.append(r)
            r = deepcopy(original);r["valid"] = False;versions.append(r)
            r = deepcopy(original);r["samples"].pop(10);versions.append(r)
            r = deepcopy(original);r["source"]["frequency_hz"] *= 2;versions.append(r)
            for index, report in enumerate(versions):
                report["sha256"] = canonical_model_sha256({k: v for k, v in report.items() if k != "sha256"})
                with self.subTest(case=path.name, corruption=index):
                    with self.assertRaises(EvidenceError):
                        audit_solo_threshold_trace(report)
