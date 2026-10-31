"""Compare every rendered native sample/channel with declared, immutable inputs."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..live_finalization_reports import read_live_report_source, render_live_finalization
from ..native_evidence import EvidenceError, load
from ..recognition_metrics import load_evaluation
from .test_owned_posttune_worker_reports import observations


class LiveFinalizationReportsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        keys = ("TIMELEARNER_LIVE_REPORTS", "TIMELEARNER_LIVE_FINALIZATION_NATIVE", "TIMELEARNER_LIVE_PRIMARY_INVENTORY")
        if not all(os.environ.get(key) for key in keys):
            raise unittest.SkipTest("requires all sixteen actual native cases and temporal reports")
        cls.root, cls.native, cls.inventory = (Path(os.environ[key]) for key in keys)
        cls.index = load(cls.root/"render-index.json")
        cls.records = cls.index["reports"]
        declared = load(Path(__file__).resolve().parents[1]/"Specifications/native-live-finalization-addressed.json")
        expected = {name for name, kind in declared["expected_controls"].items() if kind == "native_live_finalization_control"}
        if len(cls.records) != 16 or {row["source"] for row in cls.records} != expected:
            raise RuntimeError("requires every completed, stopped and preflight scenario")

    def test_primary_hashes_whole_records_and_every_train_probe_preserved(self):
        for row in self.records:
            with self.subTest(case=row["source"]):
                source = self.native/row["source"];folder = self.root/row["output"]
                record, case, packets, originals = read_live_report_source(source, self.inventory)
                manifest = load(folder/"manifest.json")
                self.assertEqual(manifest["source_control_sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
                self.assertEqual(manifest["source_inventory_sha256"], hashlib.sha256(self.inventory.read_bytes()).hexdigest())
                self.assertEqual(manifest["source_primary_files"], originals)
                self.assertEqual(load(folder/"primary/live-record.json.gz"), record)
                for name, checksum in load(folder/"SHA256SUMS.json").items():
                    self.assertEqual(hashlib.sha256((folder/name).read_bytes()).hexdigest(), checksum)
                if not packets:
                    self.assertIsNone(case);self.assertFalse((folder/"training").exists())
                    self.assertFalse(manifest["recognition_presented"])
                    continue
                training = load(folder/"training/manifest.json")
                self.assertEqual(len(training["reports"]), len(packets))
                for entry, packet in zip(training["reports"], packets):
                    probe = folder/"training"/entry["folder"]
                    self.assertEqual(load(probe/"primary/probe.json"), load(packet))
                    self.assertEqual((probe/"primary/trace.csv").read_bytes(), packet.with_suffix(".csv").read_bytes())
                    item = load(probe/"manifest.json")
                    with packet.with_suffix(".csv").open(encoding="utf-8") as stream:
                        self.assertEqual(item["trace_quality"]["sample_count"], sum(1 for _ in stream)-1)
                    self.assertEqual(len(item["figures"]), len(load(packet)["observation"]["specification"]["baseline"]))
                if record["scenario"] == 2:
                    self.assertFalse(training["data_complete"])
                    self.assertIsNone(manifest["frozen_replay_report"])
                    self.assertFalse((folder/"frozen").exists())

    def test_every_complete_pattern_soma_sample_and_readable_zoom(self):
        from PIL import Image
        for row in self.records:
            source = load(self.native/row["source"]);folder = self.root/row["output"]
            expected = {}
            if source["scenario"] in (0, 1):
                actual = observations(source["live"]["post_tune"])+source["frozen_replay"]["observations"]
                expected = {(o["run_id"], o["trial_id"]): o for o in actual}
                self.assertEqual(len(expected), len(actual))
            seen = set()
            for spec in folder.rglob("evaluation.json"):
                if spec.parent.name != "primary":
                    continue
                directory = spec.parent.parent;manifest = load(directory/"manifest.json")
                _, actual = load_evaluation(spec)
                for o in actual:
                    key = (o["run_id"], o["trial_id"])
                    self.assertEqual(o, expected[key]);seen.add(key)
                self.assertEqual({(f["trial_id"], f["descriptor"]["index"]) for f in manifest["figures"]},
                                 {(o["trial_id"], i) for o in actual for i in range(len(o["samples"][0]["soma"]))})
                for figure in manifest["figures"]:
                    self.assertTrue(any(v["time_view"] != "overview" for v in figure["views"]))
                    for view in figure["views"]:
                        self.assertFalse(view["downsampling"])
                        if view["time_view"] != "overview":
                            self.assertGreaterEqual(view["minimum_native_tick_pixels_on_zoom"], 8)
                        png, svg, pdf = (directory/name for name in view["files"])
                        with Image.open(png) as image:
                            self.assertEqual(image.size, (1920, 960))
                        self.assertIn("Actual shared input", svg.read_text())
                        self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))
            self.assertEqual(seen, set(expected))
            for probe in (folder/"training").glob("probe-*/manifest.json"):
                manifest = load(probe)
                for figure in manifest["figures"]:
                    for view in figure["views"]:
                        self.assertFalse(view["downsampling"])
                        if view["time_view"] != "overview":
                            self.assertGreaterEqual(view["minimum_native_tick_pixels_on_zoom"], 8)
                        png, svg, pdf = (probe.parent/name for name in view["files"])
                        with Image.open(png) as image:
                            self.assertEqual(image.size, (1920, 960))
                        self.assertIn("Actual shared input", svg.read_text())
                        self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))

    def test_changed_inventory_and_false_preflight_completion_reject_before_output(self):
        row = next(row for row in self.records if row["source"].endswith("_local_6.json"))
        source = self.native/row["source"]
        inventory = load(self.inventory)
        with tempfile.TemporaryDirectory(dir=self.root.parent) as temporary:
            root = Path(temporary);wrong = deepcopy(inventory)
            next(item for item in wrong["files"] if item["path"] == source.name)["sha256"] = "0"*64
            wrong_path = root/"wrong-inventory.json";wrong_path.write_text(json.dumps(wrong))
            output = root/"invalid-hash"
            with self.assertRaises(EvidenceError):
                render_live_finalization(source, wrong_path, output)
            self.assertFalse(output.exists())
            changed = load(source);changed["live"]["status"] = "completed"
            changed_path = root/source.name;changed_path.write_text(json.dumps(changed))
            wrong = deepcopy(inventory)
            item = next(item for item in wrong["files"] if item["path"] == source.name)
            item.update(bytes=changed_path.stat().st_size, sha256=hashlib.sha256(changed_path.read_bytes()).hexdigest())
            wrong_path.write_text(json.dumps(wrong));output = root/"false-completion"
            with self.assertRaises(EvidenceError):
                render_live_finalization(changed_path, wrong_path, output)
            self.assertFalse(output.exists())
