"""Measured native LTZone proposals and independently rebuilt confirmation trials.

Schema-1 fixture designs require an explicit adapter; they never claim that the
missing request fields were persisted by the original producer.
"""
import copy
import contextlib
import gzip
import io
import json
import math
import os
from pathlib import Path
import unittest
import tempfile

from ..calibration import RULE, calibration_dataset_digest, select_threshold, confirm_threshold
from ..learned_evidence import load_case
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load
from ..threshold_proposal_evidence import audit_threshold_proposal, audit_threshold_proposal_execution


CRITERION = {"id": "post_anchor_target_whole_window_foil_v1", "anchor": "last_stimulus",
             "begin_offset": 0., "end_offset": None, "reject_target_outside_window": True}


def measurement(root, base, phase, candidate, selection=None):
    prefix = base+"_"+phase
    design = load(root/(prefix+"_calibration_design.json"))
    if (design["kind"] != "native_threshold_potential_fixture_design" or
            type(design["schema_version"]) is not int or design["schema_version"] not in (1, 2) or
            design["primary_trial_ids"] != ["trial_0", "trial_1"] or
            design["robustness_trial_ids"] != ["trial_2", "trial_3"] or
            design["foil_rule"] != "first_isi_preserved_remaining_isi_times_8" or
            design["model_revision"] != candidate["model_revision"] or
            design["record_threshold_potential"] is not True or design["calibration_scope"] != "reset_per_trial"):
        raise RuntimeError("unsupported native fixture design")
    model = candidate["source_recognition"]["source_solo"]["configuration"]["model"]
    trials, observations, declared = [], [], []
    for i in range(4):
        pattern = [v if i % 2 == 0 or j == 0 else v*8 for j, v in enumerate(model["initial_isi"])]
        row = {"trial_id": "trial_"+str(i), "sample_id": "training_target" if i % 2 == 0 else "foil_dispersed",
               "label": "target" if i % 2 == 0 else "foil", "pattern_isi": pattern, "pattern_hash": sha(pattern),
               "duration": math.ceil((sum(pattern)+.03)*model["frequency_hz"])/model["frequency_hz"],
               "maximum_samples": 1000000,
               "reset_policy": "reset_per_trial" if i < 2 else "preserve_neuron_dynamics"}
        declared.append(row)
        if i < 2:
            trials.append({k: v for k, v in row.items() if k not in ("pattern_isi", "maximum_samples")})
            trials[-1].update(presentation_index=i, observation=prefix+"_frozen_trial_"+str(i)+".json")
            observations.append(load(root/trials[-1]["observation"]))
    if design["schema_version"] == 2:
        if (design["declared_trials"] != declared or design["criterion"] != CRITERION or
                design["proposal_threshold_bounds"] != {"minimum": 1.e-6, "maximum": 1.} or
                type(design["observation_schema_version"]) is not int or design["observation_schema_version"] != 2):
            raise RuntimeError("saved native request design differs from fixture contract")
    return {"candidate": candidate, "evaluation_spec": {"kind": "timelearner_recognition_evaluation_spec",
            "schema_version": 1, "run_id": design["run_id"], "model_revision": candidate["model_revision"],
            "coverage_policy": "per_trial_windows", "criterion": copy.deepcopy(CRITERION), "trials": trials},
            "observations": observations, "execution": {"attempt_id": base, "clock_id": base,
            "stage": "confirmation" if selection is not None else "search", "selection_sha256": selection}}


class NativeThresholdProposalEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("TIMELEARNER_THRESHOLD_POTENTIAL_DIR")
        if not value:
            raise unittest.SkipTest("requires real complete threshold-potential fixtures")
        cls.root = Path(value)
        paths = sorted(cls.root.glob("*_threshold_proposal.json"))
        expected = {top+"_"+frequency+"_N1_learned_boundary_configured_recognition_10"
                    for top in ("Classic", "Branch") for frequency in ("2000", "20000")}
        if {p.name.removesuffix("_threshold_proposal.json") for p in paths} != expected:
            raise RuntimeError("requires all four native topology/frequency proposal fixtures")
        cls.cases = []
        for path in paths:
            base = path.name.removesuffix("_threshold_proposal.json")
            proposal = load(path)
            source_case = load_case(cls.root/(base+"_learned_state.json"))
            high = load(cls.root/(base+"_candidate_high_recognition_candidate.json"))
            characterization = measurement(cls.root, base, "candidate_high", high)
            if proposal["threshold"] is None:
                if (cls.root/(base+"_proposal_candidate.json")).exists():
                    raise RuntimeError("candidate exists without a proposed threshold")
                cls.cases.append((base, source_case, characterization, proposal, None, None))
                continue
            candidate = load(cls.root/(base+"_proposal_candidate.json"))
            search = measurement(cls.root, base, "proposal_search", candidate)
            model = candidate["source_recognition"]["source_solo"]["configuration"]["model"]
            trials = []
            for t in search["evaluation_spec"]["trials"]:
                row = {k: v for k, v in t.items() if k not in ("observation", "pattern_hash")}
                row["pattern_isi"] = [v if t["label"] == "target" or j == 0 else v*8
                                      for j, v in enumerate(model["initial_isi"])]
                trials.append(row)
            spec = {"kind": "timelearner_threshold_calibration_spec", "schema_version": 1,
                    "calibration_id": base, "protocol": "historical_same_matrix", "data_partition_id": "declared-reset-primary",
                    "source_recognition_sha256": candidate["source_recognition"]["sha256"],
                    "source_model_revision": candidate["source_recognition"]["model_revision"],
                    "coverage_policy": "per_trial_windows", "criterion": copy.deepcopy(CRITERION), "trials": trials,
                    "thresholds": [candidate["threshold"]], "maximum_candidates": 1, "selection_rule": RULE}
            spec["dataset_digest"] = calibration_dataset_digest(spec["coverage_policy"], spec["criterion"], trials)
            cls.cases.append((base, source_case, characterization, proposal, search, spec))

    def audit(self, proposal, characterization, source):
        return audit_threshold_proposal(proposal, characterization["evaluation_spec"], characterization["observations"],
                                        characterization["candidate"], source, minimum_threshold=1.e-6, maximum_threshold=1.)

    def test_actual_bracket_is_derived_from_primary_ltz_frames(self):
        for _, source, characterization, proposal, _, _ in self.cases:
            result = self.audit(proposal, characterization, source)
            self.assertTrue(result["proposal_math_verified"])
            self.assertEqual(result["status"], proposal["status"])
            self.assertFalse(result["calibrated"])

    def test_actual_fresh_confirmation_uses_common_timing_scorer(self):
        for base, source, _, _, search, spec in self.cases:
            if search is None:
                continue
            selected = select_threshold(spec, [search], source)
            if selected["status"] != "pending_confirmation":
                self.assertEqual(selected["status"], "nonseparable")
                self.assertFalse(selected["calibrated"])
                continue
            confirmed = confirm_threshold(spec, [search], source, selected,
                measurement(self.root, base, "proposal_confirmation", search["candidate"], selected["sha256"]))
            self.assertIn(confirmed["status"], ("confirmed", "confirmation_failed"))
            self.assertEqual(confirmed["calibrated"], confirmed["status"] == "confirmed")
            self.assertFalse(confirmed["native_execution_verified"])
            self.assertIsNone(confirmed["evaluation_verdict"])

    def test_proposal_candidate_execution_and_restoration_links(self):
        for base, source, characterization, proposal, search, _ in self.cases:
            if search is None:
                continue
            record = load(self.root/(base+"_proposal_protocol.json"))
            restored = load(self.root/(base+"_proposal_restoration.json"))
            kwargs = {"characterization": characterization["candidate"], "search_run_id": search["evaluation_spec"]["run_id"],
                      "confirmation_run_id": base+"_proposal_confirmation_frozen"}
            actual = audit_threshold_proposal_execution(record, proposal, search["candidate"], restored, source, **kwargs)
            self.assertTrue(actual["declared_links_consistent"])
            self.assertFalse(actual["native_execution_verified"])
            for field in ("candidate_sha256", "proposal_sha256", "source_recognition_sha256", "confirmation_run_id"):
                bad = copy.deepcopy(record);bad[field] = "wrong"
                with self.assertRaises(EvidenceError):
                    audit_threshold_proposal_execution(bad, proposal, search["candidate"], restored, source, **kwargs)
            bad = copy.deepcopy(restored);bad["restored"] = 1
            with self.assertRaises(EvidenceError):
                audit_threshold_proposal_execution(record, proposal, search["candidate"], bad, source, **kwargs)

    def test_resigned_forged_bracket_is_rejected(self):
        _, source, characterization, proposal, _, _ = next(row for row in self.cases if row[0].startswith("Branch_2000_"))
        for key in ("threshold", "lower_bound", "target_minimum_inside", "minimum_threshold"):
            changed = copy.deepcopy(proposal); changed[key] *= 1.01
            changed["sha256"] = sha({k: v for k, v in changed.items() if k != "sha256"})
            with self.assertRaises(EvidenceError): self.audit(changed, characterization, source)

    def test_missing_corrupt_spiking_characterization_is_rejected(self):
        _, source, characterization, proposal, _, _ = self.cases[0]
        for change in ("missing", "nonfinite", "source", "spiking"):
            bad = copy.deepcopy(characterization)
            if change == "missing": bad["observations"].pop()
            elif change == "nonfinite": bad["observations"][0]["samples"][0]["lt_potential"] = float("nan")
            elif change == "source": bad["observations"][0]["threshold_potential_source"]["path"] = "$.Soma1.SumPotential"
            else: bad["observations"][0]["spike_count"] = 1
            with self.assertRaises(EvidenceError): self.audit(proposal, bad, source)

    def test_search_data_cannot_be_reused_as_confirmation(self):
        _, source, _, _, search, spec = next(row for row in self.cases if row[0].startswith("Branch_2000_"))
        self.assertIsNotNone(search)
        selected = select_threshold(spec, [search], source)
        reused = copy.deepcopy(search)
        reused["execution"].update(stage="confirmation", selection_sha256=selected["sha256"])
        with self.assertRaises(EvidenceError): confirm_threshold(spec, [search], source, selected, reused)

    def test_production_cli_roundtrip_and_output_collision(self):
        from ..__main__ import main
        base, source, _, _, search, spec = next(row for row in self.cases if row[0].startswith("Branch_2000_"))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def write(name, value):
                (root/name).write_text(json.dumps(value, allow_nan=False), encoding="utf-8")
            def bundle(name, m):
                evaluation = copy.deepcopy(m["evaluation_spec"])
                by_id = {o["trial_id"]: o for o in m["observations"]}
                for row in evaluation["trials"]:
                    row["observation"] = name+"-"+row["trial_id"]+".json.gz"
                    (root/row["observation"]).write_bytes(gzip.compress(json.dumps(by_id[row["trial_id"]]).encode(), mtime=0))
                write(name+"-evaluation.json", evaluation)
                write(name+"-candidate.json", m["candidate"])
                write(name+".json", {"kind": "timelearner_threshold_measurement_set", "schema_version": 1,
                    "measurements": [{"candidate": name+"-candidate.json", "evaluation": name+"-evaluation.json", "execution": m["execution"]}]})
            def invoke(*args):
                output, error = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
                    code = main(list(map(str, args)))
                return code, output.getvalue(), error.getvalue()
            write("spec.json", spec);bundle("search", search)
            shared = [root/"spec.json", "--measurements", root/"search.json", "--source-solo", self.root/(base+"_learned_state.json")]
            code, _, error = invoke("calibrate", "select", *shared, "--output", root/"selected.json")
            self.assertEqual(code, 0, error)
            selected = load(root/"selected.json")
            self.assertEqual(selected, select_threshold(spec, [search], source))
            bundle("confirmation", measurement(self.root, base, "proposal_confirmation", search["candidate"], selected["sha256"]))
            args = ["calibrate", "confirm", *shared, "--selection", root/"selected.json",
                    "--confirmation", root/"confirmation.json", "--output", root/"confirmed.json"]
            code, _, error = invoke(*args)
            self.assertEqual(code, 0, error)
            self.assertEqual(load(root/"confirmed.json")["status"], "confirmed")
            original = (root/"confirmed.json").read_bytes()
            code, output, error = invoke(*args)
            self.assertEqual(code, 2)
            self.assertFalse(output)
            self.assertIn("reason", json.loads(error))
            self.assertEqual(original, (root/"confirmed.json").read_bytes())

    def test_measurement_descriptor_cannot_escape_portable_bundle(self):
        from ..calibration_io import load_measurements
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"measurements.json"
            for name in ("../candidate.json", "/tmp/candidate.json", "C:/candidate.json", "nested\\candidate.json"):
                path.write_text(json.dumps({"kind": "timelearner_threshold_measurement_set", "schema_version": 1,
                    "measurements": [{"candidate": name, "evaluation": name, "execution": {}}]}))
                with self.assertRaises(EvidenceError): load_measurements(path)
