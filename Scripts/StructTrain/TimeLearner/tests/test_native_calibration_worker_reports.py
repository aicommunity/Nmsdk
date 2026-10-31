"""All-pattern reports from actual production Console/owned CLI jobs."""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..calibration_transaction_reports import render_calibration_run
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load
from ..recognition_metrics import load_evaluation, score_threshold_candidate


class NativeCalibrationWorkerReportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_NATIVE_CALIBRATION_WORKER_REPORT_DIR")
        runs = os.environ.get("TIMELEARNER_NATIVE_CALIBRATION_RUN_DIR")
        if not directory or not runs:
            raise unittest.SkipTest("requires complete production Console/CLI report cache and primary runs")
        cls.root, cls.runs = Path(directory), Path(runs)
        cls.paths = sorted(p for p in cls.root.iterdir() if p.is_dir() and (p/"manifest.json").exists())
        counts = {}
        for path in cls.paths:
            status = load(path/"manifest.json")["transaction_status"]
            counts[status] = counts.get(status, 0)+1
        if counts != {"calibrated": 6, "nonseparable": 2, "budget_exhausted": 2}:
            raise RuntimeError("requires all six direct Console and four recorded CLI run reports")

    def test_every_complete_matrix_reproduces_primary_scoring_and_all_somas(self):
        matrices = pairs = 0
        for path in self.paths:
            outer = load(path/"manifest.json")
            self.assertFalse(outer["visual_acceptance_complete"])
            self.assertIsNone(outer["evaluation_verdict"])
            if path.name.startswith("cli-a2-"):
                binding = load(path/"run-binding.json")
                self.assertTrue(binding["source_primary_checked"])
                self.assertTrue(binding["run_audit"]["full_grid_model_binding_verified"])
            for item in outer["matrices"]:
                folder = path/item["name"];manifest = load(folder/"manifest.json")
                spec, observations = load_evaluation(folder/"primary/evaluation.json")
                model = load(folder/"primary/model.json")
                self.assertEqual(score_threshold_candidate(spec, observations, model), load(folder/"analysis.json"))
                source = model["source_recognition"]
                channels = 1 if source["source_solo"]["configuration"]["model"]["branch"] else len(source["recognition_inputs"])
                self.assertEqual({(f["presentation_index"], f["descriptor"]["index"]) for f in manifest["figures"]},
                                 {(i, channel) for i in range(len(spec["trials"])) for channel in range(channels)})
                self.assertEqual({o["label"] for o in observations}, {"target", "foil"})
                matrices += 1;pairs += len(manifest["figures"])
        self.assertEqual((matrices, pairs), (22, 66))

    def test_all_native_input_overlays_are_readable_and_every_file_hash_matches(self):
        from PIL import Image
        for path in self.paths:
            sums = load(path/"SHA256SUMS.json")
            self.assertEqual(set(sums), {p.relative_to(path).as_posix() for p in path.rglob("*")
                if p.is_file() and p != path/"SHA256SUMS.json"})
            for name, digest in sums.items():
                self.assertEqual(hashlib.sha256((path/name).read_bytes()).hexdigest(), digest)
            for matrix in load(path/"manifest.json")["matrices"]:
                folder = path/matrix["name"]
                for figure in load(folder/"manifest.json")["figures"]:
                    self.assertTrue(any(v["time_view"] != "overview" for v in figure["views"]))
                    for view in figure["views"]:
                        self.assertFalse(view["downsampling"])
                        if view["time_view"] != "overview":
                            self.assertGreaterEqual(view["minimum_native_tick_pixels_on_zoom"], 8)
                        png, svg, _ = [folder/name for name in view["files"]]
                        self.assertEqual(Image.open(png).size, (1920, 960))
                        self.assertIn("Actual shared input (native samples)", svg.read_text(encoding="utf-8"))

    def test_rehashed_wrong_runtime_binding_cannot_generate_a_report(self):
        for top in ("Classic", "Branch"):
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory);run = root/"attempt";shutil.copytree(self.runs/top, run)
                path = run/"run-manifest.json";manifest = copy.deepcopy(load(path))
                manifest["runtime_fingerprint"] = "0"*64;manifest.pop("sha256");manifest["sha256"] = sha(manifest)
                path.write_text(json.dumps(manifest)+"\n", encoding="utf-8")
                with self.assertRaisesRegex(EvidenceError, "worker_run_runtime_scope_changed"):
                    render_calibration_run(path, root/"report")
                self.assertFalse((root/"report").exists())
