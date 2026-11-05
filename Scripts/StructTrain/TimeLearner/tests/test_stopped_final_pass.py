"""Server-only readers of real native sweep-budget fixtures; no synthetic peaks."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256
from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError
from Scripts.StructTrain.TimeLearner.stopped_final_pass import audit_negative_final_pass, load_inputs


class StoppedFinalPass(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = Path(os.environ["TIMELEARNER_STOPPED_FINAL_PRIMARY"]).resolve(strict=True)
        cls.descriptors = [cls.directory / (topology + "-N" + str(mode) + ".inputs.json")
                           for topology in ("Classic", "Branch") for mode in (0, 1)]
        if not all(path.is_file() for path in cls.descriptors):
            raise RuntimeError("all_four_actual_native_sweep_budget_cases_required")

    def case(self):
        return deepcopy(load_inputs(self.descriptors[0]))

    @staticmethod
    def resign(package):
        package["sha256"] = canonical_model_sha256({k: v for k, v in package.items() if k != "sha256"})

    def test_actual_classic_branch_n0_n1_negative_final_passes(self):
        for path in self.descriptors:
            with self.subTest(case=path.name):
                package, summary, packets, traces = load_inputs(path)
                result = audit_negative_final_pass(package, summary, packets, traces)
                self.assertEqual(len(result["residuals"]), len(package["protocol"]["inputs"]))
                self.assertTrue(result["complete_measured_final_pass"])
                self.assertTrue(any(not r["within_timing"] or not r["within_amplitude"] for r in result["residuals"]))
                self.assertEqual(result["training_outcome"], "budget_exhausted")
                self.assertFalse(result["training_completed"])
                self.assertFalse(result["certificate_present"])
                self.assertIsNone(result["evaluation_verdict"])
                self.assertEqual(package["certificate"], None)
                self.assertEqual(summary["certificate"], None)

    def test_final_packet_permutation_preserves_id_based_residuals(self):
        package, summary, packets, traces = self.case()
        original = audit_negative_final_pass(package, summary, packets, traces)
        package["final_packets"].reverse()
        self.resign(package)
        actual = audit_negative_final_pass(package, summary, packets, traces)
        self.assertEqual(actual["residuals"], original["residuals"])

    def test_missing_final_input_is_not_a_complete_pass(self):
        package, summary, packets, traces = self.case()
        package["final_packets"].pop()
        self.resign(package)
        with self.assertRaisesRegex(EvidenceError, "incomplete_negative_final_pass"):
            audit_negative_final_pass(package, summary, packets, traces)

    def test_duplicate_final_packet_is_rejected(self):
        package, summary, packets, traces = self.case()
        package["final_packets"][-1] = package["final_packets"][0]
        self.resign(package)
        with self.assertRaises(EvidenceError):
            audit_negative_final_pass(package, summary, packets, traces)

    def test_changed_summary_tolerance_is_rejected(self):
        package, summary, packets, traces = self.case()
        summary["tolerances"]["sync"] += 1.
        with self.assertRaisesRegex(EvidenceError, "final_pass_tolerances_changed"):
            audit_negative_final_pass(package, summary, packets, traces)

    def test_resigned_loose_criteria_cannot_hide_the_negative_outcome(self):
        package, summary, packets, traces = self.case()
        loose = {"amplitude_absolute": 100., "amplitude_relative": 0., "sync": 100.}
        package["configuration"]["search"]["tolerances"] = dict(loose)
        summary["tolerances"] = dict(loose)
        self.resign(package)
        with self.assertRaisesRegex(EvidenceError, "sweep_budget_stop_has_no_measured_final_violation"):
            audit_negative_final_pass(package, summary, packets, traces)

    def test_source_digest_cannot_be_ignored(self):
        package, summary, packets, traces = self.case()
        package["reason"] = "different_reason"
        with self.assertRaisesRegex(EvidenceError, "package_digest_mismatch"):
            audit_negative_final_pass(package, summary, packets, traces)

    def test_missing_csv_cannot_be_replaced_by_a_valid_flag(self):
        package, summary, packets, traces = self.case()
        traces.pop(next(iter(traces)))
        with self.assertRaises(EvidenceError):
            audit_negative_final_pass(package, summary, packets, traces)

    def test_unknown_summary_schema_is_rejected(self):
        for version in (99, 1.0, True):
            with self.subTest(version=version):
                package, summary, packets, traces = self.case()
                summary["schema_version"] = version
                with self.assertRaisesRegex(EvidenceError, "unknown_negative_final_summary_schema"):
                    audit_negative_final_pass(package, summary, packets, traces)

    def test_noninteger_protocol_schema_is_rejected(self):
        package, summary, packets, traces = self.case()
        package["protocol"]["schema_version"] = 3.0
        self.resign(package)
        with self.assertRaisesRegex(EvidenceError, "unknown_negative_final_protocol_schema"):
            audit_negative_final_pass(package, summary, packets, traces)

    def test_sweep_budget_cannot_be_changed_in_the_summary(self):
        package, summary, packets, traces = self.case()
        summary["configuration"]["maximum_sweeps"] += 1
        with self.assertRaisesRegex(EvidenceError, "negative_final_pass_attempt_mismatch"):
            audit_negative_final_pass(package, summary, packets, traces)

    def test_production_cli_checks_the_actual_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "result.json"
            result = subprocess.run([sys.executable, "-m", "Scripts.StructTrain.TimeLearner", "analyze",
                                     str(self.descriptors[0]), "--format", "stopped-final-pass", "--output", str(output)],
                                    capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
            parsed = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(parsed["complete_measured_final_pass"])
            self.assertFalse(parsed["certificate_present"])

    def test_unknown_descriptor_schema_fails_without_a_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            source, output = Path(temporary) / "source.json", Path(temporary) / "result.json"
            source.write_text(json.dumps({"kind": "timelearner_stopped_final_pass_inputs", "schema_version": 99,
                                          "package": "missing.json", "summary": "missing.json", "trials": []}), encoding="utf-8")
            result = subprocess.run([sys.executable, "-m", "Scripts.StructTrain.TimeLearner", "analyze", str(source),
                                     "--format", "stopped-final-pass", "--output", str(output)], capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn(b"unknown_stopped_final_pass_inputs", result.stderr)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
