"""Actual frozen native experiment; its classification quality is measured."""
import os
from pathlib import Path
import unittest

from ..frozen_diagnostic_order import run


class FrozenDiagnosticOrderNativeTest(unittest.TestCase):
    def test_same_order_platform_control_then_each_other_target_position(self):
        result = run(Path(os.environ['TIMELEARNER_FROZEN_ORDER_SOURCE'])/'run-manifest.json',
                     Path(os.environ['TIMELEARNER_FROZEN_ORDER_CONTROLS']))
        self.assertFalse(result['training_completed'])
        self.assertFalse(result['independent_evaluation'])
        self.assertEqual(result['independent_trainings'], 0)
        self.assertTrue(result['deterministic_order_probes'])
        self.assertIsNone(result['scientific_verdict'])
        self.assertLessEqual(result['baseline_maximum_sample_absolute_difference'],
                             result['baseline_sample_absolute_tolerance'])
        self.assertEqual([r['name'] for r in result['actual_results']], ['baseline', 'study'])
        rotations = [r for phase in result['actual_results'] for r in phase['rotations']]
        size = len(rotations)
        self.assertEqual({r['rotation'] for r in rotations}, set(range(size)))
        self.assertEqual({r['target_position'] for r in rotations}, set(range(size)))
        self.assertEqual(result['expected_trials'], size*size)
        for phase in result['actual_results']:
            metrics = phase['metrics']
            self.assertEqual(metrics['validity'], 'valid')
            self.assertEqual(metrics['model_revision'], result['model_revision'])
            self.assertEqual(metrics['effective_threshold'], result['threshold'])
            self.assertTrue(metrics['diagnostic_only'])
            self.assertFalse(metrics['training_completed'])
            self.assertIsNone(metrics['evaluation_verdict'])
        for rotation in rotations:
            self.assertEqual(len(rotation['trials']), size)
            self.assertEqual(rotation['counts']['TP']+rotation['counts']['FN'], 1)
            self.assertEqual(rotation['counts']['FP']+rotation['counts']['TN'], size-1)
        # TP/FP/FN/TN are actual observations; no desired scientific PASS is asserted.
