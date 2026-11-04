"""Actual historical Git XML/CSV, explicit onset and native trial preparation."""
from contextlib import redirect_stdout, redirect_stderr
from copy import deepcopy
import csv
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET

from ..__main__ import main
from ..native_evidence import EvidenceError, load
from ..phasea_matrix import REVISION, PARAMETERS, OBSERVATIONS, extract, from_git, trial_design


class PhaseAMatrixTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get('TIMELEARNER_PHASEA_MATRIX_SOURCE')
        if not directory:
            raise unittest.SkipTest('requires real historical Bin Git source and extraction witness')
        fixture = Path(directory)
        binding = load(fixture/'binding.json')
        cls.repository = Path(binding['bin_repository'])
        if binding['revision'] != REVISION:
            raise AssertionError('wrong historical source revision')
        cls.raw = [subprocess.check_output(['git', '-C', str(cls.repository), 'show', REVISION+':'+path])
                   for path in (PARAMETERS, OBSERVATIONS)]
        cls.actual = from_git(cls.repository)
        if cls.actual != load(fixture/'matrix.json'):
            raise AssertionError('production extraction differs from actual Git source')

    def test_actual_git_matrix_retains_onset_all_labels_and_source_blobs(self):
        rows = self.actual['patterns']
        self.assertEqual(len(rows), 8)
        self.assertEqual(next(r['pattern_isi'] for r in rows if r['label'] == 'target'), [.01, .08, .16, .24])
        self.assertTrue(all(r['pattern_isi'][0] == .01 for r in rows))
        self.assertEqual(self.actual['historical_dataset_properties']['Delay'], '1.5')
        self.assertFalse(self.actual['historical_presentation_reproduced'])
        self.assertFalse(self.actual['response_metrics_imported'])
        self.assertEqual({r['path'] for r in self.actual['sources']}, {PARAMETERS, OBSERVATIONS})
        for source in self.actual['sources']:
            blob = subprocess.check_output(['git', '-C', str(self.repository), 'rev-parse', REVISION+':'+source['path']], text=True).strip()
            self.assertEqual(blob, source['blob_sha1'])

    def test_csv_row_order_does_not_select_the_target_or_change_pattern_identity(self):
        reader = csv.DictReader(io.StringIO(self.raw[1].decode('utf-8-sig')))
        rows = list(reader);self.assertEqual(rows[0]['target_class'], '1')
        output = io.StringIO();writer = csv.DictWriter(output, fieldnames=reader.fieldnames)
        writer.writeheader();writer.writerows(rows[1:]+rows[:1])
        other = extract(self.raw[0], output.getvalue().encode(), REVISION)
        self.assertEqual(other['patterns'], self.actual['patterns'])
        self.assertEqual(other['pattern_matrix_sha256'], self.actual['pattern_matrix_sha256'])
        self.assertNotEqual(other['sources'][1]['sha256'], self.actual['sources'][1]['sha256'])

    def test_corrupted_missing_duplicate_or_disagreeing_input_data_is_rejected(self):
        root = ET.fromstring(self.raw[0]);data = root.find('.//DatasetMatrix/Parameters/MatrixData')
        data.text = data.text.replace('0.08', 'nan', 1)
        with self.assertRaisesRegex(EvidenceError, 'nonfinite_property'):
            extract(ET.tostring(root), self.raw[1], REVISION)
        reader = csv.DictReader(io.StringIO(self.raw[1].decode('utf-8-sig')));rows = list(reader)
        for mutation in ('missing', 'duplicate', 'interval', 'label'):
            changed = deepcopy(rows)
            if mutation == 'missing':changed.pop()
            if mutation == 'duplicate':changed[1]['trial'] = changed[0]['trial']
            if mutation == 'interval':changed[2]['isi0'] = 'nan'
            if mutation == 'label':changed[2]['target_class'] = '1'
            output = io.StringIO();writer = csv.DictWriter(output, fieldnames=reader.fieldnames)
            writer.writeheader();writer.writerows(changed)
            with self.subTest(mutation=mutation), self.assertRaises(EvidenceError):
                extract(self.raw[0], output.getvalue().encode(), REVISION)

    def test_rotations_bind_the_learned_target_and_do_not_share_mutable_patterns(self):
        original = deepcopy(self.actual)
        trials = trial_design(self.actual, [.01, .08, .16, .24], 'stock-frozen')
        self.assertEqual(len(trials), 64)
        self.assertEqual(len({r['trial_id'] for r in trials}), 64)
        self.assertEqual({i % 8 for i, r in enumerate(trials) if r['label'] == 'target'}, set(range(8)))
        self.assertTrue(all(r['maximum_samples'] == 4005 and r['duration'] == 2 for r in trials))
        trials[0]['pattern_isi'][0] = 10
        self.assertEqual(self.actual, original)
        self.assertTrue(all(r['pattern_isi'][0] == .01 for r in trials[1:]))
        with self.assertRaisesRegex(EvidenceError, 'learned_target_mismatch'):
            trial_design(self.actual, [.01, .03], 'wrong-target')
        with self.assertRaisesRegex(EvidenceError, 'sample_budget_exceeded'):
            trial_design(self.actual, [.01, .08, .16, .24], 'overflow', duration=1e308)

    def test_production_cli_reads_exact_git_data_and_refuses_overwrite_or_symbolic_revision(self):
        with tempfile.TemporaryDirectory() as directory, redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            target = Path(directory)/'matrix.json'
            args = ['phasea-matrix', '--bin-repository', str(self.repository), '--output', str(target)]
            self.assertEqual(main(args), 0)
            self.assertEqual(load(target), self.actual)
            before = target.read_bytes()
            self.assertEqual(main(args), 2)
            self.assertEqual(target.read_bytes(), before)
            other = Path(directory)/'invalid.json'
            self.assertEqual(main(['phasea-matrix', '--bin-repository', str(self.repository), '--revision', 'develop',
                                   '--output', str(other)]), 2)
            self.assertFalse(other.exists())
