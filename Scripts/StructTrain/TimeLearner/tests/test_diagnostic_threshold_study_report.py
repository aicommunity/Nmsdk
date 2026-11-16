"""Plot the actual fixed-threshold eight-pattern experiment, without reruns."""
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from ..reports import render_diagnostic_evaluation


class DiagnosticThresholdStudyReportTest(unittest.TestCase):
    def test_complete_candidate_matrix_has_all_somas_and_readable_native_ticks(self):
        from PIL import Image

        source = Path(os.environ['TIMELEARNER_THRESHOLD_COMPLETED_STUDY']).resolve(strict=True)
        result = load(source/'result.json')
        self.assertEqual(result['kind'], 'same_matrix_stopped_threshold_native_result')
        self.assertTrue(result['baseline_waveforms_equal'])
        self.assertFalse(result['training_completed'])
        self.assertFalse(result['calibrated'])
        self.assertFalse(result['independent_evaluation'])
        self.assertIsNone(result['scientific_verdict'])
        candidate = source/'runs/candidate'
        # The ordinary production diagnostic scorer runs inside this renderer.
        # Native spiking counts, rather than the nonspiking proxy, are retained.
        output = Path(os.environ['TMPDIR'])/'fixed-threshold-eight-pattern-gallery'
        rendered = render_diagnostic_evaluation(candidate/'native/evaluation.json',
            candidate/'native/model.json', candidate/'input/source/train_stopped_state.json', output)
        manifest = load(output/'manifest.json')
        metrics = load(output/'analysis.json')
        actual = next(r['metrics'] for r in result['actual_results'] if r['name'] == 'candidate')
        self.assertEqual(metrics, actual)
        self.assertEqual(metrics['effective_threshold'], result['proposal']['threshold'])
        self.assertTrue(metrics['diagnostic_threshold_experiment'])
        self.assertFalse(metrics['calibration_performed'])
        self.assertEqual(manifest['missing_observation_ids'], [])
        self.assertEqual(len(manifest['declared_trials']), 8)
        self.assertTrue(all(t['complete'] and t['sample_count'] > 0
                            for t in manifest['declared_trials']))
        self.assertEqual(rendered['trial_soma_pairs'], manifest['expected_trial_soma_pairs'])
        self.assertEqual(len(manifest['figures']), manifest['expected_trial_soma_pairs'])
        self.assertEqual({f['sample_id'] for f in manifest['figures']},
                         {t['sample_id'] for t in metrics['trials']})
        self.assertFalse(manifest['visual_acceptance_complete'])
        for figure in manifest['figures']:
            self.assertTrue(any(v['time_view'] == 'overview' for v in figure['views']))
            self.assertTrue(any(v['time_view'] != 'overview' and
                v['minimum_native_tick_pixels_on_zoom'] >= 8 for v in figure['views']))
            for view in figure['views']:
                self.assertFalse(view['downsampling'])
                with Image.open(output/view['files'][0]) as image:
                    self.assertEqual(image.size, (1920, 960))
        # The common production renderer owns both channels; no test-local
        # projection can hide a missing LT plot in ordinary baseline reports.
        decisions = load(output/'lt-decision-views.json')
        self.assertTrue(decisions['projection_for_plotting_only'])
        self.assertFalse(decisions['native_observations_changed'])
        self.assertTrue(decisions['all_declared_trials_rendered'])
        self.assertTrue(decisions['all_observations_complete'])
        self.assertEqual(decisions['unavailable_trials'], [])
        self.assertEqual(decisions['threshold'], result['proposal']['threshold'])
        self.assertEqual(len(decisions['trials']), 8)
        for figure in manifest['figures']:
            self.assertTrue(all('reference_level' not in v for v in figure['views']))
        for item in decisions['trials']:
            self.assertEqual(item['source_descriptor']['path'], '$.LTZone.Potential')
            self.assertTrue(any(v['time_view'] == 'overview' for v in item['views']))
            self.assertTrue(any(v['time_view'] != 'overview' and
                v['minimum_native_tick_pixels_on_zoom'] >= 8 for v in item['views']))
            for view in item['views']:
                self.assertFalse(view['downsampling'])
                self.assertEqual(view['reference_level'], result['proposal']['threshold'])
                self.assertEqual(view['reference_level_visible'],
                    view['y_limits'][0] <= view['reference_level'] <= view['y_limits'][1])
                with Image.open(output/item['folder']/view['files'][0]) as image:
                    self.assertEqual(image.size, (1920, 960))
