"""Exact finite suite planning through the actual Windows validation worker."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest


WORKER = Path(__file__).resolve().parents[1]/'workers/windows-vs2026/validate-native.py'
SPEC = importlib.util.spec_from_file_location('actual_windows_native_validation', WORKER)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def suite():
    return {'schema_version': 2, 'expected_test_ids': ['DTO/Declaration', 'Model/ActualGraph', 'Search/Measured'],
            'maximum_wall_seconds': 60, 'partitions': [
                {'name': 'declarations', 'expected_test_ids': ['DTO/Declaration'], 'maximum_wall_seconds': 10},
                {'name': 'models', 'expected_test_ids': ['Model/ActualGraph'], 'maximum_wall_seconds': 30},
                {'name': 'search', 'expected_test_ids': ['Search/Measured'], 'maximum_wall_seconds': 20}]}


class WindowsNativeValidationPlanTest(unittest.TestCase):
    def test_declared_partition_order_test_names_and_limits_are_preserved_without_mutation(self):
        spec = suite(); before = deepcopy(spec)
        plan = VALIDATOR.validation_plan(spec)
        self.assertEqual(plan, spec['partitions'])
        plan[0]['expected_test_ids'].append('Unrequested/Test')
        self.assertEqual(spec, before)

    def test_single_gate_legacy_layout_is_retained(self):
        spec = suite(); spec['schema_version'] = 1; spec.pop('partitions')
        self.assertEqual(VALIDATOR.validation_plan(spec), [{'name': 'single',
            'expected_test_ids': spec['expected_test_ids'], 'maximum_wall_seconds': 60}])

    def test_missing_extra_or_duplicate_cases_cannot_reduce_the_declared_suite(self):
        for defect in ('missing', 'extra', 'duplicate'):
            spec = suite()
            if defect == 'missing': spec['partitions'].pop()
            elif defect == 'extra': spec['partitions'][0]['expected_test_ids'].append('Unrequested/Test')
            else: spec['partitions'][0]['expected_test_ids'].append('Model/ActualGraph')
            with self.subTest(defect=defect), self.assertRaisesRegex(RuntimeError, 'inventory_mismatch'):
                VALIDATOR.validation_plan(spec)

    def test_partition_identity_and_schema_are_finite_and_unambiguous(self):
        for defect in ('same-name', 'case-alias', 'path', 'unknown-field', 'wildcard'):
            spec = suite()
            if defect == 'same-name': spec['partitions'][1]['name'] = spec['partitions'][0]['name']
            elif defect == 'case-alias': spec['partitions'][1]['name'] = spec['partitions'][0]['name'].upper()
            elif defect == 'path': spec['partitions'][0]['name'] = '../outside'
            elif defect == 'unknown-field': spec['partitions'][0]['ignored_option'] = True
            else: spec['partitions'][0]['expected_test_ids'] = ['DTO/*']
            with self.subTest(defect=defect), self.assertRaises(RuntimeError):
                VALIDATOR.validation_plan(spec)

    def test_partition_limits_cannot_silently_replenish_the_whole_allowance(self):
        spec = suite(); spec['partitions'][0]['maximum_wall_seconds'] = 11
        with self.assertRaisesRegex(RuntimeError, 'wall_exceeded'):
            VALIDATOR.validation_plan(spec)
        for value in (True, 0, -1, float('nan'), float('inf'), 10**1000):
            spec = suite(); spec['partitions'][0]['maximum_wall_seconds'] = value
            with self.subTest(value=value), self.assertRaises(RuntimeError):
                VALIDATOR.validation_plan(spec)

    def test_unknown_versions_and_legacy_unconsumed_partitions_are_rejected(self):
        for version in (True, 1.0, 0, 4):
            spec = suite(); spec['schema_version'] = version
            with self.subTest(version=version), self.assertRaises(RuntimeError):
                VALIDATOR.validation_plan(spec)
        spec = suite(); spec['schema_version'] = 1
        with self.assertRaisesRegex(RuntimeError, 'undeclared'):
            VALIDATOR.validation_plan(spec)

    def test_data_version3_uses_full_names_and_explicit_gate_source(self):
        spec = {'schema_version': 3, 'expected_test_ids': ['Model.ActualGraph'],
                'maximum_wall_seconds': 60, 'gate_source_root': str(WORKER.parents[4]),
                'gate_source_commit': 'a'*40, 'artifact_directories': {},
                'data_inputs': [{'name': 'classic-package6.qz',
                    'path': str(WORKER.parent/'fixture.qz'), 'bytes': 323020, 'sha256': 'b'*64}]}
        before = deepcopy(spec)
        self.assertEqual(VALIDATOR.validation_plan(spec), [{'name': 'single',
            'expected_test_ids': ['Model.ActualGraph'], 'maximum_wall_seconds': 60}])
        self.assertEqual(spec, before)
        for key in ('gate_source_root', 'gate_source_commit', 'data_inputs', 'artifact_directories'):
            bad = deepcopy(spec); del bad[key]
            with self.subTest(key=key), self.assertRaises(RuntimeError):
                VALIDATOR.validation_plan(bad)
        for change in (dict(expected_test_ids=['Model/ActualGraph']), dict(data_inputs=[]),
                       dict(gate_source_commit='not-a-commit'),
                       dict(artifact_directories={'PATH':'runtime'})):
            with self.subTest(change=change), self.assertRaises(RuntimeError):
                VALIDATOR.validation_plan(dict(spec, **change))

    def test_legacy_validation_cannot_ignore_new_data_controls(self):
        for key in ('data_inputs', 'artifact_directories', 'gate_source_root', 'gate_source_commit'):
            bad = suite(); bad[key] = 'unconsumed'
            with self.subTest(key=key), self.assertRaisesRegex(RuntimeError, 'requires_version3'):
                VALIDATOR.validation_plan(bad)
