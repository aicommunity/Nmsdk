"""Plot the actual fixed-threshold eight-pattern experiment, without reruns."""
import os
import gzip
import json
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
        recorded = {}
        for figure in manifest['figures']:
            with gzip.open(output/'primary'/f"trial-{figure['presentation_index']:04d}.json.gz", 'rt') as stream:
                recorded[figure['trial_id']] = json.load(stream)
        for figure in manifest['figures']:
            self.assertTrue(all('reference_level' not in v for v in figure['views']))
            with gzip.open(output/'primary'/f"trial-{figure['presentation_index']:04d}.json.gz", 'rt') as stream:
                observed = json.load(stream)
            values = [s['soma'][figure['descriptor']['index']] for s in observed['samples']]
            channel = figure['descriptor']['index']
            shared_minimum = min(s['soma'][channel] for o in recorded.values() for s in o['samples'])
            self.check_positive_lobe_views(figure['views'], values, shared_minimum)
        for item in decisions['trials']:
            self.assertEqual(item['source_descriptor']['path'], '$.LTZone.Potential')
            figure = next(f for f in manifest['figures'] if f['trial_id'] == item['trial_id'])
            with gzip.open(output/'primary'/f"trial-{figure['presentation_index']:04d}.json.gz", 'rt') as stream:
                observed = json.load(stream)
            shared_minimum = min(s['lt_potential'] for o in recorded.values() for s in o['samples'])
            self.check_positive_lobe_views(item['views'], [s['lt_potential'] for s in observed['samples']], shared_minimum)
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

    def check_positive_lobe_views(self, views, values, shared_minimum):
        ordinary = [v for v in views if v['y_scale'] != 'positive_lobe_detail']
        overview = next(v for v in ordinary if v['time_view'] == 'overview')
        self.assertLessEqual(overview['y_limits'][0], min(values))
        self.assertGreaterEqual(overview['y_limits'][1], max(values))
        companions = [v for v in views if v['y_scale'] == 'positive_lobe_detail']
        if shared_minimum < 0. < max(values):
            self.assertTrue(companions)
            full = next(v for v in companions if v['time_view'] == 'overview')
            if min(values) < 0.:
                self.assertGreater(full['samples_outside_display_y'], 0)
            self.assertEqual(full['shared_recorded_minimum'], shared_minimum)
            self.assertGreaterEqual(full['y_limits'][1], max(values))
            self.assertTrue(any(v['time_view'] != 'overview' and
                                v['minimum_native_tick_pixels_on_zoom'] >= 8 for v in companions))
            self.assertTrue(all(v['display_range_only'] and v['ordinary_full_recovery_views_retained']
                                for v in companions))
        else:
            self.assertEqual(companions, [])
