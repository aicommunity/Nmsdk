"""Corrupt actual stock JSON/CSV; never synthesize an acceptable measured peak."""
from copy import deepcopy
import csv
import os
from pathlib import Path
import tempfile
import unittest

from ..candidate_recovery_evidence import audit_unassigned_burst
from ..native_evidence import EvidenceError, audit_probe, load
from ..stock_failure_reports import select_failure_boundary


class CandidateRecoveryPrimaryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("TIMELEARNER_STOCK_THRESHOLD_STUDY")
        if not value:raise unittest.SkipTest("requires four actual stock cold threshold runs")
        cls.cases = []
        names = {f"{topology}-threshold-{threshold}" for topology in ("Classic", "Branch")
                 for threshold in ("training100", "low")}
        root = Path(value)/"runs"
        if {p.name for p in root.iterdir()} != names:
            raise RuntimeError("requires exact four-condition stock primary inventory")
        for name in sorted(names):
            folder = root/name/"native"
            selected = select_failure_boundary(folder)
            row = selected["probes"][-1]
            package = load(folder/"train_stopped_state.json")
            cls.cases.append((name, load(folder/row["packet"]), folder/row["trace"], package["protocol"],
                              selected, folder))

    def test_real_missing_and_ambiguous_bursts_remain_invalid(self):
        seen = set()
        for name, packet, trace, protocol, _, _ in self.cases:
            with self.subTest(name=name):
                before = deepcopy(packet)
                result = audit_unassigned_burst(packet, trace, protocol)
                seen.add(result["validity"])
                self.assertTrue(result["unassigned_burst_classified"])
                self.assertTrue(result["trace_checked"])
                self.assertEqual(result["expected_stimulus_count"], 4)
                self.assertFalse(result["valid_observation"])
                self.assertFalse(result["training_transition_verified"])
                self.assertFalse(result["certificate_consistent"])
                self.assertIsNone(result["evaluation_verdict"])
                self.assertFalse(audit_probe(packet, trace)["valid_observation"])
                self.assertEqual(packet, before)
        self.assertEqual(seen, {"missing", "ambiguous"})

    def test_other_failures_and_context_corruptions_are_not_recovery(self):
        for name, packet, trace, protocol, _, _ in self.cases:
            for mutation in ("incomplete", "valid", "end_reason", "status", "fresh", "packet_reason",
                             "base", "protocol", "sample", "pattern", "dimension", "selected",
                             "window", "extra_reason", "duplicate_reason", "spikes", "stimulus_order",
                             "event_relative", "first_stimulus", "wave_relative", "wave_id"):
                changed = deepcopy(packet);p = deepcopy(protocol)
                observation = changed["observation"];spec = observation["specification"]
                if mutation == "incomplete":observation["complete"] = False
                elif mutation == "valid":observation["valid"] = True
                elif mutation == "end_reason":observation["end_reason"] = "cancelled"
                elif mutation == "status":changed["native_status"] = "cancelled"
                elif mutation == "fresh":changed["requires_fresh_verification"] = True
                elif mutation == "packet_reason":changed["reasons"] = ["numeric_error"]
                elif mutation == "base":changed["current_base_revision"] = "changed"
                elif mutation == "protocol":p["revision"] = "changed"
                elif mutation == "sample":p["sample_id"] = "changed"
                elif mutation == "pattern":p["pattern_hash"] = "changed"
                elif mutation == "dimension":spec["baseline"].append(0)
                elif mutation == "selected":changed["prepared"]["selected_input_index"] = 999
                elif mutation == "window":spec["windows"][0]["input_id"] = "unknown"
                elif mutation == "extra_reason":observation["reasons"].append("nonfinite_soma")
                elif mutation == "duplicate_reason":observation["reasons"] = [observation["reasons"][0]]*2
                elif mutation == "spikes":observation["spike_count"] = 0
                elif mutation == "stimulus_order":observation["stimuli"].reverse()
                elif mutation == "event_relative":observation["stimuli"][0]["relative_to_trial_start"] += .0005
                elif mutation == "first_stimulus":observation["first_stimulus_time"] += .0005
                elif mutation == "wave_relative":observation["burst_assignments"][0]["waves"][0]["relative_to_trial_start"] += .0005
                else:observation["burst_assignments"][0]["waves"][0]["stimulus_id"] = "pulse0"
                with self.subTest(name=name, mutation=mutation), self.assertRaises(EvidenceError):
                    audit_unassigned_burst(changed, trace, p)

    def test_unassigned_peak_cannot_gain_invented_numeric_fields(self):
        for name, packet, trace, protocol, _, _ in self.cases:
            for field in ("amplitude", "raw_potential", "time", "plateau_end", "delay_from_stimulus",
                          "relative_to_trial_start", "candidate_count"):
                changed = deepcopy(packet);changed["observation"]["peaks"][0][field] = 1
                with self.subTest(name=name, field=field), self.assertRaises(EvidenceError):
                    audit_unassigned_burst(changed, trace, protocol)

    def test_raw_trace_damage_cannot_be_hidden_by_invalid_flag(self):
        for name, packet, trace, protocol, _, _ in self.cases:
            with trace.open(newline="") as stream:original = list(csv.reader(stream))
            for mutation in ("censored", "nonfinite", "duplicate_clock", "sample_gap", "stimulus", "soma", "clipped"):
                rows = deepcopy(original)
                if mutation == "censored":rows.pop()
                elif mutation == "nonfinite":rows[100][2] = "NaN"
                elif mutation == "duplicate_clock":rows[100][0] = rows[99][0]
                elif mutation == "sample_gap":rows[100][0] = str(float(rows[100][0])+.00025)
                elif mutation == "stimulus":
                    onset = next(i for i in range(2, len(rows)) if float(rows[i][1]) > 0 and float(rows[i-1][1]) <= 0)
                    rows[onset][1] = "0"
                elif mutation == "soma":
                    wave = packet["observation"]["burst_assignments"][0]["waves"][0]
                    index = min(range(1, len(rows)), key=lambda i:abs(float(rows[i][0])-wave["time"]))
                    channel = packet["observation"]["burst_assignments"][0]["channel"]
                    rows[index][channel+2] = str(float(rows[index][channel+2])+.0001)
                else:
                    channel = packet["observation"]["burst_assignments"][0]["channel"]
                    rows[-1][channel+2] = "10"
                with tempfile.TemporaryDirectory() as temporary:
                    changed = Path(temporary)/"trace.csv"
                    with changed.open("w", newline="") as stream:csv.writer(stream).writerows(rows)
                    with self.subTest(name=name, mutation=mutation), self.assertRaises(EvidenceError):
                        audit_unassigned_burst(packet, changed, protocol)

    def test_valid_preceding_observation_is_not_a_recovery_rejection(self):
        checked = 0
        for name, _, _, protocol, selected, folder in self.cases:
            for row in selected["probes"][:-1]:
                checked += 1
                with self.subTest(name=name), self.assertRaises(EvidenceError):
                    audit_unassigned_burst(load(folder/row["packet"]), folder/row["trace"], protocol)
        self.assertGreater(checked, 0)


if __name__ == "__main__":unittest.main()
