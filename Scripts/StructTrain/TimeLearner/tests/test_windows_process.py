"""Exercise the production Windows backend on the optional remote worker."""
import copy
import json
import os
from pathlib import Path
import sys
import threading
import time
import unittest

from .. import windows_process
from ..native_evidence import EvidenceError
from ..runtime import digest_json, file_record, runtime_content_identity, source_closure


class WindowsProcessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.name != 'nt':raise unittest.SkipTest('requires the actual Windows worker')
        sdk = os.environ.get('TIMELEARNER_WINDOWS_SDK_SOURCE')
        output = os.environ.get('TIMELEARNER_WINDOWS_PROCESS_OUTPUT')
        if not sdk or not output:raise unittest.SkipTest('requires explicit immutable SDK and evidence paths')
        cls.root = Path(output);cls.root.mkdir(parents=True, exist_ok=False)
        cls.lock = cls.root/'worker.lock';cls.source = Path(sdk)
        backend = file_record(Path(windows_process.__file__))
        cls.manifest = {'schema_version': 2, 'windows_source_root': str(cls.source),
            'source_closure': source_closure(cls.source), 'executable': file_record(Path(sys.executable)),
            'app_ini': file_record(Path(__file__)), 'compiler': file_record(Path(sys.executable)),
            'resolved_libraries': [file_record(p) for p in Path(sys.executable).parent.glob('*.dll')],
            'loaded_process_files': None, 'windows_backend': backend,
            'build_flags': {'role': 'owned_windows_process_fixture', 'windows_backend_sha256': backend['sha256']},
            'loader_environment': {key: os.environ.get(key) for key in ('PATH', 'QT_PLUGIN_PATH', 'QT_QPA_PLATFORM')}}
        cls.manifest['runtime_identity'] = runtime_content_identity(cls.manifest)
        cls.manifest['runtime_fingerprint'] = digest_json(cls.manifest['runtime_identity'])

    def run_fixture(self, name, code, *, wall=5, processes=1, cancel=None, extra=None, memory=128*1024**2, cooperative=False):
        result = windows_process.execute(self.manifest, ['-X', 'utf8', '-c', code, *(extra or [])],
            self.root, self.root/name, memory_bytes=memory, maximum_processes=processes,
            maximum_wall_seconds=wall, lock_file=self.lock, cancel_file=cancel, cooperative_capture=cooperative)
        (self.root/(name+'-observed.json')).write_text(json.dumps(result, indent=2)+'\n')
        return result

    def complete(self, result, execution='completed'):
        self.assertEqual(result['execution'], execution, result)
        self.assertEqual(result['validity'], 'valid', result)
        self.assertTrue(result['all_processes_closed'])
        self.assertEqual(result['runtime_provenance'], 'loaded_files_captured')
        self.assertIsNone(result['scientific_verdict'])

    def stopped(self, result, execution):
        self.assertEqual(result['execution'], execution, result)
        self.assertTrue(result['all_processes_closed'])
        self.assertIsNone(result['scientific_verdict'])
        self.assertIn(result['validity'], ('valid', 'provenance_missing', 'not_executed'))
        if result['validity'] != 'valid':
            self.assertNotEqual(result['runtime_provenance'], 'loaded_files_captured')

    def test_completed_argv_and_unicode_are_not_shell_commands(self):
        result = self.run_fixture('quoted', 'import sys,json,time;print(json.dumps(sys.argv[1:],ensure_ascii=False));time.sleep(.3)',
                                  extra=['with space', 'данные', 'literal&text'])
        self.complete(result)
        self.assertEqual(json.loads((self.root/'quoted/stdout.log').read_text(encoding='utf-8')),
                         ['with space', 'данные', 'literal&text'])
        limits = json.loads((self.root/'quoted/limits-before-exec.json').read_text())
        self.assertEqual(limits['memory_bytes'], 128*1024**2)
        self.assertEqual(limits['maximum_processes'], 1)
        owner = json.loads((self.root/'quoted/owned-process.json').read_text())
        self.assertTrue(owner['suspended_until_limits_applied'])

    def test_exit_259_is_a_terminal_nonzero_exit(self):
        result = self.run_fixture('exit259', 'import time;time.sleep(.3);raise SystemExit(259)')
        self.complete(result, 'process_error');self.assertEqual(result['returncode'], 259)

    def test_memory_limit_rejects_allocation(self):
        code = 'import time\ntry:\n a=bytearray(512*1024*1024)\n print("unexpected_allocation")\nexcept MemoryError:\n print("memory_limit_observed")\ntime.sleep(.3)'
        result = self.run_fixture('memory', code)
        self.complete(result)
        self.assertEqual((self.root/'memory/stdout.log').read_text().strip(), 'memory_limit_observed')
        after = json.loads((self.root/'memory/limits-after.json').read_text())
        self.assertEqual(after['memory_bytes'], 128*1024**2)
        # Preserve the raw peak counter without inferring an undocumented bound.
        # Enforcement is tested by actual allocation failure and the paired
        # successful allocation under a larger limit, not a peak inequality.
        self.assertGreater(after['peak_job_memory_bytes'], 0)

    def test_same_allocation_succeeds_with_larger_limit(self):
        result = self.run_fixture('larger-memory',
            'import time;a=bytearray(512*1024*1024);print(len(a));time.sleep(.3)', memory=768*1024**2)
        self.complete(result)
        self.assertEqual((self.root/'larger-memory/stdout.log').read_text().strip(), str(512*1024*1024))

    def test_timeout_closes_the_owned_job(self):
        result = self.run_fixture('timeout', 'import time;time.sleep(30)', wall=.3)
        self.stopped(result, 'timeout')

    def test_timeout_after_capture_preserves_runtime_evidence(self):
        result = self.run_fixture('captured-timeout', 'import time;time.sleep(30)', wall=5)
        self.complete(result, 'timeout');self.assertTrue(result['child_resumed'])

    def test_remaining_owned_descendant_is_closed_and_not_success(self):
        code = 'import subprocess,sys,time;subprocess.Popen([sys.executable,"-c","import time;time.sleep(30)"],creationflags=0x08000000);time.sleep(.4)'
        result = self.run_fixture('descendant', code, processes=4)
        self.complete(result, 'descendants_remaining')
        self.assertTrue(result['descendants_at_main_exit'])

    def test_cancel_before_start_does_not_resume_a_child(self):
        cancel = self.root/'cancel-before.request';cancel.write_text('cancel')
        result = self.run_fixture('cancel-before', 'import time;time.sleep(30)', cancel=cancel)
        self.assertEqual(result['execution'], 'cancelled');self.assertFalse(result['child_resumed'])
        self.assertFalse((self.root/'cancel-before/owned-process.json').exists())

    def test_cancel_running_job(self):
        cancel = self.root/'cancel-running.request';owner = self.root/'cancel-running/owned-process.json'
        def request():
            deadline = time.monotonic()+10
            while not owner.exists() and time.monotonic() < deadline:time.sleep(.02)
            if owner.exists():time.sleep(.15);cancel.write_text('cancel')
        thread = threading.Thread(target=request, daemon=True);thread.start()
        result = self.run_fixture('cancel-running', 'import time;time.sleep(30)', cancel=cancel)
        thread.join(timeout=10);self.complete(result, 'cancelled');self.assertTrue(result['child_resumed'])

    def test_host_lock_refuses_another_worker(self):
        cancel = self.root/'lock-first.request';owner = self.root/'lock-first/owned-process.json';results = []
        thread = threading.Thread(target=lambda: results.append(self.run_fixture('lock-first', 'import time;time.sleep(30)', wall=15, cancel=cancel)))
        thread.start();deadline = time.monotonic()+10
        try:
            while not owner.exists() and time.monotonic() < deadline:time.sleep(.02)
            self.assertTrue(owner.exists())
            with self.assertRaisesRegex(RuntimeError, 'windows_worker_already_reserved'):
                self.run_fixture('lock-second', 'import time;time.sleep(.3)')
        finally:
            cancel.write_text('cancel');thread.join(timeout=20)
        self.assertFalse(thread.is_alive());self.assertEqual(len(results), 1)
        self.stopped(results[0], 'cancelled')

    def test_changed_runtime_is_refused_before_execution(self):
        changed = copy.deepcopy(self.manifest);changed['executable']['sha256'] = '0'*64
        with self.assertRaises(EvidenceError):
            windows_process.execute(changed, [], self.root, self.root/'changed', memory_bytes=128*1024**2,
                maximum_processes=1, maximum_wall_seconds=1, lock_file=self.lock)
        self.assertFalse((self.root/'changed').exists())

    def test_invalid_limits_do_not_start_a_child(self):
        for name, change in [('memory-bool', {'memory_bytes': True}), ('wall-nan', {'maximum_wall_seconds': float('nan')}),
                             ('process-zero', {'maximum_processes': 0})]:
            limits = {'memory_bytes': 128*1024**2, 'maximum_processes': 1, 'maximum_wall_seconds': 1, **change}
            with self.assertRaises(EvidenceError):
                windows_process.execute(self.manifest, [], self.root, self.root/name, lock_file=self.lock, **limits)
            self.assertFalse((self.root/name).exists())

    def cooperative_fixture(self, wrong_identity=False):
        # Protocol fixture only. The C++ implementation is checked by actual SDK gates.
        return ('import sys,os,json,time,ctypes;from pathlib import Path;sys.path.insert(0,'+
                repr(str(Path(__file__).resolve().parents[4]))+');'
                'from Scripts.StructTrain.TimeLearner.windows_process import _Windows;'
                'a=_Windows();identity=a.identity(ctypes.c_void_p(-1));'
                'folder=Path(sys.argv[sys.argv.index("--timelearner-capture-directory")+1]);'
                'ready={"kind":"native_runtime_capture_ready","schema_version":2,"pid":'+
                ('0' if wrong_identity else 'os.getpid()')+',"creation_filetime":identity["creation_filetime"]};'
                '(folder/"ready.tmp").write_text(json.dumps(ready));(folder/"ready.tmp").rename(folder/"capture-ready.json");'
                'deadline=time.monotonic()+4\n'
                'while not (folder/"capture-ack.json").exists() and time.monotonic()<deadline:time.sleep(.005)\n'
                'ack=json.loads((folder/"capture-ack.json").read_text());'
                'assert ack==dict(ready,kind="native_runtime_capture_ack")')

    def test_cooperative_boundary_binds_live_creation_identity(self):
        result = self.run_fixture('cooperative', self.cooperative_fixture(), wall=10, cooperative=True)
        self.complete(result);self.assertEqual(result['cooperative_capture'], 'completed')
        self.assertTrue((self.root/'cooperative/boundary-loaded-files.json').exists())

    def test_wrong_cooperative_identity_closes_the_owned_process(self):
        result = self.run_fixture('wrong-identity', self.cooperative_fixture(True), wall=10, cooperative=True)
        self.assertEqual(result['validity'], 'invalid_or_incomplete')
        self.assertEqual(result['reason'], 'windows_cooperative_capture_identity_changed')
        self.assertTrue(result['all_processes_closed'])
        self.assertFalse((self.root/'wrong-identity/capture-ack.json').exists())

    def test_fast_exit_without_requested_boundary_is_not_provenance(self):
        result = self.run_fixture('missing-boundary', 'print("no capture boundary")', cooperative=True)
        self.assertEqual(result['validity'], 'provenance_missing')
        self.assertEqual(result['runtime_provenance'], 'not_captured')
        self.assertTrue(result['all_processes_closed'])

    def test_windows_gate_specification_declares_process_limits(self):
        from ..native_gate import supported_specification
        spec = dict(kind='timelearner_native_test_gate', schema_version=4, runtime_manifest='runtime.json',
                    source_root='source', expected_test_ids=['Fixture/Case'], maximum_wall_seconds=10,
                    asan_options='', cooperative_runtime_capture=True,
                    process_limits={'memory_bytes':128*1024**2,'maximum_processes':1}, worker_lock='worker.lock')
        self.assertTrue(supported_specification(spec))
        for change in ({'process_limits':{'memory_bytes':True,'maximum_processes':1}},
                       {'cooperative_runtime_capture':False}, {'worker_lock':''}):
            self.assertFalse(supported_specification(dict(spec, **change)))
