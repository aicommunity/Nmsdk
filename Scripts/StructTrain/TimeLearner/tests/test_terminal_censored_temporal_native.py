"""Actual L22 Train cutoff remains visible without becoming a complete group."""
import os
from pathlib import Path
import unittest

from ..composite_training_temporal import render
from ..native_evidence import EvidenceError, load


class TerminalCensoredTemporalNativeTest(unittest.TestCase):
    def test_actual_l22_cutoff_is_labeled_and_missing_trials_are_not_filled(self):
        from PIL import Image
        native = Path(os.environ['TIMELEARNER_L22_TRAIN_NATIVE']).resolve(strict=True)
        package = load(native/'train_stopped_state.json')
        self.assertEqual(package['model_revision'],
            '3b8a160f2fe6f5ace6aa377f5d42117bcc922bcdd746358ca8d7c34fc67a6b1c')
        record = package['measurement_archive']['records'][61]
        self.assertEqual(record['logical_request']['base_model_revision'], package['model_revision'])
        self.assertFalse(record['complete_group'])
        output = Path(os.environ['TMPDIR'])/'L22-terminal-censored-temporal'
        with self.assertRaisesRegex(EvidenceError, 'training_report_group_incomplete'):
            render(native, output, [62])
        self.assertFalse(output.exists())
        report = render(native, output, [62], allow_incomplete_groups=True)
        self.assertEqual(report['schema_version'], 3)
        group = report['groups'][0]
        self.assertIsNone(group['selection'])
        self.assertFalse(group['complete_group'])
        self.assertEqual([r['complete'] for r in group['recorded_trials']], [True, True, False])
        self.assertEqual([r['sample_count'] for r in group['recorded_trials']], [3601, 3601, 415])
        self.assertEqual(group['recorded_trials'][-1]['end_reason'], 'native_training_time_budget_exhausted')
        self.assertTrue(report['missing_trials_not_synthesized'])
        self.assertFalse(report['training_certificate_eligible'])
        self.assertFalse(report['visual_acceptance_complete'])
        self.assertIsNone(report['scientific_verdict'])
        self.assertFalse(report['downsampling'])
        self.assertEqual({f['channel'] for f in report['figures']}, {0, 1, 2, 3})
        for figure in report['figures']:
            for filename in figure['files']:
                self.assertGreater((output/filename).stat().st_size, 100)
            with Image.open(output/figure['files'][0]) as image:
                self.assertGreaterEqual(image.width, 2800)
                self.assertGreaterEqual(image.height, 1400)
