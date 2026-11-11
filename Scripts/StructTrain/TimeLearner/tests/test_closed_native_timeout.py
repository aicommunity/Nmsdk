"""Closed timeout artifact interpretation; real files, no native execution claim."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from ..closed_native_collection import verify_native_observations
from ..native_evidence import EvidenceError


class ClosedNativeTimeoutTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix='native-timeout-observation-')
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve()
        self.plan = [{'name':'complete', 'expected_ids':['Suite/First', 'Suite/Second']},
                     {'name':'stopped', 'expected_ids':['Suite/Third']}]
        self.children = {'complete':{}, 'stopped':{}}
        self.incomplete = {'stopped':{'execution':'timeout', 'gate_reason':'native_gate_loaded_runtime_missing',
                                    'junit_state':'missing', 'record_state':'missing'}}
        self.write('complete/native.xml', '<testsuites>'
            '<testcase classname="Suite" name="First" status="run" result="completed"/>'
            '<testcase classname="Suite" name="Second" status="run" result="completed"><failure/></testcase>'
            '</testsuites>', raw=True)
        self.write('complete-actual-tests.json', {'source':'native.xml',
            'observed_ids':['Suite/First','Suite/Second'], 'failed_ids':['Suite/Second'], 'not_completed_ids':[]})
        self.gate = {'kind':'timelearner_native_test_gate_result', 'schema_version':1, 'execution':'timeout',
                     'validity':'incomplete_test_observation', 'assertion_status':'not_assessed',
                     'reason':'native_gate_loaded_runtime_missing', 'inventory':None, 'scientific_verdict':None}
        self.write('stopped-result.json', self.gate)
        self.write('stopped/result.json', self.gate)
        self.write('stopped/process/result.json', {'execution':'timeout', 'all_processes_closed':True})

    def write(self, relative, value, *, raw=False):
        path = self.root/relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value if raw else json.dumps(value), encoding='utf-8')

    def verify(self):
        return verify_native_observations(self.root, self.plan, self.children, self.incomplete)

    def test_closed_timeout_without_xml_keeps_only_actual_completed_cases(self):
        self.assertEqual(self.verify(), (['Suite/First','Suite/Second'], ['Suite/Second']))
        self.assertFalse((self.root/'stopped/native.xml').exists())
        self.assertFalse((self.root/'stopped-actual-tests.json').exists())

    def test_legacy_complete_junit_and_failed_case_contract_is_unchanged(self):
        self.assertEqual(verify_native_observations(self.root, self.plan, {'complete':{}}),
                         (['Suite/First','Suite/Second'], ['Suite/Second']))

    def test_legacy_path_does_not_infer_empty_observation_for_missing_xml(self):
        with self.assertRaises(FileNotFoundError):
            verify_native_observations(self.root, self.plan, self.children)

    def test_claimed_timeout_requires_matching_original_gate_copies(self):
        bad = deepcopy(self.gate); bad['reason'] = 'different-outcome'
        self.write('stopped/result.json', bad)
        with self.assertRaisesRegex(EvidenceError, 'timeout_outcome_changed'):
            self.verify()

    def test_timeout_must_agree_with_actual_process_result_and_closed_group(self):
        for process in ({'execution':'completed','all_processes_closed':True},
                        {'execution':'timeout','all_processes_closed':False}):
            self.write('stopped/process/result.json', process)
            with self.subTest(process=process), self.assertRaisesRegex(EvidenceError, 'timeout_outcome_changed'):
                self.verify()

    def test_newly_present_xml_cannot_be_ignored_to_keep_old_timeout_declaration(self):
        self.write('stopped/native.xml', '<testsuites/>', raw=True)
        with self.assertRaisesRegex(EvidenceError, 'timeout_xml_state_changed'):
            self.verify()

    def test_corrected_worker_empty_record_is_preserved_without_promoting_expected_ids(self):
        self.incomplete['stopped']['record_state'] = 'present'
        record = {'source':'native.xml', 'observed_ids':[], 'failed_ids':[], 'not_completed_ids':[],
                  'unobserved_expected_ids':['Suite/Third'], 'gate_execution':'timeout',
                  'gate_validity':'incomplete_test_observation', 'gate_reason':self.gate['reason'],
                  'observation_error':{'type':'FileNotFoundError', 'reason':'original XML not written'},
                  'scientific_verdict':None}
        self.write('stopped-actual-tests.json', record)
        self.assertEqual(self.verify(), (['Suite/First','Suite/Second'], ['Suite/Second']))
        record['observed_ids'] = ['Suite/Third']
        self.write('stopped-actual-tests.json', record)
        with self.assertRaisesRegex(EvidenceError, 'timeout_invented_cpp_observation'):
            self.verify()

    def test_added_actual_record_requires_an_explicit_new_frozen_declaration(self):
        self.write('stopped-actual-tests.json', {})
        with self.assertRaisesRegex(EvidenceError, 'timeout_record_state_changed'):
            self.verify()

    def test_unknown_child_or_unimplemented_timeout_dialect_is_rejected(self):
        self.incomplete['undeclared'] = deepcopy(self.incomplete['stopped'])
        with self.assertRaisesRegex(EvidenceError, 'incomplete_child_scope'):
            self.verify()
        del self.incomplete['undeclared']
        self.incomplete['stopped']['execution'] = 'completed'
        with self.assertRaisesRegex(EvidenceError, 'incomplete_child_contract'):
            self.verify()


if __name__ == '__main__':
    unittest.main()
