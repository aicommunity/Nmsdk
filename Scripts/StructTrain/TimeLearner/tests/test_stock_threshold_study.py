"""Actual paired stock cold runs; identity and missing-condition regressions."""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..condition import ConditionSpec
from ..native_evidence import EvidenceError, load
from ..n1_protocol_robustness import _signed, _write
from ..stock_threshold_study import _condition, audit


class StockThresholdStudyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_STOCK_THRESHOLD_STUDY')
        if not value:
            raise unittest.SkipTest('requires all four real stock cold threshold controls')
        cls.root = Path(value)
        cls.design = load(cls.root/'design.json')

    def test_actual_complete_matrix_is_audited_without_requiring_scientific_success(self):
        result = audit(self.root)
        self.assertEqual(result['validity'], 'valid')
        self.assertEqual(result['training_runs'], 4)
        self.assertEqual(result['preflight_runs'], 4)
        self.assertEqual({(r['topology'], r['initial_threshold']) for r in result['rows']},
                         {(t, v) for t in ('Classic', 'Branch') for v in (.0117, 100.)})
        self.assertFalse(result['classification_assessed'])
        self.assertIsNone(result['scientific_verdict'])

    def test_attempt_and_binary_path_do_not_change_the_condition(self):
        row = self.design['rows'][0];name = row['name']
        job = load(self.root/'jobs'/f'{name}.json')
        expected = load(self.root/'expected'/f'{name}.json')
        code, runtime = load(self.root/'code-identity.json'), load(self.root/'runtime.json')
        first = _condition(job, expected, code, runtime)
        moved = deepcopy(runtime);moved['executable']['path'] = '/moved/NeuroModelerConsole'
        other = deepcopy(job);other['configuration']['run_id'] = 'different-attempt'
        self.assertEqual(_condition(other, expected, code, moved), first)
        other['configuration']['search']['tolerances']['sync'] /= 2
        changed = _condition(other, expected, code, moved)
        self.assertNotEqual(ConditionSpec.loads(json.dumps(first['condition'])).fingerprint,
                            ConditionSpec.loads(json.dumps(changed['condition'])).fingerprint)

    def test_rehashed_missing_condition_cannot_keep_a_complete_matrix(self):
        with tempfile.TemporaryDirectory(dir=self.root.parent) as directory:
            root = Path(directory)
            design = deepcopy(self.design);design['rows'].pop()
            _write(root/'design.json', _signed(design))
            shutil.copyfile(self.root/'index.json', root/'index.json')
            with self.assertRaisesRegex(EvidenceError, 'stock_pair_incomplete_matrix'):
                audit(root)
