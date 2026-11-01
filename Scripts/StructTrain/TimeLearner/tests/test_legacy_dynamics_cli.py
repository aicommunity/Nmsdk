"""Production CLI, full historical module parity and malformed legacy telemetry."""
import contextlib
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from ..__main__ import main
from ..legacy_dynamics import analyze_file, parse_record
from .test_legacy_dynamics import record


class LegacyDynamicsMigrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(os.environ["TIMELEARNER_ORIGINAL_DYNAMICS_MODULE"])
        spec = importlib.util.spec_from_file_location("_historical_branch_dynamics", path)
        cls.old = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.old
        spec.loader.exec_module(cls.old)

    def invoke(self, path, *options):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = main(["analyze", str(path), "--format", "branch-dynamics", *options])
        return status, stdout.getvalue(), stderr.getvalue()

    def test_full_original_module_and_new_summary_agree_on_valid_recorded_format(self):
        text = record(0.01, -0.5, 0.5, 0.0) + record(0.02, 0.25, 1.2, 1.45)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"branch.log";path.write_text(text)
            self.assertEqual(self.old.parse_record(text.splitlines()[0]), parse_record(text.splitlines()[0]))
            for settings in ({}, {"time_step_hz": 2000.0},
                             {"time_step_hz": 20000.0, "rest_bound": 0.5, "soma_abs_limit": 1.0}):
                self.assertEqual(self.old.analyze_file(path, **settings), analyze_file(path, **settings))

    def test_cli_preserves_source_and_exposes_only_descriptive_unknown(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"branch.log";path.write_text(record(0.01, -0.5, 0.5, 0.0))
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            status, text, error = self.invoke(path, "--time-step-hz", "2000")
            self.assertEqual(status, 0, error)
            result = json.loads(text)
            self.assertEqual(result["validity"], "unknown")
            self.assertIsNone(result["evaluation_verdict"])
            self.assertFalse(result["analysis"]["classification_verified"])
            self.assertEqual(result["analysis"]["source_sha256"], before)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before)

    def test_module_cli_works_from_another_directory_without_bin_path(self):
        root = Path(__file__).resolve().parents[4]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"branch.log";path.write_text(record(0.01, -0.5, 0.5, 0.0))
            result = subprocess.run([sys.executable, "-m", "Scripts.StructTrain.TimeLearner",
                "analyze", str(path), "--format", "branch-dynamics"], cwd=directory,
                env={**os.environ, "PYTHONPATH": str(root), "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["validity"], "unknown")

    def test_bad_vector_tokens_remain_visible_and_cannot_produce_finite_gain(self):
        for bad in ("bad", "nan", "inf", ""):
            with self.subTest(token=bad), tempfile.TemporaryDirectory() as directory:
                text = record(0.01, -0.5, 0.5, 0.0).replace("synaptic_inputs=1e-07", "synaptic_inputs=1e-07:"+bad)
                channel = parse_record(text)["components"][0]["channels"][0]
                self.assertEqual(len(channel["bio"]["synaptic_inputs"]), 2)
                self.assertFalse(math.isfinite(channel["synaptic_conductance"]))
                path = Path(directory)/"bad.log";path.write_text(text)
                status, output, error = self.invoke(path, "--time-step-hz", "2000")
                self.assertEqual(status, 0, error)
                summary = json.loads(output)["analysis"]
                self.assertTrue(summary["non_finite_examples"])
                self.assertEqual(summary["channels"]["s.c0"]["synaptic_conductance"]["non_finite"], 1)
                self.assertEqual(summary["channels"]["s.c0"]["explicit_step_gain_from_observed_time_constant"]["count"], 0)

    def test_nonfinite_zero_and_negative_diagnostic_options_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"branch.log";path.write_text(record(0.01, -0.5, 0.5, 0.0))
            for option in ("--rest-bound", "--soma-abs-limit", "--time-step-hz"):
                for value in ("nan", "inf", "0", "-1"):
                    with self.subTest(option=option, value=value):
                        status, output, error = self.invoke(path, option+"="+value)
                        self.assertEqual(status, 2)
                        self.assertFalse(output)
                        self.assertEqual(json.loads(error)["validity"], "invalid")

    def test_unknown_record_schema_cannot_be_scored(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"unknown.log";path.write_text("schema=99;trainer=branch;now=0\n")
            status, output, error = self.invoke(path)
            self.assertEqual(status, 2)
            self.assertFalse(output)
            self.assertIsNone(json.loads(error)["evaluation_verdict"])

    def test_actually_modified_log_cannot_be_published_as_one_immutable_source(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"changing.log";path.write_text(record(0.01, -0.5, 0.5, 0.0))
            original_parser = parse_record
            changed = False
            def append_during_read(line):
                nonlocal changed
                if not changed:
                    with path.open("a") as output:
                        output.write(record(0.02, -0.4, 0.4, 0.0))
                    changed = True
                return original_parser(line)
            with patch("Scripts.StructTrain.TimeLearner.legacy_dynamics.parse_record", append_during_read):
                status, output, error = self.invoke(path)
            self.assertTrue(changed)
            self.assertEqual(status, 2)
            self.assertFalse(output)
            self.assertEqual(json.loads(error)["reason"], "dynamics_source_changed_during_analysis")

    def test_existing_output_and_missing_input_are_process_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"branch.log";path.write_text(record(0.01, -0.5, 0.5, 0.0))
            output = Path(directory)/"prior.json";output.write_text("prior")
            for source, options in ((path, ("--output", str(output))), (path.with_name("missing.log"), ())):
                status, text, error = self.invoke(source, *options)
                self.assertEqual(status, 2)
                self.assertFalse(text)
                result = json.loads(error)
                self.assertEqual((result["execution"], result["validity"]), ("process_error", "unknown"))
            self.assertEqual(output.read_text(), "prior")

    def test_diagnostic_options_cannot_be_applied_to_native_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"irrelevant.json";path.write_text("{}")
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                status = main(["analyze", str(path), "--format", "domain", "--rest-bound", "1"])
            self.assertEqual(status, 2)
            self.assertFalse(stdout.getvalue())
            self.assertEqual(json.loads(stderr.getvalue())["reason"], "rest_bound_is_only_for_branch_dynamics")


if __name__ == "__main__":
    unittest.main()
