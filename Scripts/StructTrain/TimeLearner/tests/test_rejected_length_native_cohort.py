"""Execute the unchanged, already-built recovery cohort in isolated outputs.

The first SDK attempt remains failed. This is a separate execution gate for
the same frozen binary/source; it does not claim another fresh SDK build.
"""
import os
from pathlib import Path
import unittest
from xml.etree import ElementTree as ET

from ..contained_process import inspect
from ..native_calibration_worker import _write
from ..native_evidence import load, require
from ..native_gate import run_native_gate
from ..owned_native_job import status
from ..process_runner import verify_runtime
from ..runtime import source_closure


class RejectedLengthNativeCohortTest(unittest.TestCase):
    def test_same_frozen_binary_and_cases_with_independent_native_outputs(self):
        controls = Path(os.environ['TIMELEARNER_RECOVERY_NATIVE_CONTROLS']).resolve(strict=True)
        declaration = load(controls/'declaration.json')
        require(set(declaration) == {'source', 'source_commit', 'runtime', 'cohort',
                'original_controller', 'original_output'}, 'recovery_native_controls_schema')
        source = Path(declaration['source']).resolve(strict=True)
        self.assertEqual(source_closure(source)['root']['head'], declaration['source_commit'])
        original = Path(declaration['original_output']).resolve(strict=True)
        closed = status(declaration['original_controller'])
        self.assertTrue(closed['result']['outer_closed'])
        self.assertFalse(closed['supervisor_live'])
        self.assertEqual(closed['result']['record_errors'], [])
        terminal = load(original/'terminal.json')
        self.assertTrue(terminal['built'])
        self.assertFalse(terminal['job_validation_passed'])
        self.assertEqual(terminal['audited_completed_cpp_cases'], 142)
        failures = [f for c in ET.parse(original/'bounded-scoped-n0-search/native.xml').getroot().iter('testcase')
                    for f in c.findall('failure')]
        self.assertEqual(len(failures), 26)
        self.assertTrue(all(any(reason in f.attrib.get('message', f.text or '') for reason in
            ('window5_output_new_only', 'package_fixture_new_only', 'composite_archive_output_new_only'))
            for f in failures))
        cohort = load(Path(declaration['cohort']))
        expected = cohort['selected_ids']
        leaves = cohort['runplan']
        self.assertEqual(len(expected), 142)
        self.assertEqual(len(leaves), 30)
        self.assertEqual(len(leaves[0]['expected_ids']), 113)
        self.assertTrue(all(len(leaf['expected_ids']) == 1 for leaf in leaves[1:]))
        self.assertCountEqual(expected, load(original/'compiled-inventory-crosscheck.json')['expected'])
        self.assertCountEqual(expected, [case for leaf in leaves for case in leaf['expected_ids']])
        self.assertEqual(len(set(leaf['name'] for leaf in leaves)), len(leaves))
        runtime = load(Path(declaration['runtime']))
        self.assertEqual(runtime['source_closure'], source_closure(source))
        verify_runtime(runtime)
        output = Path(os.environ['TMPDIR'])/'rejected-length-native-cohort'
        output.mkdir()
        rows = []
        for leaf in leaves:
            spec = dict(kind='timelearner_native_test_gate', schema_version=3,
                runtime_manifest=declaration['runtime'], source_root=str(source),
                expected_test_ids=leaf['expected_ids'], maximum_wall_seconds=leaf['wall_seconds'],
                asan_options='', cooperative_runtime_capture=True,
                process_limits=dict(memory_bytes=8*1024**3, tasks=128))
            path = output/(leaf['name']+'-gate.json')
            _write(path, spec)
            result = run_native_gate(path, output/leaf['name'])
            rows.append(dict(name=leaf['name'], expected_ids=leaf['expected_ids'], result=result))
            _write(output/'progress.json', dict(rows=rows, scientific_verdict=None))
            self.assertTrue(inspect(output/leaf['name']/'process/contained')['all_processes_closed'])
            self.assertEqual((result['execution'], result['validity'], result['assertion_status']),
                             ('completed', 'valid', 'passed'))
            self.assertEqual(result['inventory']['observed'], len(leaf['expected_ids']))
            self.assertEqual(result['inventory']['failed_test_ids'], [])
        verify_runtime(runtime)
        self.assertEqual(runtime['source_closure'], source_closure(source))
        _write(output/'index.json', dict(kind='timelearner_rejected_length_native_revalidation',
            schema_version=1, rows=rows, completed_cpp_cases=len(expected), original_failure_retained=True,
            same_frozen_binary=True, fresh_sdk_build=False, scientific_verdict=None))
