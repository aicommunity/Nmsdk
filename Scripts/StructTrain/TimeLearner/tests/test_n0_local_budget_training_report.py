"""Show the actual measured-best restore and the subsequent ambiguous N0 input."""
import os
from pathlib import Path
import unittest

from ..composite_training_temporal import render
from ..native_evidence import load


class N0LocalBudgetTrainingReportTest(unittest.TestCase):
    def test_restored_inexact_candidate_and_first_last_rejections_remain_distinct(self):
        from PIL import Image

        native = Path(os.environ['TIMELEARNER_N0_LOCAL_BUDGET_REPORT_NATIVE']).resolve(strict=True)
        package = load(native/'train_stopped_state.json')
        summary = load(native/'train_stopped_summary.json')
        self.assertEqual(package['configuration']['search']['maximum_candidates_per_input'], 12)
        self.assertEqual(package['configuration']['model']['normalization'], 'N0')
        self.assertTrue(package['configuration']['model']['branch'])
        self.assertEqual(summary['outcome'], 'invalid_observation')
        self.assertIsNone(summary['certificate'])
        candidates = summary['candidates']
        self.assertEqual(len(candidates), 13)  # Twelve candidates plus a fresh best restoration.
        restored = candidates[-1]
        self.assertEqual(restored['full_parameters'], candidates[10]['full_parameters'])
        self.assertNotEqual(restored['trial_id'], candidates[10]['trial_id'])
        self.assertTrue(restored['within_timing'])
        self.assertFalse(restored['within_amplitude'])
        events = [d['event'] for d in summary['recovery_ledger']['deliveries']]
        self.assertEqual(len(events), 5)
        self.assertTrue(all(e['kind'] == 'timelearner_candidate_window_recovery_event' for e in events))
        transitions = [e['transition'] for e in events]
        self.assertEqual([t['candidate_input_index'] for t in transitions], [1]*5)
        self.assertEqual([t['validity'] for t in transitions], ['ambiguous']*5)
        self.assertEqual([t['full_parameters'][1]['length'] for t in transitions], list(range(28, 33)))
        self.assertEqual([t['disposition'] for t in transitions], ['cursor_advanced']*4+['invalid_budget_stop'])
        records = package['measurement_archive']['records']
        self.assertEqual(len(records), 40)
        self.assertTrue(all(r['complete_group'] for r in records))
        restored_group = next(i for i, r in enumerate(records, 1)
                              if r['logical_request']['trial_id'] == restored['trial_id'])
        ordinals = {r['group_id']: i for i, r in enumerate(records, 1)}
        groups = [restored_group, ordinals[events[0]['group_id']], ordinals[events[-1]['group_id']]]
        self.assertEqual(groups, [30, 32, 40])
        output = Path(os.environ['TMPDIR'])/'n0-local-budget-training-gallery'
        report = render(native, output, groups, native_window_zooms=True)
        self.assertEqual(report['package_audit']['training_outcome'], 'invalid_observation')
        self.assertEqual([g['ordinal'] for g in report['groups']], groups)
        self.assertEqual([g['selection']['geometry']['validity'] for g in report['groups']],
                         ['valid', 'ambiguous', 'ambiguous'])
        self.assertEqual(len(report['figures']), 12)
        self.assertTrue(all(len(g['primary_references']) == 6 for g in report['groups']))
        self.assertFalse(report['downsampling'])
        self.assertFalse(report['training_certificate_eligible'])
        self.assertFalse(report['visual_acceptance_complete'])
        self.assertIsNone(report['scientific_verdict'])
        for figure in report['figures']:
            if figure['view'].endswith('-native'):
                self.assertGreaterEqual(figure['minimum_native_tick_pixels'], 8.)
            with Image.open(output/figure['files'][0]) as image:
                self.assertEqual(image.size, (2880, 2880))
            self.assertTrue((output/figure['files'][1]).is_file())
            self.assertTrue((output/figure['files'][2]).read_bytes().startswith(b'%PDF-'))
