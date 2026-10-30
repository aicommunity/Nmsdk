"""Read real native calibrated packages and refuse forged confirmation claims."""
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..calibrated_evidence import audit_calibrated_state
from ..learned_evidence import load_case
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load
from ..recognition_metrics import score_recognition_evaluation, score_threshold_candidate
from ..recognition_trial_evidence import audit_recognition_trial


def frozen_measurement(path, package):
    # Explicit adapter for NativeCalibratedState's GTest protocol: after import
    # it repeats the same four declared requests with a new fixed run/name.
    # Durations/patterns come from the saved prior design, never end-begin or
    # an observed waveform. This fixture is not independent held-out data.
    base = path.name.removesuffix("_calibrated_state.json")
    design = load(path.with_name(base+"_proposal_confirmation_calibration_design.json"))
    if design["schema_version"] != 2 or len(design["declared_trials"]) != 4:
        raise RuntimeError("requires the full saved native declaration")
    trials, observations = [], []
    for index, request in enumerate(design["declared_trials"]):
        name = base+"_calibrated_frozen_trial_"+str(index)+".json"
        trials.append({**{key: request[key] for key in
                         ("trial_id", "sample_id", "label", "pattern_hash", "reset_policy", "duration")},
                       "presentation_index": index, "observation": name})
        observations.append(load(path.with_name(name)))
    return {"kind": "timelearner_recognition_evaluation_spec", "schema_version": 1,
            "run_id": base+"_calibrated_frozen", "model_revision": package["model_revision"],
            "coverage_policy": "per_trial_windows", "criterion": design["criterion"], "trials": trials}, observations


def resign(package):
    proof = package["calibration_proof"]
    proof.pop("sha256", None);proof["sha256"] = sha(proof)
    archive = package["neuron"]
    archive["metadata"]["calibration"]["confirmation_sha256"] = proof["sha256"]
    archive.pop("sha256", None);archive["sha256"] = sha(archive)
    package.pop("sha256", None);package["sha256"] = sha(package)
    return package


class CalibratedEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("TIMELEARNER_CALIBRATED_STATE_DIR")
        if not value: raise unittest.SkipTest("requires actual Classic/Branch native calibrated-state controls")
        cls.cases = []
        for path in sorted(Path(value).glob("*_calibrated_state.json")):
            source = path.with_name(path.name.removesuffix("_calibrated_state.json")+"_learned_state.json")
            cls.cases.append((path, load(path), source, load_case(source)))
        if len(cls.cases) != 2: raise RuntimeError("requires both actual native calibrated-state controls")

    def test_real_native_models_preserve_physics_and_confirm_primary_pair(self):
        for _, package, _, source in self.cases:
            result = audit_calibrated_state(package, source)
            self.assertTrue(result["calibration_evidence_consistent"])
            self.assertTrue(result["calibrated"])
            self.assertFalse(result["native_execution_verified"])
            self.assertFalse(result["native_import_verified"])
            self.assertIsNone(result["evaluation_verdict"])
            self.assertEqual(package["neuron"]["graph"], package["source_candidate"]["neuron"]["graph"])
            self.assertIsNone(package["recognition_certificate"])

    def test_resigned_execution_grid_and_boolean_claims_are_rejected(self):
        _, package, _, source = self.cases[0]
        for key, value in (("execution_attested", True), ("grid_selection_verified", True),
                           ("grid_selection_verified", 0), ("calibrated", 1)):
            changed = copy.deepcopy(package);changed["calibration_proof"][key] = value
            with self.assertRaises(EvidenceError): audit_calibrated_state(resign(changed), source)

    def test_reusing_search_as_confirmation_is_rejected(self):
        _, package, _, source = self.cases[0]
        changed = copy.deepcopy(package);proof = changed["calibration_proof"]
        proof["confirmation"] = copy.deepcopy(proof["search"])
        proof["confirmation_assessment"] = copy.deepcopy(proof["search_assessment"])
        with self.assertRaisesRegex(EvidenceError, "fresh_run"):
            audit_calibrated_state(resign(changed), source)

    def test_resigned_damaged_raw_samples_are_rejected(self):
        _, package, _, source = self.cases[0]
        changed = copy.deepcopy(package)
        changed["calibration_proof"]["confirmation"]["observations"][0]["samples"][0]["soma"][0] = None
        with self.assertRaises(EvidenceError): audit_calibrated_state(resign(changed), source)

    def test_production_analysis_cli_reads_actual_source_primary_data(self):
        from ..__main__ import main
        path, _, source, _ = self.cases[0]
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            main(["analyze", str(path), "--format", "calibrated-state", "--source-solo", str(source)])
        result = json.loads(output.getvalue())["analysis"]
        self.assertTrue(result["calibration_evidence_consistent"])
        self.assertFalse(result["native_execution_verified"])

    def test_frozen_response_is_recomputed_without_changing_the_model(self):
        for path, package, _, _ in self.cases:
            before = sha(package);spec, observations = frozen_measurement(path, package)
            result = score_recognition_evaluation(spec, observations, package)
            physical = score_threshold_candidate(spec, observations, package["source_candidate"])
            self.assertEqual(result["pooled_counts"], physical["pooled_counts"])
            self.assertEqual(result["trials"], physical["trials"])
            self.assertTrue(result["calibration_evidence_checked"])
            self.assertFalse(result["statistical_independence_verified"])
            self.assertFalse(result["evaluation_partition_verified"])
            self.assertIsNone(result["evaluation_verdict"])
            self.assertEqual(sha(package), before)
            self.assertTrue(audit_recognition_trial(observations[0], package)["calibration_evidence_checked"])

    def test_calibration_run_cannot_be_relabelled_as_frozen_evaluation(self):
        path, package, _, _ = self.cases[0];spec, observations = frozen_measurement(path, package)
        spec["run_id"] = package["calibration_proof"]["confirmation"]["requests"][0]["run_id"]
        with self.assertRaisesRegex(EvidenceError, "reuses_calibration_run"):
            score_recognition_evaluation(spec, observations, package)

    def test_unconfirmed_or_forged_models_cannot_enter_frozen_scoring(self):
        path, package, _, _ = self.cases[0];spec, observations = frozen_measurement(path, package)
        with self.assertRaisesRegex(EvidenceError, "explicit_calibration_scoring"):
            score_recognition_evaluation(spec, observations, package["source_candidate"])
        changed = copy.deepcopy(package);changed["calibration_proof"]["execution_attested"] = True
        with self.assertRaises(EvidenceError): score_recognition_evaluation(spec, observations, resign(changed))

    def test_production_frozen_evaluation_cli_keeps_calibration_and_test_separate(self):
        from ..__main__ import main
        path, package, _, _ = self.cases[0];spec, observations = frozen_measurement(path, package)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for index, (trial, observation) in enumerate(zip(spec["trials"], observations)):
                name = "trial-"+str(index)+".json";trial["observation"] = name
                (root/name).write_text(json.dumps(observation, allow_nan=False))
            (root/"evaluation.json").write_text(json.dumps(spec, allow_nan=False))
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                main(["analyze", str(root/"evaluation.json"), "--format", "recognition-evaluation", "--model", str(path)])
            result = json.loads(output.getvalue())["analysis"]
            self.assertTrue(result["calibration_evidence_checked"])
            self.assertIsNone(result["evaluation_verdict"])
