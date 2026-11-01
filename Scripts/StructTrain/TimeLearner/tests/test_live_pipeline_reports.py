"""All production Train probes and every completed pattern/soma response."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..__main__ import main as cli
from ..live_pipeline_reports import read_pipeline_report, render_pipeline_run
from ..native_evidence import EvidenceError, load
from ..recognition_metrics import load_evaluation
from .live_pipeline_corpus import signed
from .test_owned_posttune_worker_reports import observations


class LivePipelineReportsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not all(os.environ.get(k) for k in ("TIMELEARNER_LIVE_PIPELINE_CORPUS", "TIMELEARNER_LIVE_PIPELINE_REPORTS")):
            raise unittest.SkipTest("requires actual production corpus and rendered reports")
        cls.source = Path(os.environ["TIMELEARNER_LIVE_PIPELINE_CORPUS"])
        cls.reports = Path(os.environ["TIMELEARNER_LIVE_PIPELINE_REPORTS"])
        cls.rows = load(cls.source/"index.json")["records"]
        if len(cls.rows) != 14:
            raise RuntimeError("requires every actual production operation")

    def test_full_source_binding_and_every_training_sample_preserved(self):
        for row in self.rows:
            name = row["name"];source = self.source/"runs"/name/"run-manifest.json";folder = self.reports/name
            original, _, _, _, _, _, packets = read_pipeline_report(source)
            m = load(folder/"manifest.json")
            with self.subTest(run=name):
                self.assertEqual(m["source_manifest_sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
                self.assertEqual(m["source_artifacts"], original["artifacts"])
                self.assertEqual(load(folder/"primary/run-manifest.json.gz"), original)
                for path, digest in load(folder/"SHA256SUMS.json").items():
                    self.assertEqual(hashlib.sha256((folder/path).read_bytes()).hexdigest(), digest)
                self.assertEqual(m["training_packet_order"], [p.name for p in packets])
                if not packets:
                    self.assertFalse((folder/"training").exists());continue
                entries = load(folder/"training/manifest.json")["reports"]
                self.assertEqual(len(entries), len(packets));previous = float("-inf")
                for entry, packet in zip(entries, packets):
                    probe = folder/"training"/entry["folder"];r = load(packet);o = r["observation"]
                    self.assertEqual(load(probe/"primary/probe.json"), r)
                    self.assertEqual((probe/"primary/trace.csv").read_bytes(), packet.with_suffix(".csv").read_bytes())
                    meta = load(probe/"manifest.json")
                    with packet.with_suffix(".csv").open(encoding="utf-8") as stream:
                        self.assertEqual(meta["trace_quality"]["sample_count"], sum(1 for _ in stream)-1)
                    self.assertEqual(len(meta["figures"]), len(o["specification"]["baseline"]))
                    self.assertGreater(o["specification"]["begin"], previous);previous = o["specification"]["begin"]
                if not load(self.source/"runs"/name/"native/execution.json")["completed_boundary"]:
                    self.assertFalse(load(folder/"training/manifest.json")["data_complete"])
                    self.assertFalse((folder/"posttune").exists())

    def test_all_patterns_somas_and_readable_zoom_without_downsampling(self):
        from PIL import Image
        for row in self.rows:
            name = row["name"];root = self.source/"runs"/name;folder = self.reports/name
            expected = []
            if row["operation"] == "evaluate":
                expected = load_evaluation(root/"native/evaluation.json")[1]
            elif (root/"native/finalization.json").exists():
                r = load(root/"native/finalization.json")
                if r["post_tune"]:expected = observations(r["post_tune"])
            by_id = {(o["run_id"], o["trial_id"]): o for o in expected};self.assertEqual(len(by_id), len(expected));seen = set()
            for spec in folder.rglob("evaluation.json"):
                if spec.parent.name != "primary":continue
                directory = spec.parent.parent;m = load(directory/"manifest.json");actual = load_evaluation(spec)[1]
                for o in actual:
                    key = (o["run_id"], o["trial_id"]);self.assertEqual(o, by_id[key]);seen.add(key)
                self.assertEqual({(f["trial_id"], f["descriptor"]["index"]) for f in m["figures"]},
                                 {(o["trial_id"], i) for o in actual for i in range(len(o["samples"][0]["soma"]))})
            self.assertEqual(seen, set(by_id))
            for metadata in folder.rglob("manifest.json"):
                for figure in load(metadata).get("figures", []):
                    self.assertTrue(any(v["time_view"] != "overview" for v in figure["views"]))
                    for view in figure["views"]:
                        self.assertFalse(view["downsampling"])
                        if view["time_view"] != "overview":self.assertGreaterEqual(view["minimum_native_tick_pixels_on_zoom"], 8)
                        png, svg, pdf = (metadata.parent/path for path in view["files"])
                        with Image.open(png) as image:self.assertEqual(image.size, (1920, 960))
                        self.assertIn("Actual shared input", svg.read_text());self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))

    def test_unknown_manifest_and_cli_overlays_rejected_before_output(self):
        source = self.source/"runs"/self.rows[0]["name"]/"run-manifest.json"
        with tempfile.TemporaryDirectory(dir=self.reports.parent) as temporary:
            root = Path(temporary);changed = load(source);changed["unrecognized"] = True
            bad = root/"bad.json";bad.write_text(json.dumps(signed(changed)))
            output = root/"bad-report"
            with self.assertRaises(EvidenceError):render_pipeline_run(bad, output)
            self.assertFalse(output.exists())
            for i, option in enumerate(("--model", "--trace", "--source-solo", "--artifacts", "--primary-inventory")):
                output = root/("forbidden-"+str(i))
                with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                    code = cli(["report", str(source), "--format", "pipeline-run", option, str(source), "--output", str(output)])
                self.assertEqual(code, 2);self.assertFalse(output.exists())
