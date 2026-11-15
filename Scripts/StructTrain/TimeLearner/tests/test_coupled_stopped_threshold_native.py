"""One declared Same-Matrix threshold, verified by actual native spikes."""
import os
from pathlib import Path
import unittest

from ..diagnostic_threshold_study import run


class CoupledStoppedThresholdNativeTest(unittest.TestCase):
    def test_actual_fixed_threshold_keeps_stopped_training_role(self):
        result=run(Path(os.environ['TIMELEARNER_COUPLED_MATRIX_RUN'])/'run-manifest.json',
                   Path(os.environ['TIMELEARNER_COUPLED_THRESHOLD_CONTROLS']))
        self.assertTrue(result['baseline_waveforms_equal'])
        self.assertFalse(result['training_completed'])
        self.assertFalse(result['calibrated'])
        self.assertFalse(result['independent_evaluation'])
        self.assertIsNone(result['scientific_verdict'])
        self.assertEqual([r['name'] for r in result['actual_results']],['baseline100','candidate'])
        self.assertEqual(len(result['proposal']['rows']),8)
        self.assertFalse(result['proposal']['classification_assessed'])
        for row in result['actual_results']:
            metrics=row['metrics']
            self.assertEqual(metrics['validity'],'valid')
            self.assertEqual(metrics['pooled_counts']['targets'],1)
            self.assertEqual(metrics['pooled_counts']['foils'],7)
            self.assertEqual(len(metrics['trials']),8)
            self.assertTrue(metrics['diagnostic_only'])
            self.assertFalse(metrics['training_completed'])
            self.assertIsNone(metrics['evaluation_verdict'])
        # No demanded positive target response, FP count, separability or margin.
