"""Declared protocol invariants and the actual native fixed-model experiment."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..frozen_protocols import run, variant_trials
from ..native_evidence import EvidenceError


class FrozenProtocolContractTest(unittest.TestCase):
    def test_variants_preserve_all_stimulus_and_identity_data(self):
        source = [dict(sample_id='target', label='target'), dict(sample_id='foil', label='foil')]
        for i, row in enumerate(source):
            row.update(pattern_hash=str(i), pattern_isi=[.01,.08], duration=2.,
                reset_policy='reset_per_trial', record_threshold_potential=True,
                run_id='old', trial_id=str(i), maximum_samples=4005)
        before = deepcopy(source)
        changed = variant_trials(source, 'new', 4., 'preserve_neuron_dynamics')
        self.assertEqual(source, before)
        for old, new in zip(source, changed):
            self.assertEqual({k: v for k, v in old.items() if k not in
                ('run_id','trial_id','duration','maximum_samples','reset_policy')},
                {k: v for k, v in new.items() if k not in
                ('run_id','trial_id','duration','maximum_samples','reset_policy')})
        self.assertEqual([r['maximum_samples'] for r in changed], [8005,8005])
        for duration, policy in [(1.,'reset_per_trial'), (True,'reset_per_trial'),
                                  (float('nan'),'reset_per_trial'), (4.,'unknown')]:
            with self.subTest(duration=duration,policy=policy), self.assertRaises(EvidenceError):
                variant_trials(source,'bad',duration,policy)


class FrozenProtocolNativeTest(unittest.TestCase):
    def test_actual_frozen_full_windows_and_reset_policies(self):
        result=run(Path(os.environ['TIMELEARNER_FROZEN_PROTOCOL_SOURCE'])/'run-manifest.json',
                   Path(os.environ['TIMELEARNER_FROZEN_PROTOCOL_CONTROLS']))
        self.assertEqual([r['name'] for r in result['actual_results']],
            ['baseline','long-reset','continuous','long-continuous'])
        self.assertEqual(result['baseline_maximum_sample_absolute_difference'],0.)
        self.assertEqual(result['expected_trials'],32)
        self.assertFalse(result['isolated_iti_intervention'])
        self.assertFalse(result['training_completed'])
        self.assertFalse(result['independent_evaluation'])
        for row in result['actual_results']:
            self.assertEqual(len(row['metrics']['trials']),8)
            self.assertIsNone(row['metrics']['evaluation_verdict'])
        # Quality is a measured result, never a demanded positive outcome.
