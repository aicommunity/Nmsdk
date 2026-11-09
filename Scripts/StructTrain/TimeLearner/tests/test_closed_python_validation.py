"""Synthetic metadata regressions only; no real40/73 or native/model attestation."""
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import sqlite3
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from Scripts.StructTrain.TimeLearner import closed_python_validation as subject
from Scripts.StructTrain.TimeLearner import collector_provenance as provenance
from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations, ReservationError
from Scripts.StructTrain.TimeLearner.runtime import digest_json


IDS = ['Scripts.StructTrain.TimeLearner.tests.test_synthetic.Example.test_a',
       'Scripts.StructTrain.TimeLearner.tests.test_synthetic.Example.test_b']


def fixture(failed=False):
    expected = {'suite_id':'synthetic-metadata', 'package_fingerprint':'a'*64, 'test_ids':list(IDS),
        'failures':[IDS[1]] if failed else [], 'errors':[], 'skipped':[],
        'diagnostic_fragments':{IDS[1]:['AssertionError: synthetic marker']} if failed else {},
        'gate_outcome':'failed' if failed else 'passed', 'controller_execution':'process_error' if failed else 'completed',
        'controller_returncode':1 if failed else 0, 'worker_operation_passed':not failed}
    suite = {'kind':'timelearner_python_validation_suite', 'schema_version':1, 'suite_id':expected['suite_id'],
        'package_fingerprint':expected['package_fingerprint'], 'modules':['Scripts.StructTrain.TimeLearner.tests.test_synthetic'],
        'expected_test_ids':list(IDS), 'fixtures':{}}
    result = {'kind':'timelearner_python_validation_result', 'schema_version':1, 'suite_id':expected['suite_id'],
        'package_fingerprint':expected['package_fingerprint'], 'execution':'completed', 'assertion_status':expected['gate_outcome'],
        'expected_test_ids':list(IDS), 'executed_tests':2, 'failures':list(expected['failures']), 'errors':[], 'skipped':[],
        'fixtures':{}, 'scientific_verdict':None}
    lines = ['test_a ('+IDS[0]+') ... ok', 'test_b ('+IDS[1]+') ... '+('FAIL' if failed else 'ok'), '']
    if failed:
        lines += ['='*70, 'FAIL: test_b ('+IDS[1]+')', '-'*70, 'Traceback (most recent call last):',
            '  File "synthetic-metadata-only.py", line 1, in test_b', 'AssertionError: synthetic marker', '']
    lines += ['-'*70, 'Ran 2 tests in 0.001s', '', 'FAILED (failures=1)' if failed else 'OK', '']
    controller = {'kind':'timelearner_process_result', 'schema_version':2,
        'execution':expected['controller_execution'], 'returncode':expected['controller_returncode'],
        'runtime_provenance':'loaded_files_captured', 'all_processes_closed':True, 'runtime_fingerprint':'b'*64}
    terminal = {'operation':'python-validation', 'operation_passed':not failed, 'heartbeat_errors':[], 'scientific_verdict':None}
    return expected, suite, result, '\n'.join(lines).encode(), controller, terminal


def manifest():
    expected = fixture()[0]
    unit = 'timelearner-11111111-1111-1111-1111-111111111111.service'
    binding = {'kind':'timelearner_contained_binding', 'schema_version':1, 'request_sha256':'a'*64,
        'unit':unit, 'invocation_id':'b'*32, 'control_group':'/synthetic/'+unit, 'initial_main_pid':123,
        'initial_start_ticks':'456'}
    binding['sha256'] = digest_json(binding)
    repository = {'path':'/tmp/synthetic-metadata-repository', 'commit':'1'*40}
    return {'kind':'timelearner_closed_python_validation_collection', 'schema_version':1,
        'collection_id':'synthetic-metadata-collection', 'worker_host':'M40', 'execution_root':'/media/user/Data/TimeLearnerRefactor',
        'collector_tool':copy.deepcopy(repository), 'job':{'path':'/media/user/Data/TimeLearnerRefactor/readbacks/synthetic-gate',
            'id':'synthetic-gate', 'original_tool':copy.deepcopy(repository), 'source':copy.deepcopy(repository),
            'plan':copy.deepcopy(repository), 'binding':binding, 'lease_token':'synthetic-token',
            'request_sha256':'a'*64, 'suite_sha256':'b'*64}, 'expected':expected, 'files':[],
        'git':[{'role':'synthetic-reference', 'repository':repository['path'], 'repository_head':'1'*40,
            'commit':'1'*40, 'path':'metadata.json', 'git_blob':'2'*40, 'expected_bytes':1,
            'expected_sha256':'3'*64, 'maximum_bytes':1}], 'projections':[], 'fixture_reference_roles':[],
        'extra_metadata_note':'', 'limits':{'maximum_capture_bytes':1024**2, 'maximum_git_bytes':1024**2,
            'minimum_free_bytes':512*1024**2, 'maximum_output_bytes':16*1024**2}}


def released():
    return {'token':'synthetic', 'job_id':'synthetic', 'owner':{'pid':123}, 'resources':[{'path':'synthetic'}],
        'state':'released', 'created':1.0, 'deadline':2.0, 'updated':1.5, 'release_note':'synthetic metadata only',
        'heartbeat_expired':False, 'owner_status':'missing', 'inspection_required':False, 'scientific_verdict':None}


class ClosedPythonValidationTest(unittest.TestCase):
    def test_complete_positive_metadata_is_distinct_from_kernel_attestation(self):
        result = subject.validate_python_outcome(*fixture())
        self.assertEqual((result['gate_outcome'], result['passed']), ('passed', 2))
        self.assertFalse(result['kernel_closure_attested'])
        self.assertIsNone(result['scientific_verdict'])

    def test_complete_negative_metadata_retains_failure_and_controller_false(self):
        result = subject.validate_python_outcome(*fixture(True))
        self.assertEqual(result['gate_outcome'], 'failed')
        self.assertEqual(result['failures'], [IDS[1]])
        self.assertEqual(result['passed'], 1)

    def test_unexpected_failure_identifier_is_not_collector_success(self):
        rows = list(fixture(True));rows[2]['failures'] = [IDS[0]]
        with self.assertRaisesRegex(EvidenceError, 'unexpected_failures'):subject.validate_python_outcome(*rows)

    def test_truncated_log_after_last_status_is_rejected(self):
        rows = list(fixture());rows[3] = rows[3].split(b'\n\n')[0]+b'\n'
        with self.assertRaisesRegex(EvidenceError, 'run_count_or_truncation'):subject.validate_python_outcome(*rows)

    def test_wrong_run_count_and_wrong_final_footer_are_rejected(self):
        for before,after in [(b'Ran 2 tests',b'Ran 3 tests'), (b'\nOK\n',b'\nFAILED (failures=1)\n')]:
            rows = list(fixture());rows[3] = rows[3].replace(before,after)
            with self.assertRaises(EvidenceError):subject.validate_python_outcome(*rows)

    def test_negative_log_must_retain_scoped_traceback_and_reason(self):
        for token in (b'Traceback (most recent call last):', b'AssertionError: synthetic marker'):
            rows = list(fixture(True));rows[3] = rows[3].replace(token,b'not retained')
            with self.assertRaisesRegex(EvidenceError, 'diagnostic_missing'):subject.validate_python_outcome(*rows)

    def test_duplicate_or_aliased_log_status_is_rejected(self):
        rows = list(fixture());rows[3] = b'test_a ('+IDS[0].encode()+b') ... ok\n'+rows[3]
        with self.assertRaisesRegex(EvidenceError, 'duplicate_or_alias'):subject.validate_python_outcome(*rows)

    def test_result_missing_fields_and_inconsistent_expected_pass_are_invalid(self):
        rows = list(fixture());del rows[2]['fixtures']
        with self.assertRaisesRegex(EvidenceError, 'result_schema'):subject.validate_python_outcome(*rows)
        rows = list(fixture(True));rows[0]['gate_outcome'] = 'passed'
        with self.assertRaisesRegex(EvidenceError, 'not_consistent'):subject.validate_python_outcome(*rows)

    def test_copied_suite_and_foreign_controller_runtime_are_rejected(self):
        expected,suite,result,_,controller,_ = fixture()
        copied = copy.deepcopy(suite);copied['suite_id'] = 'foreign'
        with self.assertRaisesRegex(EvidenceError, 'copied_suite_changed'):
            subject.validate_saved_joins(suite,copied,result,controller,{'returncode':0},{'runtime_fingerprint':'b'*64},{},{})
        controller['runtime_fingerprint'] = 'c'*64
        with self.assertRaisesRegex(EvidenceError, 'controller_runtime_changed'):
            subject.validate_saved_joins(suite,suite,result,controller,{'returncode':0},{'runtime_fingerprint':'b'*64},{},{})

    def test_result_fixture_and_child_process_outcome_joins_are_checked(self):
        _,suite,result,_,controller,_ = fixture()
        result['fixtures'] = {'foreign':{}}
        with self.assertRaisesRegex(EvidenceError, 'result_fixture_changed'):
            subject.validate_saved_joins(suite,suite,result,controller,{'returncode':0},{'runtime_fingerprint':'b'*64},{},{})
        result['fixtures'] = {}
        with self.assertRaisesRegex(EvidenceError, 'validation_process_outcome'):
            subject.validate_saved_joins(suite,suite,result,controller,{'returncode':True},{'runtime_fingerprint':'b'*64},{},{})

    def test_immutable_lease_identity_excludes_observation_fields_only(self):
        before = released();after = copy.deepcopy(before)
        after.update(heartbeat_expired=True, owner_status='identity_live')
        subject.compare_released_lease(before,after)
        self.assertFalse(before['heartbeat_expired'])
        after['release_note'] = 'changed'
        with self.assertRaisesRegex(EvidenceError, 'lease_changed'):subject.compare_released_lease(before,after)

    def test_held_lease_and_unknown_persisted_drift_are_not_exempted(self):
        before = released();after = copy.deepcopy(before);after['state'] = 'held'
        with self.assertRaisesRegex(EvidenceError, 'not_released'):subject.compare_released_lease(before,after)
        after = copy.deepcopy(before);after['new_persisted_field'] = 1
        with self.assertRaisesRegex(EvidenceError, 'lease_changed'):subject.compare_released_lease(before,after)

    def test_sorted_key_serialization_preserves_explicit_projection_array(self):
        patterns = ['/z/','/a/','/.gitignore']
        value = json.loads(json.dumps({'z':0,'patterns':patterns,'a':1},sort_keys=True))
        self.assertEqual(subject.validate_projection_patterns(patterns,value['patterns']),patterns)

    def test_projection_map_and_reordered_array_are_rejected(self):
        with self.assertRaises(EvidenceError):subject.validate_projection_patterns({'/a/':1},['/a/'])
        with self.assertRaises(EvidenceError):subject.validate_projection_patterns(['/z/','/a/'],['/a/','/z/'])

    def test_synthetic_manifest_has_strict_missing_field_and_boolean_budget_checks(self):
        self.assertEqual(subject.validate_manifest(manifest())['expected']['gate_outcome'],'passed')
        value = manifest();del value['job']['source']
        with self.assertRaises(EvidenceError):subject.validate_manifest(value)
        value = manifest();value['limits']['maximum_git_bytes'] = True
        with self.assertRaises(EvidenceError):subject.validate_manifest(value)

    def test_opaque_sqlite_role_requires_note_and_does_not_mint_attestation(self):
        value = manifest();value['files'] = [{'role':'case-db', 'root':'/tmp/synthetic-extra',
            'relative_path':'case.sqlite3', 'expected_bytes':8, 'expected_sha256':'a'*64,
            'maximum_bytes':8, 'staged_name':'case-db', 'archive_path':'extra/case.sqlite3', 'purpose':'opaque_extra'}]
        with self.assertRaisesRegex(EvidenceError, 'opaque_reason_required'):subject.validate_manifest(value)
        value['extra_metadata_note'] = 'Synthetic opaque SQLite bytes; no nested kernel claim.'
        self.assertEqual(subject.validate_manifest(value)['files'][0]['purpose'],'opaque_extra')

    def test_invalid_public_prepared_value_never_creates_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);output = root/'output'
            fake = subject.PreparedClosedCollection(root/'missing.json','a'*64,{},None,None,{},{},{},{},{},{},{},{},())
            with self.assertRaises((EvidenceError,OSError)):subject.collect_prepared(fake,output)
            self.assertFalse(output.exists())

    def test_materialization_uses_real_helper_correct_parent_and_frozen_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);source = root/'input';source.write_bytes(b'original metadata')
            role = provenance.RequiredFileRole('extra',root,'input',17,hashlib.sha256(b'original metadata').hexdigest(),100,'extra')
            captured = provenance.capture_required_file_roles([role]);source.write_bytes(b'changed')
            stage = root/'stage';stage.mkdir();supervisor = mock.Mock();supervisor.materialize.return_value = {}
            prepared = SimpleNamespace(captured=captured,supervisor=supervisor,archive_paths={'extra':'extra/input'})
            paths = subject._materialize_inputs(prepared,stage)
            self.assertEqual(paths['extra/input'].read_bytes(),b'original metadata')
            supervisor.materialize.assert_called_once_with(stage,stage/'supervisor')

    def test_inventory_aggregate_budget_stops_before_next_body_read(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);(root/'a').write_bytes(b'123456');(root/'b').write_bytes(b'123456')
            with mock.patch.object(subject.provenance,'_frozen',wraps=provenance._frozen) as reader:
                with self.assertRaisesRegex(EvidenceError, 'capture_budget'):subject._inventory(root,10)
            self.assertEqual(reader.call_count,1)

    def test_atomic_marker_failure_keeps_partial_object_without_success_name(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);marker = root/'artifact-inventory.json'
            with mock.patch.object(subject.os,'fsync',side_effect=[None,OSError('synthetic finalization failure')]):
                with self.assertRaises(OSError):subject._atomic_marker(marker,{'synthetic':'metadata'})
            self.assertFalse(marker.exists())
            self.assertEqual(len(list(root.glob('*.finalizing-*'))),1)

    def test_existing_marker_is_not_overwritten_by_new_finalization(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory)/'marker.json';marker.write_bytes(b'old')
            with self.assertRaises(FileExistsError):subject._atomic_marker(marker,{'new':'metadata'})
            self.assertEqual(marker.read_bytes(),b'old')

    def test_cli_invalid_manifest_fails_before_output_or_writer_api(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);path = root/'manifest.json';path.write_bytes(b'{"kind":"wrong"}')
            with mock.patch.object(Reservations,'open_existing',side_effect=AssertionError('writer forbidden')):
                with mock.patch('sys.stdout',new=io.StringIO()):
                    status = subject.main(['collect',str(path),'--manifest-sha256',hashlib.sha256(path.read_bytes()).hexdigest(),'--output',str(root/'out')])
            self.assertEqual(status,2);self.assertFalse((root/'out').exists())

    def test_stage_refuses_missing_last_marker_before_git_index_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);output = root/'report';output.mkdir()
            with mock.patch.object(subject.publisher,'stage_artifact_set',side_effect=AssertionError('Git forbidden')):
                with self.assertRaises((EvidenceError,OSError)):subject.stage_collection_artifacts(output,root)

    def test_error_recorded_during_heartbeat_join_blocks_finalization(self):
        errors = [];stop = mock.Mock();thread = mock.Mock();thread.is_alive.return_value = False
        thread.join.side_effect = lambda timeout:errors.append('synthetic late heartbeat failure')
        with self.assertRaisesRegex(EvidenceError, 'after_join'):subject._finish_heartbeat(stop,thread,errors)
        stop.set.assert_called_once()


@unittest.skipUnless(os.name == 'posix','Linux metadata gate only')
class ReadonlyReservationsSnapshotTest(unittest.TestCase):
    def test_real_valid_ledger_read_uses_ro_deferred_select_without_writer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);db = root/'ledger.sqlite3';registry = Reservations(db)
            lease = registry.reserve('synthetic',[{'path':str(root/'owned'),'access':'write'}],ttl_seconds=60)
            registry.release(lease['token'],note='synthetic metadata only')
            original = sqlite3.connect;statements = [];uris = []
            def connect(database,*args,**kwargs):
                uris.append(database);connection = original(database,*args,**kwargs);connection.set_trace_callback(statements.append);return connection
            before = db.read_bytes()
            with mock.patch.object(Reservations,'_transaction',side_effect=AssertionError('writer forbidden')):
                with mock.patch.object(sqlite3,'connect',side_effect=connect):view = Reservations.read_snapshot(db)
            self.assertEqual(view['leases'][0]['token'],lease['token']);self.assertEqual(view['leases'][0]['state'],'released')
            self.assertTrue(all('mode=ro' in str(uri) for uri in uris));self.assertIn('BEGIN',statements)
            for sql in statements:
                normalized = sql.strip().removesuffix(';').strip().upper()
                command = normalized.split(None,1)[0]
                self.assertIn(command,('SELECT','BEGIN','ROLLBACK'))
                if command != 'SELECT':self.assertIn(normalized,('BEGIN','ROLLBACK'))
            self.assertEqual(db.read_bytes(),before)

    def test_valid_read_then_schema_tamper_and_alias_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);db = root/'ledger.sqlite3';Reservations(db)
            self.assertEqual(Reservations.read_snapshot(db)['schema_version'],1)
            alias = root/'alias.sqlite3';alias.symlink_to(db)
            with self.assertRaises(ReservationError):Reservations.read_snapshot(alias)
            with sqlite3.connect(db) as connection:connection.execute("UPDATE metadata SET value='foreign' WHERE key='worker_host'")
            with self.assertRaises(ReservationError):Reservations.read_snapshot(db)

    def test_missing_ledger_read_never_creates_database(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'missing.sqlite3'
            with self.assertRaises(ReservationError):Reservations.read_snapshot(path)
            self.assertFalse(path.exists())

    def test_readonly_capacity_and_managed_policy_are_not_inferred_or_migrated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);capacity = {'slots':2,'memory_bytes':1024,'disk_bytes':2048}
            budget = root/'budget.sqlite3';Reservations(budget,capacity=capacity)
            self.assertEqual(Reservations.read_snapshot(budget)['capacity'],capacity)
            managed = root/'managed.sqlite3';quantities = {**capacity,'tasks':4}
            Reservations(managed,capacity=quantities,managed_units=True)
            with self.assertRaises(ReservationError):Reservations.read_snapshot(managed)
            view = Reservations.read_snapshot(managed,managed_units=True)
            self.assertEqual(view['schema_version'],3);self.assertEqual(view['managed_unit_intents'],[])
            self.assertEqual(view['capacity'],quantities)
