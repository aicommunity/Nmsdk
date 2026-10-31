"""Inspect reports produced from all real Classic/Branch native PostTune primaries."""
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


class PostTuneTransactionReportsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("TIMELEARNER_POSTTUNE_REPORT_DIR")
        if not value:
            raise unittest.SkipTest("requires full actual native PostTune visual cache")
        cls.cases = sorted(p.parent for p in Path(value).glob("*/manifest.json")
                           if load(p).get("kind") == "timelearner_posttune_transaction_visual_report")
        if len(cls.cases) != 24:
            raise RuntimeError("requires all 24 actual Classic/Branch transaction reports")

    def test_all_weight_candidates_and_real_calibration_are_preserved(self):
        for path in self.cases:
            outer = load(path/"manifest.json")
            raw = load(path/"primary/transaction.json.gz")
            self.assertEqual(outer["source_transaction_sha256"], raw["sha256"])
            self.assertFalse(outer["visual_acceptance_complete"])
            self.assertFalse(outer["native_execution_verified"])
            self.assertIsNone(outer["evaluation_verdict"])
            self.assertEqual(len(outer["weight_matrices"]), len(raw["candidates"]))
            for item, candidate in zip(outer["weight_matrices"], raw["candidates"]):
                folder = path/item["name"]
                spec, observations = load_evaluation(folder/"primary/evaluation.json")
                self.assertEqual(load(folder/"primary/model.json"), candidate["candidate"])
                by_id = {o["trial_id"]: o for o in candidate["matrix"]["observations"]}
                self.assertEqual(observations, [by_id[q["trial_id"]] for q in spec["trials"]])
                self.assertEqual(item["measured_gap"], candidate["measured_gap"])
            if raw["calibration"] is None:
                self.assertIsNone(outer["calibration"])
            else:
                self.assertEqual(load(path/"calibration/primary/transaction.json.gz"), raw["calibration"])
                child = load(path/"calibration/manifest.json")
                self.assertEqual(child["completed_matrices"], len(raw["calibration"]["candidates"])+
                                 int(raw["calibration"]["status"] in {"calibrated", "confirmation_failed"}))
            self.assertIn("do not establish independent Test", (path/"index.html").read_text())

    def test_every_pattern_soma_and_detail_view_is_readable_with_native_inputs(self):
        from PIL import Image
        for path in self.cases:
            outer = load(path/"manifest.json")
            folders = [path/item["name"] for item in outer["weight_matrices"]]
            if outer["calibration"] is not None:
                folders += [path/"calibration"/item["name"] for item in load(path/"calibration/manifest.json")["matrices"]]
            pairs = 0
            for folder in folders:
                spec, observations = load_evaluation(folder/"primary/evaluation.json")
                manifest = load(folder/"manifest.json")
                count = len(observations[0]["samples"][0]["soma"])
                self.assertEqual({(f["trial_id"], f["descriptor"]["index"]) for f in manifest["figures"]},
                                 {(q["trial_id"], i) for q in spec["trials"] for i in range(count)})
                pairs += len(manifest["figures"])
                for figure in manifest["figures"]:
                    self.assertTrue(any(v["time_view"] != "overview" for v in figure["views"]))
                    for view in figure["views"]:
                        self.assertFalse(view["downsampling"])
                        if view["time_view"] != "overview":
                            self.assertGreaterEqual(view["minimum_native_tick_pixels_on_zoom"], 8)
                        png, svg, pdf = (folder/name for name in view["files"])
                        with Image.open(png) as im:
                            self.assertEqual(im.size, (1920, 960))
                        self.assertIn("Actual shared input", svg.read_text())
                        self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))
            self.assertEqual(pairs, outer["trial_soma_pairs"])

    def test_cache_checksums_and_partial_probe_scope(self):
        for path in self.cases:
            sums = load(path/"SHA256SUMS.json")
            self.assertEqual(set(sums)|{"SHA256SUMS.json"},
                             {p.relative_to(path).as_posix() for p in path.rglob("*") if p.is_file()})
            for name, digest in sums.items():
                self.assertEqual(hashlib.sha256((path/name).read_bytes()).hexdigest(), digest)
            self.assertFalse(load(path/"manifest.json")["incomplete_matrix_plotted_as_complete"])

    def test_cli_rejects_corrupted_source_before_creating_output(self):
        from ..__main__ import main
        primaries = Path(os.environ["TIMELEARNER_POSTTUNE_TRANSACTION_DIR"])
        sources = {load(p)["sha256"]: p for p in primaries.glob("*_learned_state.json")}
        path = self.cases[0]
        value = copy.deepcopy(load(path/"primary/transaction.json.gz"))
        value["schema_version"] = 999
        value["sha256"] = sha({k: v for k, v in value.items() if k != "sha256"})
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root/"bad.json", root/"report"
            source.write_text(json.dumps(value))
            with contextlib.redirect_stderr(io.StringIO()):
                status = main(["report", str(source), "--format", "posttune-transaction",
                               "--source-solo", str(sources[value["source_recognition"]["source_solo"]["sha256"]]),
                               "--output", str(output)])
            self.assertEqual(status, 2)
            self.assertFalse(output.exists())
