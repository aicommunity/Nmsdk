"""Real system binaries, manager/cgroup closure and exit capture; no neurons."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest

from . import test_process_runner as process_fixture
from .. import contained_process
from ..contained_runner import execute, inspect_attempt
from ..native_evidence import EvidenceError
from ..native_gate import FIELDS, supported_specification


@unittest.skipUnless(sys.platform == 'linux', 'actual Linux cgroup worker required')
class ContainedRunnerTest(unittest.TestCase):
    manifest = process_fixture.OwnedProcessTest.manifest

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='timelearner-contained-runner-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.ini = self.root/'app.ini';self.ini.write_text('actual process fixture\n')
        self.outputs = []
        self.addCleanup(self.close_and_retain)

    def close_and_retain(self):
        for output in self.outputs:
            if (output/'contained/request.json').exists():
                closure = contained_process.stop(output/'contained')
                self.assertTrue(closure['all_processes_closed'])
                (output/'test-final-membership.json').write_text(json.dumps(closure, indent=2))
        destination = os.environ.get('TIMELEARNER_CONTAINED_RUNNER_EVIDENCE_DIR')
        if destination:
            destination = Path(destination)/self._testMethodName
            destination.mkdir(parents=True, exist_ok=False)
            for path in self.root.rglob('*'):
                if path.is_file() and path.suffix in ('.json', '.log', '.py'):
                    target = destination/path.relative_to(self.root);target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(path, target)

    def run_process(self, manifest=None, args=None, *, wall=4, cooperative=False, name='attempt'):
        output = self.root/name;self.outputs.append(output)
        return execute(manifest or self.manifest(), args or ['.3'], self.root, output, wall,
                       memory_bytes=128*1024**2, tasks=32, cooperative_capture=cooperative)

    def wait(self, callback, timeout=8):
        deadline = time.monotonic()+timeout
        while time.monotonic()<deadline:
            if (value := callback()):return value
            time.sleep(.01)
        self.fail('owned attempt condition timed out')

    def test_complete_suffix_process_has_real_maps_limits_and_closed_whole_group(self):
        result = self.run_process(args=['.7'])
        self.assertEqual(result['execution'], 'completed', result)
        self.assertEqual(result['returncode'], 0)
        self.assertEqual(result['runtime_provenance'], 'loaded_files_captured')
        self.assertTrue(result['all_processes_closed'])
        self.assertEqual(result['ownership_scope'], 'bound_cgroup')
        self.assertIsNone(result['scientific_verdict'])
        self.assertEqual(inspect_attempt(self.root/'attempt'), result)
        kernel = json.loads((self.root/'attempt/contained/limits-readback.json').read_text())
        self.assertEqual(kernel['memory.max'], str(128*1024**2))
        self.assertEqual(kernel['pids.max'], '32')

    def test_nonzero_exit_preserves_actual_output_and_status(self):
        result = self.run_process(self.manifest('console.e05b', '/bin/sh'),
                                  ['-c', 'printf stdout_actual; printf stderr_actual >&2; exit 7'])
        self.assertEqual(result['execution'], 'process_error')
        self.assertEqual(result['returncode'], 7)
        self.assertTrue(result['all_processes_closed'])
        self.assertEqual((self.root/'attempt/stdout.log').read_text(), 'stdout_actual')
        self.assertEqual((self.root/'attempt/stderr.log').read_text(), 'stderr_actual')

    def test_zero_main_exit_with_live_child_never_completes_and_hits_wall_budget(self):
        result = self.run_process(self.manifest('parent.rs2', '/bin/sh'),
                                  ['-c', '/bin/sleep 20 & exit 0'], wall=1)
        self.assertEqual(result['execution'], 'timeout', result)
        self.assertTrue(result['all_processes_closed'])
        self.assertLess(result['wall_seconds'], 5)
        self.assertNotEqual(result['execution'], 'completed')

    def test_cancel_closes_all_descendants_and_preserves_unrelated_process(self):
        output = self.root/'attempt';unrelated = subprocess.Popen(['/bin/sleep', '20'])
        def cancel():
            self.wait(lambda:(output/'owned-process.json').exists())
            (output/'cancel.request').write_text('explicit request\n')
        thread = threading.Thread(target=cancel);thread.start()
        try:
            result = self.run_process(self.manifest('parent.rs2', '/bin/sh'),
                                      ['-c', '/bin/sleep 20 & wait'])
            thread.join(timeout=10)
            self.assertFalse(thread.is_alive())
            self.assertEqual(result['execution'], 'interrupted', result)
            self.assertTrue(result['all_processes_closed'])
            self.assertIsNone(unrelated.poll())
        finally:
            unrelated.terminate();unrelated.wait();thread.join(timeout=10)

    def test_runtime_mutation_after_launch_invalidates_provenance(self):
        def mutate():
            self.wait(lambda:(self.root/'attempt/owned-process.json').exists())
            self.ini.write_text('changed during execution')
        thread = threading.Thread(target=mutate);thread.start()
        result = self.run_process(args=['.5']);thread.join(timeout=10)
        self.assertEqual(result['execution'], 'process_error', result)
        self.assertEqual(result['runtime_provenance'], 'invalid_or_incomplete_runtime')
        self.assertIn('runtime_content_changed', result['reason'])
        self.assertTrue(result['all_processes_closed'])

    def capture_program(self, *, wrong=False):
        script = self.root/'capture.py'
        script.write_text('import os,sys,json,time\nfrom pathlib import Path\n'
            'p=Path(sys.argv[sys.argv.index("--timelearner-capture-directory")+1])\n'
            'ticks=Path("/proc/self/stat").read_text().rsplit(") ",1)[1].split()[19]\n'
            'ready={"kind":"native_runtime_capture_ready","schema_version":1,"pid":os.getpid(),'
            '"start_ticks":'+('"0"' if wrong else 'ticks')+'}\n'
            '(p/"capture-ready.json").write_text(json.dumps(ready))\n'
            'deadline=time.monotonic()+10\n'
            'while not (p/"capture-ack.json").exists() and time.monotonic()<deadline:time.sleep(.01)\n'
            'assert (p/"capture-ack.json").exists()\nprint("actual handshake completed")\n')
        return script

    def test_cooperative_capture_reads_actual_python_process_maps_before_ack(self):
        script = self.capture_program()
        result = self.run_process(self.manifest('capture.rs1', sys.executable), [str(script)], cooperative=True)
        self.assertEqual(result['execution'], 'completed', result)
        self.assertEqual(result['runtime_provenance'], 'loaded_files_captured')
        self.assertTrue((self.root/'attempt/loaded-files.json').exists())
        self.assertTrue((self.root/'attempt/capture-ack.json').exists())
        self.assertIn('actual handshake completed', (self.root/'attempt/stdout.log').read_text())

    def test_wrong_capture_identity_stops_the_owned_group_without_ack(self):
        script = self.capture_program(wrong=True)
        result = self.run_process(self.manifest('capture.rs1', sys.executable), [str(script)], cooperative=True)
        self.assertEqual(result['execution'], 'process_error', result)
        self.assertIn('cooperative_capture_identity_changed', result['reason'])
        self.assertTrue(result['all_processes_closed'])
        self.assertFalse((self.root/'attempt/capture-ack.json').exists())

    def test_crashed_frontend_leaves_observable_owned_group_until_explicit_stop(self):
        manifest = self.manifest();runtime = self.root/'runtime.json';runtime.write_text(json.dumps(manifest))
        output = self.root/'lost-controller';self.outputs.append(output)
        code = ('import json,sys;from pathlib import Path;'
                'from Scripts.StructTrain.TimeLearner.contained_runner import execute;'
                'execute(json.loads(Path(sys.argv[1]).read_text()),["20"],sys.argv[2],sys.argv[3],'
                '8,memory_bytes=134217728,tasks=32)')
        controller = subprocess.Popen([sys.executable, '-c', code, str(runtime), str(self.root), str(output)],
                                      cwd=Path(__file__).resolve().parents[4])
        try:
            self.wait(lambda:(output/'owned-process.json').exists())
            controller.kill();controller.wait()
            state = inspect_attempt(output)
            self.assertFalse(state['all_processes_closed'])
            self.assertEqual(state['execution'], 'running')
            self.assertFalse((output/'result.json').exists())
            self.assertTrue(contained_process.stop(output/'contained')['all_processes_closed'])
            self.assertNotEqual(inspect_attempt(output)['execution'], 'completed')
        finally:
            if controller.poll() is None:controller.kill();controller.wait()

    def test_reused_output_changed_runtime_and_preset_cancellation_are_refused(self):
        manifest = self.manifest()
        self.run_process(manifest)
        with self.assertRaises(FileExistsError):self.run_process(manifest)
        self.ini.write_text('changed')
        with self.assertRaises(EvidenceError):self.run_process(manifest, name='changed')
        manifest = self.manifest('cancel.rs1');output = self.root/'preset';output.mkdir()
        (output/'cancel.request').write_text('already cancelled')
        with self.assertRaisesRegex(EvidenceError, 'already_exists'):
            execute(manifest, ['1'], self.root, output, 4, memory_bytes=1024**2, tasks=32)

    def test_invalid_limits_are_rejected_without_creating_a_service(self):
        manifest = self.manifest()
        for memory,tasks,wall in [(True,32,4),(1024,True,4),(0,32,4),(1024,0,4),(1024,32,.1),(1024,32,float('nan'))]:
            output = self.root/'invalid'
            with self.assertRaises(EvidenceError):
                execute(manifest, ['1'], self.root, output, wall, memory_bytes=memory, tasks=tasks)
            self.assertFalse(output.exists())

    def test_native_gate_v3_requires_explicit_limits_and_retains_old_contracts(self):
        spec = dict.fromkeys(FIELDS)
        spec.update(kind='timelearner_native_test_gate', schema_version=1)
        self.assertTrue(supported_specification(spec))
        spec.update(schema_version=2, cooperative_runtime_capture=True)
        self.assertTrue(supported_specification(spec))
        spec.update(schema_version=3, process_limits={'memory_bytes':128*1024**2,'tasks':32})
        self.assertTrue(supported_specification(spec))
        spec['cooperative_runtime_capture'] = False
        self.assertTrue(supported_specification(spec))
        for limits in [None, {}, {'memory_bytes':True,'tasks':32}, {'memory_bytes':1024,'tasks':True},
                       {'memory_bytes':1024,'tasks':32,'extra':1}]:
            self.assertFalse(supported_specification(dict(spec, process_limits=limits)))
        self.assertFalse(supported_specification(dict(spec, schema_version=True)))
