"""Actual stock Branch N4 search: retain outcome and render measured controls.

Join first/last measured candidates and rejections to the actual search history;
show the last complete but unconsumed budget group separately. Anchor timing
probes are not candidate measurements. This corrected post-hoc display rule
creates neither new model execution nor a scientific verdict.
"""
import os
from pathlib import Path
import unittest

from ..composite_training_temporal import render
from ..native_calibration_worker import _write
from ..native_evidence import load
from ..plotting import plotting_runtime
from ..training_search_report import analyze_search_history


class BranchFullDomainReportTest(unittest.TestCase):
    def test_actual_branch_search_and_predeclared_control_views(self):
        plotting_runtime()
        from PIL import Image

        run = Path(os.environ['TIMELEARNER_BRANCH_TRAIN_RUN']).resolve(strict=True)
        execution = load(run/'native/execution.json')
        package = load(run/'native'/execution['package_path'])
        model = package['configuration']['model']
        self.assertTrue(model['branch'])
        self.assertEqual(len(model['inputs']), 4)
        self.assertEqual(model['normalization'], 'N1')
        self.assertEqual(model['frequency_hz'], 2000)
        self.assertFalse(any(n['path'].startswith('$.LTMembrane') for n in
                             package['neuron']['graph']['identity']['model']['nodes']))
        self.assertEqual(package['configuration']['search']['tolerances'],
                         dict(amplitude_absolute=1e-5, amplitude_relative=0., sync=.02))
        self.assertEqual(package['configuration']['search']['maximum_invalid_observations'], 4)
        analysis = analyze_search_history(run/'run-manifest.json')
        self.assertEqual(analysis['topology'], 'Branch')
        self.assertEqual(analysis['actual_model_revision'], package['model_revision'])
        self.assertEqual(analysis['outcome'], execution['training_outcome'])
        self.assertIsNone(analysis['training_or_final_verification_verdict'])
        self.assertIsNone(analysis['scientific_verdict'])

        records = package['measurement_archive']['records']
        # A candidate window also exists on anchor remeasurements. Join actual
        # accepted candidates/rejections to the authoritative search history.
        measured_ids = {c['measurement_group_id'] for c in analysis['recorded_candidate_measurements']}
        rejected_ids = {r['trial_id'] for r in analysis['recorded_rejections']}
        complete = [i for i, record in enumerate(records, 1) if record['complete_group']
                    and record['group_id'] in measured_ids]
        self.assertTrue(complete)
        self.assertEqual(len(complete), len(measured_ids))
        rejected = [i for i, record in enumerate(records, 1) if record['complete_group']
                    and record['logical_request']['trial_id'] in rejected_ids]
        terminal = [i for i, record in enumerate(records, 1) if record['complete_group']
                    and record['group_id'] not in measured_ids
                    and record['logical_request']['input_index'] != analysis['anchor_index']
                    and record['rejection_reason'] == 'native_training_time_budget_exhausted']
        self.assertTrue(all(records[i-1]['logical_request']['input_index'] != analysis['anchor_index']
                            and not records[i-1]['rejection_reason'] for i in complete))
        selected = sorted(set([complete[0], complete[-1]] +
                              ([rejected[0], rejected[-1]] if rejected else []) +
                              ([terminal[-1]] if terminal else [])))
        output = Path(os.environ['TMPDIR'])/'Branch-full-domain-scientific-report'
        report = render(run/'native', output, selected)
        self.assertEqual([g['ordinal'] for g in report['groups']], selected)
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
        _write(output/'search-analysis.json', analysis)
        _write(output/'selection-rule.json', dict(
            kind='branch_actual_search_predeclared_views', schema_version=1,
            rule='first_last_history_joined_candidate_and_rejection_plus_last_complete_unconsumed_budget_group',
            complete_candidate_groups=complete, rejected_candidate_groups=rejected,
            complete_unconsumed_budget_groups=terminal,
            selected_groups=selected, new_model_execution=False,
            classification_assessed=False, scientific_verdict=None))
