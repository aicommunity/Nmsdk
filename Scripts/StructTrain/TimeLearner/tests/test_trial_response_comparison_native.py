"""Regression checks on closed native DATA responses, with explicit mutations.

The mutations below are adversarial in-memory fixtures, never experiment data.
The complete actual 56-trial scientific comparison is a separate derived audit.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import unittest

from ..frozen_diagnostic_order import compare_samples
from ..frozen_physical_order_audit import audit_closed_order
from ..native_evidence import EvidenceError, after
from ..trial_response_comparison import compare_trial_responses


class TrialResponseComparisonNativeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = Path(os.environ['TIMELEARNER_RESPONSE_SOURCE'])
        study = Path(os.environ['TIMELEARNER_RESPONSE_STUDY'])
        cls.model = json.loads((source/'input/job.json').read_bytes())['source_model_data']
        originals = {o['sample_id']: o for p in (source/'native').glob('trial-*.json')
                     for o in [json.loads(p.read_bytes())]}
        cls.observed = json.loads((study/'run/native/trial-0.json').read_bytes())
        cls.expected = originals[cls.observed['sample_id']]
        cls.spiking = next(o for p in (source/'native').glob('trial-*.json')
                           for o in [json.loads(p.read_bytes())] if o['spike_count'])

    def compare(self, left=None, right=None):
        return compare_trial_responses(self.expected if left is None else left,
            self.observed if right is None else right, self.model, physical_data=True)

    def test_actual_changed_position_has_same_response_on_stimulus_clock(self):
        self.assertNotEqual(self.expected['begin'], self.observed['begin'])
        with self.assertRaises(EvidenceError):
            compare_samples(self.expected['samples'], self.observed['samples'], 1e-12)
        result = self.compare()
        self.assertTrue(result['response_preserved'])
        self.assertEqual(result['maximum_absolute_signal_difference'], 0.)
        self.assertEqual(result['time_basis'], 'actual_stimulus_onset')

    def test_same_observation_has_exact_zero_difference(self):
        result = self.compare(self.expected, self.expected)
        self.assertTrue(result['response_preserved'])
        self.assertEqual(result['maximum_absolute_sample_difference'], 0.)

    def test_small_physical_signal_change_is_not_hidden_by_clock_alignment(self):
        changed = deepcopy(self.observed)
        changed['samples'][100]['soma'][0] += 1e-4
        result = self.compare(right=changed)
        self.assertFalse(result['response_preserved'])
        self.assertIn('response_signal_changed', result['difference_reasons'])
        self.assertGreater(result['maximum_absolute_signal_difference'], 1e-5)

    def test_delayed_stimulus_onset_does_not_hide_window_offset_change(self):
        changed = deepcopy(self.observed)
        dt = 1/changed['frequency_hz']
        old = set(changed['stimulus_times'])
        changed['stimulus_times'] = [t+dt for t in changed['stimulus_times']]
        changed['stimulus_onset'] += dt
        for sample in changed['samples']:
            sample['stimulus_history'] = [v for t in sample['stimulus_history']
                for v in [t+dt if t in old else t] if not after(v, sample['time'])]
        result = self.compare(right=changed)
        self.assertFalse(result['response_preserved'])
        self.assertFalse(result['window_offsets_equal'])

    def test_shorter_closed_window_cannot_be_compared_as_full_response(self):
        changed = deepcopy(self.observed)
        changed['samples'].pop()
        changed['end'] = changed['closed_at'] = changed['samples'][-1]['time']
        result = self.compare(right=changed)
        self.assertFalse(result['response_preserved'])
        self.assertFalse(result['sample_counts_equal'])
        self.assertFalse(result['window_offsets_equal'])

    def test_actual_spike_timing_change_is_detected(self):
        changed = deepcopy(self.spiking)
        dt = 1/changed['frequency_hz']
        old = set(changed['spike_times'])
        changed['spike_times'] = [t+dt for t in changed['spike_times']]
        changed['relative_spike_times'] = [t+dt for t in changed['relative_spike_times']]
        for sample in changed['samples']:
            sample['spike_history'] = [v for t in sample['spike_history']
                for v in [t+dt if t in old else t] if not after(v, sample['time'])]
        result = self.compare(self.spiking, changed)
        self.assertFalse(result['response_preserved'])
        self.assertFalse(result['stimulus_and_spike_events_equal'])

    def test_nonfinite_and_unknown_sample_fields_are_invalid(self):
        for key, value in (('lt_output', float('nan')), ('unknown_channel', 0.)):
            with self.subTest(key=key):
                changed = deepcopy(self.observed)
                changed['samples'][100][key] = value
                with self.assertRaises(EvidenceError):
                    self.compare(right=changed)

    def test_unknown_schema_and_incomplete_observation_are_invalid(self):
        changed = deepcopy(self.observed)
        changed['schema_version'] = 999
        with self.assertRaises(EvidenceError):
            self.compare(right=changed)
        changed = deepcopy(self.observed)
        changed.update(complete=False, censored=True, valid=False, reason='interrupted')
        with self.assertRaises(EvidenceError):
            self.compare(right=changed)

    def test_tolerance_cannot_be_relaxed(self):
        with self.assertRaises(EvidenceError):
            compare_trial_responses(self.expected, self.observed, self.model,
                physical_data=True, absolute_tolerance=1e-3)

    def test_full_closed_corpus_production_reanalysis(self):
        result = audit_closed_order(Path(os.environ['TIMELEARNER_RESPONSE_CONTROLS']),
            Path(os.environ['TMPDIR'])/'closed-order-stimulus-relative-reanalysis.json')
        self.assertEqual(result['source_control_trials'], 8)
        self.assertEqual(result['new_study_trials'], 56)
        self.assertEqual(len(result['rows']), 56)
        self.assertTrue(result['all_input_bytes_unchanged'])
        self.assertTrue(result['all_eight_target_positions_observed'])
        self.assertTrue(result['classifications_preserved'])
        self.assertFalse(result['native_rerun_performed'])
        self.assertFalse(result['training_completed'])
        self.assertIsNone(result['scientific_verdict'])
        # Response preservation is a measured result, not a desired PASS.
