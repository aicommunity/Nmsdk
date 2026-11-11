"""Corrupt actual C++ service artifacts, not a second copy of the recorder."""
import copy
import csv
import os
import re
import tempfile
import unittest
from pathlib import Path

from Scripts.StructTrain.TimeLearner.native_evidence import (
    EvidenceError, audit_probe, audit_training_summary, load,
)
from Scripts.StructTrain.TimeLearner.learned_evidence import audit_learned_state, load_case


class NativeEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_NATIVE_EVIDENCE_DIR")
        if not directory:
            raise unittest.SkipTest("requires actual native service output")
        cls.directory = Path(directory)
        paths = [p for p in cls.directory.glob("*_service_*.json")
                 if re.search(r"_service_\d+\.json$", p.name)]
        if not paths:
            raise RuntimeError("missing actual C++ probe evidence")
        cls.paths = sorted(paths)
        cls.path = cls.paths[0]
        cls.packet = load(cls.path)
        cls.packets = {}
        cls.audits = []
        for path in cls.paths:
            packet = load(path)
            cls.audits.append(audit_probe(packet, path.with_suffix(".csv")))
            trial = packet["observation"]["specification"]["trial_id"]
            if trial in cls.packets:
                raise RuntimeError("duplicate native trial ID")
            cls.packets[trial] = packet
        summary_paths = sorted(cls.directory.glob("*_training_summary.json"))
        required = {f"{topology}_2000_N{normalization}_automatic_service_training_summary.json"
                    for topology in ("Classic", "Branch") for normalization in (0, 1)}
        if not required.issubset({p.name for p in summary_paths}):
            raise RuntimeError("requires every Classic/Branch x N0/N1 automatic-service summary")
        # A full run also contains cold-start and configured-service controls.
        # Audit every supplied summary instead of rejecting those extra cases.
        cls.summaries = [load(p) for p in summary_paths]
        cls.diagnostics = [s for s in cls.summaries if s['certificate'] is None]
        if len(cls.diagnostics) < 4:
            raise RuntimeError('requires actual diagnostic automatic-service outcomes')
        # Certificate mutation tests must start from a real completed package,
        # not a certificate invented for an exhausted diagnostic service run.
        cls.certified_cases = [load_case(p) for p in sorted(cls.directory.glob('*_learned_state.json'))
                               if load(p)['kind'] == 'timelearner_completed_state' and load(p)['certificate'] is not None]
        if not cls.certified_cases:
            raise RuntimeError('requires completed native model packages and their primary traces')
        for case in cls.certified_cases:
            result = audit_learned_state(*case)
            if not result['certificate_consistent'] or result['evaluation_verdict'] is not None:
                raise RuntimeError('completed package does not provide an auditable training certificate')

    def test_actual_native_traces(self):
        for result in self.audits:
            self.assertTrue(result["valid_observation"])
            self.assertIsNone(result["evaluation_verdict"])

    def test_actual_diagnostic_training_has_no_certificate(self):
        for summary in self.summaries:
            result = audit_training_summary(summary, self.packets, "pulse0", require_certificate=False)
            self.assertEqual(result['certificate_consistent'], summary['certificate'] is not None)
            if summary['certificate'] is None:
                self.assertEqual(summary['model_state_kind'], 'diagnostic')
                self.assertIsNone(result['exact'])
            self.assertIsNone(result["evaluation_verdict"])

    def test_default_gate_rejects_diagnostics_without_certificates(self):
        for summary in self.diagnostics:
            with self.assertRaises(EvidenceError):
                audit_training_summary(summary, self.packets, 'pulse0')

    def test_diagnostic_analysis_cannot_claim_exact(self):
        for original in self.diagnostics:
            summary = copy.deepcopy(original);summary['outcome'] = 'exact'
            with self.assertRaisesRegex(EvidenceError, '^missing_or_unknown_certificate$'):
                audit_training_summary(summary, self.packets, 'pulse0', require_certificate=False)

    def test_actual_completed_model_certificates_are_recomputed(self):
        for package, summary, packets, _ in self.certified_cases:
            result = audit_training_summary(summary, packets, 'pulse0')
            self.assertTrue(result['certificate_consistent'])
            self.assertEqual(result['exact'], package['certificate']['exact'])
            self.assertIsNone(result['evaluation_verdict'])

    def test_unknown_schema(self):
        packet = copy.deepcopy(self.packet)
        packet["evidence_schema_version"] = 999
        with self.assertRaises(EvidenceError):
            audit_probe(packet, self.path.with_suffix(".csv"))

    def test_duplicate_stimulus_id(self):
        packet = copy.deepcopy(self.packet)
        packet["observation"]["stimuli"][1]["id"] = packet["observation"]["stimuli"][0]["id"]
        with self.assertRaises(EvidenceError):
            audit_probe(packet, self.path.with_suffix(".csv"))

    def test_unknown_spikes_cannot_become_zero(self):
        packet = copy.deepcopy(self.packet)
        packet["observation"]["spike_count"] = 0
        with self.assertRaises(EvidenceError):
            audit_probe(packet, self.path.with_suffix(".csv"))

    def test_incomplete_observation_is_not_valid(self):
        packet = copy.deepcopy(self.packet)
        packet["observation"]["complete"] = False
        result = audit_probe(packet, self.path.with_suffix(".csv"))
        self.assertFalse(result["valid_observation"])
        self.assertEqual(result["reason"], "incomplete_observation")

    def test_corrupted_peak_is_not_silently_accepted(self):
        packet = copy.deepcopy(self.packet)
        packet["observation"]["peaks"][0]["raw_potential"] += .01
        with self.assertRaises(EvidenceError):
            audit_probe(packet, self.path.with_suffix(".csv"))

    def test_isolated_window_cannot_select_one_of_multiple_waves(self):
        packet = copy.deepcopy(self.packet)
        spec = packet["observation"]["specification"]
        self.assertGreater(len(spec["expected_stimulus_ids"]), 1,
                           "this corruption control requires a real multi-wave burst")
        spec["windows"][0]["begin"] = spec["begin"]
        spec["windows"][0]["end"] = spec["end"]
        requested = packet["requested_specification"]
        # The source may already use assigned selection and a whole-burst
        # window. Explicitly test isolated semantics rather than a no-op edit.
        if packet["evidence_schema_version"] == 2:
            spec["peak_selection"] = requested["peak_selection"] = "isolated_window"
        requested["windows"][0]["begin"] = 0
        requested["windows"][0]["end"] = requested["end"]
        with self.assertRaises(EvidenceError):
            audit_probe(packet, self.path.with_suffix(".csv"))

    def test_nonfinite_and_damaged_csv_tokens(self):
        with self.path.with_suffix(".csv").open(newline="") as stream:
            original = list(csv.reader(stream))
        for token in ("nan", "inf", "damaged-number"):
            rows = copy.deepcopy(original)
            rows[2][2] = token
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "trace.csv"
                with path.open("w", newline="") as stream:
                    csv.writer(stream).writerows(rows)
                with self.assertRaises(EvidenceError):
                    audit_probe(self.packet, path)

    def test_duplicate_trace_timestamp(self):
        with self.path.with_suffix(".csv").open(newline="") as stream:
            rows = list(csv.reader(stream))
        rows[2][0] = rows[1][0]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trace.csv"
            with path.open("w", newline="") as stream:
                csv.writer(stream).writerows(rows)
            with self.assertRaises(EvidenceError):
                audit_probe(self.packet, path)

    def test_certificate_exact_is_recomputed_from_actual_trials(self):
        for _, original, packets, _ in self.certified_cases:
            summary = copy.deepcopy(original)
            summary['certificate']['exact'] = not original['certificate']['exact']
            with self.assertRaises(EvidenceError):
                audit_training_summary(summary, packets, 'pulse0')

    def test_reference_label_is_not_row_position(self):
        _, original, packets, _ = self.certified_cases[0]
        summary = copy.deepcopy(original)
        summary["references"].reverse()
        summary["certificate"]["residuals"].reverse()
        self.assertEqual(audit_training_summary(summary, packets, 'pulse0')['exact'], original['certificate']['exact'])

    def test_missing_final_trial(self):
        _, summary, source, _ = self.certified_cases[0]
        packets = dict(source)
        trial = summary["certificate"]["residuals"][0]["trial_id"]
        del packets[trial]
        with self.assertRaises(EvidenceError):
            audit_training_summary(summary, packets, "pulse0")

    def test_peak_selection_is_part_of_the_training_protocol(self):
        _, summary, source, _ = self.certified_cases[0]
        packets = copy.deepcopy(source)
        trial = summary["certificate"]["residuals"][0]["trial_id"]
        specification = packets[trial]["observation"]["specification"]
        original = specification["peak_selection"]
        specification["peak_selection"] = ("isolated_window" if original == "assigned_burst_wave"
                                             else "assigned_burst_wave")
        self.assertNotEqual(specification["peak_selection"], original)
        with self.assertRaises(EvidenceError):
            audit_training_summary(summary, packets, "pulse0")


class AssignedNativeEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_ASSIGNED_EVIDENCE_DIR")
        if not directory:
            raise unittest.SkipTest("requires actual assigned-window C++ output")
        cls.paths = sorted(Path(directory).glob("*assigned_window*_evidence.json"))
        if len(cls.paths) != 4:
            raise RuntimeError("requires Classic/Branch isolated and assigned native output")

    def test_actual_policies_have_different_measurement_validity(self):
        for path in self.paths:
            packet = load(path)
            trace = Path(str(path).replace("_evidence.json", ".csv"))
            result = audit_probe(packet, trace)
            assigned = packet["observation"]["specification"]["peak_selection"] == "assigned_burst_wave"
            self.assertEqual(result["valid_observation"], assigned)
            self.assertEqual(result["trace_checked"], assigned)
            self.assertIsNone(result["evaluation_verdict"])

    def test_policy_cannot_be_injected_into_legacy_envelope(self):
        path = next(p for p in self.paths if load(p)["observation"]["valid"])
        packet = load(path)
        packet["evidence_schema_version"] = 1
        with self.assertRaises(EvidenceError):
            audit_probe(packet, Path(str(path).replace("_evidence.json", ".csv")))

    def test_assigned_policy_still_requires_neighbour_samples(self):
        path = next(p for p in self.paths if load(p)["observation"]["valid"])
        packet = load(path)
        spec = packet["observation"]["specification"]
        peak = packet["observation"]["peaks"][0]
        # Strictly smaller than peak.time, yet later than the previous sample.
        begin = peak["time"] - spec["maximum_sample_gap"] / 2
        spec["windows"][0]["begin"] = begin
        packet["requested_specification"]["windows"][0]["begin"] = begin - spec["begin"]
        with self.assertRaises(EvidenceError):
            audit_probe(packet, Path(str(path).replace("_evidence.json", ".csv")))

    def test_unknown_or_changed_policy_is_rejected(self):
        path = next(p for p in self.paths if load(p)["observation"]["valid"])
        for value in ("unknown", "isolated_window"):
            packet = load(path)
            packet["observation"]["specification"]["peak_selection"] = value
            with self.assertRaises(EvidenceError):
                audit_probe(packet, Path(str(path).replace("_evidence.json", ".csv")))


if __name__ == "__main__":
    unittest.main()
