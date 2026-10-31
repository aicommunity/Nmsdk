"""All 26 production transactions: native source, every complete pattern and soma."""
import hashlib
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from ..recognition_metrics import load_evaluation


def observations(report):
    result=[]
    for row in report["candidates"]:result.extend(row["matrix"]["observations"])
    if report["kind"]=="native_post_tune_transaction":
        if report.get("final_threshold_responses_observed") and report.get("finalization")=="keep_fixed_threshold":
            result.extend(report["final_model_matrix"]["observations"])
        if report["calibration"]:result.extend(observations(report["calibration"]))
    elif report["status"] in ("calibrated","confirmation_failed"):
        result.extend(report["confirmation"]["observations"])
    return result


class OwnedPostTuneWorkerReportsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=os.environ.get("TIMELEARNER_OWNED_WORKER_REPORTS")
        native=os.environ.get("TIMELEARNER_OWNED_WORKER_CORPUS")
        if not root or not native:
            raise unittest.SkipTest("requires complete actual owned Console corpus and 26 temporal reports")
        cls.root,cls.native=Path(root),Path(native)
        cls.index=load(cls.root/"render-index.json")
        if len(cls.index["reports"])!=26:
            raise RuntimeError("requires twenty PostTune and six standalone calibration reports")

    def test_all_native_transactions_and_primary_hashes_bound(self):
        kinds={}
        for item in self.index["reports"]:
            folder=self.root/item["output"];source=self.native/item["source"]
            kinds[item["kind"]]=kinds.get(item["kind"],0)+1
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),item["source_file_sha256"])
            transaction=source.parent/"transaction.json" if source.name=="run-manifest.json" else source
            if source.name=="run-manifest.json":transaction=source.parent/"native/transaction.json"
            self.assertEqual(load(folder/"primary/transaction.json.gz"),load(transaction))
            for name,digest in load(folder/"SHA256SUMS.json").items():
                self.assertEqual(hashlib.sha256((folder/name).read_bytes()).hexdigest(),digest)
        self.assertEqual(kinds,{"posttune_run":20,"calibration_transaction":6})

    def test_all_complete_native_samples_somas_inputs_and_readable_views(self):
        from PIL import Image
        for item in self.index["reports"]:
            source=self.native/item["source"]
            transaction=source.parent/"native/transaction.json" if source.name=="run-manifest.json" else source
            expected={(o["run_id"],o["trial_id"]):o for o in observations(load(transaction))}
            seen=set();folder=self.root/item["output"]
            for spec_path in folder.rglob("evaluation.json"):
                if spec_path.parent.name!="primary":continue
                directory=spec_path.parent.parent
                manifest=load(directory/"manifest.json")
                spec,actual=load_evaluation(spec_path)
                for row in actual:
                    key=(row["run_id"],row["trial_id"])
                    self.assertEqual(row,expected[key]);seen.add(key)
                figures=manifest["figures"]
                self.assertEqual({(f["trial_id"],f["descriptor"]["index"]) for f in figures},
                                 {(o["trial_id"],i) for o in actual for i in range(len(o["samples"][0]["soma"]))})
                for figure in figures:
                    self.assertTrue(any(v["time_view"]!="overview" for v in figure["views"]))
                    for view in figure["views"]:
                        self.assertFalse(view["downsampling"])
                        if view["time_view"]!="overview":self.assertGreaterEqual(view["minimum_native_tick_pixels_on_zoom"],8)
                        png,svg,pdf=(directory/name for name in view["files"])
                        with Image.open(png) as image:self.assertEqual(image.size,(1920,960))
                        self.assertIn("Actual shared input",svg.read_text())
                        self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))
            self.assertEqual(seen,set(expected))
