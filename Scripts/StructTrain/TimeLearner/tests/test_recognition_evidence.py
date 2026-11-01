"""Corrupt actual converted graphs and declared frozen observation windows."""
import copy
import contextlib
import csv
import os
import io
import json
import struct
import tempfile
import unittest
from pathlib import Path

from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256
from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError
from Scripts.StructTrain.TimeLearner.recognition_evidence import audit_recognition_state, load_case


class RecognitionEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_RECOGNITION_EVIDENCE_DIR")
        if not directory:
            raise unittest.SkipTest("requires genuine recognition packages and declared probes")
        cls.cases = [load_case(path) for path in sorted(Path(directory).glob("*_recognition_state.json"))]
        cls.paths = sorted(Path(directory).glob("*_recognition_state.json"))
        if len(cls.cases) != 8:
            raise RuntimeError("requires eight native recognition conversion scenarios")

    def test_actual_conversion_and_complete_frozen_data(self):
        for case in self.cases:
            with self.subTest(model=case[0]["model_revision"]):
                result = audit_recognition_state(*case)
                self.assertTrue(result["conversion_math_verified"])
                self.assertTrue(result["frozen_transport"]["complete"])
                self.assertFalse(result["native_import_verified"])
                self.assertFalse(result["frozen_transport"]["spikes_known"])
                self.assertIsNone(result["evaluation_verdict"])

    def test_actual_cli(self):
        from Scripts.StructTrain.TimeLearner.__main__ import main
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            code = main(["analyze", str(self.paths[0]), "--format", "recognition"])
        self.assertEqual(code, 0, error.getvalue())
        self.assertTrue(json.loads(output.getvalue())["analysis"]["conversion_math_verified"])

    def reject(self, edit, *, resign_graph=False):
        case = copy.deepcopy(self.cases[0])
        edit(*case)
        package = case[0]
        if resign_graph:
            identity = package["neuron"]["graph"]["identity"]
            identity["sha256"] = canonical_model_sha256(identity["model"])
            package["model_revision"] = identity["sha256"]
            package["conversion_record"]["result_identity"] = identity["sha256"]
        for value in (package["neuron"], package):
            value["sha256"] = canonical_model_sha256({k: v for k, v in value.items() if k != "sha256"})
        with self.assertRaises(EvidenceError):
            audit_recognition_state(*case)

    def test_solo_certificate_is_not_a_recognition_certificate(self):
        self.reject(lambda p, *_: p.__setitem__("recognition_certificate", p["source_solo"]["certificate"]))

    def test_changed_factor(self):
        self.reject(lambda p, *_: p["conversion_record"]["decisions"][0].__setitem__("factor", 99.))

    def test_changed_child_capacity_with_updated_identity(self):
        def edit(p, *_):
            node = next(n for n in p["neuron"]["graph"]["identity"]["model"]["nodes"] if "Capacity" in n["parameters"])
            data = node["parameters"]["Capacity"]["data"]
            data["value"] = struct.pack(">d", 2 * struct.unpack(">d", bytes.fromhex(data["value"]))[0]).hex()
        self.reject(edit, resign_graph=True)

    def test_changed_inherited_threshold(self):
        self.reject(lambda p, *_: p["neuron"]["metadata"]["calibration"].__setitem__("threshold", 99.))

    def test_changed_storage_definition(self):
        self.reject(lambda p, *_: p["neuron"]["class_definitions"].clear())

    def test_incomplete_observation(self):
        self.reject(lambda p, source, spec, obs, trace: obs.__setitem__("complete", False))

    def test_frozen_model_change(self):
        self.reject(lambda p, source, spec, obs, trace: obs.__setitem__("frozen_after_b", "changed"))

    def test_unknown_probe_schema(self):
        self.reject(lambda p, source, spec, obs, trace: spec.__setitem__("schema_version", 999))

    def corrupt_trace(self, edit):
        package, source, spec, observation, path = copy.deepcopy(self.cases[0])
        with path.open(newline="") as stream:
            rows = list(csv.reader(stream))
        edit(rows, observation)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "frozen.csv"
            with path.open("w", newline="") as stream:
                csv.writer(stream).writerows(rows)
            with self.assertRaises(EvidenceError):
                audit_recognition_state(package, source, spec, observation, path)

    def test_missing_middle_frame_with_corrected_count(self):
        def edit(rows, obs):
            rows.pop(len(rows) // 2)
            obs["sample_count"] -= 1
        self.corrupt_trace(edit)

    def test_truncated_window_with_corrected_count(self):
        def edit(rows, obs):
            del rows[-10:]
            obs["sample_count"] = len(rows) - 1
            obs["last_sample_time"] = float(rows[-1][0])
        self.corrupt_trace(edit)

    def test_pair_mismatch(self):
        self.corrupt_trace(lambda rows, obs: rows[20].__setitem__(4, str(float(rows[20][4]) + .001)))

    def test_constant_nonzero_rest_is_not_a_response(self):
        def edit(rows, obs):
            for row in rows[1:]:
                row[3:] = ["2"] * (len(row) - 3)
            obs["maximum_soma"] = 2.
            obs["soma_variation"] = 0.
        self.corrupt_trace(edit)
