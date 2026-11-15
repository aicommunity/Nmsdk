"""Actual coupled-search success at input2 and later ambiguous input1; no rerun."""
import os
from pathlib import Path
import unittest

from ..composite_training_temporal import render
from ..native_calibration_worker import _write
from ..native_evidence import load
from ..plotting import plotting_runtime
from ..training_search_report import analyze_search_history


class N1CoupledSearchScientificReportTest(unittest.TestCase):
    def test_local_ready_candidate_and_rejected_input_are_separate_from_terminal_state(self):
        plotting_runtime()
        from PIL import Image

        run = Path(os.environ['TIMELEARNER_N1_COUPLED_RUN']).resolve(strict=True)
        analysis = analyze_search_history(run/'run-manifest.json')
        self.assertEqual(analysis['topology'], 'Branch')
        self.assertEqual(analysis['outcome'], 'invalid_observation')
        self.assertEqual(analysis['reason'], 'rejected_candidate_window:ambiguous')
        self.assertIsNone(analysis['training_or_final_verification_verdict'])
        self.assertEqual(analysis['final_verification_group_ids'], [])
        ready = [c for c in analysis['recorded_candidate_measurements']
                 if c['within_timing'] and c['within_amplitude']]
        self.assertEqual(len(ready), 1)
        good = ready[0]
        self.assertEqual(good['input_index'], 2)
        self.assertEqual(good['parameters']['length'], 27)
        self.assertLess(abs(good['amplitude_residual']), 1e-5)
        self.assertLessEqual(max(abs(good['timing_low']), abs(good['timing_high'])), .02)
        # Graph SHA alone must not promote another logical parameter assignment.
        self.assertNotEqual(analysis['actual_parameters'], good['full_parameters'])
        self.assertFalse(analysis['actual_model_matched_in_candidate_history'])
        rejected = analysis['recorded_rejections']
        self.assertEqual(len(rejected), 5)
        self.assertTrue(all(r['reason'] == 'rejected_candidate_window:ambiguous' for r in rejected))
        execution = load(run/'native/execution.json')
        package = load(run/'native'/execution['package_path'])
        self.assertEqual(package['configuration']['search']['tolerances'],
                         dict(amplitude_absolute=1e-5, amplitude_relative=0., sync=.02))
        records = package['measurement_archive']['records']
        good_groups = [i for i, r in enumerate(records, 1) if r['group_id'] == good['measurement_group_id']]
        bad_groups = [i for i, r in enumerate(records, 1)
                      if r['logical_request']['trial_id'] == rejected[-1]['trial_id']]
        self.assertEqual(len(good_groups), 1)
        self.assertEqual(len(bad_groups), 1)
        bad = records[bad_groups[0]-1]
        self.assertEqual(bad['logical_request']['input_id'], 'input1')
        self.assertTrue(bad['complete_group'])
        self.assertNotEqual(bad['selection']['geometry']['validity'], 'valid')
        selected = good_groups+bad_groups
        output = Path(os.environ['TMPDIR'])/'N1-coupled-search-scientific-report'
        report = render(run/'native', output, selected)
        self.assertFalse(report['downsampling'])
        self.assertFalse(report['training_certificate_eligible'])
        self.assertIsNone(report['scientific_verdict'])
        self.assertEqual(len(report['groups']), 2)
        for group in report['groups']:
            self.assertTrue(group['complete_group'])
            self.assertEqual(len(group['recorded_trials']), 6)
            self.assertTrue(all(t['complete'] and t['sample_count'] == 3601
                                for t in group['recorded_trials']))
        for figure in report['figures']:
            with Image.open(output/figure['files'][0]) as image:
                self.assertGreaterEqual(image.width, 2800)
                self.assertGreaterEqual(image.height, 2800)
        _write(output/'selection.json', dict(kind='actual_coupled_search_scientific_selection',
            schema_version=1, local_ready_candidate=good, terminal_parameters=analysis['actual_parameters'],
            terminal_model_is_not_that_candidate=True, rejected_input=1,
            rejected_trial=rejected[-1], selected_groups=selected,
            classification_assessed=False, new_model_execution=False, scientific_verdict=None))
