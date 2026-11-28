"""Derived prefix comparisons on the actual complete historical M4 responses."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..frozen_fourth_pulse_analysis import compare_probe_prefix
from ..native_evidence import EvidenceError, after, load


class FourthProbePrefixTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = Path(os.environ['TIMELEARNER_FOURTH_PREFIX_SOURCE'])
        cls.model = load(source/'model.json')
        cls.reset = load(source/'r3-short-reset/expected/trial-5.json')
        cls.preserve = load(source/'r3-short-preserve/expected/trial-5.json')

    def compare(self, left, right):
        return compare_probe_prefix(left, right, self.model)

    def test_actual_complete_controls_keep_the_early_preserve_spike(self):
        for observation in (self.reset, self.preserve):
            result = self.compare(observation, observation)
            self.assertTrue(result['recorded_signal_and_event_prefix_preserved'])
            self.assertTrue(result['full_observations_retained'])
            self.assertAlmostEqual(result['cutoff_relative_seconds'], .48)
            self.assertFalse(result['classification_recomputed_from_prefix'])
        result = self.compare(self.preserve, self.preserve)
        self.assertEqual(len(result['observed_spikes_before_cutoff']), 1)
        self.assertAlmostEqual(result['observed_spikes_before_cutoff'][0], .242)

    def test_absolute_clock_translation_preserves_the_actual_prefix(self):
        shifted = deepcopy(self.preserve)
        for k in ('begin', 'end', 'closed_at', 'stimulus_onset'):
            shifted[k] += 64.
        for k in ('stimulus_times', 'spike_times'):
            shifted[k] = [t+64. for t in shifted[k]]
        # Derived fields must describe the translated binary64 clocks exactly;
        # retaining their old spelling can violate the native roundoff check.
        for absolute, relative in (('stimulus_times', 'relative_stimulus_times'),
                                   ('spike_times', 'relative_spike_times')):
            shifted[relative] = [t-shifted['stimulus_onset'] for t in shifted[absolute]]
        for sample in shifted['samples']:
            sample['time'] += 64.
            for k in ('stimulus_history', 'spike_history'):
                sample[k] = [t+64. for t in sample[k]]
        self.assertTrue(self.compare(self.preserve, shifted)
                        ['recorded_signal_and_event_prefix_preserved'])

    def test_incomplete_trial_cannot_be_relabelled_as_a_valid_prefix(self):
        incomplete = deepcopy(self.reset)
        incomplete.update(complete=False, censored=True)
        with self.assertRaises(EvidenceError):
            self.compare(self.reset, incomplete)

    def test_a_changed_recorded_pre_fourth_signal_is_reported(self):
        changed = deepcopy(self.reset)
        sample = changed['samples'][20]
        self.assertLess(sample['time'], changed['stimulus_times'][3])
        sample['soma'][0] += 1e-7
        sample['lt_potential'] += 1e-7
        result = self.compare(self.reset, changed)
        self.assertFalse(result['recorded_signal_and_event_prefix_preserved'])
        self.assertIn('prefix_signals_changed', result['difference_reasons'])

    def test_a_later_signal_does_not_replace_the_pre_fourth_comparison(self):
        changed = deepcopy(self.reset)
        sample = next(s for s in changed['samples']
                      if after(s['time'], changed['stimulus_times'][3]+.02))
        sample['soma'][0] += 1e-7
        sample['lt_potential'] += 1e-7
        self.assertTrue(self.compare(self.reset, changed)
                        ['recorded_signal_and_event_prefix_preserved'])

    def test_reset_and_preserve_are_not_the_same_condition(self):
        with self.assertRaises(EvidenceError):
            self.compare(self.reset, self.preserve)
