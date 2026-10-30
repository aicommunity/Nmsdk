"""Read real native calibrated packages and refuse forged confirmation claims."""
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import unittest

from ..calibrated_evidence import audit_calibrated_state
from ..learned_evidence import load_case
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load


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
