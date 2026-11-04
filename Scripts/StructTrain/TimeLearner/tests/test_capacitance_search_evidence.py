"""Schema4 readers consume actual native codec, boundary and C-edit trial data."""
import copy
import os
from pathlib import Path
import unittest

from ..capacitance_policy import audit_capacitance_search_policy
from ..learned_evidence import audit_learned_state, load_case as learned_case
from ..stopped_evidence import audit_stopped_state, load_case as stopped_case
from ..native_evidence import EvidenceError, audit_probe, audit_training_summary, load
from ..model_identity import canonical_model_sha256
from .native_declared_corpus import model_spec2_cohort, require_model_spec2_records, audit_model_spec2_recognition_replay


class CapacitanceSearchEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get('TIMELEARNER_CAPACITANCE_SEARCH_EVIDENCE_DIR')
        if not root:
            raise unittest.SkipTest('requires actual schema4 native codecs/boundaries and negative activation controls')
        cls.root = Path(root)
        cls.completed = sorted(cls.root.glob('*_csearch_learned_state.json'))
        cls.stopped = sorted(cls.root.glob('*_csearch_stopped_state.json'))
        cls.activation = sorted(cls.root.glob('*_csearch_activation_stopped_state.json'))
        cls.codecs = sorted(cls.root.glob('*_csearch_codec*_schema4_configuration.json'))
        completed2 = [load(p) for p in cls.completed if load(p)['configuration']['model']['schema_version'] == 2]
        codecs2 = [load(p) for p in cls.codecs if load(p)['model']['schema_version'] == 2]
        require_model_spec2_records(completed2, model_spec2_cohort(cls.root, 'On'))
        require_model_spec2_records(codecs2, model_spec2_cohort(cls.root, 'codec'))
        if [len(cls.completed)-len(completed2), len(cls.stopped), len(cls.activation), len(cls.codecs)-len(codecs2)] != [4, 4, 4, 4]:
            raise RuntimeError('requires four baseline cases per schema4 group and the complete declared ModelSpec2 cohorts')

    @staticmethod
    def case(path):
        return learned_case(path) if path.name.endswith('_learned_state.json') else stopped_case(path)

    @staticmethod
    def audit(case):
        return (audit_learned_state if case[0]['kind'] == 'timelearner_completed_state' else audit_stopped_state)(*case)

    @staticmethod
    def resign(value):
        value['sha256'] = canonical_model_sha256({k: v for k, v in value.items() if k != 'sha256'})
        return value

    def test_actual_native_packages_and_full_primary_data(self):
        for path in self.completed+self.stopped+self.activation:
            with self.subTest(path=path.name):
                case = self.case(path);result = self.audit(case)
                self.assertEqual(case[0]['schema_version'], 4)
                self.assertTrue(result['capacitance_history']['consistent'])
                self.assertTrue(result['capacitance_state']['consistent'])
                self.assertIsNone(result['evaluation_verdict'])

    def test_fresh_process_keeps_policy_C0_and_exact_native_waveform(self):
        for path in self.completed+self.stopped:
            with self.subTest(path=path.name):
                package = load(path)
                if package['configuration']['model']['schema_version'] == 2:
                    self.assertTrue(audit_model_spec2_recognition_replay(path, package)['waveform_bytes_exact'])
                    continue
                suffix = '_learned_state.json' if path in self.completed else '_stopped_state.json'
                stem = path.name.removesuffix(suffix);fresh = load(path.with_name(stem+'_fresh_process.json'))
                self.assertEqual(fresh['capacitance_history'], package['capacitance_history'])
                self.assertEqual(fresh['capacitance_state'], package['capacitance_state'])
                self.assertEqual(fresh['capacitance_search'], package['configuration']['capacitance_search'])
                self.assertEqual(fresh['model']['sha256'], package['model_revision'])
                csv_path = path.with_name(stem+'_fresh_process.csv')
                self.assertTrue(audit_probe(fresh['probe'], csv_path)['trace_checked'])
                original = path.with_name(stem+('_frozen_test.csv' if path in self.completed else '_frozen.csv'))
                self.assertEqual(csv_path.read_bytes(), original.read_bytes())

    def test_activation_measures_real_changed_C_and_is_not_classification_success(self):
        for path in self.activation:
            with self.subTest(path=path.name):
                package, summary, packets, traces = self.case(path)
                result = audit_training_summary(summary, packets, package['protocol']['origin_stimulus_id'], require_certificate=False)
                self.assertEqual(result['training_summary_schema'], 4)
                self.assertIsNone(result['exact']);self.assertIsNone(result['evaluation_verdict'])
                self.assertIsNone(package['certificate']);self.assertNotEqual(package['training_outcome'], 'exact')
                self.assertTrue(any(scale != 1. for c in summary['candidates'] for scale in c['capacitance']['membrane_scales'].values()))
                if summary['configuration']['normalization'] == 'tip_resistance':
                    self.assertTrue(any(scale != 1. for d in summary['resistance_domains'] for scale in d['requested_capacitance']['membrane_scales'].values()))

    def test_codec_preserves_the_explicit_Off_schema3_representation(self):
        for path in self.codecs:
            with self.subTest(path=path.name):
                value = load(path);self.assertEqual(value['schema_version'], 4)
                result = audit_capacitance_search_policy(value['capacitance_search'],
                    maximum_relative_change=value['capacitance_history']['maximum_relative_change'], configuration=value['search'])
                self.assertTrue(result['policy_validated']);self.assertFalse(result['native_lifecycle_verified'])
                off = load(path.with_name(path.name.replace('_schema4_configuration.json', '_schema3_configuration.json')))
                expected = {k: v for k, v in value.items() if k != 'capacitance_search'};expected['schema_version'] = 3
                self.assertEqual(off, expected)

    def test_unknown_and_boolean_policy_fields_are_rejected(self):
        for path in self.codecs:
            original = load(path)['capacitance_search']
            for key, value in [('enumeration', 'assumed_monotone'), ('maximum_contexts', True),
                               ('maximum_cursor_elements', 0), ('minimum_scale', 0.), ('subdivision_depth', 21)]:
                policy = dict(original);policy[key] = value
                with self.subTest(path=path.name, key=key), self.assertRaises(EvidenceError):
                    audit_capacitance_search_policy(policy)
            policy = dict(original, unused_factor=1)
            with self.assertRaises(EvidenceError):audit_capacitance_search_policy(policy)

    def test_package_cannot_silently_change_the_archived_policy(self):
        for path in self.completed+self.stopped:
            with self.subTest(path=path.name):
                case = list(self.case(path));case[0] = copy.deepcopy(case[0])
                case[0]['configuration']['capacitance_search']['maximum_cursor_elements'] += 1
                self.resign(case[0])
                with self.assertRaises(EvidenceError):self.audit(case)

    def test_schema_downgrade_cannot_keep_hidden_search(self):
        for path in self.completed+self.stopped:
            with self.subTest(path=path.name):
                case = list(self.case(path));case[0] = copy.deepcopy(case[0]);case[0]['schema_version'] = 3
                case[0]['configuration']['schema_version'] = 3;self.resign(case[0])
                with self.assertRaises(EvidenceError):self.audit(case)

    def test_summary_must_use_the_same_search_policy(self):
        for path in self.completed+self.stopped:
            with self.subTest(path=path.name):
                case = list(self.case(path));case[1] = copy.deepcopy(case[1])
                case[1]['configuration']['capacitance_search']['maximum_contexts'] += 1
                with self.assertRaises(EvidenceError):self.audit(case)

    def test_search_requires_compatible_owned_limits(self):
        for path in self.codecs:
            value = load(path)
            with self.assertRaises(EvidenceError):
                audit_capacitance_search_policy(value['capacitance_search'], maximum_relative_change=.1, configuration=value['search'])

    def test_missing_reference_current_or_trial_witness_cannot_validate_search(self):
        for path in self.completed+self.stopped:
            with self.subTest(path=path.name):
                for key in ['capture_witness_id', 'current_witness_id']:
                    case = list(self.case(path));case[0] = copy.deepcopy(case[0])
                    case[0]['capacitance_history']['witnesses'].pop(case[0]['capacitance_history'][key]);self.resign(case[0])
                    with self.assertRaises(EvidenceError):self.audit(case)

    def test_archive_policy_is_checked_even_when_configuration_and_summary_match(self):
        for path in self.completed+self.stopped:
            with self.subTest(path=path.name):
                case = list(self.case(path));case[0] = copy.deepcopy(case[0])
                case[0]['neuron']['metadata']['training']['capacitance_search']['maximum_contexts'] += 1
                self.resign(case[0])
                with self.assertRaises(EvidenceError):self.audit(case)
