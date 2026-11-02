"""Real native diagnostic conversions, with deliberate corruption controls."""
import copy
import os
import unittest
from pathlib import Path

from ..diagnostic_recognition_evidence import audit_diagnostic_recognition, audit_diagnostic_recognition_trial
from ..learned_evidence import load_case as load_completed
from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError, load
from ..recognition_evidence import audit_recognition_source
from ..recognition_trial_evidence import audit_recognition_trial


def signed(value):
    value.pop("sha256", None)
    value["sha256"] = canonical_model_sha256(value)
    return value


class DiagnosticRecognitionEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("TIMELEARNER_DIAGNOSTIC_RECOGNITION_DIR")
        if not value:
            raise unittest.SkipTest("requires actual native diagnostic18 output")
        cls.native = Path(value)/"native"

    def cases(self):
        for topology in ("Classic", "Branch"):
            for n in (0, 1):
                for mode in ("partial", "budget"):
                    prefix = f"{topology}_2000_N{n}_diagnostic_{mode}"
                    source = load(self.native/(prefix+"_stopped_package.json"))
                    summary = load(self.native/(prefix+"_training_outcome.json"))
                    packets, traces = {}, {}
                    for i in range(1, len(source["observed_packets"])+1):
                        file = self.native/(prefix+f"_training_proof_{i}.json")
                        packet = load(file); trial = packet["requested_specification"]["trial_id"]
                        self.assertNotIn(trial, packets)
                        packets[trial], traces[trial] = packet, file.with_suffix(".csv")
                    model = load(self.native/(prefix+"_diagnostic_recognition.json"))
                    yield prefix, model, (source, summary, packets, traces)

    def test_eight_actual_conversions_preserve_unfinished_training_and_physics(self):
        count = 0
        for prefix, model, case in self.cases():
            result = audit_diagnostic_recognition(model, case); count += 1
            self.assertTrue(result["diagnostic_only"])
            self.assertTrue(result["conversion_math_verified"])
            self.assertTrue(result["other_physics_preserved"])
            self.assertFalse(result["certificate_present"])
            self.assertFalse(result["native_import_verified"])
            self.assertEqual(result["training_outcome"], "budget_exhausted")
            self.assertIsNone(result["evaluation_verdict"])
        self.assertEqual(count, 8)

    def test_full_and_censored_native_trials_remain_distinct(self):
        complete = censored = 0
        for prefix, model, case in self.cases():
            for name in [str(i) for i in range(4)]+["cancelled", "gap"]:
                observation = load(self.native/(prefix+"_frozen_trial_"+name+".json"))
                result = audit_diagnostic_recognition_trial(observation, model, case)
                if name in ("cancelled", "gap"):
                    self.assertFalse(result["valid_observation"]); self.assertFalse(result["complete"]); censored += 1
                else:
                    self.assertTrue(result["valid_observation"]); self.assertTrue(result["complete"]); complete += 1
                self.assertTrue(result["diagnostic_only"]); self.assertIsNone(result["evaluation_verdict"])
        self.assertEqual((complete, censored), (32, 16))

    def test_ordinary_readers_never_accept_diagnostic_packages(self):
        for prefix, model, case in self.cases():
            with self.assertRaises(EvidenceError): audit_recognition_source(model, case)
            observation = load(self.native/(prefix+"_frozen_trial_0.json"))
            with self.assertRaises(EvidenceError): audit_recognition_trial(observation, model)
            forged = copy.deepcopy(model); forged.update(kind="timelearner_recognition_state", state_kind="recognition")
            signed(forged)
            with self.assertRaises(EvidenceError): audit_recognition_source(forged, case)
            with self.assertRaises(EvidenceError): audit_diagnostic_recognition(forged, case)

    def test_changed_physics_cannot_be_hidden_by_resigning_the_archive(self):
        _, model, case = next(self.cases()); model = copy.deepcopy(model)
        identity = model["neuron"]["graph"]["identity"]
        identity["model"]["nodes"][0]["class"] = "UndeclaredReplacement"
        identity["sha256"] = model["model_revision"] = canonical_model_sha256(identity["model"])
        signed(model["neuron"]); signed(model)
        with self.assertRaises(EvidenceError): audit_diagnostic_recognition(model, case)

    def test_partial_capture_does_not_acquire_historical_scaling_references(self):
        _, model, case = next(row for row in self.cases() if row[0] == "Branch_2000_N1_diagnostic_partial")
        model = copy.deepcopy(model)
        model["conversion_spec"].update(mode="historical_branch_n1_v1", resistance_bounds=[{"minimum": 1e6, "maximum": 1e12}]*2)
        signed(model)
        with self.assertRaisesRegex(EvidenceError, "requires_complete_references"):
            audit_diagnostic_recognition(model, case)

    def test_false_certificate_and_lost_primary_trace_are_rejected(self):
        _, model, case = next(self.cases())
        source = copy.deepcopy(case[0]); source["certificate"] = {"exact": True}; signed(source)
        changed = copy.deepcopy(model); changed["source_solo"] = source; signed(changed)
        with self.assertRaises(EvidenceError): audit_diagnostic_recognition(changed, (source, *case[1:]))
        traces = dict(case[3]); traces[next(iter(traces))] = self.native/"missing-primary.csv"
        with self.assertRaises(EvidenceError): audit_diagnostic_recognition(model, (*case[:3], traces))

    def test_nonfinite_measured_potential_is_not_a_valid_diagnostic_response(self):
        prefix, model, case = next(self.cases())
        observation = load(self.native/(prefix+"_frozen_trial_0.json"))
        observation["samples"][0]["soma"][0] = float("nan")
        with self.assertRaises(EvidenceError): audit_diagnostic_recognition_trial(observation, model, case)

    def test_ordinary_completed_sources_still_use_ordinary_readers(self):
        sources = {load(p)["sha256"]: (p, load_completed(p)) for p in self.native.glob("*_learned_state.json")}
        topologies = set()
        for path in self.native.glob("*.json"):
            model = load(path)
            if model.get("kind") != "timelearner_recognition_state": continue
            path_source, case = sources[model["source_solo"]["sha256"]]
            self.assertTrue(audit_recognition_source(model, case)["conversion_math_verified"])
            prefix = path_source.name.removesuffix("_learned_state.json")
            for index in range(4):
                observation = load(self.native/(prefix+f"_frozen_trial_{index}.json"))
                self.assertTrue(audit_recognition_trial(observation, model)["valid_observation"])
            topologies.add(case[0]["configuration"]["model"]["branch"])
            with self.assertRaises(EvidenceError): audit_diagnostic_recognition(model, case)
        self.assertEqual(topologies, {False, True})
