"""Portable production bindings and full native-sample plot coverage."""
import contextlib
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import load
from ..recognition_metrics import load_evaluation


class PostTuneRunReportsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("TIMELEARNER_POSTTUNE_RUN_REPORT_DIR")
        source = os.environ.get("TIMELEARNER_POSTTUNE_CONTROLLER_WORKER_DIR")
        if not value or not source:
            raise unittest.SkipTest("requires all 18 real production run reports and portable primaries")
        cls.root, cls.source = Path(value), Path(source)
        cls.controls = load(cls.source/"controls.json")["records"]
        if len(cls.controls) != 18:
            raise RuntimeError("requires 18 actual production controls")

    def test_all_reports_bind_actual_production_run_and_full_transactions(self):
        for control in self.controls:
            path = self.root/control["name"]
            run = load(self.source/control["name"]/"run-manifest.json")
            manifest, binding = load(path/"manifest.json"), load(path/"run-binding.json")
            self.assertEqual(binding["run_manifest_sha256"], run["sha256"])
            self.assertEqual(manifest["runtime_fingerprint"], run["runtime_fingerprint"])
            self.assertEqual(binding["source_closure"], run["source_closure"])
            self.assertTrue(binding["run_audit"]["run_evidence_consistent"])
            self.assertFalse(binding["native_execution_verified"])
            self.assertFalse(binding["visual_acceptance_complete"])
            self.assertIsNone(binding["evaluation_verdict"])
            self.assertEqual(load(path/"primary/transaction.json.gz"),
                             load(self.source/control["name"]/"native/transaction.json"))

    def test_all_patterns_somas_and_native_samples_survive_rendering(self):
        from PIL import Image
        for control in self.controls:
            path = self.root/control["name"]
            parent = load(path/"manifest.json")
            raw = load(path/"primary/transaction.json.gz")
            jobs = [(path/item["name"], row["matrix"]) for item, row in zip(parent["weight_matrices"], raw["candidates"])]
            self.assertEqual(len(jobs), len(raw["candidates"]))
            if raw["calibration"]:
                child = load(path/"calibration/manifest.json")
                for item in child["matrices"]:
                    matrix = (raw["calibration"]["confirmation"] if item["name"] == "fresh-confirmation" else
                              raw["calibration"]["candidates"][int(item["name"].split("-")[1])]["matrix"])
                    jobs.append((path/"calibration"/item["name"], matrix))
            pairs = 0
            for folder, matrix in jobs:
                spec, observations = load_evaluation(folder/"primary/evaluation.json")
                source = {o["trial_id"]: o for o in matrix["observations"]}
                self.assertEqual(observations, [source[q["trial_id"]] for q in spec["trials"]])
                count = len(observations[0]["samples"][0]["soma"])
                figures = load(folder/"manifest.json")["figures"]
                self.assertEqual({(f["trial_id"], f["descriptor"]["index"]) for f in figures},
                                 {(q["trial_id"], i) for q in spec["trials"] for i in range(count)})
                pairs += len(figures)
                for figure in figures:
                    self.assertTrue(any(v["time_view"] != "overview" for v in figure["views"]))
                    for view in figure["views"]:
                        self.assertFalse(view["downsampling"])
                        if view["time_view"] != "overview":
                            self.assertGreaterEqual(view["minimum_native_tick_pixels_on_zoom"], 8)
                        png, svg, pdf = (folder/name for name in view["files"])
                        with Image.open(png) as image:
                            self.assertEqual(image.size, (1920, 960))
                        self.assertIn("Actual shared input", svg.read_text())
                        self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))
            self.assertEqual(pairs, parent["trial_soma_pairs"])

    def test_complete_cache_hashes_and_invalid_binding_before_output(self):
        for control in self.controls:
            folder = self.root/control["name"]
            sums = load(folder/"SHA256SUMS.json")
            self.assertEqual(set(sums)|{"SHA256SUMS.json"},
                             {p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file()})
            for name, digest in sums.items():
                self.assertEqual(hashlib.sha256((folder/name).read_bytes()).hexdigest(), digest)
        from ..__main__ import main
        run = copy.deepcopy(load(self.source/self.controls[0]["name"]/"run-manifest.json"))
        run["kind"] = "unknown_run_kind"
        run["sha256"] = sha({k: v for k, v in run.items() if k != "sha256"})
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root/"run.json", root/"report"
            source.write_text(json.dumps(run))
            with contextlib.redirect_stderr(io.StringIO()):
                status = main(["report", str(source), "--format", "posttune-run", "--output", str(output)])
            self.assertEqual(status, 2)
            self.assertFalse(output.exists())
