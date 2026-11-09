"""Actual kernel/lease tests for the maintained native controller loop.

No compiler, neuron or scientific model executes. Outputs and deliberately held
negative leases are retained under the explicitly consumed test fixture path.
Public JSON cannot select this private fixed fixture instead of the native worker.
"""
import json
import os
from pathlib import Path
import sys
import threading
import time
import unittest
from unittest.mock import patch

from .. import owned_native_job as subject
from ..contained_process import inspect
from ..resource_reservations import Reservations
from ..runtime import file_record,resolved_libraries,runtime_content_identity,digest_json


@unittest.skipUnless(sys.platform=='linux','actual Linux user-manager/cgroup required')
class OwnedNativeKernelTest(unittest.TestCase):
    def setUp(self):
        bound=os.environ.get('TIMELEARNER_OWNED_NATIVE_TEST_OUTPUT')
        if not bound:
            self.fail('missing consumed TIMELEARNER_OWNED_NATIVE_TEST_OUTPUT fixture')
        parent=Path(bound).resolve(strict=True)
        self.root=parent/self._testMethodName;self.root.mkdir(exist_ok=False)
        self.controller=self.root/'controller';self.controller.mkdir()
        self.output=self.root/'native-output'
        self.registry=Reservations(self.root/'registry.sqlite3')
        ini=self.root/'fixture-input.json';ini.write_text(json.dumps({'private_kernel_fixture':True}),encoding='utf-8')
        binary=Path(sys.executable).resolve(strict=True)
        self.runtime={'schema_version':2,'source_closure':{'fixture':'real kernel; no C++ or model'},
            'executable':file_record(binary),'app_ini':file_record(ini),
            'compiler':file_record(Path('/bin/true').resolve(strict=True)),'build_flags':{},
            'resolved_libraries':resolved_libraries(binary),'loaded_process_files':None,
            'loader_environment':{k:os.environ[k] for k in ('LD_LIBRARY_PATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM') if k in os.environ}}
        self.runtime['runtime_identity']=runtime_content_identity(self.runtime)
        self.runtime['runtime_fingerprint']=digest_json(self.runtime['runtime_identity'])
        (self.root/'fixture-runtime.json').write_text(json.dumps(self.runtime),encoding='utf-8')

    def execute_fixture(self,mode,*,wall=20,guard=None):
        args=['-B','-m','Scripts.StructTrain.TimeLearner.tests.owned_native_fixture',mode,str(self.root),'--reserve']
        code=subject._run_owned(self.runtime,args,Path(__file__).resolve().parents[4],self.controller,
            self.output,[self.output/'leaf/process/contained'],self.registry,self.root.name,
            {'memory_bytes':256*1024**2,'tasks':32,'maximum_wall_seconds':wall},
            {'minimum_free_bytes':1024**2,'maximum_increment_bytes':32*1024**2},[self.root],control_guard=guard)
        result=json.loads((self.controller/'supervisor-result.json').read_bytes())
        rows=self.registry.inspect()['leases']
        (self.root/'test-observation.json').write_text(json.dumps({'returncode':code,'leases':rows,
            'result':result,'actual_kernel_test':True,'Cpp_or_model_execution':False,'scientific_verdict':None},indent=2),encoding='utf-8')
        self.assertTrue(inspect(self.controller/'process/contained')['all_processes_closed'])
        self.assertEqual(len(rows),1)
        return code,result,rows[0]

    def test_actual_exit_zero_closes_outer_before_exact_worker_lease_release(self):
        code,result,row=self.execute_fixture('exit0')
        self.assertEqual(code,0,result);self.assertEqual(row['state'],'released')
        self.assertFalse(result['record_errors']);self.assertTrue(result['outer_closed'])
        self.assertIsNone(result['reason'])
        original=json.loads((self.controller/'original-outcome.json').read_bytes())
        self.assertEqual(original['kernel_before_stop']['state']['ExecMainStatus'],'0')

    def test_nonzero_actual_exit_is_not_converted_into_completed_by_cleanup(self):
        code,result,row=self.execute_fixture('exit7')
        self.assertEqual(code,2,result);self.assertEqual(row['state'],'released')
        original=json.loads((self.controller/'original-outcome.json').read_bytes())
        self.assertEqual(original['kernel_before_stop']['state']['ExecMainStatus'],'7')
        self.assertTrue(original['cleanup_does_not_attest_execution_success'])

    def test_actual_whole_deadline_closes_owned_unit_without_success(self):
        code,result,row=self.execute_fixture('wait',wall=3)
        self.assertEqual(code,2,result);self.assertEqual(row['state'],'released')
        self.assertTrue(result['outer_closed'])
        self.assertTrue(result['reason'] is not None or result['last_before_cleanup']['state']['Result']!='success')

    def test_actual_cancel_request_closes_owned_unit_without_restart(self):
        def cancel_after_start():
            deadline=time.monotonic()+15
            while time.monotonic()<deadline:
                if (self.output/'fixture-started.json').exists():
                    (self.controller/'cancel.request').write_bytes(b'cancel');return
                time.sleep(.02)
        thread=threading.Thread(target=cancel_after_start);thread.start()
        try:code,result,row=self.execute_fixture('wait')
        finally:thread.join(timeout=16)
        self.assertFalse(thread.is_alive());self.assertEqual(code,2,result)
        self.assertIn('owned_native_cancel_requested',result['reason']['reason'])
        self.assertEqual(row['state'],'released')

    def test_actual_nested_child_closes_before_worker_lease_release(self):
        code,result,row=self.execute_fixture('nested')
        self.assertEqual(code,0,result);self.assertEqual(row['state'],'released')
        self.assertEqual(len(result['children_closed']),1)
        child=result['children_closed'][0]
        self.assertTrue(child['closure']['all_processes_closed'])
        self.assertTrue(inspect(child['directory'])['all_processes_closed'])

    def test_actual_unbound_child_intent_adopted_only_after_dead_worker(self):
        code,result,row=self.execute_fixture('unbound')
        self.assertEqual(code,0,result);self.assertEqual(row['state'],'released')
        self.assertTrue(json.loads((self.output/'injected-unbound.json').read_bytes())['fault_injection'])
        self.assertEqual(len(result['children_closed']),1)
        self.assertTrue(result['children_closed'][0]['closure']['all_processes_closed'])

    def test_partial_final_request_holds_lease_and_does_not_invent_child_closure(self):
        code,result,row=self.execute_fixture('partial')
        self.assertEqual(code,2,result);self.assertEqual(row['state'],'held')
        self.assertTrue(result['outer_closed']);self.assertFalse(result['children_closed'])
        self.assertTrue(any(x.get('phase')=='child_close' for x in result['record_errors']))
        self.assertEqual((self.output/'leaf/process/contained/request.json').read_bytes(),b'{')

    def test_started_receipt_fault_still_closes_actual_outer_and_holds_lease(self):
        original=subject._write
        def write(path,value):
            if Path(path).name=='started-binding.json':
                # Fault only after the real worker has created its own lease;
                # otherwise an early stop tests a different no-reservation path.
                deadline=time.monotonic()+10
                while not (self.output/'reservation.json').is_file() and time.monotonic()<deadline:
                    time.sleep(.02)
                if not (self.output/'reservation.json').is_file():
                    raise AssertionError('real fixture reservation did not become observable')
                raise OSError('explicit_fixture_started_receipt_failure')
            return original(path,value)
        with patch.object(subject,'_write',side_effect=write):
            code,result,row=self.execute_fixture('exit0')
        self.assertEqual(code,2,result);self.assertEqual(row['state'],'held')
        self.assertTrue(result['outer_closed'])
        self.assertTrue(any(x.get('file')=='started-binding.json' for x in result['record_errors']))

    def test_observer_broken_pipe_cannot_abort_actual_unit_cleanup(self):
        with patch('builtins.print',side_effect=BrokenPipeError('explicit_fixture_observer_disconnect')):
            code,result,row=self.execute_fixture('exit0')
        self.assertEqual(code,0,result);self.assertEqual(row['state'],'released')
        self.assertTrue((self.controller/'started-binding.json').is_file())


if __name__=='__main__':
    unittest.main()
