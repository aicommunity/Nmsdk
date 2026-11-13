"""Actual fixed threshold experiment; no demanded optimistic spike outcome."""
import os
from pathlib import Path
import unittest

from ..diagnostic_threshold_study import run


class DiagnosticThresholdStudyNativeTest(unittest.TestCase):
    def test_actual_baseline_replay_then_fixed_same_matrix_candidate(self):
        result = run(Path(os.environ['TIMELEARNER_THRESHOLD_SOURCE_RUN'])/'run-manifest.json',
                     Path(os.environ['TIMELEARNER_THRESHOLD_CONTROLS']))
        self.assertTrue(result['baseline_waveforms_equal'])
        self.assertFalse(result['training_completed'])
        self.assertFalse(result['calibrated'])
        self.assertFalse(result['independent_evaluation'])
        self.assertIsNone(result['scientific_verdict'])
        self.assertEqual([r['name'] for r in result['actual_results']], ['baseline100', 'candidate'])
        self.assertEqual(len(result['proposal']['rows']), 8)
        self.assertLess(result['proposal']['full_matrix_peak_margin'], 0)
        self.assertFalse(result['proposal']['classification_assessed'])
        for row in result['actual_results']:
            metrics = row['metrics']
            self.assertEqual(metrics['validity'], 'valid')
            self.assertEqual(metrics['pooled_counts']['targets'], 1)
            self.assertEqual(metrics['pooled_counts']['foils'], 7)
            self.assertEqual(len(metrics['trials']), 8)
            self.assertTrue(metrics['diagnostic_only'])
            self.assertFalse(metrics['training_completed'])
            self.assertIsNone(metrics['evaluation_verdict'])
        # Counts are actual measurements. In particular, the nonspiking proxy
        # is not asserted as the outcome of the real spiking candidate.
