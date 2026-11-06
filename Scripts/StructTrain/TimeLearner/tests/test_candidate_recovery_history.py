"""Hypothetical decision metadata over actual invalid stock JSON/CSV.

These are validator mutation tests. They do not attest that the historical
controller executed the newly declared recovery policy.
"""
from copy import deepcopy
import unittest

from ..candidate_recovery import RECOVERY_MODE
from ..candidate_recovery_history import audit_recovery_history
from ..native_evidence import EvidenceError, load
from .test_candidate_recovery_evidence import CandidateRecoveryPrimaryTest


class CandidateRecoveryHistoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        CandidateRecoveryPrimaryTest.setUpClass()
        cls.cases = CandidateRecoveryPrimaryTest.cases

    def fixture(self, case):
        _, packet, trace, protocol, _, folder = case
        summary = load(folder/"train_stopped_summary.json")
        self.assertIn(summary["schema_version"], (1, 2))
        trial = packet["requested_specification"]["trial_id"];prepared = packet["prepared"]
        index = next(i for i, v in enumerate(protocol["inputs"]) if v["id"] == prepared["input_id"])
        validity = packet["observation"]["burst_assignments"][0]["validity"]
        event = {"action_serial": int(trial.rsplit("/", 1)[1]), "input_index": index,
            "candidate_input_index": 0 if index == len(protocol["inputs"])-1 else index,
            "sweep": 0, "model_epoch": prepared["model_epoch"], "invalid_before": 0, "invalid_after": 1,
            "run_id": packet["requested_specification"]["run_id"], "trial_id": trial,
            "base_model_revision": prepared["base_model_revision"],
            "effective_model_revision": prepared["effective_model_revision"],
            "phase": "anchor" if index == len(protocol["inputs"])-1 else "input", "validity": validity,
            "full_parameters": deepcopy(summary["actual_parameters"]), "capacitance": None,
            "disposition": "cursor_advanced", "status_after": "searching", "reason_after": ""}
        summary.update(base_schema_version=summary["schema_version"], schema_version=5,
            invalid_measurement_recovery=RECOVERY_MODE, invalid_observations=1,
            search_history_retained=True, candidate_recovery_events=[event],
            rejections=[{"trial_id": trial, "reason": "unassigned_burst_candidate:"+validity}])
        summary["configuration"]["maximum_invalid_observations"] = 2
        return summary, {trial: deepcopy(packet)}, {trial: trace}, protocol

    def test_bound_metadata_and_primary_are_consistent_without_claiming_execution(self):
        for case in self.cases:
            values = self.fixture(case);before = deepcopy(values[:2])
            result = audit_recovery_history(*values)
            self.assertEqual(result["recorded_events_checked"], 1)
            self.assertTrue(result["recovery_increments_primary_consistent"])
            self.assertFalse(result["all_invalid_observations_independently_recounted"])
            self.assertIsNone(result["evaluation_verdict"])
            self.assertEqual(values[:2], before)

    def test_terminal_budget_and_restored_best_require_exact_reasons_and_limits(self):
        for case in self.cases:
            for disposition in ("invalid_budget_stop", "restored_best_stop"):
                values = self.fixture(case);summary = values[0];event = summary["candidate_recovery_events"][0]
                event["disposition"] = disposition
                if disposition == "invalid_budget_stop":
                    summary["configuration"]["maximum_invalid_observations"] = 1
                    summary["invalid_observations"] = 2
                    event.update(invalid_before=1, invalid_after=2, status_after="invalid_observation",
                                 reason_after=summary["rejections"][0]["reason"])
                else:
                    event.update(status_after="search_unresolved", reason_after="restored_best_candidate_has_unassigned_burst")
                summary.update(state="finished", outcome=event["status_after"], reason=event["reason_after"])
                audit_recovery_history(*values)
                for field, value in (("reason_after", "wrong"), ("status_after", "exact"), ("invalid_after", 0)):
                    changed = deepcopy(summary);changed["candidate_recovery_events"][0][field] = value
                    with self.assertRaises(EvidenceError):audit_recovery_history(changed, *values[1:])

    def test_bad_context_phase_bounds_charge_or_coverage_are_rejected(self):
        mutations = ("serial", "phase", "candidate", "epoch", "revision", "unknown", "bounds", "charge",
                     "total", "counter_reset", "missing_event", "missing_rejection", "duplicate_rejection", "mode")
        for case in self.cases:
            for mutation in mutations:
                values = self.fixture(case);s = values[0];e = s["candidate_recovery_events"][0]
                if mutation == "serial":e["action_serial"] += 1
                elif mutation == "phase":e["phase"] = "final"
                elif mutation == "candidate":e["candidate_input_index"] = len(values[3]["inputs"])-1
                elif mutation == "epoch":e["model_epoch"] += 1
                elif mutation == "revision":e["base_model_revision"] = "changed"
                elif mutation == "unknown":e["unreviewed_factor"] = True
                elif mutation == "bounds":e["full_parameters"][0]["synapses"] = 129
                elif mutation == "charge":e["invalid_after"] = 0
                elif mutation == "total":s["invalid_observations"] = 4
                elif mutation == "counter_reset":e["invalid_before"] = 1;e["invalid_after"] = 1
                elif mutation == "missing_event":s["candidate_recovery_events"] = []
                elif mutation == "missing_rejection":s["rejections"] = []
                elif mutation == "duplicate_rejection":s["rejections"].append(deepcopy(s["rejections"][0]))
                else:e["disposition"] = "unknown"
                with self.subTest(case=case[0], mutation=mutation), self.assertRaises(EvidenceError):
                    audit_recovery_history(*values)

    def test_final_or_capture_trial_cannot_be_disguised_as_search_recovery(self):
        for role in ("final/0/verify/1/1", "capture/1"):
            values = self.fixture(self.cases[0]);summary, packets, traces, protocol = values
            event = summary["candidate_recovery_events"][0];old = event["trial_id"]
            new = event["run_id"]+"/"+role;event["trial_id"] = new
            summary["rejections"][0]["trial_id"] = new
            packet = packets.pop(old);packets[new] = packet;traces[new] = traces.pop(old)
            packet["requested_specification"]["trial_id"] = new
            packet["observation"]["specification"]["trial_id"] = new
            with self.assertRaisesRegex(EvidenceError, "recovery_event_trial_or_order_mismatch"):
                audit_recovery_history(*values)

    def test_unretained_history_is_unknown_and_cannot_hide_recovery(self):
        values = self.fixture(self.cases[0]);summary = values[0]
        summary.update(search_history_retained=False, invalid_observations=None,
                       candidate_recovery_events=[], rejections=[], candidates=[], resistance_domains=[])
        for field in ("search_probes", "applied_edits", "accepted_parameters"):summary.pop(field, None)
        result = audit_recovery_history(*values)
        self.assertFalse(result["history_retained"]);self.assertIsNone(result["invalid_observations"])
        summary["rejections"] = [{"trial_id": "hidden", "reason": "unassigned_burst_candidate:missing"}]
        with self.assertRaises(EvidenceError):audit_recovery_history(*values)


if __name__ == "__main__":unittest.main()
