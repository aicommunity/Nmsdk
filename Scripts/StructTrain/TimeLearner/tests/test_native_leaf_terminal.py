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
    def invoke(self, result, xml, expected_reason=None, previous=None):
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
            previous = list(previous or [])
            worker.gates = len(previous)
            worker.observed, worker.failed, worker.passed = list(previous), [], list(previous)
            ids = ['Suite/First', 'Suite/Second']
            worker.expected = previous+ids

            def run_gate(spec, output):
                starting = json.loads((root/'progress.json').read_bytes())
                self.assertEqual(starting['current_gate_status'], 'running')
                self.assertEqual(starting['completed_cases'], len(previous))
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
            leaf = {'name':'leaf', 'expected_ids':ids, 'wall_seconds':30}
            if expected_reason:
                with self.assertRaisesRegex(ValueError, expected_reason):
                    worker.gate(leaf)
            else:
                worker.gate(leaf)
            return (json.loads((root/'leaf-actual-tests.json').read_bytes()),
                    worker.observed, worker.failed, worker.passed,
                    json.loads((root/'progress.json').read_bytes()))

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
        self.assertEqual((observed, failed, passed), ([], [], []))
        self.assertEqual(progress['current_gate_status'], 'rejected')
        self.assertEqual(progress['completed_cases'], 0)
        self.assertEqual(progress['completed_leaf_gates'], 1)
        self.assertNotIn('closed_leaf_gates', progress)
        self.assertIsNone(record['scientific_verdict'])

    def test_process_error_without_xml_is_not_reported_as_timeout_or_file_failure(self):
        record, *rest = self.invoke(self.result('process_error', False), None,
                                   'native_gate_rejected:leaf:process_error')
        self.assertEqual(record['gate_execution'], 'process_error')
        self.assertEqual(rest[:3], [[], [], []])
        self.assertEqual(rest[3]['current_gate_status'], 'rejected')

    def test_timeout_with_partial_xml_keeps_only_completed_case(self):
        xml = ('<testsuites><testcase classname="Suite" name="First" status="run" result="completed"/>'
               '<testcase classname="Suite" name="Second" status="notrun" result="suppressed"/></testsuites>')
        record, observed, _, passed, progress = self.invoke(
            self.result('timeout', False), xml, 'native_gate_rejected:leaf:timeout')
        self.assertEqual(observed, ['Suite/First'])
        self.assertEqual(passed, observed)
        self.assertEqual(record['not_completed_ids'], ['Suite/Second'])
        self.assertEqual(record['unobserved_expected_ids'], ['Suite/Second'])
        self.assertEqual(progress['current_gate_status'], 'rejected')
        self.assertEqual(progress['passed_cases'], 1)

    def test_timeout_with_truncated_xml_keeps_parse_error_separate(self):
        record, observed, _, passed, _ = self.invoke(
            self.result('timeout', False), '<testsuites>', 'native_gate_rejected:leaf:timeout')
        self.assertEqual(record['observation_error']['type'], 'ParseError')
        self.assertEqual((observed, passed), ([], []))

    def test_claimed_success_without_xml_cannot_pass(self):
        record, _, _, passed, progress = self.invoke(self.result(), None, 'native_JUnit_unreadable:leaf')
        self.assertEqual(record['gate_execution'], 'completed')
        self.assertEqual(passed, [])
        self.assertEqual(progress['current_gate_status'], 'rejected')
        self.assertEqual(progress['observation_error']['type'], 'FileNotFoundError')

    def test_claimed_success_with_corrupt_xml_cannot_pass(self):
        record, _, _, passed, progress = self.invoke(self.result(), '<bad>', 'native_JUnit_unreadable:leaf')
        self.assertEqual(record['observation_error']['type'], 'ParseError')
        self.assertEqual(passed, [])
        self.assertEqual(progress['current_gate_status'], 'rejected')
        self.assertEqual(progress['observation_error']['type'], 'ParseError')

    def test_completed_gate_requires_actual_matching_case_ids(self):
        record, observed, failed, passed, progress = self.invoke(self.result(), self.xml())
        self.assertEqual(observed, ['Suite/First', 'Suite/Second'])
        self.assertEqual(passed, observed)
        self.assertEqual(failed, [])
        self.assertEqual(record['unobserved_expected_ids'], [])
        self.assertIsNone(record['observation_error'])
        self.assertEqual(progress['current_gate_status'], 'accepted')
        self.assertEqual(progress['schema_version'], 2)
        self.assertEqual(progress['completed_cases'], 2)
        self.assertIsNone(progress['validation_reason'])
        self.assertIsNone(progress['scientific_verdict'])

    def test_failed_case_is_recorded_even_if_gate_claims_success(self):
        record, observed, failed, passed, progress = self.invoke(
            self.result(), self.xml(True), 'actual_JUnit_selection_mismatch')
        self.assertEqual(observed, ['Suite/First', 'Suite/Second'])
        self.assertEqual(failed, ['Suite/Second'])
        self.assertEqual(passed, ['Suite/First'])
        self.assertEqual(progress['current_gate_status'], 'rejected')
        self.assertEqual(progress['failed_test_ids'], ['Suite/Second'])
        self.assertEqual(progress['validation_reason'], 'actual_JUnit_selection_mismatch')

    def test_duplicate_case_does_not_raise_passed_count(self):
        xml = self.xml().replace('name="Second"', 'name="First"')
        record, observed, failed, passed, progress = self.invoke(
            self.result(), xml, 'native_JUnit_unreadable:leaf')
        self.assertEqual(record['observation_error']['reason'], 'duplicate_JUnit_case')
        self.assertEqual((observed, failed, passed), ([], [], []))
        self.assertEqual(progress['current_gate_status'], 'rejected')
        self.assertEqual(progress['completed_cases'], 0)

    def test_actual_failed_gate_updates_progress_before_rejecting(self):
        result = self.result()
        result['assertion_status'] = 'failed'
        result['inventory']['failed_test_ids'] = ['Suite/Second']
        _, _, _, _, progress = self.invoke(result, self.xml(True), 'native_gate_rejected:leaf')
        self.assertEqual(progress['completed_cases'], 2)
        self.assertEqual(progress['passed_cases'], 1)
        self.assertEqual(progress['failed_test_ids'], ['Suite/Second'])
        self.assertEqual(progress['current_gate_assertion_status'], 'failed')
        self.assertEqual(progress['current_gate_status'], 'rejected')

    def test_rejected_runtime_with_passing_xml_never_admits_gate(self):
        _, _, _, _, progress = self.invoke(self.result(valid=False), self.xml(), 'native_gate_rejected:leaf')
        self.assertEqual(progress['passed_cases'], 2)
        self.assertEqual(progress['current_gate_validity'], 'incomplete_test_observation')
        self.assertEqual(progress['current_gate_status'], 'rejected')
        self.assertIsNone(progress['scientific_verdict'])

    def test_failed_next_leaf_preserves_previous_counts_without_claiming_closure(self):
        _, observed, _, passed, progress = self.invoke(
            self.result('timeout', False), None, 'native_gate_rejected:leaf:timeout', ['Earlier/Pass'])
        self.assertEqual(observed, ['Earlier/Pass'])
        self.assertEqual(passed, ['Earlier/Pass'])
        self.assertEqual(progress['completed_cases'], 1)
        self.assertEqual(progress['passed_cases'], 1)
        self.assertEqual(progress['completed_leaf_gates'], 2)
        self.assertEqual(progress['expected_cases'], 3)
        self.assertEqual(progress['current_gate'], 'leaf')
        self.assertEqual(progress['current_gate_status'], 'rejected')
        self.assertNotIn('closed_leaf_gates', progress)


if __name__ == '__main__':
    unittest.main()
