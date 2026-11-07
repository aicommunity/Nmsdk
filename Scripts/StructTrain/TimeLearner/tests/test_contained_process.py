"""Actual user-manager/cgroup controls on the two Linux workers; no neural runs."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import shutil
import time
import unittest

from ..contained_process import start, inspect, stop, adopt, _signed
from ..native_evidence import EvidenceError


@unittest.skipUnless(sys.platform == 'linux', 'actual Linux cgroup worker required')
class ContainedProcessTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='timelearner-contained-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.ini = self.root/'app.ini';self.ini.write_text('actual system process; no neural model\n')
        self.outputs = []
        self.addCleanup(self.close_units)

    def close_units(self):
        evidence = os.environ.get('TIMELEARNER_CONTAINED_EVIDENCE_DIR')
        errors = []
        for output in reversed(self.outputs):
            try:
                final = stop(output)
                (output/'test-final-membership.json').write_text(json.dumps(final, indent=2))
            except Exception as error:
                errors.append(str(error))
        if evidence:
            destination = Path(evidence)/self._testMethodName
            destination.mkdir(parents=True, exist_ok=False)
            for path in self.root.rglob('*'):
                if path.is_file() and (path.suffix in ('.json', '.log', '.py') or path.name in ('child', 'start.ack')):
                    target = destination/path.relative_to(self.root);target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(path, target)
        if errors:raise RuntimeError('; '.join(errors))

    def manifest(self, name='sleep.rs2', binary='/bin/sleep'):
        from .test_process_runner import OwnedProcessTest
        return OwnedProcessTest.manifest(self, name, binary)

    def launch(self, arguments=None, *, manifest=None, wall=30):
        output = self.root/('attempt-'+str(len(self.outputs)))
        start(manifest or self.manifest(), arguments or ['20'], self.root, output,
              memory_bytes=128*1024**2, tasks=32, maximum_wall_seconds=wall)
        self.outputs.append(output)
        return output

    def wait(self, callback, timeout=10):
        deadline = time.monotonic()+timeout
        while time.monotonic() < deadline:
            result = callback()
            if result:return result
            time.sleep(.02)
        self.fail('owned cgroup condition did not complete')

    def test_actual_kernel_limits_suffix_binary_and_complete_group_closure(self):
        output = self.launch(['.2'])
        state = inspect(output)
        self.assertEqual(state['memory_max'], 128*1024**2)
        self.assertEqual(state['tasks_max'], 32)
        self.assertTrue(json.loads((output/'request.json').read_text())['executable'].endswith('.rs2'))
        self.wait(lambda:inspect(output)['all_processes_closed'])
        self.assertTrue(stop(output)['all_processes_closed'])
        self.assertNotEqual(inspect(output)['execution'], 'completed')

    def test_nonzero_exit_and_actual_stdout_stderr_are_preserved(self):
        output = self.launch(['-c', 'printf actual_stdout; printf actual_stderr >&2; exit 7'],
                             manifest=self.manifest('console.e05b', '/bin/sh'))
        state = self.wait(lambda:s if (s:=inspect(output))['all_processes_closed'] else None)
        self.assertEqual(state['state']['ExecMainStatus'], '7')
        self.assertEqual((output/'stdout.log').read_text(), 'actual_stdout')
        self.assertEqual((output/'stderr.log').read_text(), 'actual_stderr')

    def test_a_child_in_a_new_session_cannot_outlive_explicit_group_stop(self):
        script = self.root/'fork.py';pidfile = self.root/'child.json'
        script.write_text('import subprocess,time,json\nfrom pathlib import Path\n'
                          'p=subprocess.Popen(["/bin/sleep","20"],start_new_session=True)\n'
                          'Path('+repr(str(pidfile))+').write_text(json.dumps({"pid":p.pid}))\n'
                          'time.sleep(20)\n')
        output = self.launch([str(script)], manifest=self.manifest('python.rs1', sys.executable))
        self.wait(pidfile.exists);pid = json.loads(pidfile.read_text())['pid']
        self.assertTrue(Path('/proc', str(pid)).exists())
        self.assertTrue(stop(output)['all_processes_closed'])
        proc = Path('/proc', str(pid), 'stat')
        self.assertTrue(not proc.exists() or proc.read_text().rsplit(') ',1)[1].split()[0] in ('Z','X'))

    def test_main_exit_does_not_release_a_live_descendant(self):
        script = self.root/'orphan.py';pidfile = self.root/'child'
        script.write_text('import subprocess\nfrom pathlib import Path\n'
                          'p=subprocess.Popen(["/bin/sleep","20"],start_new_session=True)\n'
                          'Path('+repr(str(pidfile))+').write_text(str(p.pid))\n')
        output = self.launch([str(script)], manifest=self.manifest('orphan.rs2', sys.executable))
        self.wait(pidfile.exists)
        state = self.wait(lambda:s if (s:=inspect(output))['state'].get('MainPID') == '0' else None)
        self.assertFalse(state['all_processes_closed']);self.assertEqual(state['execution'], 'running')
        self.assertTrue(stop(output)['all_processes_closed'])

    def test_controller_exit_does_not_make_the_contained_attempt_complete(self):
        manifest = self.manifest();runtime = self.root/'runtime.json';runtime.write_text(json.dumps(manifest))
        output = self.root/'lost-controller'
        code = ('import sys,json,os;from pathlib import Path;from Scripts.StructTrain.TimeLearner.contained_process import start;'
                'start(json.loads(Path(sys.argv[1]).read_text()),["20"],sys.argv[2],sys.argv[3],'
                'memory_bytes=134217728,tasks=32,maximum_wall_seconds=30);os._exit(17)')
        result = subprocess.run([sys.executable, '-c', code, str(runtime), str(self.root), str(output)],
                                cwd=Path(__file__).resolve().parents[4],
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 17, result.stderr)
        self.outputs.append(output)
        self.assertEqual(inspect(output)['execution'], 'running')
        self.assertTrue(stop(output)['all_processes_closed'])

    def test_recovery_of_crash_before_binding_never_starts_the_native_program(self):
        runtime = self.root/'runtime.json';runtime.write_text(json.dumps(self.manifest()))
        output = self.root/'unbound-controller'
        code = ('import sys,json,os;from pathlib import Path;import Scripts.StructTrain.TimeLearner.contained_process as c;'
                'c.adopt=lambda p:os._exit(19);c.start(json.loads(Path(sys.argv[1]).read_text()),["20"],sys.argv[2],sys.argv[3],'
                'memory_bytes=134217728,tasks=32,maximum_wall_seconds=30)')
        result = subprocess.run([sys.executable, '-c', code, str(runtime), str(self.root), str(output)],
                                cwd=Path(__file__).resolve().parents[4],
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 19, result.stderr)
        self.assertFalse((output/'owned-unit.json').exists());self.assertFalse((output/'start.ack').exists())
        adopt(output);self.outputs.append(output)
        self.assertTrue(stop(output)['all_processes_closed'])
        self.assertFalse((output/'start.ack').exists())

    def test_runtime_deadline_ends_all_members_without_controller_polling(self):
        output = self.launch(wall=1)
        state = self.wait(lambda:s if (s:=inspect(output))['all_processes_closed'] else None)
        self.assertNotEqual(state['execution'], 'completed')
        if state['state'].get('LoadState') != 'not-found':
            self.assertEqual(state['state']['Result'], 'timeout')

    def test_stop_does_not_touch_an_unrelated_actual_process(self):
        unrelated = subprocess.Popen(['/bin/sleep', '20'])
        try:
            output = self.launch()
            self.assertTrue(stop(output)['all_processes_closed'])
            self.assertIsNone(unrelated.poll())
        finally:
            unrelated.terminate();unrelated.wait(timeout=5)

    def test_changed_invocation_is_refused_before_signalling(self):
        output = self.launch();path = output/'owned-unit.json';original = path.read_bytes()
        changed = json.loads(original);changed['invocation_id'] = 'f'*32
        path.write_text(json.dumps(_signed({k:v for k,v in changed.items() if k != 'sha256'})))
        try:
            with self.assertRaisesRegex(EvidenceError, 'invocation_changed'):stop(output)
        finally:path.write_bytes(original)
        self.assertFalse(inspect(output)['all_processes_closed'])

    def test_request_corruption_and_reused_output_fail_closed(self):
        output = self.launch();path = output/'request.json';original = path.read_bytes()
        changed = json.loads(original);changed['unit'] = 'another.service';path.write_text(json.dumps(changed))
        try:
            with self.assertRaisesRegex(EvidenceError, 'record_changed'):inspect(output)
        finally:path.write_bytes(original)
        with self.assertRaises(FileExistsError):
            start(json.loads((output/'runtime.json').read_text()), ['20'], self.root, output,
                  memory_bytes=134217728, tasks=32, maximum_wall_seconds=30)
        self.assertFalse(inspect(output)['all_processes_closed'])

    def test_invalid_requests_do_not_launch_a_service(self):
        for limits in ({'memory_bytes': True}, {'tasks': 0}, {'maximum_wall_seconds': .1}, {'maximum_wall_seconds': float('nan')}):
            values={'memory_bytes':134217728,'tasks':32,'maximum_wall_seconds':30,**limits}
            with self.assertRaises(EvidenceError):start(self.manifest(), ['20'], self.root, self.root/'invalid', **values)
        self.assertFalse((self.root/'invalid').exists())

    def test_actual_paths_with_spaces_preserve_runtime_and_logs(self):
        self.root = self.root/'directory with spaces';self.root.mkdir()
        output = self.launch(['-c', 'printf preserved_spaces'], manifest=self.manifest('console space.rs1', '/bin/sh'))
        self.wait(lambda:inspect(output)['all_processes_closed'])
        self.assertEqual((output/'stdout.log').read_text(), 'preserved_spaces')

    def test_service_path_expansion_is_refused_before_creating_outputs(self):
        manifest = self.manifest()
        for name in ('percent%H', 'variable${HOME}'):
            output = self.root/name
            with self.assertRaisesRegex(EvidenceError, 'requires_literal_location'):
                start(manifest, ['20'], self.root, output, memory_bytes=134217728, tasks=32, maximum_wall_seconds=30)
            self.assertFalse(output.exists())
