"""Actual production Win32 Job closure controls; no replacement process API."""
from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import threading
import time
import unittest
from unittest.mock import patch

from ..windows_process import execute
from ..native_evidence import EvidenceError
from ..runtime import file_record,source_closure,runtime_content_identity,digest_json


class WindowsJobDrainTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.name!='nt':raise unittest.SkipTest('requires actual Windows Job API')
        sdk=os.environ.get('TIMELEARNER_WINDOWS_SDK_SOURCE');out=os.environ.get('TIMELEARNER_WINDOWS_DRAIN_OUTPUT')
        if not sdk or not out:raise unittest.SkipTest('requires explicit immutable source and owned output')
        cls.source=Path(sdk);cls.root=Path(out);cls.root.mkdir(parents=True,exist_ok=False);cls.lock=cls.root/'worker.lock'
        cls.driver=Path(__file__).parent/'fixtures/windows_job_drain_driver.py'
        from .. import windows_process
        backend=file_record(Path(windows_process.__file__))
        cls.base={'schema_version':2,'windows_source_root':str(cls.source),'source_closure':source_closure(cls.source),
            'executable':file_record(Path(sys.executable)),'app_ini':file_record(cls.driver),'compiler':file_record(Path(sys.executable)),
            'resolved_libraries':[file_record(p) for p in Path(sys.executable).parent.glob('*.dll')],
            'loaded_process_files':None,'windows_backend':backend,
            'build_flags':{'role':'actual_windows_owned_job_drain_fixture','windows_backend_sha256':backend['sha256']},
            'loader_environment':{k:os.environ.get(k) for k in ('PATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM')}}

    def manifest(self,seconds=None,fault_label=None):
        result=deepcopy(self.base)
        if seconds is not None:result['build_flags']['owned_job_drain_seconds']=seconds
        if fault_label is not None:result['build_flags']['controlled_test_fault_injection']=fault_label
        result['runtime_identity']=runtime_content_identity(result);result['runtime_fingerprint']=digest_json(result['runtime_identity'])
        return result

    def run_case(self,name,*,sleep=1.,seconds=None,wall=10,code=0,cancel=None,override=None,fault_label=None):
        manifest=self.manifest(seconds,fault_label);output=self.root/name
        kwargs={} if seconds is None else {'owned_job_drain_seconds':seconds}
        if override is not None:kwargs['owned_job_drain_seconds']=override
        result=execute(manifest,['-B','-X','utf8',str(self.driver),'parent','--directory',str(output/'data'),
            '--sleep',str(sleep),'--code',str(code)],self.root,output,memory_bytes=256*1024**2,maximum_processes=8,
            maximum_wall_seconds=wall,lock_file=self.lock,cancel_file=cancel,**kwargs)
        self.assertTrue(result['all_processes_closed']);self.assertIsNone(result['scientific_verdict'])
        return result,output

    def test_default_zero_preserves_immediate_descendant_refusal_and_old_request(self):
        result,out=self.run_case('default-zero')
        self.assertEqual(result['execution'],'descendants_remaining');self.assertEqual(result['returncode'],0)
        self.assertNotIn('owned_job_drain',result);self.assertNotIn('owned_job_drain',json.loads((out/'request.json').read_text(encoding='utf-8')))

    def test_opt_in_waits_for_natural_whole_job_closure_with_live_child_identity(self):
        result,out=self.run_case('natural',seconds=4.)
        self.assertEqual(result['execution'],'completed',result);self.assertEqual(result['validity'],'valid')
        self.assertEqual(result['main_returncode'],0);self.assertTrue(result['owned_job_drain']['natural_empty'])
        child=json.loads((out/'data/child-ready.json').read_text(encoding='utf-8'))
        matches=[row for row in result['owned_job_drain']['identities'] if row['pid']==child['pid'] and row['creation_filetime']==child['creation_filetime']]
        self.assertEqual(len(matches),1);self.assertTrue(matches[0]['own_job_membership_checked'])
        self.assertEqual(matches[0]['executable_file']['sha256'],self.base['executable']['sha256'])
        request=json.loads((out/'request.json').read_text(encoding='utf-8'))
        self.assertEqual(request['owned_job_drain']['seconds'],4.)

    def test_persistent_child_is_rejected_at_signed_grace_deadline(self):
        result,_=self.run_case('persistent',sleep=30.,seconds=.3)
        self.assertEqual(result['execution'],'descendants_remaining');self.assertFalse(result['owned_job_drain']['natural_empty'])

    def test_original_whole_wall_caps_a_long_grace(self):
        result,_=self.run_case('whole-wall',sleep=30.,seconds=30.,wall=4)
        self.assertEqual(result['execution'],'timeout',result)
        self.assertLessEqual(result['owned_job_drain']['deadline_elapsed'],4.)

    def test_cancellation_during_drain_remains_a_failure(self):
        out=self.root/'cancel';marker=self.root/'cancel-request';errors=[]
        def cancel():
            deadline=time.monotonic()+8
            while not (out/'owned-job-drain-started.json').is_file():
                if time.monotonic()>deadline:errors.append('drain_not_started');return
                time.sleep(.01)
            marker.write_text('cancel owned fixture',encoding='utf-8')
        worker=threading.Thread(target=cancel);worker.start()
        try:result,_=self.run_case('cancel',sleep=30.,seconds=8.,cancel=marker)
        finally:worker.join(10)
        self.assertFalse(worker.is_alive());self.assertEqual(errors,[]);self.assertEqual(result['execution'],'cancelled',result)

    def test_nonzero_main_is_never_promoted_by_a_grace(self):
        result,_=self.run_case('nonzero',sleep=30.,seconds=4.,code=42)
        self.assertNotEqual(result['execution'],'completed');self.assertEqual(result['returncode'],42)
        self.assertEqual(result['main_returncode'],42)

    def test_explicit_signed_zero_still_refuses_remaining_children(self):
        result,out=self.run_case('signed-zero',seconds=0.)
        self.assertEqual(result['execution'],'descendants_remaining');self.assertFalse(result['owned_job_drain']['natural_empty'])
        self.assertIn('owned_job_drain',json.loads((out/'request.json').read_text(encoding='utf-8')))

    def test_injected_open_failure_for_a_real_owned_child_cannot_become_success(self):
        # Real parent/child, limits, Job membership and cleanup remain in use.
        # Only this query is fault-injected; this is not an observed OS denial.
        import ctypes
        def denied(_pid):ctypes.set_last_error(5);return None
        with patch('Scripts.StructTrain.TimeLearner.windows_process._open_owned_process',side_effect=denied):
            result,out=self.run_case('controlled-open-failure',sleep=30.,seconds=4.,fault_label='OpenProcess query deliberately returns NULL')
        self.assertEqual(result['execution'],'process_error');self.assertEqual(result['validity'],'provenance_missing')
        self.assertEqual(result['reason'],'owned_process_identity_unavailable')
        self.assertFalse(result['owned_job_drain']['natural_empty'])
        self.assertTrue(any(gap['alive_state']=='unknown' and gap['still_in_owned_job'] for gap in result['owned_job_drain']['gaps']))
        request=json.loads((out/'request.json').read_text(encoding='utf-8'))
        self.assertIn('controlled_test_fault_injection',request['runtime']['build_flags'])

    def test_invalid_unsigned_or_mismatched_policy_never_creates_output(self):
        for index,value in enumerate((True,False,-1.,float('nan'),float('inf'))):
            with self.subTest(value=value),self.assertRaises(EvidenceError):self.run_case('invalid-'+str(index),override=value)
            self.assertFalse((self.root/('invalid-'+str(index))).exists())
        with self.assertRaises(EvidenceError):self.run_case('unsigned',override=1.)
        with self.assertRaises(EvidenceError):self.run_case('mismatch',seconds=1.,override=2.)
        with self.assertRaises(EvidenceError):self.run_case('signed-bool',seconds=True,override=1.)
        self.assertFalse((self.root/'unsigned').exists());self.assertFalse((self.root/'mismatch').exists())
        self.assertFalse((self.root/'signed-bool').exists())
