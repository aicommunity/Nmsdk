"""Use the complete real stopped Classic/Rs run; never substitute a model stub."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..native_evidence import EvidenceError
from ..training_search_report import analyze_search_history


class ActualLargeSearchSummaryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.primary_root = Path(os.environ['TIMELEARNER_LARGE_SEARCH_PRIMARY']).resolve(strict=True)

    def test_full_production_cli_retains_actual_terminal_and_all_measured_candidates(self):
        from ..__main__ import main
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)/'large-search-report.json'
            with contextlib.redirect_stdout(io.StringIO()):
                code = main(['analyze', str(self.primary_root/'run-manifest.json'),
                             '--format', 'native-search-history',
                             '--maximum-summary-bytes', str(512*1024**2), '--output', str(output)])
            self.assertEqual(code, 0)
            document = json.loads(output.read_bytes());result = document['analysis']
            self.assertEqual(document['validity'], 'valid')
            self.assertEqual(result['schema_version'], 3)
            self.assertEqual(result['source_summary']['bytes'], 276897143)
            self.assertEqual(result['actual_model_revision'],
                '47e37d8b4eb61a19619a22bb61904d499dc30d649f8525b058e4356055956159')
            self.assertEqual(result['normalization'], 'N1')
            self.assertEqual(result['topology'], 'Classic')
            self.assertEqual(len(result['actual_parameters']), 4)
            points = result['historical_search']['recorded_candidate_measurements']
            self.assertEqual(len(points), 27)
            self.assertEqual(sum(p['within_timing'] for p in points), 15)
            self.assertFalse(any(p['within_timing'] and p['within_amplitude'] for p in points))
            self.assertEqual(result['outcome'], 'budget_exhausted')
            self.assertTrue(result['data_audit']['run_evidence_consistent'])
            self.assertFalse(result['native_execution_attested'])
            self.assertFalse(result['historical_measurements_rebound_to_actual_epoch'])
            self.assertIsNone(result['scientific_verdict'])
            self.assertIsNone(document['evaluation_verdict'])
            saved = Path(os.environ['TMPDIR'])/'actual-large-Classic-Rs-search-report.json'
            with saved.open('xb') as stream:stream.write(output.read_bytes())

    def test_legacy_default_does_not_silently_expand_its_read_budget(self):
        with self.assertRaisesRegex(EvidenceError, 'collector_file_type_or_size'):
            analyze_search_history(self.primary_root/'run-manifest.json')

    def test_invalid_budgets_are_rejected_before_any_source_access(self):
        for budget in (True, False, 0, -1, 1.5, float('nan'), float('inf'), 1024**3+1):
            with self.subTest(budget=budget), self.assertRaisesRegex(EvidenceError, 'invalid_summary_budget'):
                analyze_search_history(Path('source-not-to-be-opened.json'), maximum_summary_bytes=budget)

    def test_cli_rejects_an_ineffective_budget_on_another_analysis_format(self):
        from ..__main__ import main
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = main(['analyze', 'source-not-to-be-opened.json', '--format', 'domain',
                         '--maximum-summary-bytes', '1024'])
        self.assertEqual(code, 2)
        result = json.loads(stderr.getvalue())
        self.assertEqual(result['reason'], 'maximum_summary_bytes_is_only_for_native_search_history')
        self.assertIsNone(result['evaluation_verdict'])


if __name__ == '__main__':
    unittest.main()
