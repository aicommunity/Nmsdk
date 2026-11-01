"""Audit actual 31-case N0 regression runs; never infer missing phase coverage."""
from copy import deepcopy
import os
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from ..native_evidence import EvidenceError, audit_probe, audit_training_summary, load
from ..model_identity import canonical_model_sha256


class N0CandidateRegressionEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_N0_CANDIDATE_RUN")
        if not directory:
            raise unittest.SkipTest("requires actual complete 31-case native N0 regression run")
        cls.root = Path(directory)
        cls.spec = load(Path(__file__).parents[1]/"specs/n0-candidate-order-native-v1.json")
        process = load(cls.root/"process/result.json")
        if (process["execution"] != "completed" or process["returncode"] != 0
                or process["runtime_provenance"] != "loaded_files_captured"):
            raise RuntimeError("requires completed native process with loaded-file provenance")
        xml = ET.parse(cls.root/"native.xml").getroot()
        cases = list(xml.iter("testcase"))
        ids = [c.get("classname", "")+"/"+c.get("name", "") for c in cases]
        if (len(ids) != 31 or len(set(ids)) != 31 or set(ids) != set(cls.spec["expected_test_ids"])
                or any(c.get("status") != "run" or c.get("result") != "completed"
                       or any(c.find(tag) is not None for tag in ("failure", "error", "skipped"))
                       for c in cases)):
            raise RuntimeError("native N0 regression declared test set did not fully pass")
        cls.native = cls.root/"native-evidence"
        cls.cases = []
        for phase in cls.spec["phases"]:
            summary = load(cls.native/phase["summary"])
            total = summary["reference_probes"]+summary["search_probes"]
            expected = {phase["probe_prefix"]+str(i)+".json" for i in range(1, total+1)}
            # The native fixture exports its effective model with the same
            # prefix. It is mandatory graph evidence, not an extra trial.
            model_name = phase["probe_prefix"]+"model.json"
            if not expected or {p.name for p in cls.native.glob(phase["probe_prefix"]+"*.json")} != expected | {model_name}:
                raise RuntimeError("missing or extra declared N0 training probe/model")
            model = load(cls.native/model_name)
            if (model["valid"] is not True
                    or model["sha256"] != canonical_model_sha256(model["model"])
                    or model["sha256"] != summary["actual_model_revision"]):
                raise RuntimeError("N0 effective graph does not match the training model")
            packets, paths = {}, []
            for name in sorted(expected):
                path = cls.native/name
                packet = load(path)
                audit_probe(packet, path.with_suffix(".csv"))
                trial = packet["observation"]["specification"]["trial_id"]
                if trial in packets:
                    raise RuntimeError("duplicate N0 phase trial ID")
                packets[trial] = packet
                paths.append(path)
            cls.cases.append((summary, packets, paths))
        actual = {p.name for p in cls.native.glob("*_training_summary.json")}
        if actual != {p["summary"] for p in cls.spec["phases"]}:
            raise RuntimeError("missing or extra N0 training phase")

    def test_all_four_actual_negative_certificates_match_primary_measurements(self):
        self.assertEqual(len(self.cases), 4)
        for summary, packets, _ in self.cases:
            with self.subTest(run=summary["actual_model_revision"]):
                self.assertEqual(summary["configuration"]["normalization"], "synapse_count")
                result = audit_training_summary(summary, packets, "pulse0")
                self.assertTrue(result["certificate_consistent"])
                self.assertFalse(result["exact"])
                self.assertIsNone(result["evaluation_verdict"])
                self.assertEqual(result["reference_count"], 2)

    def test_missing_final_trial_or_changed_final_residual_and_binding_reject(self):
        for summary, packets, _ in self.cases:
            trial = summary["certificate"]["residuals"][0]["trial_id"]
            missing = dict(packets)
            del missing[trial]
            with self.assertRaises(EvidenceError):
                audit_training_summary(summary, missing, "pulse0")
            for mutation in ("residual", "revision", "exact"):
                value = deepcopy(summary)
                if mutation == "residual":
                    value["certificate"]["residuals"][0]["amplitude_residual"] += .001
                elif mutation == "revision":
                    value["certificate"]["model_revision"] = "stale-model"
                else:
                    value["certificate"]["exact"] = True
                with self.subTest(mutation=mutation), self.assertRaises(EvidenceError):
                    audit_training_summary(value, packets, "pulse0")

    def test_captured_target_and_candidate_timing_cannot_be_rewritten(self):
        for summary, packets, _ in self.cases:
            self.assertTrue(summary["candidates"])
            for mutation in ("target", "candidate"):
                value = deepcopy(summary)
                if mutation == "target":
                    value["references"][0]["raw_potential"] += .001
                else:
                    value["candidates"][0]["timing_low"] += .001
                with self.subTest(mutation=mutation), self.assertRaises(EvidenceError):
                    audit_training_summary(value, packets, "pulse0")

    def test_trailing_csv_sample_loss_is_rejected(self):
        for _, _, paths in self.cases:
            path = paths[-1]
            lines = path.with_suffix(".csv").read_bytes().splitlines(keepends=True)
            self.assertGreater(len(lines), 3)
            with tempfile.TemporaryDirectory(prefix="tl-n0-truncated-") as directory:
                trace = Path(directory)/"truncated.csv"
                trace.write_bytes(b"".join(lines[:-1]))
                with self.assertRaises(EvidenceError):
                    audit_probe(load(path), trace)
