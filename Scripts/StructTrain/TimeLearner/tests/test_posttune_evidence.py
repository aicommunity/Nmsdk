"""Mutate actual reconstruction/rollback output and native parallel waveforms."""
import copy
import contextlib
import csv
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError
from Scripts.StructTrain.TimeLearner.posttune_evidence import audit_reconstruction, load_case


class PostTuneEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_POSTTUNE_EVIDENCE_DIR")
        if not directory:
            raise unittest.SkipTest("requires actual native PostTune reconstruction artifacts")
        cls.cases = [load_case(p) for p in sorted(Path(directory).glob("*_reconstruction.json"))]
        cls.paths = sorted(Path(directory).glob("*_reconstruction.json"))
        required = {(2000, mode, False, False) for mode in range(5)}
        required |= {(20000, 3, False, False), (2000, 3, True, False), (2000, 3, False, True)}
        observed = {(r["frequency"], r["mode"], r["injected_attach_failure"], r["external_listener"]) for r, _, _ in cls.cases}
        if not required.issubset(observed):
            raise RuntimeError("missing native mode/frequency/rollback/listener controls")
        n0 = [case for path, case in zip(cls.paths, cls.cases) if "_N0_" in path.name]
        if {case[0]["frequency"] for case in n0} != {2000, 20000}:
            raise RuntimeError("requires multi-synapse N0 reconstruction at both frequencies")
        for record, _, _ in n0:
            if "$.Dendrite1_2.ExcSynapse3" not in {node["path"] for node in record["before_model"]["model"]["nodes"]}:
                raise RuntimeError("N0 control did not actually create the third synapse")

    def test_actual_parallel_transport(self):
        for case in self.cases:
            with self.subTest(mode=case[0]["mode"], frequency=case[0]["frequency"]):
                result = audit_reconstruction(*case)
                self.assertTrue(result["graph_and_waveform_exact"])
                self.assertFalse(result["whole_posttune_selection_verified"])
                self.assertFalse(result["native_execution_verified"])
                self.assertFalse(result["spikes_known"])
                self.assertIsNone(result["evaluation_verdict"])

    def reject(self, edit):
        case = copy.deepcopy(self.cases[0])
        edit(*case)
        with self.assertRaises(EvidenceError):
            audit_reconstruction(*case)

    def test_unknown_schema_and_scientific_claim(self):
        self.reject(lambda r, *_: r.__setitem__("schema_version", True))
        self.reject(lambda r, *_: r.__setitem__("evaluation_verdict", "PASS"))

    def test_actual_cli(self):
        from Scripts.StructTrain.TimeLearner.__main__ import main
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            status = main(["analyze", str(self.paths[0]), "--format", "posttune-reconstruction"])
        self.assertEqual(status, 0, error.getvalue())
        self.assertTrue(json.loads(output.getvalue())["analysis"]["graph_and_waveform_exact"])
        self.assertIsNone(json.loads(output.getvalue())["evaluation_verdict"])

    def test_changed_graph_or_false_rollback(self):
        self.reject(lambda r, *_: r["after_model"].__setitem__("sha256", "changed"))
        self.reject(lambda r, *_: r.__setitem__("reconstructed", not r["reconstructed"]))

    def test_incomplete_or_changed_frozen_model(self):
        self.reject(lambda r, before, after: after[1].__setitem__("complete", False))
        self.reject(lambda r, before, after: after[1].__setitem__("frozen_after", "changed"))

    def test_duplicate_trial_or_wrong_stimulus(self):
        def duplicate(r, before, after):
            after[0]["trial_id"] = before[0]["trial_id"]
            after[1]["trial_id"] = before[0]["trial_id"]
        self.reject(duplicate)
        self.reject(lambda r, before, after: after[0].__setitem__("dataset_delay", after[0]["dataset_delay"] + .01))

    def test_missing_frame_or_damaged_number(self):
        for corrupt in ("missing", "nan", "damaged-number"):
            record, before, after = copy.deepcopy(self.cases[0])
            with after[2].open(newline="") as stream:
                rows = list(csv.reader(stream))
            if corrupt == "missing":
                rows.pop(len(rows) // 2)
                after[1]["sample_count"] -= 1
            else:
                rows[20][2] = corrupt
            with tempfile.TemporaryDirectory() as directory:
                trace = Path(directory) / "after.csv"
                with trace.open("w", newline="") as stream:
                    csv.writer(stream).writerows(rows)
                with self.assertRaises(EvidenceError):
                    audit_reconstruction(record, before, (after[0], after[1], trace))
