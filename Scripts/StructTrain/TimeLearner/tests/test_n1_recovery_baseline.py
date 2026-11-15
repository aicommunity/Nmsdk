"""Confirm five algorithmic counterexamples on the unchanged accepted N1 binary.

A passing Python check means expected native assertion failures were reproduced.
It never relabels the baseline SDK, training or classification as successful.
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


class N1RejectedRecoveryBaselineTest(unittest.TestCase):
    def test_frozen_baseline_reproduces_all_five_algorithmic_failures(self):
        controls = Path(os.environ['TIMELEARNER_N1_BASELINE_CONTROLS']).resolve(strict=True)
        declaration = load(controls/'declaration.json')
        require(set(declaration) == {'source', 'source_commit', 'pulse_commit', 'runtime',
                'cohort', 'original_controller', 'original_output'}, 'n1_baseline_controls_schema')
        source = Path(declaration['source']).resolve(strict=True)
        before = source_closure(source)
        self.assertEqual(before['root']['head'], declaration['source_commit'])
        self.assertEqual(before['Libraries/Nmsdk-PulseLib']['head'], declaration['pulse_commit'])
        self.assertEqual(declaration['pulse_commit'], '5052cfe1683ca38920b514aedfc3c37f4bd41aef')
        original = Path(declaration['original_output']).resolve(strict=True)
        closed = status(declaration['original_controller'])
        self.assertTrue(closed['result']['outer_closed'])
        self.assertFalse(closed['supervisor_live'])
        self.assertEqual(closed['result']['record_errors'], [])
        terminal = load(original/'terminal.json')
        self.assertTrue(terminal['built'])
        self.assertFalse(terminal['job_validation_passed'])
        expected_names = ['ClassicN1FixedRsExploresBeyondNearestMesh',
            'BranchN1FixedRsExploresBeyondNearestMesh',
            'ClassicN1RejectedWindowExploresFreshRs',
            'BranchN1RejectedWindowExploresFreshRs',
            'BranchN1FourInputsSeparateOnlyUpstreamBank']
        expected = ['NativeCandidateWindowRecovery/'+name for name in expected_names]
        cohort = load(Path(declaration['cohort']))
        self.assertEqual(cohort['selected_ids'], expected)
        self.assertEqual([case for leaf in cohort['runplan'] for case in leaf['expected_ids']], expected)
        self.assertTrue(all(len(leaf['expected_ids']) == 1 for leaf in cohort['runplan']))
        self.assertCountEqual(expected, load(original/'compiled-inventory-crosscheck.json')['expected'])
        runtime = load(Path(declaration['runtime']))
        self.assertEqual(runtime['source_closure'], before)
        verify_runtime(runtime)
        output = Path(os.environ['TMPDIR'])/'n1-recovery-baseline-counterexamples'
        output.mkdir()
        rows = []
        for leaf in cohort['runplan']:
            spec = dict(kind='timelearner_native_test_gate', schema_version=3,
                runtime_manifest=declaration['runtime'], source_root=str(source),
                expected_test_ids=leaf['expected_ids'], maximum_wall_seconds=leaf['wall_seconds'],
                asan_options='', cooperative_runtime_capture=True,
                process_limits=dict(memory_bytes=8*1024**3, tasks=128))
            path = output/(leaf['name']+'-gate.json')
            _write(path, spec)
            result = run_native_gate(path, output/leaf['name'])
            rows.append(dict(name=leaf['name'], expected_ids=leaf['expected_ids'], result=result))
            _write(output/('progress-'+str(len(rows)).zfill(2)+'.json'),
                   dict(rows=rows, scientific_verdict=None))
            self.assertTrue(inspect(output/leaf['name']/'process/contained')['all_processes_closed'])
            self.assertEqual((result['execution'], result['validity'], result['assertion_status']),
                             ('completed', 'valid', 'failed'))
            self.assertEqual(result['inventory']['observed'], 1)
            self.assertEqual(result['inventory']['failed_test_ids'], leaf['expected_ids'])
            cases = list(ET.parse(output/leaf['name']/'native.xml').getroot().iter('testcase'))
            self.assertEqual(len(cases), 1)
            self.assertEqual(cases[0].findall('error'), [])
            self.assertEqual(cases[0].findall('skipped'), [])
            failures = cases[0].findall('failure')
            self.assertTrue(failures)
            messages = [f.attrib.get('message', f.text or '') for f in failures]
            property_name = ('action->parameters.at(active).length' if 'FixedRs' in leaf['expected_ids'][0]
                             else 'action->parameters.at(active).resistance')
            self.assertTrue(any(property_name in message for message in messages), messages)
            self.assertTrue(all('C++ exception' not in message and 'composite_fixture_' not in message
                                for message in messages), messages)
        verify_runtime(runtime)
        self.assertEqual(source_closure(source), before)
        _write(output/'index.json', dict(kind='timelearner_n1_recovery_baseline_counterexamples',
            schema_version=1, rows=rows, completed_cpp_cases=5, expected_native_assertion_failures=5,
            baseline_sdk_passed=False, same_frozen_binary=True, fresh_sdk_build=False,
            scientific_verdict=None))
