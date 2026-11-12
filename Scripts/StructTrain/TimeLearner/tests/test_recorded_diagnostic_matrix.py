"""Strict diagnostic declarations; no model execution is inferred here."""
from copy import deepcopy
import unittest

from ..native_data_checks import validate_request
from .test_native_data_checks import declaration


def diagnostic_request():
    value = declaration();value.update(schema_version=2, operation='diagnostic-evaluate',
        matrix=dict(parameters_name='phasea.xml', observations_name='phasea.csv', revision='a'*40))
    value['inputs'] = [dict(name=n, path='/media/user/Data/TimeLearnerRefactor/input/'+n,
                           bytes=100, sha256='b'*64)
                       for n in ('phasea.xml', 'phasea.csv', 'classic.qz', 'classic-summary.json',
                                 'branch.qz', 'branch-summary.json')]
    value['cases'] = [dict(name=role, source_name=role+'.qz', summary_name=role+'-summary.json',
                          source_raw_bytes=1000, source_raw_sha256='c'*64)
                      for role in ('classic', 'branch')]
    return value


class RecordedDiagnosticMatrixDeclarationTest(unittest.TestCase):
    def test_explicit_diagnostic_request_keeps_two_finite_children(self):
        value = diagnostic_request();self.assertEqual(validate_request(value), value)
        self.assertEqual([r['name'] for r in value['cases']], ['classic', 'branch'])

    def test_training_calibration_and_ordinary_evaluation_are_not_authorized(self):
        for operation in ('train', 'calibrate', 'evaluate', 'export', None):
            value = diagnostic_request();value['operation'] = operation
            with self.subTest(operation=operation), self.assertRaisesRegex(ValueError, 'diagnostic_operation'):
                validate_request(value)

    def test_raw_model_size_and_digest_are_explicit_and_bounded(self):
        for change in (dict(source_raw_bytes=True), dict(source_raw_bytes=0),
                       dict(source_raw_bytes=256*1024**2+1), dict(source_raw_sha256='bad')):
            value = diagnostic_request();value['cases'][0].update(change)
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, 'raw_binding'):
                validate_request(value)

    def test_no_unbound_missing_or_reused_input_role(self):
        for mode in ('missing', 'extra', 'reused', 'untyped'):
            value = diagnostic_request()
            if mode == 'missing':value['cases'][0]['source_name'] = 'missing.qz'
            elif mode == 'extra':value['inputs'].append(dict(name='extra', path='/media/user/Data/TimeLearnerRefactor/input/extra', bytes=1, sha256='d'*64))
            elif mode == 'reused':value['cases'][0]['summary_name'] = 'classic.qz'
            else:value['cases'][0]['source_name'] = []
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, 'input_roles'):
                validate_request(value)

    def test_case_name_cannot_escape_or_alias_another_output(self):
        for name in ('../outside', 'a/b', 'BRANCH', None):
            value = diagnostic_request();value['cases'][0]['name'] = name
            with self.subTest(name=name), self.assertRaises(ValueError):validate_request(value)

    def test_unknown_case_fields_and_missing_cases_are_rejected(self):
        for cases in ([], [dict(name='classic')], diagnostic_request()['cases']*2):
            value = diagnostic_request();value['cases'] = cases
            with self.subTest(size=len(cases)), self.assertRaisesRegex(ValueError, 'diagnostic_cases'):
                validate_request(value)
        value = diagnostic_request();value['cases'][0]['threshold'] = .1
        with self.assertRaisesRegex(ValueError, 'diagnostic_cases'):validate_request(value)

    def test_matrix_requires_exact_git_revision_and_bound_source_roles(self):
        for change in (dict(revision='HEAD'), dict(parameters_name='missing.xml'),
                       dict(observations_name=[]), dict(extra='command')):
            value = diagnostic_request();value['matrix'].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):validate_request(value)

    def test_legacy_test_request_cannot_acquire_diagnostic_fields(self):
        value = diagnostic_request();value['schema_version'] = 1
        with self.assertRaisesRegex(ValueError, 'request_schema'):validate_request(value)
        value = diagnostic_request();value['environment'] = {}
        with self.assertRaisesRegex(ValueError, 'request_schema'):validate_request(value)

    def test_single_case_requires_exactly_its_own_inputs(self):
        value = diagnostic_request();value['cases'] = value['cases'][:1]
        value['inputs'] = [r for r in value['inputs'] if not r['name'].startswith('branch')]
        self.assertEqual(validate_request(value), value)
        before = deepcopy(value);validate_request(value);self.assertEqual(value, before)
