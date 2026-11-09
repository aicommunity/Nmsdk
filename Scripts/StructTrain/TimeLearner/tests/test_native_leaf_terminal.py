"""Production Worker.gate outcome handling; controlled metadata, no native claim."""
import copy
import json
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
import unittest

from .. import native_acceptance_worker as subject


class NativeLeafTerminalTest(unittest.TestCase):
    def invoke(self, result, xml, expected_reason=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            worker = object.__new__(subject.Worker)
            worker.out = root
            worker.source = root/'source'
            worker.runtime = root/'runtime'
            worker.paths = {'build':root/'build'}
            worker.job = {'limits':{'whole_wall_seconds':60,
                'leaf_memory_bytes':128*1024**2, 'leaf_tasks':16}, 'asan_options':None}
            worker.started = time.monotonic()
            worker.guard = lambda:None
            worker.gates = 0
            worker.observed, worker.failed, worker.passed = [], [], []
            worker.expected = ['Suite/First', 'Suite/Second']

            def run_gate(spec, output):
                output.mkdir()
                if xml is not None:
                    (output/'native.xml').write_text(xml, encoding='utf-8')
                request = output/'process/contained/request.json'
                request.parent.mkdir(parents=True)
                request.write_text(json.dumps({'environment':{
                    'TIMELEARNER_COMPOSITE_OUTPUT':str(output/'native-composite')}}))
                return copy.deepcopy(result)

            worker.api = (SimpleNamespace(snapshot=lambda *args:{}),
                          SimpleNamespace(run_native_gate=run_gate))
            leaf = {'name':'leaf', 'expected_ids':worker.expected, 'wall_seconds':30}
            if expected_reason:
                with self.assertRaisesRegex(ValueError, expected_reason):
                    worker.gate(leaf)
            else:
                worker.gate(leaf)
            return (json.loads((root/'leaf-actual-tests.json').read_bytes()),
                    worker.observed, worker.failed, worker.passed,
                    (root/'progress.json').exists())

    @staticmethod
    def result(execution='completed', valid=True):
        return {'execution':execution,
                'validity':'valid' if valid else 'incomplete_test_observation',
                'assertion_status':'passed' if valid else 'not_assessed',
                'reason':None if valid else 'native_gate_loaded_runtime_missing',
                'inventory':{'observed':2, 'failed_test_ids':[]} if valid else None}

    @staticmethod
    def xml(second_failure=False):
        failure = '<failure/>' if second_failure else ''
        return ('<testsuites><testsuite>'
            '<testcase classname="Suite" name="First" status="run" result="completed"/>'
            '<testcase classname="Suite" name="Second" status="run" result="completed">'+
            failure+'</testcase></testsuite></testsuites>')

    def test_timeout_without_xml_preserves_original_reason_and_no_invented_cases(self):
        record, observed, failed, passed, progress = self.invoke(
            self.result('timeout', False), None, 'native_gate_rejected:leaf:timeout')
        self.assertEqual(record['gate_reason'], 'native_gate_loaded_runtime_missing')
        self.assertEqual(record['observation_error']['type'], 'FileNotFoundError')
        self.assertEqual(record['unobserved_expected_ids'], ['Suite/First', 'Suite/Second'])
        self.assertEqual((observed, failed, passed, progress), ([], [], [], False))
        self.assertIsNone(record['scientific_verdict'])

    def test_process_error_without_xml_is_not_reported_as_timeout_or_file_failure(self):
        record, *rest = self.invoke(self.result('process_error', False), None,
                                   'native_gate_rejected:leaf:process_error')
        self.assertEqual(record['gate_execution'], 'process_error')
        self.assertEqual(rest, [[], [], [], False])

    def test_timeout_with_partial_xml_keeps_only_completed_case(self):
        xml = ('<testsuites><testcase classname="Suite" name="First" status="run" result="completed"/>'
               '<testcase classname="Suite" name="Second" status="notrun" result="suppressed"/></testsuites>')
        record, observed, _, passed, progress = self.invoke(
            self.result('timeout', False), xml, 'native_gate_rejected:leaf:timeout')
        self.assertEqual(observed, ['Suite/First'])
        self.assertEqual(passed, observed)
        self.assertEqual(record['not_completed_ids'], ['Suite/Second'])
        self.assertEqual(record['unobserved_expected_ids'], ['Suite/Second'])
        self.assertFalse(progress)

    def test_timeout_with_truncated_xml_keeps_parse_error_separate(self):
        record, observed, _, passed, _ = self.invoke(
            self.result('timeout', False), '<testsuites>', 'native_gate_rejected:leaf:timeout')
        self.assertEqual(record['observation_error']['type'], 'ParseError')
        self.assertEqual((observed, passed), ([], []))

    def test_claimed_success_without_xml_cannot_pass(self):
        record, _, _, passed, progress = self.invoke(self.result(), None, 'native_JUnit_unreadable:leaf')
        self.assertEqual(record['gate_execution'], 'completed')
        self.assertEqual((passed, progress), ([], False))

    def test_claimed_success_with_corrupt_xml_cannot_pass(self):
        record, _, _, passed, progress = self.invoke(self.result(), '<bad>', 'native_JUnit_unreadable:leaf')
        self.assertEqual(record['observation_error']['type'], 'ParseError')
        self.assertEqual((passed, progress), ([], False))

    def test_completed_gate_requires_actual_matching_case_ids(self):
        record, observed, failed, passed, progress = self.invoke(self.result(), self.xml())
        self.assertEqual(observed, ['Suite/First', 'Suite/Second'])
        self.assertEqual(passed, observed)
        self.assertEqual(failed, [])
        self.assertEqual(record['unobserved_expected_ids'], [])
        self.assertIsNone(record['observation_error'])
        self.assertTrue(progress)

    def test_failed_case_is_recorded_even_if_gate_claims_success(self):
        record, observed, failed, passed, progress = self.invoke(
            self.result(), self.xml(True), 'actual_JUnit_selection_mismatch')
        self.assertEqual(observed, ['Suite/First', 'Suite/Second'])
        self.assertEqual(failed, ['Suite/Second'])
        self.assertEqual(passed, ['Suite/First'])
        self.assertFalse(progress)

    def test_duplicate_case_does_not_raise_passed_count(self):
        xml = self.xml().replace('name="Second"', 'name="First"')
        record, observed, failed, passed, progress = self.invoke(
            self.result(), xml, 'native_JUnit_unreadable:leaf')
        self.assertEqual(record['observation_error']['reason'], 'duplicate_JUnit_case')
        self.assertEqual((observed, failed, passed, progress), ([], [], [], False))


if __name__ == '__main__':
    unittest.main()
