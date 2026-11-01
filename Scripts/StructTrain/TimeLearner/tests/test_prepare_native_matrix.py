"""Preparation uses real cold templates; no model or runtime is fabricated."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from ..native_evidence import EvidenceError, load
from ..native_calibration_worker import _signed
from ..prepare import prepare_matrix


class PrepareNativeMatrixTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_NATIVE_PREFLIGHT_DIR")
        if not directory:
            raise unittest.SkipTest("requires real cold production templates")
        cls.root = Path(directory)

    def specification(self):
        return {"kind": "timelearner_native_matrix_preparation", "schema_version": 1,
            "templates": {t+"-N"+n: load(self.root/"runs"/("pipeline-"+t+"-N"+n)/"input/job.json")
                          for t in ("Classic", "Branch") for n in ("0", "1")},
            "input_counts": [1, 2, 4, 6], "frequencies_hz": [2000, 20000],
            "isi_seconds": .02, "probe_duration": .3, "window_width": .015,
            "n0_candidate_repeats": 2, "run_prefix": "declared-preflight-matrix"}

    def test_preserves_actual_last_reference_and_storage_profiles(self):
        spec = self.specification();jobs = prepare_matrix(spec)
        self.assertEqual(len(jobs), 32)
        for name, job in jobs.items():
            template = spec["templates"][name.split("-inputs")[0]]
            self.assertEqual(job["configuration"]["model"]["inputs"][-1], template["configuration"]["model"]["inputs"][-1])
            self.assertEqual(job["configuration"]["search"]["bounds"][-1], template["configuration"]["search"]["bounds"][-1])
            self.assertEqual(job["profile_archives"], template["profile_archives"])
            self.assertEqual(job["configuration"]["model"]["neuron_class"], template["configuration"]["model"]["neuron_class"])

    def test_does_not_rescale_scientific_tolerances(self):
        spec = self.specification()
        for name, job in prepare_matrix(spec).items():
            original = spec["templates"][name.split("-inputs")[0]]
            self.assertEqual(job["configuration"]["search"]["tolerances"], original["configuration"]["search"]["tolerances"])

    def test_declares_complete_windows_and_sample_budget(self):
        specification = self.specification()
        for name, job in prepare_matrix(specification).items():
            c = job["configuration"];frequency = c["model"]["frequency_hz"]
            self.assertEqual(len(c["windows"]), len(c["model"]["inputs"]))
            original_window = specification["templates"][name.split("-inputs")[0]]["configuration"]["windows"][0]
            self.assertIsInstance(original_window, dict)
            self.assertTrue(all(type(window) is dict and set(window) == set(original_window) for window in c["windows"]))
            self.assertLessEqual(c["windows"][-1]["end"], c["duration"])
            self.assertGreaterEqual(c["maximum_samples"], c["duration"]*frequency+1)
            self.assertEqual(c["maximum_sample_gap"], 1/frequency)

    def test_never_mutates_templates(self):
        spec = self.specification();previous = copy.deepcopy(spec)
        prepare_matrix(spec);self.assertEqual(spec, previous)

    def test_rejects_unknown_fields_and_invalid_or_duplicate_axes(self):
        for key, value in (("extra", 1), ("input_counts", [0]), ("input_counts", [True]),
                           ("frequencies_hz", [2000, 2000]), ("frequencies_hz", ["2000"])):
            spec = self.specification();spec[key] = value
            with self.assertRaises(EvidenceError):prepare_matrix(spec)

    def test_rejects_clipped_window_and_unbounded_sample_budget(self):
        for key, value in (("probe_duration", .01), ("probe_duration", 1e308)):
            spec = self.specification();spec[key] = value
            with self.assertRaises(EvidenceError):prepare_matrix(spec)

    def test_refuses_implicit_inhibition_remapping(self):
        spec = self.specification();template = spec["templates"]["Classic-N1"]
        template["configuration"]["model"]["inhibition"] = [{"input_index": 0, "offset": 1, "resistance": 1e8}]
        spec["templates"]["Classic-N1"] = _signed({k: v for k, v in template.items() if k != "sha256"})
        with self.assertRaisesRegex(EvidenceError, "preparation_requires_two_input_uninhibited_template"):
            prepare_matrix(spec)

    def test_cli_prepares_jobs_without_running_a_model(self):
        with tempfile.TemporaryDirectory() as temporary:
            spec = Path(temporary)/"specification.json";output = Path(temporary)/"prepared"
            spec.write_text(json.dumps(self.specification()), encoding="utf-8")
            result = subprocess.run([sys.executable, "-m", "Scripts.StructTrain.TimeLearner", "prepare", str(spec),
                                     "--output", str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = load(output/"manifest.json")
            self.assertEqual(len(manifest["job_sha256"]), 32)
            self.assertFalse(manifest["effective_model_checked"])
            self.assertFalse(manifest["training_started"])
            self.assertFalse((output/"process").exists())
