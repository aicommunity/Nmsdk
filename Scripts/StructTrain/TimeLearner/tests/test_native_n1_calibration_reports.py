"""Actual positive N1 grid matrices, source binding and readable native traces."""
import copy
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..calibration_transaction_reports import render_calibration_run
from ..native_evidence import EvidenceError, load
from ..recognition_metrics import load_evaluation, score_threshold_candidate
from .live_pipeline_corpus import signed
from .test_native_calibration_worker_reports import NativeCalibrationWorkerReportTest as _Shared


class NativeN1CalibrationReportsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        values = [os.environ.get(k) for k in ("TIMELEARNER_POSITIVE_N1_CALIBRATION", "TIMELEARNER_POSITIVE_N1_CALIBRATION_REPORTS")]
        if not all(values):
            raise unittest.SkipTest("requires actual positive N1 grid primary and all rendered matrices")
        cls.source, cls.root = map(Path, values)
        index = load(cls.source/"index.json")
        cls.rows = index["records"]
        if index["kind"] != "positive_n1_measured_calibration_controls" or len(cls.rows) != 2:
            raise RuntimeError("incomplete positive N1 calibration corpus")
        cls.paths = [cls.root/r["name"] for r in cls.rows]

    # Reuse the existing production report integrity/scale check unchanged.
    test_all_native_input_overlays_are_readable_and_every_file_hash_matches = (
        _Shared.test_all_native_input_overlays_are_readable_and_every_file_hash_matches)

    def test_every_real_matrix_is_bound_to_all_its_original_pattern_samples_and_scores(self):
        for row in self.rows:
            source = self.source/"runs"/row["name"]
            report = load(source/"native/transaction.json")
            output = self.root/row["name"]
            self.assertEqual(load(output/"primary/transaction.json.gz"), report)
            binding = load(output/"run-binding.json")
            self.assertEqual(binding["run_manifest_sha256"], load(source/"run-manifest.json")["sha256"])
            self.assertTrue(binding["source_primary_checked"])
            matrices = [("candidate-"+format(i, "04d"), r["matrix"], r["candidate"])
                        for i, r in enumerate(report["candidates"])]
            if report["status"] == "calibrated":
                matrices.append(("fresh-confirmation", report["confirmation"],
                                 report["candidates"][report["selected_index"]]["candidate"]))
            self.assertEqual([m["name"] for m in load(output/"manifest.json")["matrices"]], [m[0] for m in matrices])
            for name, matrix, candidate in matrices:
                folder = output/name
                spec, actual = load_evaluation(folder/"primary/evaluation.json")
                self.assertEqual({o["trial_id"]: o for o in actual},
                                 {o["trial_id"]: o for o in matrix["observations"]})
                self.assertEqual(load(folder/"primary/model.json"), candidate)
                self.assertEqual(load(folder/"analysis.json"), score_threshold_candidate(spec, actual, candidate))
                channels = 1 if candidate["source_recognition"]["source_solo"]["configuration"]["model"]["branch"] else 2
                self.assertEqual({(f["presentation_index"], f["descriptor"]["index"])
                                  for f in load(folder/"manifest.json")["figures"]},
                                 {(i, c) for i in range(len(actual)) for c in range(channels)})

    def test_rehashed_wrong_runtime_cannot_generate_a_positive_grid_report(self):
        for row in self.rows:
            with tempfile.TemporaryDirectory(dir=self.root.parent) as directory:
                root = Path(directory);source = root/"source"
                shutil.copytree(self.source/"runs"/row["name"], source)
                path = source/"run-manifest.json";manifest = copy.deepcopy(load(path))
                manifest["runtime_fingerprint"] = "0"*64
                path.write_text(json.dumps(signed(manifest))+"\n")
                with self.assertRaisesRegex(EvidenceError, "worker_run_runtime_scope_changed"):
                    render_calibration_run(path, root/"report")
                self.assertFalse((root/"report").exists())


del _Shared


if __name__ == "__main__":
    unittest.main()
