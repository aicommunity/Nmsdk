"""Request and filesystem boundaries; no neural or native build fixtures."""
import copy
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from .. import owned_python_job as subject
from ..archive_retirement import snapshot
from ..contained_runner import execute
from ..native_evidence import EvidenceError


def request():
    return {'kind': 'timelearner_owned_python_job', 'schema_version': 1, 'job_id': 'fixture-job',
        'worker_host': 'M40', 'execution_root': '/media/user/Data/TimeLearnerRefactor', 'tool_commit': 'a'*40,
        'limits': {'memory_bytes': 512*1024**2, 'tasks': 32, 'maximum_wall_seconds': 240},
        'disk': {'minimum_free_bytes': 512*1024**2, 'maximum_output_bytes': 256*1024**2},
        'operation': {'kind': 'python-validation', 'source':
            {'path': '/media/user/Data/TimeLearnerRefactor/source-fixture', 'commit': 'b'*40},
            'suite': {'path': '/media/user/Data/TimeLearnerRefactor/requests/suite.json', 'sha256': 'c'*64},
            'fixtures': {}}}


class OwnedPythonJobTest(unittest.TestCase):
    def test_reviewed_typed_request_is_preserved_without_implicit_fields(self):
        value = request();before = copy.deepcopy(value)
        self.assertEqual(subject.validate_request(value), before)
        self.assertEqual(value, before)

    def test_unknown_fields_native_actions_and_path_job_ids_refuse(self):
        for change in [('field', 'surprise'), ('operation', 'native-model'), ('job', '../other')]:
            value = request()
            if change[0] == 'field': value[change[1]] = True
            elif change[0] == 'operation': value['operation']['kind'] = change[1]
            else: value['job_id'] = change[1]
            with self.subTest(change=change), self.assertRaises(EvidenceError):
                subject.validate_request(value)

    def test_invalid_limits_and_boolean_schema_never_clip_to_defaults(self):
        for field, value in [('memory_bytes', 0), ('tasks', True), ('maximum_wall_seconds', float('inf'))]:
            document = request();document['limits'][field] = value
            with self.subTest(field=field), self.assertRaises(EvidenceError):
                subject.validate_request(document)
        document = request();document['schema_version'] = True
        with self.assertRaises(EvidenceError): subject.validate_request(document)

    def test_source_and_input_bindings_require_full_digest_and_absolute_path(self):
        for field, value in [('sha256', 'abc'), ('path', '../suite.json')]:
            document = request();document['operation']['suite'][field] = value
            with self.subTest(field=field), self.assertRaises(EvidenceError): subject.validate_request(document)
        document = request();document['operation']['source']['commit'] = 'HEAD'
        with self.assertRaises(EvidenceError): subject.validate_request(document)

    def test_validation_leases_suite_parent_as_real_directory_tree(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);source = root/'source';source.mkdir()
            requests = root/'requests';requests.mkdir();suite = requests/'suite.json';suite.write_text('{}')
            fixture = root/'fixture';fixture.mkdir();job = root/'job';job.mkdir()
            operation = {'source': {'path': str(source)}, 'suite': {'path': str(suite)},
                         'fixtures': {'TIMELEARNER_CONFIG_CORPUS': str(fixture)}}
            registry = subject.Reservations(root/'registry.sqlite3')
            with patch.object(subject, 'SOURCE', source):
                resources = subject._validation_resources(operation, job)
            lease = registry.reserve('actual-directory-tree-contract', resources)
            try:
                registry.validate_paths(lease['token'])
                self.assertEqual({r['canonical_path'] for r in lease['resources']},
                                 {str(source), str(requests), str(fixture), str(job)})
                self.assertTrue(all(Path(r['canonical_path']).is_dir() for r in lease['resources']))
                self.assertEqual(sum(r['access'] == 'write' for r in lease['resources']), 1)
            finally:
                registry.release(lease['token'], note='Metadata fixture completed; no contained model or build.')

    def test_callbacks_are_checked_before_any_runtime_or_output_side_effect(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ['on_started', 'monitor']:
                with self.subTest(name=name), self.assertRaises(EvidenceError):
                    execute({}, [], root, root/'output', 1, memory_bytes=128*1024**2,
                            tasks=32, **{name: 'not-callable'})
                self.assertEqual(list(root.iterdir()), [])

    def test_closed_observer_pipe_does_not_raise_into_execution_control(self):
        class Broken:
            def write(self, value): raise BrokenPipeError('observer disconnected')
            def flush(self): pass
        with patch.object(subject.sys, 'stdout', Broken()):
            subject._display('structured observation only')
            replacement = subject.sys.stdout
            self.assertFalse(isinstance(replacement, Broken))
            replacement.close()

    def test_callable_hook_failure_stops_only_the_bound_group_and_cannot_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);executable = root/'python';executable.write_bytes(b'not executed')
            binding = {'initial_main_pid': 123, 'initial_start_ticks': '456', 'unit': 'fixture.service',
                       'invocation_id': 'a'*32, 'control_group': '/fixture.service'}
            state = {'ExecMainCode': '1', 'ExecMainStatus': '0'}
            closed = {'all_processes_closed': True, 'state': state}
            def start(manifest, arguments, cwd, output, **kwargs):
                output.mkdir();(output/'request.json').write_text('{}')
                return binding
            def fail(_):
                raise RuntimeError('observer-hook-failure')
            for hook in ('on_started', 'monitor'):
                output = root/hook
                with self.subTest(hook=hook), \
                     patch('Scripts.StructTrain.TimeLearner.contained_runner.verify_runtime', return_value=executable), \
                     patch('Scripts.StructTrain.TimeLearner.contained_runner.contained_process.start', side_effect=start), \
                     patch('Scripts.StructTrain.TimeLearner.contained_runner.contained_process.inspect', return_value=closed), \
                     patch('Scripts.StructTrain.TimeLearner.contained_runner.contained_process.stop', return_value=closed) as stop:
                    manifest = {'loader_environment': {}, 'runtime_fingerprint': 'fixture',
                                'executable': {'sha256': hashlib.sha256(executable.read_bytes()).hexdigest()}}
                    with patch.dict(subject.os.environ, {}, clear=True):
                        result = execute(manifest, [], root, output, 1, memory_bytes=128*1024**2,
                                         tasks=32, **{hook: fail})
                    stop.assert_called_once_with(output/'contained')
                    self.assertEqual(result['execution'], 'process_error')
                    self.assertEqual(result['reason'], 'observer-hook-failure')
                    self.assertTrue(result['all_processes_closed'])

    def test_readbacks_parent_alias_cannot_redirect_owned_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);base = root/'worker';base.mkdir();outside = root/'outside';outside.mkdir()
            (base/'readbacks').symlink_to(outside, target_is_directory=True)
            document = request();document['execution_root'] = str(base);document['worker_host'] = 'fixture-host'
            document['operation']['source']['path'] = str(base/'source')
            document['operation']['suite']['path'] = str(base/'requests/suite.json')
            with patch.object(subject, 'SOURCE', base/'tool'), patch.object(subject.socket, 'gethostname', return_value='fixture-host'):
                with self.assertRaises(EvidenceError): subject._paths(document)
            self.assertEqual(list(outside.iterdir()), [])

    def test_retained_glog_alias_is_lstat_readlink_only_even_when_dangling(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);runtime = root/'runtime-old';logs = runtime/'EventsLog';logs.mkdir(parents=True)
            (runtime/'retained.txt').write_bytes(b'unique retained bytes')
            alias = logs/'NeuroModeler.INFO';alias.symlink_to('unavailable-destination')
            result = snapshot(root, ['runtime-old'])
            self.assertEqual(result['links']['runtime-old']['EventsLog/NeuroModeler.INFO']['link_text'], 'unavailable-destination')
            self.assertTrue(result['links']['runtime-old']['EventsLog/NeuroModeler.INFO']['link_not_followed'])
            self.assertEqual(set(result['regular']['runtime-old']), {'retained.txt'})
            self.assertEqual(result['regular']['runtime-old']['retained.txt']['sha256'], hashlib.sha256(b'unique retained bytes').hexdigest())
            self.assertTrue(alias.is_symlink())

    def git_source(self, root):
        (root/'Scripts').mkdir();(root/'Scripts/fixture.py').write_bytes(b'# source metadata only\n')
        subprocess.run(['git', 'init', '--quiet', str(root)], check=True)
        subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(root), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                        'commit', '--quiet', '-m', 'source metadata fixture'], check=True)
        return subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()

    def test_source_projection_is_verified_against_exact_git_blob_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);commit = self.git_source(root)
            value = subject._source_snapshot(root, commit)
            self.assertEqual(set(value['files']), {'Scripts/fixture.py'})
            self.assertEqual(value['files']['Scripts/fixture.py']['sha256'], hashlib.sha256((root/'Scripts/fixture.py').read_bytes()).hexdigest())
            self.assertFalse(value['SDK_gitlinks_materialized_or_verified'])

    def test_changed_source_or_wrong_epoch_cannot_keep_projection_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);commit = self.git_source(root)
            with self.assertRaises((EvidenceError, subprocess.CalledProcessError)):
                subject._source_snapshot(root, '0'*40)
            (root/'Scripts/fixture.py').write_bytes(b'changed source bytes\n')
            with self.assertRaises(EvidenceError): subject._source_snapshot(root, commit)


if __name__ == '__main__':
    unittest.main()
