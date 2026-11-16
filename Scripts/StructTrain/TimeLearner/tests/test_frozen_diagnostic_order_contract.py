"""Order and complete-sample comparator regressions; no synthetic neuron."""
from copy import deepcopy
import math
import unittest

from ..frozen_diagnostic_order import compare_samples, rotated_trials
from ..native_evidence import EvidenceError


class FrozenDiagnosticOrderContractTest(unittest.TestCase):
    def patterns(self):
        return [dict(sample_id=f'sample-{i}', label='target' if i == 0 else 'foil',
                     reset_policy='reset_per_trial', record_threshold_potential=True,
                     pattern_isi=[.01, .08+i*.01], duration=2., maximum_samples=4005,
                     pattern_hash=str(i), run_id='prior', trial_id=f'prior-{i}')
                for i in range(8)]

    def test_all_target_positions_preserve_stimuli_and_full_windows(self):
        original = self.patterns();before = deepcopy(original)
        trials = rotated_trials(original, 'frozen-order', list(range(8)))
        self.assertEqual(len(trials), 64)
        self.assertEqual(len({t['trial_id'] for t in trials}), 64)
        self.assertEqual(original, before)
        positions = set()
        for rotation in range(8):
            group = trials[rotation*8:(rotation+1)*8]
            self.assertEqual([t['sample_id'] for t in group],
                             [t['sample_id'] for t in original[rotation:]+original[:rotation]])
            positions.add(next(i for i, t in enumerate(group) if t['label'] == 'target'))
            for trial in group:
                source = next(t for t in original if t['sample_id'] == trial['sample_id'])
                self.assertEqual({k: v for k, v in trial.items() if k not in ('trial_id', 'run_id')},
                                 {k: v for k, v in source.items() if k not in ('trial_id', 'run_id')})
        self.assertEqual(positions, set(range(8)))

    def test_duplicate_ambiguous_identity_and_continuous_modes_are_refused(self):
        for mutation in ('duplicate', 'labels', 'continuous', 'missing_lt'):
            patterns = self.patterns()
            if mutation == 'duplicate':patterns[1]['sample_id'] = patterns[0]['sample_id']
            elif mutation == 'labels':patterns[1]['label'] = 'target'
            elif mutation == 'continuous':patterns[1]['reset_policy'] = 'preserve_neuron_dynamics'
            else:patterns[1]['record_threshold_potential'] = False
            with self.assertRaises(EvidenceError):rotated_trials(patterns, 'new', [0])
        for rotations in ([], [1, 1], [True], [-1], [8]):
            with self.assertRaises(EvidenceError):rotated_trials(self.patterns(), 'new', rotations)

    def test_every_sample_and_channel_is_compared(self):
        samples = [dict(time=i*.0005, lt_potential=.05+i*.001,
                        soma=[dict(potential=.03+i*.002, valid=True)]) for i in range(40)]
        self.assertEqual(compare_samples(samples, deepcopy(samples), 1e-10), 0.)
        changed = deepcopy(samples);changed[17]['soma'][0]['potential'] += 1e-5
        with self.assertRaisesRegex(EvidenceError, 'waveform_changed'):
            compare_samples(samples, changed, 1e-10)
        with self.assertRaisesRegex(EvidenceError, 'sample_count_changed'):
            compare_samples(samples, samples[:-1], 1e-10)
        changed = deepcopy(samples);del changed[17]['lt_potential']
        with self.assertRaisesRegex(EvidenceError, 'sample_fields_changed'):
            compare_samples(samples, changed, 1e-10)

    def test_nonfinite_values_and_widened_tolerance_are_refused(self):
        for bad in (math.nan, math.inf, -math.inf):
            with self.assertRaises(EvidenceError):compare_samples([bad], [bad], 1e-10)
        for tolerance in (1e-5, -1e-10, math.nan):
            with self.assertRaises(EvidenceError):compare_samples([0.], [0.], tolerance)

    def test_explicit_platform_tolerance_keeps_native_samples(self):
        difference = compare_samples([0., .01], [0., .01+1e-12], 1e-10)
        self.assertGreater(difference, 0.)
        self.assertLess(difference, 1e-10)
        with self.assertRaises(EvidenceError):compare_samples([0.], [1e-12], 0.)
