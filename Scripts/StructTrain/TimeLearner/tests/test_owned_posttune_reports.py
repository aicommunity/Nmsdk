"""Every completed native phase matrix retains all soma samples and actual inputs."""
import hashlib
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from ..recognition_metrics import load_evaluation


class OwnedPostTuneReportsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("TIMELEARNER_OWNED_POSTTUNE_REPORTS")
        native = os.environ.get("TIMELEARNER_OWNED_POSTTUNE_NATIVE")
        if not root or not native:
            raise unittest.SkipTest("requires actual owned phase records and rendered reports")
        cls.root, cls.native = Path(root), Path(native)
        cls.records = sorted(cls.native.glob("*_managed_finalization_*_owned_*.json"))
        if len(cls.records) != 10:
            raise RuntimeError("requires ten actual completed/interrupted phase reports")

    def test_sources_and_terminal_results_preserved(self):
        for path in self.records:
            with self.subTest(case=path.name):
                folder = self.root/path.stem
                record, manifest = load(path), load(folder/"manifest.json")
                self.assertEqual(load(folder/"primary/owned-record.json.gz"), record)
                self.assertEqual(manifest["source_record_sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
                self.assertTrue(manifest["owner_phase_implemented"])
                self.assertEqual(manifest["interrupted"], record["interrupted"])
                self.assertFalse(manifest["visual_acceptance_complete"])
                self.assertIsNone(manifest["scientific_verdict"])
                self.assertEqual(load(folder/"posttune/primary/transaction.json.gz"), record["transaction"])
                for name, digest in load(folder/"SHA256SUMS.json").items():
                    self.assertEqual(hashlib.sha256((folder/name).read_bytes()).hexdigest(), digest)
                if record["interrupted"]:
                    self.assertEqual(manifest["trial_soma_pairs"], 0)
                    self.assertFalse(list(folder.rglob("*.png")))

    def test_complete_patterns_channels_and_readable_time_scale(self):
        from PIL import Image
        for path in self.records:
            record = load(path)
            folder = self.root/path.stem/"posttune"
            parent = load(folder/"manifest.json")
            jobs = [(folder/item["name"], row["matrix"]) for item, row in zip(parent["weight_matrices"], record["transaction"]["candidates"])]
            if not record["interrupted"]:
                jobs.append((folder/"final-model", record["transaction"]["final_model_matrix"]))
            pairs = 0
            for directory, matrix in jobs:
                spec, observations = load_evaluation(directory/"primary/evaluation.json")
                source = {o["trial_id"]: o for o in matrix["observations"]}
                self.assertEqual(observations, [source[q["trial_id"]] for q in spec["trials"]])
                figures = load(directory/"manifest.json")["figures"]
                channels = len(observations[0]["samples"][0]["soma"])
                self.assertEqual({(f["trial_id"], f["descriptor"]["index"]) for f in figures},
                                 {(q["trial_id"], i) for q in spec["trials"] for i in range(channels)})
                pairs += len(figures)
                for figure in figures:
                    self.assertTrue(any(v["time_view"] != "overview" for v in figure["views"]))
                    for view in figure["views"]:
                        self.assertFalse(view["downsampling"])
                        if view["time_view"] != "overview":
                            self.assertGreaterEqual(view["minimum_native_tick_pixels_on_zoom"], 8)
                        with Image.open(directory/view["files"][0]) as image:
                            self.assertEqual(image.size, (1920, 960))
            self.assertEqual(pairs, parent["trial_soma_pairs"])
