"""Fixed-threshold production jobs validated against real source/model primaries."""
import copy
import os
from pathlib import Path
import unittest

from ..learned_evidence import load_case
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load
from ..native_calibration_worker import validate_job, audit_run_manifest


def resign(job):
    job["sha256"] = sha({k: v for k, v in job.items() if k != "sha256"})
    return job


def fixed_job(job):
    job = copy.deepcopy(job)
    job["schema_version"] = 2
    job["post_tune"].update(schema_version=2, finalization="keep_fixed_threshold")
    job["thresholds"] = []
    job["maximum_candidates"] = 0
    return resign(job)


class NativeFixedPostTunePreflightTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = os.environ.get("TIMELEARNER_FIXED_POSTTUNE_SOURCE")
        if not folder:
            raise unittest.SkipTest("requires real portable source/model primaries")
        cls.root = Path(folder)

    def examples(self):
        for name in ("Classic-auto_metric", "Branch-synthetic"):
            folder = self.root/name
            manifest = load(folder/"run-manifest.json")
            yield load(folder/"input/job.json"), load_case(folder/manifest["source_package_path"])

    def test_explicit_v2_calibrate_preserves_conditions_and_fixed_changes_identity(self):
        for original, source in self.examples():
            before = validate_job(original, source, post_tune=True)
            calibrated = copy.deepcopy(original)
            calibrated["schema_version"] = 2
            calibrated["post_tune"].update(schema_version=2, finalization="calibrate")
            calibrated = resign(calibrated)
            v2 = validate_job(calibrated, source, post_tune=True)
            self.assertEqual(before["specification_sha256"], v2["specification_sha256"])
            fixed = fixed_job(original)
            proof = validate_job(fixed, source, post_tune=True)
            self.assertNotEqual(proof["conditions_digest"], before["conditions_digest"])
            self.assertNotEqual(proof["specification_sha256"], before["specification_sha256"])

    def test_unused_grid_downgrade_unknown_finalization_and_invalid_controls_rejected(self):
        for original, source in self.examples():
            for edit in ("threshold", "budget", "outer_downgrade", "inner_downgrade", "finalization", "boolean"):
                with self.subTest(owner=original["owner_class"], edit=edit):
                    job = fixed_job(original)
                    if edit == "threshold": job["thresholds"] = [1.]
                    if edit == "budget": job["maximum_candidates"] = 1
                    if edit == "outer_downgrade": job["schema_version"] = 1
                    if edit == "inner_downgrade": job["post_tune"]["schema_version"] = 1
                    if edit == "finalization": job["post_tune"]["finalization"] = "automatic"
                    if edit == "boolean": job["maximum_candidates"] = False
                    with self.assertRaises(EvidenceError):
                        validate_job(resign(job), source, post_tune=True)

    def test_fixed_probes_require_real_target_foil_design_and_complete_sample_budget(self):
        for original, source in self.examples():
            for edit in ("duplicate", "missing_foil", "short_samples", "invalid_window"):
                job = fixed_job(original)
                if edit == "duplicate": job["trials"][1]["trial_id"] = job["trials"][0]["trial_id"]
                if edit == "missing_foil": job["trials"][1]["label"] = "target"
                if edit == "short_samples": job["trials"][0]["maximum_samples"] = 2
                if edit == "invalid_window": job["specification"]["criterion"]["end_offset"] = -1
                with self.subTest(owner=original["owner_class"], edit=edit), self.assertRaises(EvidenceError):
                    validate_job(resign(job), source, post_tune=True)


class NativeFixedPostTuneOwnedRunsTest(unittest.TestCase):
    def test_actual_fixed_and_v2_calibration_run_closures(self):
        directory = os.environ.get("TIMELEARNER_FIXED_POSTTUNE_RUNS")
        if not directory:
            self.skipTest("requires actual owned Console schema-2 runs")
        root = Path(directory)
        controls = load(root/"controls.json")["records"]
        self.assertEqual(len(controls), 6)
        counts = {}
        for row in controls:
            folder = root/row["name"]
            proof = audit_run_manifest(folder/"run-manifest.json", post_tune=True)
            self.assertTrue(proof["run_evidence_consistent"])
            job = load(folder/"input/job.json")
            report = load(folder/"native/transaction.json")
            model = load(folder/"native/model.json")
            self.assertEqual(report["status"], row["expected_status"])
            self.assertEqual(load(folder/"process/result.json")["returncode"], 0)
            counts[row["phase"]] = counts.get(row["phase"], 0)+1
            if row["phase"] == "fixed":
                self.assertEqual(report["status"], "weights_selected")
                self.assertEqual(model, report["selected_package"])
                self.assertEqual(model["neuron"]["metadata"]["calibration"],
                                 job["source_recognition"]["neuron"]["metadata"]["calibration"])
                self.assertEqual(report["calibration"], {})
                self.assertFalse(proof["full_grid_model_binding_verified"])
            self.assertIsNone(proof["evaluation_verdict"])
        self.assertEqual(counts, {"fixed": 2, "v2_calibrate": 2, "legacy": 2})
