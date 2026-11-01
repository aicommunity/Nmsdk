"""Compare actual native assessments with the common independent primary scorer."""
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

from . import test_threshold_candidate_evidence as legacy_fixtures
from .test_threshold_proposal_evidence import measurement
from ..learned_evidence import load_case
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load
from ..native_calibration_evidence import audit_native_calibration_assessment


def signed(value):
    value.pop("sha256", None);value["sha256"] = sha(value)
    return value


class NativeCalibrationEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("TIMELEARNER_THRESHOLD_POTENTIAL_DIR")
        if not root or not os.environ.get("TIMELEARNER_THRESHOLD_CANDIDATE_DIR"):
            raise unittest.SkipTest("requires all actual native assessment matrices")
        fixtures = legacy_fixtures.ThresholdCandidateEvidenceTest
        fixtures.setUpClass()
        cls.cases = []
        for path, candidate, source, observations, _ in fixtures.cases:
            prefix = path.name.removesuffix("_recognition_candidate.json")
            spec = fixtures.specification(path, candidate)
            cls.add_scopes(path.parent, prefix, candidate, source, spec, observations)
        root = Path(root)
        proposed = 0
        for top in ("Classic", "Branch"):
            for frequency in ("2000", "20000"):
                base = top+"_"+frequency+"_N1_learned_boundary_configured_recognition_10"
                source = load_case(root/(base+"_learned_state.json"))
                has_proposal = load(root/(base+"_threshold_proposal.json"))["threshold"] is not None
                proposed += has_proposal
                for phase in ("candidate_low", "candidate_high", "proposal_search", "proposal_confirmation"):
                    if phase.startswith("proposal_") and not has_proposal:
                        if (root/(base+"_"+phase+"_calibration_assessment.json")).exists():
                            raise RuntimeError("assessment exists for an undeclared proposal")
                        continue
                    candidate_path = base+"_"+phase+"_recognition_candidate.json" if phase.startswith("candidate_") else base+"_proposal_candidate.json"
                    candidate = load(root/candidate_path)
                    m = measurement(root, base, phase, candidate, include_robustness=True)
                    cls.add_scopes(root, base+"_"+phase, candidate, source, m["evaluation_spec"], m["observations"])
        if len(cls.cases) != 48+4*proposed:
            raise RuntimeError("requires every complete matrix and scoped primary pair; NoGap does not create a candidate")

    @classmethod
    def add_scopes(cls, root, prefix, candidate, source, spec, observations):
        for primary in (False, True):
            name = prefix+("_primary" if primary else "")+"_calibration_assessment.json"
            scoped_spec = copy.deepcopy(spec)
            if primary: scoped_spec["trials"] = scoped_spec["trials"][:2]
            scoped = observations[:2] if primary else observations
            cls.cases.append((root/name, load(root/name), scoped_spec, scoped, candidate, source))

    def test_all_declared_native_assessments_agree_with_primary_scorer(self):
        for _, assessment, spec, observations, candidate, source in self.cases:
            result = audit_native_calibration_assessment(assessment, spec, observations, candidate, source)
            self.assertTrue(result["native_criterion_consistent"])
            self.assertFalse(result["native_execution_verified"])
            self.assertFalse(result["calibrated"])
            self.assertIsNone(result["evaluation_verdict"])

    def test_resigned_positive_and_boolean_count_claims_are_rejected(self):
        _, assessment, spec, observations, candidate, source = next(row for row in self.cases if "candidate_high" in row[0].name)
        self.assertFalse(assessment["criterion_met"])
        for change in ("positive", "false_count", "boolean_count", "criterion", "calibrated", "missing_trial"):
            bad = copy.deepcopy(assessment)
            if change == "positive":bad["criterion_met"] = True
            elif change == "false_count":bad["target_violations"] = 0
            elif change == "boolean_count":bad["pooled_counts"]["FP"] = False
            elif change == "criterion":bad["criterion"]["begin_offset"] = False
            elif change == "calibrated":bad["calibrated"] = 0
            else:bad["trials"].pop()
            with self.assertRaises(EvidenceError):
                audit_native_calibration_assessment(signed(bad), spec, observations, candidate, source)

    def test_oversampled_complete_flag_does_not_hide_non_native_grid(self):
        _, assessment, spec, observations, candidate, source = self.cases[0]
        bad = copy.deepcopy(observations)
        extra = copy.deepcopy(bad[0]["samples"][0])
        extra["time"] += .25/bad[0]["frequency_hz"]
        bad[0]["samples"].insert(1, extra)
        with self.assertRaisesRegex(EvidenceError, "recognition_sample_off_native_grid"):
            audit_native_calibration_assessment(assessment, spec, bad, candidate, source)

    def test_observation_row_order_does_not_change_native_audit(self):
        _, assessment, spec, observations, candidate, source = self.cases[0]
        self.assertEqual(audit_native_calibration_assessment(assessment, spec, observations, candidate, source),
                         audit_native_calibration_assessment(assessment, spec, list(reversed(observations)), candidate, source))

    def test_production_analysis_cli_requires_primary_spec_and_source(self):
        from ..__main__ import main
        path, _, spec, _, candidate, _ = self.cases[0]
        base = path.name.rsplit("_candidate_", 1)[0]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            declared = copy.deepcopy(spec)
            for row in declared["trials"]:
                target = path.parent/row["observation"]
                (root/target.name).write_bytes(target.read_bytes())
                row["observation"] = target.name
            (root/"evaluation.json").write_text(json.dumps(declared))
            (root/"candidate.json").write_text(json.dumps(candidate))
            output, error = io.StringIO(), io.StringIO()
            args = ["analyze", str(path), "--format", "native-calibration-assessment", "--evaluation", str(root/"evaluation.json"),
                    "--model", str(root/"candidate.json"), "--source-solo", str(path.parent/(base+"_learned_state.json"))]
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):code = main(args)
            self.assertEqual(code, 0, error.getvalue())
            self.assertTrue(json.loads(output.getvalue())["analysis"]["native_criterion_consistent"])
