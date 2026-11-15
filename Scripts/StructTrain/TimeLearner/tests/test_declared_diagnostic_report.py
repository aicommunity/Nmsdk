"""Render and verify the explicitly declared closed diagnostic population."""
import os
from pathlib import Path
import unittest

from ..native_evidence import load, require
from ..recorded_diagnostic_matrix import report_matrix


class DeclaredDiagnosticReportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        primary = Path(os.environ['TIMELEARNER_RECORDED_MATRIX_PRIMARY'])
        controller = Path(os.environ['TIMELEARNER_RECORDED_MATRIX_CONTROLLER'])
        runtime = Path(os.environ['TIMELEARNER_RECORDED_MATRIX_RUNTIME'])/'runtime.json'
        cls.expected = load(Path(os.environ['TIMELEARNER_RECORDED_MATRIX_EXPECTATIONS'])/'expected.json')
        require(set(cls.expected) == {'kind', 'schema_version', 'models'} and
                cls.expected['kind'] == 'timelearner_declared_diagnostic_report' and
                type(cls.expected['schema_version']) is int and cls.expected['schema_version'] == 1 and
                type(cls.expected['models']) is dict and cls.expected['models'],
                'declared_diagnostic_report_schema')
        request = load(controller/'request.json')
        require(set(cls.expected['models']) == {row['name'] for row in request['cases']},
                'declared_diagnostic_report_population')
        for row in cls.expected['models'].values():
            require(set(row) == {'model_revision', 'training_outcome', 'threshold', 'somas'} and
                    type(row['somas']) is int and row['somas'] > 0,
                    'declared_diagnostic_report_model')
        cls.output = Path(os.environ['TMPDIR'])/'declared-diagnostic-gallery'
        cls.result = report_matrix(primary, controller, runtime, cls.output)

    def test_complete_declared_population_retains_actual_stopped_state_and_fixed_threshold(self):
        analysis = self.result['analysis'];expected = self.expected['models']
        self.assertEqual(analysis['trials'], 8*len(expected))
        self.assertTrue(analysis['diagnostic_only']);self.assertFalse(analysis['training_completed'])
        self.assertIsNone(analysis['scientific_verdict'])
        rows = {row['name']: row for row in analysis['models']}
        self.assertEqual(set(rows), set(expected))
        for name, fact in expected.items():
            row = rows[name]
            self.assertEqual(row['source_model_revision'], fact['model_revision'])
            self.assertEqual(row['training_outcome'], fact['training_outcome'])
            self.assertEqual(row['source_threshold'], fact['threshold'])
            self.assertEqual(row['trial_count'], 8)
            self.assertEqual(row['metrics']['invalid_trial_ids'], [])
            self.assertEqual(row['metrics']['pooled_counts']['targets'], 1)
            self.assertEqual(row['metrics']['pooled_counts']['foils'], 7)
            self.assertIsNone(row['metrics']['evaluation_verdict'])

    def test_every_declared_trial_soma_pair_has_full_scale_and_resolved_zoom_views(self):
        from PIL import Image
        for name, fact in self.expected['models'].items():
            root = self.output/name/'evaluation';manifest = load(root/'manifest.json')
            expected = 8*fact['somas']
            self.assertEqual(manifest['expected_trial_soma_pairs'], expected)
            self.assertEqual(manifest['observed_trial_soma_pairs'], expected)
            self.assertEqual(len(manifest['figures']), expected)
            self.assertEqual(manifest['missing_observation_ids'], [])
            self.assertFalse(manifest['visual_acceptance_complete'])
            for figure in manifest['figures']:
                views = figure['views']
                self.assertTrue(any(view['time_view'] == 'overview' for view in views))
                self.assertTrue(any(view['time_view'] != 'overview' and
                    view['minimum_native_tick_pixels_on_zoom'] >= 8 for view in views))
                for view in views:
                    self.assertFalse(view['downsampling'])
                    self.assertGreater(view['end'], view['begin'])
                    self.assertEqual(len(view['files']), 3)
                    with Image.open(root/view['files'][0]) as image:
                        self.assertEqual(image.size, (1920, 960))
