"""Report the actual cold4 Classic search without another Train or Test."""
import os
from pathlib import Path
import unittest

from ..composite_training_temporal import render
from ..native_calibration_worker import _write
from ..native_evidence import load
from ..plotting import plotting_runtime
from ..training_search_report import analyze_search_history


class CoupledClassicTrainingReportTest(unittest.TestCase):
    def test_actual_closest_measured_candidate_and_two_ambiguous_groups(self):
        plotting_runtime()
        from PIL import Image

        run = Path(os.environ['TIMELEARNER_COUPLED_CLASSIC_TRAIN_RUN']).resolve(strict=True)
        analysis = analyze_search_history(run/'run-manifest.json')
        self.assertEqual((analysis['topology'], analysis['normalization'], analysis['input_count']),
                         ('Classic', 'N1', 4))
        self.assertEqual(analysis['actual_model_revision'],
                         '35d849faa2aaea5d2620f0fd59d9934c77760b7fde0dd49d3284539f69f68263')
        self.assertEqual(analysis['outcome'], 'invalid_observation')
        points = analysis['recorded_candidate_measurements']
        self.assertEqual(len(points), 14)
        self.assertFalse(any(p['within_timing'] and p['within_amplitude'] for p in points))
        self.assertEqual(analysis['final_verification_group_ids'], [])
        recoveries = analysis['recorded_recovery_deliveries']
        self.assertEqual(len(recoveries), 5)
        self.assertEqual([r['event']['transition']['full_parameters'][0]['length'] for r in recoveries],
                         [54,52,50,48,45])
        closest = min(points, key=lambda p: (max(abs(p['timing_low']), abs(p['timing_high'])),
                                             abs(p['amplitude_residual']), p['parameter_change_cost']))
        selected_trials = [closest['trial_id'], recoveries[0]['event']['transition']['trial_id'],
                           recoveries[-1]['event']['transition']['trial_id']]
        execution = load(run/'native/execution.json')
        package = load(run/'native'/execution['package_path'])
        self.assertIsNone(package['certificate'])
        self.assertEqual(package['configuration']['model']['frequency_hz'], 2000)
        self.assertEqual(package['configuration']['search']['maximum_invalid_observations'], 4)
        self.assertEqual(package['configuration']['search']['tolerances'],
                         dict(amplitude_absolute=1e-5, amplitude_relative=0., sync=.02))
        records = package['measurement_archive']['records']
        selected = []
        for trial in selected_trials:
            matches = [i for i, r in enumerate(records, 1) if r['logical_request']['trial_id'] == trial]
            self.assertEqual(len(matches), 1)
            selected.append(matches[0])
        self.assertEqual(len(set(selected)), 3)
        output = Path(os.environ['TMPDIR'])/'Classic-coupled-cold4-training-report'
        report = render(run/'native', output, selected)
        self.assertEqual({f['channel'] for f in report['figures']}, {0,1,2,3})
        self.assertEqual(len(report['figures']), 24)
        self.assertFalse(report['downsampling'])
        self.assertFalse(report['training_certificate_eligible'])
        self.assertIsNone(report['scientific_verdict'])
        self.assertTrue(all(g['complete_group'] and len(g['recorded_trials']) == 6 and
                            all(t['complete'] and t['sample_count'] == 3601 for t in g['recorded_trials'])
                            for g in report['groups']))
        for figure in report['figures']:
            with Image.open(output/figure['files'][0]) as image:
                self.assertGreaterEqual(image.width, 2800)
                self.assertGreaterEqual(image.height, 2800)
        _write(output/'selection.json', dict(kind='classic_coupled_cold4_training_selection', schema_version=1,
            closest_measured_candidate=closest, selected_trials=selected_trials, selected_groups=selected,
            terminal_parameters=analysis['actual_parameters'], classification_assessed=False,
            new_model_execution=False, scientific_verdict=None))
        _write(output/'search-history.json', analysis)
