"""Real archived native jobs: common diagnostic renderer, without a made-up run manifest."""
import os
from pathlib import Path
import unittest

from ..native_evidence import load, require
from ..recognition_metrics import load_diagnostic_evaluation
from ..reports import render_diagnostic_evaluation_case


class ArchivedNativeDiagnosticReportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.primary = Path(os.environ['TIMELEARNER_ARCHIVED_NATIVE_DIAGNOSTIC'])
        expected = load(Path(os.environ['TIMELEARNER_ARCHIVED_NATIVE_EXPECTATIONS'])/'expected.json')
        require(set(expected) == {'kind', 'schema_version', 'cases'} and
                expected['kind'] == 'timelearner_archived_native_diagnostic_report' and
                expected['schema_version'] == 1 and type(expected['cases']) is list and expected['cases'],
                'archived_native_report_expectations')
        cls.expected = expected['cases']
        cls.output = Path(os.environ['TMPDIR'])/'archived-native-diagnostic-gallery'
        cls.output.mkdir(exist_ok=False)
        cls.results = {}
        for row in cls.expected:
            require(set(row) == {'name', 'native_directory', 'model_revision', 'threshold', 'counts', 'trials', 'somas'} and
                    type(row['name']) is str and row['name'].isalnum() and row['name'] not in cls.results,
                    'archived_native_report_case')
            relative = Path(row['native_directory'])
            require(not relative.is_absolute() and '..' not in relative.parts, 'archived_native_report_path')
            native = cls.primary/relative
            package = load(native/'model.json')
            require(package['model_revision'] == row['model_revision'], 'archived_native_report_revision')
            recognition = package['source_recognition'] if package['kind'] == 'timelearner_diagnostic_threshold_candidate' else package
            require(recognition['kind'] == 'timelearner_diagnostic_recognition_state', 'archived_native_report_source_kind')
            source = recognition['source_solo']
            # Schema7 carries the complete training primary internally. This
            # case does not invent a missing summary, trace path or run manifest.
            require(source['kind'] == 'timelearner_stopped_state' and source['schema_version'] == 7 and
                    source['certificate'] is None, 'archived_native_report_requires_embedded_stopped_primary')
            spec, observations = load_diagnostic_evaluation(native/'evaluation.json')
            require(spec['model_revision'] == row['model_revision'] and len(observations) == row['trials'] and
                    all(o['complete'] and o['valid'] and not o['censored'] and len(o['samples']) == 4001
                        for o in observations), 'archived_native_report_complete_population')
            cls.results[row['name']] = render_diagnostic_evaluation_case(
                native/'evaluation.json', native/'model.json', (source, None, {}, {}), cls.output/row['name'])
            # The renderer reruns the common source audit/scorer; observed
            # classifications below come from that result, not its pixels.
            del package, recognition, source, observations
        links = ''.join('<li><a href="'+r['name']+'/index.html">'+r['name']+'</a></li>' for r in cls.expected)
        (cls.output/'index.html').write_text(
            '<!doctype html><meta charset="utf-8"><title>Archived native diagnostic responses</title>'
            '<h1>Actual native baseline and fixed-threshold responses</h1>'
            '<p>Stopped training, no convergence certificate. Native input overlays and readable zoom views. '
            'Same-Matrix diagnostic; visual review is separate.</p><ul>'+links+'</ul>\n', encoding='utf-8')

    def test_common_scorer_preserves_declared_counts_and_diagnostic_role(self):
        for row in self.expected:
            root = self.output/row['name']
            result = self.results[row['name']]
            analysis = load(root/'analysis.json')
            self.assertTrue(result['diagnostic_only'])
            self.assertFalse(result['training_completed'])
            self.assertEqual(analysis['validity'], 'valid')
            self.assertEqual(analysis['effective_threshold'], row['threshold'])
            for key in ('TP', 'FP', 'FN', 'TN'):
                self.assertEqual(analysis['pooled_counts'][key], row['counts'][key])
            self.assertIsNone(analysis['evaluation_verdict'])

    def test_all_patterns_and_somas_keep_actual_inputs_full_window_and_native_zoom(self):
        from PIL import Image
        for row in self.expected:
            root = self.output/row['name']
            manifest = load(root/'manifest.json')
            pairs = row['trials']*row['somas']
            self.assertEqual(manifest['expected_trial_soma_pairs'], pairs)
            self.assertEqual(manifest['observed_trial_soma_pairs'], pairs)
            self.assertEqual(len(manifest['figures']), pairs)
            self.assertEqual(manifest['missing_observation_ids'], [])
            self.assertFalse(manifest['visual_acceptance_complete'])
            for figure in manifest['figures']:
                views = figure['views']
                self.assertTrue(any(v['time_view'] == 'overview' for v in views))
                self.assertTrue(any(v['time_view'] != 'overview' and
                                    v['minimum_native_tick_pixels_on_zoom'] >= 8 for v in views))
                for view in views:
                    self.assertFalse(view['downsampling'])
                    self.assertEqual(len(view['files']), 3)
                    self.assertGreater(view['end'], view['begin'])
                    with Image.open(root/view['files'][0]) as picture:
                        self.assertEqual(picture.size, (1920, 960))
            self.assertTrue(manifest['lt_decision_views']['all_declared_trials_rendered'])
