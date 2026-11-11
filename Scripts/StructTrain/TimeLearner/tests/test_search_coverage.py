"""Coverage bookkeeping over real audited recovery Train primary."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..native_evidence import EvidenceError, load
from ..search_coverage import analyze_stock_recovery, summarize_recorded_search


class SearchCoverageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_STOCK_RECOVERY_STUDY')
        if not value:
            raise unittest.SkipTest('requires complete original eight-case native recovery study')
        cls.root = Path(value)
        cls.result = analyze_stock_recovery(cls.root)
        cls.summaries = []
        for row in cls.result['rows']:
            native = cls.root/'runs'/row['name']/'native'
            cls.summaries.append(load(native/'train_stopped_summary.json'))

    def test_actual_records_account_for_every_measured_candidate_and_typed_event(self):
        self.assertEqual(len(self.result['rows']), 8)
        for row in self.result['rows']:
            groups = row['recorded_geometry_groups']
            self.assertEqual(sum(g['measured_candidates'] for g in groups), row['measured_candidate_records'])
            self.assertEqual(sum(g['typed_unassigned_observations'] for g in groups), row['typed_unassigned_observations'])
            self.assertFalse(row['physical_infeasibility_attested'])
            self.assertFalse(row['full_search_box_exhaustion_attested'])
            self.assertIsNone(row['scientific_verdict'])

    def test_reordering_summary_rows_does_not_change_the_coverage_histogram(self):
        for summary in self.summaries:
            changed = deepcopy(summary);changed['candidates'].reverse()
            if 'candidate_recovery_events' in changed:changed['candidate_recovery_events'].reverse()
            changed['rejections'].reverse()
            self.assertEqual(summarize_recorded_search(summary), summarize_recorded_search(changed))

    def test_legacy_invalid_counter_and_unwitnessed_geometry_are_not_invented(self):
        for row in self.result['rows']:
            if row['policy'] == 'retry_same_candidate':
                self.assertIsNone(row['producer_invalid_observations'])
                self.assertTrue(row['invalid_counter_unknown_for_legacy_summary'])
                self.assertGreater(row['rejection_entries_without_full_parameter_witness'], 0)
            self.assertFalse(row['all_invalid_observations_independently_recounted'])

    def test_duplicate_or_relabelled_trial_cannot_inflate_measured_coverage(self):
        for summary in self.summaries:
            changed = deepcopy(summary);changed['candidates'].append(deepcopy(changed['candidates'][0]))
            with self.assertRaisesRegex(EvidenceError, 'coverage_duplicate_or_relabelled_trial'):
                summarize_recorded_search(changed)
