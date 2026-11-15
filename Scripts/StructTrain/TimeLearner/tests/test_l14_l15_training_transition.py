"""Recorded boundary of assigned-peak measurability; no new training runs."""
import os
from pathlib import Path
import unittest

from ..composite_training_temporal import render
from ..native_evidence import load
from ..plotting import plotting_runtime


class L14L15TrainingTransitionTest(unittest.TestCase):
    def test_actual_complete_L14_L15_L21_controls(self):
        plotting_runtime()
        from PIL import Image
        native = Path(os.environ['TIMELEARNER_L22_TRAIN_NATIVE']).resolve(strict=True)
        package = load(native/'train_stopped_state.json')
        self.assertEqual(package['model_revision'],
            '3b8a160f2fe6f5ace6aa377f5d42117bcc922bcdd746358ca8d7c34fc67a6b1c')
        groups, lengths, statuses = [44, 48, 60], [14, 15, 21], ['valid', 'ambiguous', 'ambiguous']
        for group, length, status in zip(groups, lengths, statuses):
            record = package['measurement_archive']['records'][group-1]
            self.assertTrue(record['complete_group'])
            self.assertEqual(record['logical_request']['input_id'], 'input0')
            parameters = record['window_proposal']['candidate']['parameters']
            self.assertEqual([p['length'] for p in parameters], [length, 1, 1, 1])
            self.assertTrue(all(p['resistance'] == 86000000 and p['synapses'] == 1 for p in parameters))
            self.assertEqual(record['selection']['geometry']['validity'], status)
            self.assertEqual(len(record['raw_trials']), 6)
        output = Path(os.environ['TMPDIR'])/'L14-L15-L21-training-controls'
        report = render(native, output, groups)
        self.assertEqual(report['package_audit']['training_outcome'], 'budget_exhausted')
        self.assertEqual([g['ordinal'] for g in report['groups']], groups)
        self.assertEqual([g['selection']['geometry']['validity'] for g in report['groups']], statuses)
        self.assertEqual(len(report['figures']), 24)
        self.assertFalse(report['downsampling'])
        self.assertFalse(report['training_certificate_eligible'])
        self.assertIsNone(report['scientific_verdict'])
        self.assertTrue(all(len(g['recorded_trials']) == 6 and
            all(t['complete'] and t['sample_count'] == 3601 for t in g['recorded_trials'])
            for g in report['groups']))
        for figure in report['figures']:
            with Image.open(output/figure['files'][0]) as image:
                self.assertGreaterEqual(image.width, 2800)
                self.assertGreaterEqual(image.height, 2800)
