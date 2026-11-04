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
from ..stock_threshold_study import _condition, audit, audit_final_stock
from ..model_identity import canonical_model_sha256


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


class StockFinalPhysicsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_STOCK_COLD_PHYSICS')
        if not value:
            raise unittest.SkipTest('requires real cold stock packages and initial graph readbacks')
        cls.cases = []
        for folder in sorted((Path(value)/'runs').iterdir()):
            native = folder/'native'
            execution = load(native/'execution.json')
            package = load(native/execution['package_path'])
            cls.cases.append((load(native/'initial-state.json')['identity'], package['neuron']['graph']['identity']))
        if len(cls.cases) != 2:
            raise AssertionError('requires both actual stock topologies')

    def changed(self, mutation, reason):
        for initial, final in self.cases:
            changed = deepcopy(final);mutation(changed['model'])
            changed['sha256'] = canonical_model_sha256(changed['model'])
            with self.assertRaisesRegex(EvidenceError, reason):
                audit_final_stock(initial, changed)

    def test_actual_growth_and_individual_resistance_edits_preserve_stock_physics(self):
        for initial, final in self.cases:
            result = audit_final_stock(initial, final)
            self.assertFalse(result['lt_membrane'])
            self.assertTrue(result['feedback_connections_unchanged'])

    def test_rehashed_added_lt_membrane_is_rejected(self):
        def add(model):
            node = deepcopy(next(n for n in model['nodes'] if n['path'] == '$.Soma1'))
            node['path'] = '$.LTMembrane';model['nodes'].append(node)
        self.changed(add, 'stock_pair_final_profile_changed')

    def test_rehashed_growth_channel_capacity_drift_is_rejected(self):
        def edit(model):
            node = next(n for n in model['nodes'] if n['path'] == '$.Dendrite1_1.ExcChannel')
            node['parameters']['Capacity']['data']['value'] = '3df49da7e361ce4c'
        self.changed(edit, 'stock_pair_final_channel_physics_changed:Capacity')

    def test_rehashed_feedback_destination_change_is_rejected(self):
        def edit(model):
            edge = next(b for b in model['bindings'] if b['source'] == '$.LTZone:Output')
            edge['target'] = '$.Dendrite1_1:InputFeedbackSignal'
        self.changed(edit, 'stock_pair_final_ltzone_connections_changed')
