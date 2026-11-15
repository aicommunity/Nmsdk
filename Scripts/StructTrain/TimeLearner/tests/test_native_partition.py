"""Real server native processes plus destructive checks of their observations."""
import copy
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..native_evidence import EvidenceError
from ..native_partition import aggregate_junit, project_native_outputs, run, validate


class PartitionSchemaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        name = os.environ.get('TIMELEARNER_PARTITION_SPEC')
        if not name:
            raise unittest.SkipTest('requires an actual native runtime declaration on a server')
        cls.spec = json.loads(Path(name).read_text())

    def test_original_declaration_is_explicit(self):
        gate, total, case = validate(self.spec)
        self.assertEqual(gate['schema_version'], 2)
        self.assertGreaterEqual(total, case)

    def test_bad_budget_duplicate_id_or_disabled_capture_are_rejected(self):
        for change in ['duplicate', 'disabled_capture', 'nan', 'larger_case', 'unknown_field', 'implicit_v1']:
            spec = copy.deepcopy(self.spec)
            if change == 'duplicate':
                spec['native_gate']['expected_test_ids'].append(spec['native_gate']['expected_test_ids'][0])
            elif change == 'disabled_capture':
                spec['native_gate']['cooperative_runtime_capture'] = False
            elif change == 'nan':
                spec['maximum_total_wall_seconds'] = float('nan')
            elif change == 'larger_case':
                spec['maximum_case_wall_seconds'] = spec['maximum_total_wall_seconds'] + 1
            elif change == 'unknown_field':
                spec['retry_on_failure'] = True
            else:
                spec['native_gate']['schema_version'] = 1
                del spec['native_gate']['cooperative_runtime_capture']
            with self.subTest(change=change), self.assertRaises(EvidenceError):
                validate(spec)


class ActualPartitionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        declaration = os.environ.get('TIMELEARNER_PARTITION_SPEC')
        output = os.environ.get('TIMELEARNER_PARTITION_OUTPUT')
        if not declaration or not output:
            raise unittest.SkipTest('requires real server ASan processes and a fresh output')
        cls.output = Path(output)
        cls.ids = json.loads(Path(declaration).read_text())['native_gate']['expected_test_ids']
        if len(cls.ids) != 2:
            raise ValueError('addressed regression must contain exactly two real native cases')
        cls.result = run(declaration, cls.output)

    def test_actual_two_processes_pass_with_complete_derived_inventory(self):
        self.assertEqual(self.result['validity'], 'valid', self.result)
        self.assertEqual(self.result['assertion_status'], 'passed', self.result)
        self.assertEqual(self.result['inventory']['observed'], 2)
        self.assertFalse((self.output/'process/result.json').exists())
        sources = json.loads((self.output/'junit-sources.json').read_text())['cases']
        self.assertEqual([x['test_id'] for x in sources], self.ids)
        self.assertEqual(len({(x['native_process']['pid'], x['native_process']['start_ticks']) for x in sources}), 2)
        self.assertTrue(json.loads((self.output/'native-projection.json').read_text()))

    def copy_observations(self, target):
        for index in range(2):
            folder = Path('cases')/f'{index:04d}'
            for name in ['result.json', 'native.xml', 'process/result.json', 'process/owned-process.json']:
                destination = target/folder/name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(self.output/folder/name, destination)

    def test_missing_partition_and_reused_process_cannot_aggregate(self):
        for mutation in ['missing_xml', 'same_process']:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                target = Path(directory)
                self.copy_observations(target)
                if mutation == 'missing_xml':
                    (target/'cases/0001/native.xml').unlink()
                else:
                    shutil.copyfile(target/'cases/0000/process/owned-process.json', target/'cases/0001/process/owned-process.json')
                with self.assertRaises((EvidenceError, OSError)):
                    aggregate_junit(target, self.ids)

    def test_conflicting_native_filename_is_rejected_without_overwrite(self):
        observed = next((self.output/'native').rglob('*.json'))
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for index in range(2):
                path = target/'cases'/f'{index:04d}'/'native'/observed.name
                path.parent.mkdir(parents=True)
                path.write_bytes(observed.read_bytes() + (b' ' if index else b''))
            with self.assertRaisesRegex(EvidenceError, 'filename_collision'):
                project_native_outputs(target, 2)
            self.assertEqual((target/'native'/observed.name).read_bytes(), observed.read_bytes())
