"""Strict diagnostic declarations; no model execution is inferred here."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..native_data_checks import validate_request
from .test_native_data_checks import declaration
from ..recorded_diagnostic_matrix import audit_matrix, report_matrix
from ..native_evidence import load


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


class RecordedDiagnosticMatrixJoinTest(unittest.TestCase):
    """Reject misleading closure before reading expensive recorded primary."""
    def setUp(self):
        temporary = tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name);self.data = self.root/'data';self.data.mkdir()
        self.controller = self.root/'controller';self.controller.mkdir()
        self.runtime = self.root/'runtime.json'
        self.runtime.write_bytes(b'{"runtime_fingerprint":"declared","source_closure":{}}')
        request = diagnostic_request()
        request['runtime_manifest']['sha256'] = hashlib.sha256(self.runtime.read_bytes()).hexdigest()
        self.write(self.controller/'request.json', request)
        self.write(self.data/'terminal.json', dict(operation_passed=True, heartbeat_errors=[]))
        self.write(self.controller/'supervisor-result.json', dict(outer_closed=True, reason=None,
            record_errors=[], outer_binding={}, children_closed=[]))
        self.write(self.controller/'outer-closure.json', dict(all_processes_closed=True, binding={}))
        self.write(self.controller/'original-outcome.json',
            dict(kernel_before_stop=dict(state=dict(ExecMainStatus='0', Result='success'))))
        self.write(self.controller/'reservation-final.json', [dict(state='released')])
        for stem in ('source', 'tool'):
            for suffix in ('before', 'after'):self.write(self.data/(stem+'-'+suffix+'.json'), {})

    @staticmethod
    def write(path, value):
        path.write_text(json.dumps(value), encoding='utf-8')

    def audit(self):
        return audit_matrix(self.data, self.controller, self.runtime)

    def test_failed_operation_cannot_be_rescued_by_successful_cleanup(self):
        self.write(self.data/'terminal.json', dict(operation_passed=False, heartbeat_errors=[]))
        with self.assertRaisesRegex(ValueError, 'operation_not_completed'):self.audit()

    def test_explicit_runtime_must_match_original_request_bytes(self):
        self.runtime.write_bytes(b'{}')
        with self.assertRaisesRegex(ValueError, 'pinned_runtime_changed'):self.audit()

    def test_released_outer_group_cannot_replace_missing_case_groups(self):
        with self.assertRaisesRegex(ValueError, 'foreign_or_missing_children'):self.audit()

    def test_unreleased_reservation_refuses_data_acceptance(self):
        self.write(self.controller/'reservation-final.json', [dict(state='held')])
        with self.assertRaisesRegex(ValueError, 'lease_not_released'):self.audit()


class RecordedDiagnosticMatrixPrimaryTest(unittest.TestCase):
    """Opt-in production replay of closed real N4 data, never new training."""
    @classmethod
    def setUpClass(cls):
        cls.primary = Path(os.environ['TIMELEARNER_RECORDED_MATRIX_PRIMARY'])
        cls.controller = Path(os.environ['TIMELEARNER_RECORDED_MATRIX_CONTROLLER'])
        cls.runtime = Path(os.environ['TIMELEARNER_RECORDED_MATRIX_RUNTIME'])/'runtime.json'
        cls.output = Path(os.environ['TMPDIR'])/'recorded-n4-diagnostic-gallery'
        cls.result = report_matrix(cls.primary, cls.controller, cls.runtime, cls.output)

    def test_complete_sixteen_observations_keep_stopped_outcomes(self):
        analysis = self.result['analysis']
        self.assertEqual(analysis['trials'], 16)
        self.assertTrue(analysis['diagnostic_only'])
        self.assertFalse(analysis['training_completed'])
        self.assertIsNone(analysis['scientific_verdict'])
        rows = {r['name']: r for r in analysis['models']}
        self.assertEqual(set(rows), {'classic', 'branch'})
        self.assertEqual(rows['classic']['training_outcome'], 'invalid_observation')
        self.assertEqual(rows['branch']['training_outcome'], 'budget_exhausted')
        for row in rows.values():
            self.assertEqual(row['trial_count'], 8)
            self.assertEqual(row['source_threshold'], 100.)
            self.assertIsNone(row['metrics']['evaluation_verdict'])
            self.assertEqual(row['metrics']['invalid_trial_ids'], [])
            self.assertEqual(row['metrics']['pooled_counts']['targets'], 1)
            self.assertEqual(row['metrics']['pooled_counts']['foils'], 7)

    def test_all_forty_trial_soma_pairs_have_readable_native_views(self):
        from PIL import Image
        total = 0
        for role, expected in (('classic', 32), ('branch', 8)):
            root = self.output/role/'evaluation'
            manifest = load(root/'manifest.json')
            self.assertEqual(manifest['expected_trial_soma_pairs'], expected)
            self.assertEqual(manifest['observed_trial_soma_pairs'], expected)
            self.assertEqual(manifest['missing_observation_ids'], [])
            self.assertEqual(len(manifest['figures']), expected)
            self.assertFalse(manifest['visual_acceptance_complete'])
            for figure in manifest['figures']:
                views = figure['views']
                self.assertTrue(views)
                self.assertTrue(any(v['time_view'] != 'overview' and
                    v['minimum_native_tick_pixels_on_zoom'] >= 8 for v in views))
                for view in views:
                    self.assertFalse(view['downsampling'])
                    self.assertGreater(view['end'], view['begin'])
                    self.assertEqual(len(view['files']), 3)
                    with Image.open(root/view['files'][0]) as image:
                        self.assertEqual(image.size, (1920, 960))
            total += len(manifest['figures'])
        self.assertEqual(total, 40)


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
