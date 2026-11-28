"""Compare actual closed native Reset/preserve responses; no model calculation.

Adversarial mutations below exist only in memory, never in primary data.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import unittest

from ..native_evidence import EvidenceError
from ..recognition_metrics import load_physical_model_data_evaluation
from ..trial_response_comparison import (trial_response_comparison,
                                         trial_reset_intervention_comparison)


class TrialResetInterventionNativeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = Path(os.environ['TIMELEARNER_RESET_RESPONSE_SOURCE'])
        study = Path(os.environ['TIMELEARNER_RESET_RESPONSE_STUDY'])
        manifest = json.loads((source/'run-manifest.json').read_bytes())
        cls.model = json.loads((source/manifest['source_package_path']).read_bytes())
        _, cls.before = load_physical_model_data_evaluation(source/'native/evaluation.json')
        _, cls.after = load_physical_model_data_evaluation(study/'native/evaluation.json')
        if len(cls.before) != 8 or len(cls.after) != 8:
            raise ValueError('actual_reset_intervention_eight_trial_fixture_required')

    def test_actual_eight_trials_keep_intervention_separate_from_preservation(self):
        with trial_reset_intervention_comparison(self.model, physical_data=True) as compare:
            for index, (before, after) in enumerate(zip(self.before, self.after)):
                result = compare(before, after)
                self.assertEqual(before['reset_policy'], 'reset_per_trial')
                self.assertEqual(after['reset_policy'], 'reset_per_trial' if index == 0
                                 else 'preserve_neuron_dynamics')
                self.assertEqual(result['declared_condition_changes'], [] if index == 0
                                 else ['reset_policy'])
                self.assertFalse(result['causal_pattern_attribution_proven'])
                self.assertIsNone(result['scientific_verdict'])
                if index:
                    self.assertFalse(result['response_preserved'])
                    self.assertFalse(result['same_condition_response_preserved'])
                else:
                    # Same-order first trials both reset, an actual positive
                    # control before comparing changed reset policies.
                    self.assertTrue(result['same_condition_response_preserved'])

    def test_default_comparator_still_rejects_the_actual_changed_policy(self):
        with trial_response_comparison(self.model, physical_data=True) as compare:
            self.assertTrue(compare(self.before[0], self.after[0])['response_preserved'])
            with self.assertRaisesRegex(EvidenceError, 'condition_changed:reset_policy'):
                compare(self.before[1], self.after[1])

    def test_model_change_is_not_an_authorized_intervention(self):
        changed = deepcopy(self.after[1]); changed['model_before'] = '0'*64
        with trial_reset_intervention_comparison(self.model, physical_data=True) as compare:
            with self.assertRaises(EvidenceError):
                compare(self.before[1], changed)

    def test_sample_loss_cannot_be_hidden_by_the_intervention(self):
        changed = deepcopy(self.after[1]); changed['samples'].pop()
        with trial_reset_intervention_comparison(self.model, physical_data=True) as compare:
            with self.assertRaises(EvidenceError):
                compare(self.before[1], changed)

    def test_unknown_reset_policy_is_not_admitted(self):
        changed = deepcopy(self.after[1]); changed['reset_policy'] = 'unknown'
        with trial_reset_intervention_comparison(self.model, physical_data=True) as compare:
            with self.assertRaises(EvidenceError):
                compare(self.before[1], changed)

    def test_tolerance_cannot_be_relaxed_for_a_different_reset_policy(self):
        with self.assertRaisesRegex(EvidenceError, 'fixed_tolerance_required'):
            with trial_reset_intervention_comparison(self.model, physical_data=True,
                                                     absolute_tolerance=1e-3):
                self.fail('relaxed tolerance was admitted')
