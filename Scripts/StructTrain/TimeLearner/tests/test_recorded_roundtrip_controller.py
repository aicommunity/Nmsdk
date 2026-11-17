"""Controller/DATA joins use case identity, independent of execution order."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from ..native_evidence import EvidenceError
from ..recorded_roundtrip_evidence import audit_roundtrip_controller


class RecordedRoundtripControllerTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        self.native, self.controller = root/'native', root/'controller'
        self.original = root/'original-job'
        self.cases = [
            dict(name=role, test_id='NativeRecordedRecoveryArchive/'+role.title()+'FullDomainN4Roundtrip')
            for role in ('classic', 'branch')]
        self.request = dict(kind='timelearner_native_data_checks', schema_version=1,
                            job_id=self.original.name, cases=self.cases)
        outer_binding = dict(unit='test-parent', invocation_id='parent-invocation')
        children = []
        for case in self.cases:
            role = case['name']
            binding = dict(unit='test-'+role, invocation_id=role+'-invocation')
            children.append(dict(directory=str(self.original/role/'process/contained'),
                                 binding=binding,
                                 closure=dict(binding=binding, all_processes_closed=True)))
            self.write(self.native/role/'process/contained/owned-unit.json', binding)
            self.write(self.native/role/'specification.json', dict(expected_test_ids=[case['test_id']]))
            for phase in ('before', 'after'):
                self.write(self.native/role/('data-inputs-'+phase+'.json'), dict(fixture=role))
            suite, name = case['test_id'].split('/')
            (self.native/role/'native.xml').write_text(
                '<testsuites tests="1" disabled="0" failures="0" errors="0">'
                '<testsuite><testcase classname="'+suite+'" name="'+name+'" '
                'status="run" result="completed"/></testsuite></testsuites>', encoding='utf-8')
        self.result = dict(outer_closed=True, reason=None, record_errors=[], children_closed=children,
                           outer_binding=outer_binding)
        self.write(self.controller/'supervisor-result.json', self.result)
        self.write(self.controller/'outer-closure.json',
                   dict(all_processes_closed=True, binding=outer_binding))
        self.write(self.controller/'reservation-final.json', [dict(state='released')])
        for phase in ('before', 'after'):
            self.write(self.native/('source-'+phase+'.json'), dict(commit='fixture-source'))

    @staticmethod
    def write(path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding='utf-8')

    def audit(self, cases):
        self.write(self.controller/'request.json', dict(self.request, cases=cases))
        return audit_roundtrip_controller(self.native, self.controller, original_job_path=self.original)

    def test_both_case_orders_join_identical_complete_evidence(self):
        forward = self.audit(self.cases)
        self.assertEqual(self.audit(list(reversed(self.cases))), forward)
        self.assertEqual(forward['closed_groups'], 3)
        self.assertFalse(forward['native_execution_attested'])
        self.assertIsNone(forward['scientific_verdict'])

    def test_duplicate_missing_foreign_and_mismatched_identities_rejected(self):
        mismatched = copy.deepcopy(self.cases)
        mismatched[0]['test_id'] = mismatched[1]['test_id']
        malformed = [None, {}, self.cases[:1], self.cases*2,
                     [self.cases[0], self.cases[0]], mismatched,
                     [dict(name='unknown', test_id=self.cases[0]['test_id']), self.cases[1]],
                     [dict(self.cases[0], extra=True), self.cases[1]],
                     [dict(name=[], test_id=self.cases[0]['test_id']), self.cases[1]]]
        for cases in malformed:
            with self.subTest(cases=cases), self.assertRaisesRegex(EvidenceError, 'roundtrip_controller_cases'):
                self.audit(cases)

    def test_reversed_order_still_rejects_foreign_child_binding(self):
        result = copy.deepcopy(self.result)
        result['children_closed'][1]['binding'] = dict(unit='neighbouring-job')
        self.write(self.controller/'supervisor-result.json', result)
        with self.assertRaisesRegex(EvidenceError, 'roundtrip_foreign_child_binding'):
            self.audit(list(reversed(self.cases)))

    def test_reversed_order_still_rejects_changed_data(self):
        self.write(self.native/'branch/data-inputs-after.json', dict(fixture='changed'))
        with self.assertRaisesRegex(EvidenceError, 'roundtrip_data_input_changed'):
            self.audit(list(reversed(self.cases)))
