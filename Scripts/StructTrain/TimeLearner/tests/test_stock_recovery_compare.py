"""Matched-comparison checks over real stock declarations and native primary."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from ..native_evidence import EvidenceError, load
from ..n1_protocol_robustness import _signed, _write
from ..stock_recovery_compare import match_designs, compare_studies
from ..stock_recovery_study import prepare, audit_design


class StockRecoveryComparisonTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_STOCK_RECOVERY_STUDY')
        if not value:
            raise unittest.SkipTest('requires the actual complete eight-case native recovery study')
        cls.root = Path(value)
        cls.actual = compare_studies(cls.root, cls.root)

    def prepared(self, *, changed_sweeps=False, changed_bounds=False):
        temporary = tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
        base = Path(temporary.name);templates = base/'templates';templates.mkdir()
        (templates/'jobs').mkdir();(templates/'expected').mkdir()
        original = load(self.root/'source/design.json')
        recovery = load(self.root/'design.json')
        for row in original['rows']:
            name = row['name'];job = load(self.root/'source'/(name+'.json'))
            if changed_sweeps:job['configuration']['search']['maximum_sweeps'] += 1
            if changed_bounds:job['configuration']['search']['bounds'][0]['maximum_length'] += 1
            job = _signed(job);row['job_sha256'] = job['sha256']
            _write(templates/'jobs'/(name+'.json'), job)
            source_row = next(r for r in recovery['rows'] if r['source_name'] == name)
            _write(templates/'expected'/(name+'.json'),
                   load(self.root/'expected'/(source_row['name']+'.json')))
        _write(templates/'design.json', _signed(original))
        output = base/'prepared'
        prepare(templates, self.root/'runtime.json', load(self.root/'code-identity.json'), output)
        return output

    def test_full_actual_self_comparison_is_not_eight_new_repetitions_or_classification(self):
        self.assertEqual(self.actual['paired_conditions'], 8)
        self.assertEqual(self.actual['same_attempt_pairs'], 8)
        self.assertTrue(self.actual['both_studies_primary_audited'])
        self.assertFalse(self.actual['independent_random_repeats_attested'])
        self.assertFalse(self.actual['classification_assessed'])
        self.assertFalse(self.actual['physical_infeasibility_attested'])
        self.assertIsNone(self.actual['scientific_verdict'])
        for row in self.actual['pairs']:
            self.assertEqual(row['baseline'], row['candidate'])
            self.assertTrue(row['same_attempt'])

    def test_pairing_uses_condition_labels_instead_of_design_row_position(self):
        candidate = self.prepared()
        expected = match_designs(self.root, candidate)
        design = load(candidate/'design.json');design['rows'].reverse()
        _write(candidate/'design.json', _signed(design))
        self.assertEqual(match_designs(self.root, candidate), expected)

    def test_internally_valid_changed_search_budget_is_not_a_matched_algorithm_control(self):
        candidate = self.prepared(changed_sweeps=True)
        self.assertEqual(len(audit_design(candidate)['rows']), 8)
        with self.assertRaisesRegex(EvidenceError, 'stock_compare_training_factors_changed'):
            match_designs(self.root, candidate)

    def test_internally_valid_changed_length_bound_is_not_a_matched_algorithm_control(self):
        candidate = self.prepared(changed_bounds=True)
        self.assertEqual(len(audit_design(candidate)['rows']), 8)
        with self.assertRaisesRegex(EvidenceError, 'stock_compare_training_factors_changed'):
            match_designs(self.root, candidate)

    def test_valid_design_without_native_results_cannot_be_compared_as_completed(self):
        candidate = self.prepared()
        self.assertEqual(len(match_designs(candidate, self.root)), 8)
        with self.assertRaises(OSError):
            compare_studies(candidate, self.root)

    def test_cli_refuses_existing_output_and_missing_primary_without_creating_a_verdict(self):
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw);output = base/'result.json';output.write_text('keep')
            def run(path):
                return subprocess.run([sys.executable, '-m', 'Scripts.StructTrain.TimeLearner',
                    'stock-recovery-compare', str(base/'missing'), str(self.root), '--output', str(path)],
                    cwd=Path(__file__).resolve().parents[4],
                    capture_output=True, text=True, timeout=30)
            existing = run(output)
            self.assertEqual(existing.returncode, 2)
            self.assertIn('stock_compare_output_exists', existing.stderr)
            self.assertEqual(output.read_text(), 'keep')
            absent = base/'absent.json';missing = run(absent)
            self.assertEqual(missing.returncode, 2)
            self.assertFalse(absent.exists())
