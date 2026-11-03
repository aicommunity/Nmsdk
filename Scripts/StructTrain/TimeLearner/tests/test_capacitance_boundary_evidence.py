"""Version3 boundary checks from actual native same/fresh-process transfers."""
import copy
import os
from pathlib import Path
import unittest

from ..capacitance_boundary_evidence import audit_package_capacitance_history
from ..learned_evidence import audit_learned_state, load_case as learned_case
from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError, audit_probe, load
from ..stopped_evidence import audit_stopped_state, load_case as stopped_case


class CapacitanceBoundaryEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get('TIMELEARNER_CAPACITANCE_BOUNDARY_EVIDENCE_DIR')
        if not root:
            raise unittest.SkipTest('requires actual version3 native boundary transfers')
        cls.root = Path(root)
        cls.completed = [(p, load(p)) for p in sorted(cls.root.glob('*_learned_state.json'))
                         if load(p)['schema_version'] == 3]
        cls.stopped = [(p, load(p)) for p in sorted(cls.root.glob('*_stopped_state.json'))
                       if load(p)['schema_version'] == 3]
        if len(cls.completed) != 6 or len(cls.stopped) != 6:
            raise RuntimeError('requires six completed and six stopped actual C-history boundaries')
        cls.cases = cls.completed+cls.stopped

    @staticmethod
    def case(path, package):
        return learned_case(path) if package['kind'] == 'timelearner_completed_state' else stopped_case(path)

    @staticmethod
    def resign(value):
        value['sha256'] = canonical_model_sha256({k: v for k, v in value.items() if k != 'sha256'})
        return value

    def test_actual_primary_package_readers(self):
        for path, package in self.cases:
            with self.subTest(path=path.name):
                case = self.case(path, package)
                result = (audit_learned_state if package['kind'] == 'timelearner_completed_state' else audit_stopped_state)(*case)
                self.assertTrue(result['capacitance_state']['consistent'])
                self.assertTrue(result['capacitance_history']['consistent'])
                self.assertFalse(result['capacitance_history']['dynamic_checkpoint'])
                self.assertIsNone(result['evaluation_verdict'])

    def test_fresh_process_preserves_history_and_actual_response(self):
        for path, package in self.cases:
            with self.subTest(path=path.name):
                suffix = '_learned_state.json' if package['kind'] == 'timelearner_completed_state' else '_stopped_state.json'
                stem = path.name.removesuffix(suffix)
                fresh_path = path.with_name(stem+'_fresh_process.json'); fresh = load(fresh_path)
                self.assertEqual(fresh['capacitance_history'], package['capacitance_history'])
                self.assertEqual(fresh['capacitance_state'], package['capacitance_state'])
                self.assertEqual(fresh['model']['sha256'], package['model_revision'])
                self.assertFalse(fresh['need'])
                csv_path = path.with_name(stem+'_fresh_process.csv')
                self.assertTrue(audit_probe(fresh['probe'], csv_path)['trace_checked'])
                original_csv = path.with_name(stem+('_frozen_test.csv' if package['kind'] == 'timelearner_completed_state' else '_frozen.csv'))
                self.assertEqual(csv_path.read_bytes(), original_csv.read_bytes())

    def test_only_boundary_evidence_is_retained(self):
        for _, package in self.cases:
            history = package['capacitance_history']
            self.assertEqual(set(history), {'schema_version', 'capture_witness_id', 'current_witness_id',
                                           'current_verified', 'witnesses', 'trial_witness_ids'})
            self.assertFalse(audit_package_capacitance_history(package)['search_checkpoint'])

    def test_missing_capture_witness_is_rejected(self):
        checked = 0
        for _, original in self.cases:
            package = copy.deepcopy(original);h = package['capacitance_history']
            # A missing reference in a populated registry is distinct from an
            # empty inventory, which is rejected before reference resolution.
            if len(h['witnesses']) == 1:
                continue
            del h['witnesses'][h['capture_witness_id']];self.resign(package)
            self.assertTrue(h['witnesses'])
            with self.assertRaisesRegex(EvidenceError, '^missing_capacitance_boundary_witness$'):
                audit_package_capacitance_history(package)
            checked += 1
        self.assertGreater(checked, 0, 'requires an actual multi-witness boundary for missing-reference control')

    def test_empty_boundary_inventory_is_rejected(self):
        for path, original in self.cases:
            with self.subTest(path=path.name):
                package = copy.deepcopy(original)
                package['capacitance_history']['witnesses'].clear();self.resign(package)
                with self.assertRaisesRegex(EvidenceError, '^invalid_capacitance_boundary_inventory$'):
                    audit_package_capacitance_history(package)

    def test_wrong_trial_binding_is_rejected(self):
        for _, original in self.cases:
            if not original['capacitance_history']['trial_witness_ids']:
                continue
            package = copy.deepcopy(original);trials = package['capacitance_history']['trial_witness_ids']
            trials[next(iter(trials))] = 'a'*64;self.resign(package)
            with self.assertRaisesRegex(EvidenceError, '^missing_capacitance_boundary_witness$'):
                audit_package_capacitance_history(package)

    def test_unknown_or_unverified_boundary_is_rejected(self):
        for _, original in self.cases:
            for key, value in [('schema_version', True), ('current_verified', False), ('checkpoint', {})]:
                package = copy.deepcopy(original);package['capacitance_history'][key] = value;self.resign(package)
                with self.assertRaisesRegex(EvidenceError, '^unknown_capacitance_boundary_schema$'):
                    audit_package_capacitance_history(package)

    def test_configuration_cannot_change_C_policy(self):
        for _, original in self.cases:
            package = copy.deepcopy(original);package['configuration']['capacitance_history']['maximum_relative_change'] = .3
            self.resign(package)
            with self.assertRaisesRegex(EvidenceError, '^learned_capacitance_history_policy_mismatch$'):
                audit_package_capacitance_history(package)

    def test_schema_downgrade_cannot_drop_history(self):
        for _, original in self.cases:
            package = copy.deepcopy(original);package['schema_version'] = 2;self.resign(package)
            with self.assertRaisesRegex(EvidenceError, '^unversioned_learned_capacitance_history$'):
                audit_package_capacitance_history(package)

    def test_live_summary_cannot_substitute_another_current_context(self):
        for path, package in self.cases:
            _, original, _, _ = self.case(path, package);summary = copy.deepcopy(original)
            summary['capacitance_history']['current_witness_id'] = 'a'*64
            with self.assertRaisesRegex(EvidenceError, '^capacitance_boundary_summary_context_mismatch$'):
                audit_package_capacitance_history(package, summary)

    def test_stopped_before_first_tick_does_not_invent_observations(self):
        empty = [(p, v) for p, v in self.stopped if 'before_first_tick' in p.name]
        self.assertEqual(len(empty), 2)
        for path, package in empty:
            result = audit_stopped_state(*stopped_case(path))
            self.assertEqual(result['primary_trials'], 0)
            self.assertEqual(result['reference_trials'], 0)
            self.assertFalse(result['certificate_present'])
            self.assertEqual(package['capacitance_history']['trial_witness_ids'], {})

    def test_warm_boundary_drops_old_attempt_trials_without_rebasing_C0(self):
        for path, package in self.stopped:
            stem = path.name.removesuffix('_stopped_state.json')
            warm = load(path.with_name(stem+'_warm_boundary.json'))
            self.assertEqual(warm['schema_version'], 3)
            self.assertEqual(warm['capacitance_state']['baseline'], package['capacitance_state']['baseline'])
            self.assertEqual(warm['capacitance_history']['trial_witness_ids'], {})
            self.assertEqual(warm['observed_packets'], [])
            self.assertTrue(audit_package_capacitance_history(warm)['consistent'])

    def test_configured_record_flag_is_explicit(self):
        configured = [v for p, v in self.completed if '_configured' in p.name]
        self.assertEqual(len(configured), 2)
        for package in configured:
            c = package['configuration'];self.assertEqual(c['schema_version'], 3)
            self.assertEqual(c['capacitance_history'], {'record': True, 'maximum_relative_change': .2})
            self.assertEqual(package['controller_version'], 2)
