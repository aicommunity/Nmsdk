"""Native candidate packages and full primary observations; no synthetic pass fixture."""
import copy
import hashlib
import os
import json
from pathlib import Path
import subprocess
import sys
import unittest

from ..learned_evidence import load_case
from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError, load
from ..recognition_trial_evidence import audit_recognition_trial
from ..threshold_candidate_evidence import audit_threshold_candidate


def signed(package):
    package.pop("sha256", None)
    package["sha256"] = canonical_model_sha256(package)
    return package


class ThresholdCandidateEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("TIMELEARNER_THRESHOLD_CANDIDATE_DIR")
        if not value:
            raise unittest.SkipTest("requires actual native threshold candidate trials")
        root = Path(value)
        paths = sorted(root.glob("*_recognition_candidate.json"))
        if len(paths) != 16:
            raise RuntimeError("requires Classic/Branch x N0/N1 x 2/20 kHz x low/high")
        cls.cases = []
        for path in paths:
            prefix = path.name.removesuffix("_recognition_candidate.json")
            base = prefix.rsplit("_candidate_", 1)[0]
            candidate = load(path)
            if candidate["source_recognition"] != load(root/(base+"_threshold_source.json")):
                raise RuntimeError("candidate source differs from saved source")
            cls.cases.append((path, candidate, load_case(root/(base+"_learned_state.json")),
                [load(root/(prefix+f"_frozen_trial_{i}.json")) for i in range(4)],
                [load(root/(prefix+"_frozen_trial_"+name+".json")) for name in ("cancelled", "gap")]))

    def test_actual_derivations_and_primary_training_proof(self):
        for _, package, source, _, _ in self.cases:
            result = audit_threshold_candidate(package, source)
            self.assertTrue(result["threshold_derivation_verified"])
            self.assertTrue(result["source_training_and_conversion_checked"])
            self.assertFalse(result["calibrated"])
            self.assertFalse(result["native_import_verified"])
            self.assertIsNone(result["evaluation_verdict"])

    def test_complete_target_foil_observations_and_actual_spikes(self):
        for path, package, _, trials, _ in self.cases:
            for trial in trials:
                self.assertTrue(audit_recognition_trial(trial, package)["valid_observation"])
            spikes = sum(trial["spike_count"] for trial in trials)
            if "_candidate_high_" in path.name:
                self.assertEqual(spikes, 0)
            elif "_2000_" in path.name:
                self.assertGreater(spikes, 0)

    def test_cancellation_and_sample_gap_remain_invalid(self):
        for _, package, _, _, invalid in self.cases:
            self.assertEqual([trial["reason"] for trial in invalid], ["explicit_cancel", "recognition_sample_gap"])
            for trial in invalid:
                result = audit_recognition_trial(trial, package)
                self.assertFalse(result["valid_observation"])
                self.assertFalse(result["complete"])

    def test_resigned_false_calibration_and_record_are_rejected(self):
        for _, package, source, _, _ in self.cases:
            for key, value in (("calibrated", True), ("calibrated", 0), ("schema_version", True),
                               ("original_threshold", 99.)):
                changed = copy.deepcopy(package)
                changed["candidate_record"][key] = value
                with self.assertRaises(EvidenceError):
                    audit_threshold_candidate(signed(changed), source)

    def test_resigned_other_physics_is_rejected(self):
        for _, package, source, _, _ in self.cases:
            changed = copy.deepcopy(package)
            identity = changed["neuron"]["graph"]["identity"]
            node = next(node for node in identity["model"]["nodes"] if "Capacity" in node["parameters"])
            node["parameters"]["Capacity"]["data"]["value"] = "3ff0000000000000"
            identity["sha256"] = canonical_model_sha256(identity["model"])
            changed["model_revision"] = identity["sha256"]
            signed(changed["neuron"])
            with self.assertRaises(EvidenceError):
                audit_threshold_candidate(signed(changed), source)

    def test_resigned_native_xml_damage_is_rejected(self):
        for _, package, source, _, _ in self.cases:
            changed = copy.deepcopy(package)
            graph = changed["neuron"]["graph"]
            graph["native_xml"] = graph["native_xml"].replace("<Parameters>", "<Parameters><Unknown>1</Unknown>", 1)
            graph["native_xml_sha256"] = hashlib.sha256(graph["native_xml"].encode()).hexdigest()
            signed(changed["neuron"])
            with self.assertRaises(EvidenceError):
                audit_threshold_candidate(signed(changed), source)

    def test_boolean_schema_and_nested_source_are_rejected(self):
        for _, package, source, _, _ in self.cases:
            for field, value in (("schema_version", True), ("threshold", True), ("source_recognition", package)):
                changed = copy.deepcopy(package);changed[field] = value
                with self.assertRaises(EvidenceError):
                    audit_threshold_candidate(signed(changed), source)

    def test_cli_requires_primary_source_and_audits_real_candidate_trials(self):
        path, _, _, _, _ = self.cases[0]
        prefix = path.name.removesuffix("_recognition_candidate.json")
        base = prefix.rsplit("_candidate_", 1)[0]
        source = path.with_name(base+"_learned_state.json")
        command = [sys.executable, "-m", "Scripts.StructTrain.TimeLearner", "analyze", str(path),
                   "--format", "threshold-candidate"]
        missing = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(missing.returncode, 2)
        self.assertIn("threshold_candidate_source_evidence_required", missing.stderr)
        checked = subprocess.run(command+["--source-solo", str(source)], capture_output=True, text=True)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertTrue(json.loads(checked.stdout)["analysis"]["source_training_and_conversion_checked"])
        trial = path.with_name(prefix+"_frozen_trial_0.json")
        response = subprocess.run([sys.executable, "-m", "Scripts.StructTrain.TimeLearner", "analyze", str(trial),
                                   "--format", "recognition-trial", "--model", str(path)], capture_output=True, text=True)
        self.assertEqual(response.returncode, 0, response.stderr)
        self.assertTrue(json.loads(response.stdout)["analysis"]["valid_observation"])
        self.assertIsNone(json.loads(response.stdout)["evaluation_verdict"])
