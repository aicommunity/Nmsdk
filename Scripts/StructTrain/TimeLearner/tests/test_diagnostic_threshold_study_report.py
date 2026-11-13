"""Plot the actual fixed-threshold eight-pattern experiment, without reruns."""
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from ..native_calibration_worker import _write
from ..plotting import padded_limits, render_soma
from ..recognition_metrics import load_diagnostic_evaluation
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
        # LTZone.Potential is the actual threshold decision channel; an
        # individual Soma.SumPotential must not inherit its threshold line.
        # This projection is for plotting only and is never passed to a scorer.
        _, observations = load_diagnostic_evaluation(candidate/'native/evaluation.json')
        threshold = result['proposal']['threshold']
        limits = padded_limits([threshold]+[s['lt_potential']
            for observation in observations for s in observation['samples']])
        decisions = []
        for index, observation in enumerate(observations):
            self.assertEqual(observation['threshold_potential_source']['path'], '$.LTZone.Potential')
            projected = {**observation, 'samples': [
                {**s, 'soma': [s['lt_potential']]} for s in observation['samples']]}
            folder = output/f'trial-{index:04d}-lt-decision'
            folder.mkdir()
            views = render_soma(projected, 0, '$.LTZone.Potential', limits, folder,
                potential_axis_label='LT decision potential [model units; SI unverified]',
                reference_level=threshold,
                context_label='Stopped Train; fixed Same-Matrix threshold; not calibrated')
            self.assertTrue(any(v['time_view'] == 'overview' for v in views))
            self.assertTrue(any(v['time_view'] != 'overview' and
                v['minimum_native_tick_pixels_on_zoom'] >= 8 for v in views))
            for view in views:
                self.assertFalse(view['downsampling'])
                self.assertEqual(view['reference_level'], threshold)
                with Image.open(folder/view['files'][0]) as image:
                    self.assertEqual(image.size, (1920, 960))
            decisions.append(dict(sample_id=observation['sample_id'],
                trial_id=observation['trial_id'], folder=folder.name,
                source_descriptor=observation['threshold_potential_source'], views=views))
        self.assertEqual(len(decisions), 8)
        _write(output/'lt-decision-views.json', dict(kind='native_lt_decision_plot_views',
            schema_version=1, source_model_revision=metrics['model_revision'], threshold=threshold,
            projection_for_plotting_only=True, native_observations_changed=False,
            note='Native after-children samples may already reflect LT event/reset; use actual spike markers.',
            trials=decisions, scientific_verdict=None))
