"""Recovery envelopes over actual legacy packages: data checks, not new Train.

Only metadata copies are wrapped in schema5. Primary JSON/CSV, physical models,
certificates and original artifacts remain unchanged. A passing reader does
not prove that these historical runs executed the newly declared policy.
"""
from copy import deepcopy
import hashlib
import os
from pathlib import Path
import unittest

from ..candidate_recovery import RECOVERY_MODE
from ..learned_evidence import audit_learned_state, load_case as learned_case
from ..stopped_evidence import audit_stopped_state, load_case as stopped_case
from ..stopped_final_pass import audit_negative_final_pass
from ..native_evidence import EvidenceError, load
from ..model_identity import canonical_model_sha256


def audit(case):
    function = audit_learned_state if case[0]["kind"] == "timelearner_completed_state" else audit_stopped_state
    return function(*case)


def wrap(case):
    package, summary, packets, traces = case
    package, summary = deepcopy(package), deepcopy(summary)
    config = package["configuration"]
    config.update(base_schema_version=config["schema_version"], schema_version=5,
                  invalid_measurement_recovery=RECOVERY_MODE)
    allowance = max(1, config["search"]["maximum_invalid_observations"])
    config["search"]["maximum_invalid_observations"] = allowance
    summary["configuration"]["maximum_invalid_observations"] = allowance
    summary.update(base_schema_version=summary["schema_version"], schema_version=5,
                   invalid_measurement_recovery=RECOVERY_MODE, candidate_recovery_events=[])
    if package["kind"] == "timelearner_stopped_state":
        # Model-boundary representation: search state is deliberately unknown.
        # This is a hypothetical metadata control, not a native import claim.
        summary.update(search_history_retained=False, candidates=[], rejections=[], resistance_domains=[])
        for name in ("accepted_parameters", "search_probes", "applied_edits"):
            summary.pop(name, None)
        if "candidate_repeat_groups" in summary:summary["candidate_repeat_groups"] = []
    summary["invalid_observations"] = 0 if summary["search_history_retained"] else None
    package["sha256"] = canonical_model_sha256({k: v for k, v in package.items() if k != "sha256"})
    return package, summary, packets, traces


class CandidateRecoveryApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("TIMELEARNER_RECOVERY_API_CORPUS")
        if not value:raise unittest.SkipTest("requires the exact18-case published native package corpus")
        root = Path(value).resolve(strict=True)
        manifest = load(root/"corpus.json")
        if manifest["kind"] != "candidate_recovery_api_corpus" or manifest["schema_version"] != 1:
            raise RuntimeError("unknown recovery corpus")
        for row in manifest["files"]:
            path = root/row["path"]
            if not path.resolve(strict=True).is_relative_to(root) or path.is_symlink():
                raise RuntimeError("unsafe corpus member")
            raw = path.read_bytes()
            if len(raw) != row["bytes"] or hashlib.sha256(raw).hexdigest() != row["sha256"]:
                raise RuntimeError("published native primary changed")
        cls.cases = []
        coverage = set()
        for row in manifest["cases"]:
            path = root/row["package"]
            case = learned_case(path) if path.name.endswith("_learned_state.json") else stopped_case(path)
            package, summary, packets, _ = case
            coverage.add((package["configuration"]["schema_version"], package["kind"],
                          package["configuration"]["model"]["branch"], package["configuration"]["model"]["normalization"]))
            if package["kind"] == "timelearner_completed_state":
                # No-trigger controls must not invent an invalid charge of zero.
                if not all(p["native_status"] == "completed" and p["observation"]["valid"] is True and
                           p["observation"]["complete"] is True for p in packets.values()):
                    raise RuntimeError("completed no-trigger fixture contains an invalid probe")
            elif package["configuration"]["schema_version"] not in (1, 2):
                raise RuntimeError("this boundary metadata control does not reconstruct C search history")
            cls.cases.append(case)
        expected = {(base, "timelearner_completed_state", branch, norm)
                    for base in (1, 3, 4) for branch in (False, True) for norm in ("N0", "N1")}
        expected |= {(1, "timelearner_stopped_state", branch, norm)
                     for branch in (False, True) for norm in ("N0", "N1")}
        expected |= {(2, "timelearner_stopped_state", branch, "N0") for branch in (False, True)}
        if coverage != expected or len(cls.cases) != 18:
            raise RuntimeError("requires Classic/Branch N0/N1 and the declared base1..4 package matrix")

    def test_original_native_packages_still_pass(self):
        for case in self.cases:
            with self.subTest(kind=case[0]["kind"], base=case[0]["configuration"]["schema_version"]):
                result = audit(case)
                self.assertFalse(result["native_import_verified"])
                self.assertIsNone(result["evaluation_verdict"])

    def test_completed_envelopes_preserve_measured_certificate_and_C_state(self):
        for case in self.cases:
            if case[0]["kind"] != "timelearner_completed_state":continue
            before = deepcopy(case[:2]);baseline = audit(case);values = wrap(case);result = audit(values)
            self.assertEqual(case[:2], before)
            self.assertTrue(result["certificate_consistent"])
            for name in ("model_revision", "exact", "primary_trials", "capacitance_state"):
                self.assertEqual(result[name], baseline[name])
            if "capacitance_history" in baseline:self.assertEqual(result["capacitance_history"], baseline["capacitance_history"])
            self.assertEqual(result["candidate_recovery"]["recorded_events_checked"], 0)
            self.assertEqual(result["candidate_recovery"]["invalid_observations"],
                             0 if values[1]["search_history_retained"] else None)
            self.assertFalse(result["native_import_verified"])
            self.assertIsNone(result["evaluation_verdict"])

    def test_stopped_boundary_counter_stays_unknown_without_a_certificate(self):
        for case in self.cases:
            if case[0]["kind"] != "timelearner_stopped_state":continue
            baseline = audit(case);result = audit(wrap(case))
            self.assertEqual(result["training_outcome"], baseline["training_outcome"])
            self.assertEqual(result["primary_trials"], baseline["primary_trials"])
            self.assertFalse(result["certificate_present"])
            self.assertFalse(result["search_history_retained"])
            self.assertIsNone(result["candidate_recovery"]["invalid_observations"])
            self.assertFalse(result["native_import_verified"])
            self.assertIsNone(result["evaluation_verdict"])

    def test_rehashed_wrong_mode_missing_journal_counter_or_primary_are_rejected(self):
        for case in self.cases:
            for mutation in ("mode", "journal", "counter", "trace", "base"):
                package, summary, packets, traces = wrap(case)
                traces = dict(traces)
                if mutation == "mode":package["configuration"]["invalid_measurement_recovery"] = "unknown"
                elif mutation == "journal":summary.pop("candidate_recovery_events")
                elif mutation == "counter":summary["invalid_observations"] = True
                elif mutation == "trace":traces.pop(next(iter(traces)))
                else:summary["base_schema_version"] = 5
                package["sha256"] = canonical_model_sha256({k: v for k, v in package.items() if k != "sha256"})
                with self.subTest(mutation=mutation), self.assertRaises(EvidenceError):
                    audit((package, summary, packets, traces))

    def test_negative_final_pass_keeps_residuals_and_diagnostic_status(self):
        checked = set()
        for case in self.cases:
            p = case[0]
            if p["kind"] != "timelearner_stopped_state" or p["reason"] != "maximum_sweeps_exhausted":continue
            original = audit_negative_final_pass(*case);wrapped = audit_negative_final_pass(*wrap(case))
            self.assertEqual(original["residuals"], wrapped["residuals"])
            self.assertEqual(original["model_revision"], wrapped["model_revision"])
            self.assertFalse(wrapped["training_completed"]);self.assertFalse(wrapped["certificate_present"])
            self.assertIsNone(wrapped["evaluation_verdict"])
            checked.add(p["configuration"]["model"]["branch"])
        self.assertEqual(checked, {False, True})

    def test_complete_certificate_cannot_hide_a_missing_search_probe_and_trace(self):
        checked = 0
        for case in self.cases:
            if case[0]["kind"] != "timelearner_completed_state" or not case[1]["search_history_retained"]:continue
            package, summary, packets, traces = wrap(case)
            packets, traces = dict(packets), dict(traces)
            run_id = summary["configuration"]["run_id"]
            trial = next(t for t, p in packets.items() if p["requested_specification"]["run_id"] == run_id)
            packets.pop(trial);traces.pop(trial);checked += 1
            with self.assertRaisesRegex(EvidenceError, "recovery_primary_attempt_coverage_mismatch"):
                audit((package, summary, packets, traces))
        self.assertGreater(checked, 0)


if __name__ == "__main__":unittest.main()
