"""Actual measured Rs endpoints on one Branch geometry; never rerun Train."""
import os
from pathlib import Path
import unittest

from ..composite_training_temporal import render
from ..native_calibration_worker import _write
from ..native_evidence import load
from ..plotting import plotting_runtime
from ..training_search_report import analyze_search_history


class N1LocalTurnScientificReportTest(unittest.TestCase):
    def test_actual_opposite_amplitude_errors_keep_fresh_assigned_impulse_evidence(self):
        plotting_runtime()
        from PIL import Image

        run = Path(os.environ['TIMELEARNER_N1_LOCAL_TURN_RUN']).resolve(strict=True)
        analysis = analyze_search_history(run/'run-manifest.json')
        self.assertEqual(analysis['topology'], 'Branch')
        self.assertEqual(analysis['outcome'], 'budget_exhausted')
        self.assertIsNone(analysis['training_or_final_verification_verdict'])
        execution = load(run/'native/execution.json')
        package = load(run/'native'/execution['package_path'])
        self.assertEqual(package['configuration']['search']['tolerances'],
                         dict(amplitude_absolute=1e-5, amplitude_relative=0., sync=.02))
        pair = [c for c in analysis['recorded_candidate_measurements']
            if c['input_index'] == 2 and [p['length'] for p in c['full_parameters']] == [26, 26, 25, 1]]
        self.assertEqual(len(pair), 2)
        pair.sort(key=lambda c: c['parameters']['resistance'])
        low, high = pair
        self.assertLess(low['parameters']['resistance'], high['parameters']['resistance'])
        self.assertGreater(low['amplitude_residual'], 0.)
        self.assertLess(high['amplitude_residual'], 0.)
        for c in pair:
            self.assertTrue(c['within_timing'])
            self.assertFalse(c['within_amplitude'])
        self.assertNotEqual(low['model_revision'], high['model_revision'])
        self.assertNotEqual(low['anchor_group_id'], high['anchor_group_id'])
        self.assertNotEqual(low['measurement_group_id'], high['measurement_group_id'])
        records = package['measurement_archive']['records']
        ids = {c['measurement_group_id'] for c in pair}
        selected = [i for i, r in enumerate(records, 1) if r['group_id'] in ids]
        self.assertEqual(len(selected), 2)
        output = Path(os.environ['TMPDIR'])/'N1-local-turn-amplitude-interval-report'
        report = render(run/'native', output, selected)
        self.assertFalse(report['downsampling'])
        self.assertFalse(report['training_certificate_eligible'])
        self.assertIsNone(report['scientific_verdict'])
        for group in report['groups']:
            self.assertTrue(group['complete_group'])
            self.assertEqual(len(group['recorded_trials']), 6)
            self.assertTrue(all(t['complete'] and t['sample_count'] == 3601
                                for t in group['recorded_trials']))
        for figure in report['figures']:
            with Image.open(output/figure['files'][0]) as image:
                self.assertGreaterEqual(image.width, 2800)
                self.assertGreaterEqual(image.height, 2800)
        _write(output/'selected-pair.json', dict(kind='actual_measured_n1_amplitude_interval',
            schema_version=1, candidates=pair, selected_groups=selected,
            bracket_is_not_convergence=True, classification_assessed=False,
            new_model_execution=False, scientific_verdict=None))
