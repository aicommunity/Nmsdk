"""Real Git and isolated-production-Python metadata checks; SERVER ONLY.

Tiny Git SDKs contain whole unchanged production Scripts, seven real child Git
repos and literal metadata TEST declarations. No C++ is compiled or modeled.
"""
import copy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import unittest
import shutil

from .. import native_canonical_preparation as subject
from .. import owned_python_job
from .test_native_acceptance_worker import declarations


def encode(value):return (json.dumps(value,indent=2)+'\n').encode('utf-8')
def digest(raw):return hashlib.sha256(raw).hexdigest()


class NativeCanonicalPreparationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary=tempfile.TemporaryDirectory(prefix='canonical-real-git-')
        cls.root=Path(cls.temporary.name).resolve()
        cls.base=next(b for b in subject.BASES if cls.root.is_relative_to(b))
        cls.sdk=cls.root/'sdk';cls.sdk.mkdir()
        # Sparse source deliberately omits unrelated Root blobs. archive may
        # inspect attributes outside Scripts; request only this exact Git set.
        entries=[]
        for entry in cls.git(subject.ROOT,'ls-tree','-r','-z','HEAD','--','Scripts').split(b'\0'):
            if not entry:continue
            header,name=entry.split(b'\t',1);mode,kind,oid=header.decode('ascii').split()
            relative=name.decode('utf-8');parts=relative.split('/')
            if (kind!='blob' or mode not in ('100644','100755') or parts[0]!='Scripts' or
                    PurePosixPath(relative).is_absolute() or '\\' in relative or
                    any(p in ('','.','..') for p in parts)):
                raise ValueError('fixture_Scripts_Git_entry_not_regular_safe_path')
            entries.append((relative,mode,oid))
        if not entries or len({p for p,_,_ in entries})!=len(entries):
            raise ValueError('fixture_Scripts_Git_projection_empty_or_duplicate')
        raw=cls.git(subject.ROOT,'cat-file','--batch',data=('\n'.join(o for _,_,o in entries)+'\n').encode('ascii'))
        cursor=0
        for relative,mode,oid in entries:
            end=raw.index(b'\n',cursor);header=raw[cursor:end].decode('ascii').split();cursor=end+1
            if len(header)!=3 or header[:2]!=[oid,'blob'] or not header[2].isdigit():
                raise ValueError('fixture_Scripts_Git_batch_header')
            size=int(header[2]);content=raw[cursor:cursor+size];cursor+=size
            if len(content)!=size or raw[cursor:cursor+1]!=b'\n':
                raise ValueError('fixture_Scripts_Git_batch_length')
            cursor+=1
            if hashlib.sha1(b'blob '+str(size).encode('ascii')+b'\0'+content).hexdigest()!=oid:
                raise ValueError('fixture_Scripts_Git_blob_changed')
            path=cls.sdk/relative;path.parent.mkdir(parents=True,exist_ok=True)
            with path.open('xb') as stream:stream.write(content)
            path.chmod(0o755 if mode=='100755' else 0o644)
        if cursor!=len(raw):raise ValueError('fixture_Scripts_Git_batch_trailing_bytes')
        test=cls.sdk/'Tests/actual.cpp';test.parent.mkdir()
        test.write_text('TEST(Suite,First) {}\nTEST(Suite,Second) {}\n',encoding='utf-8')
        cls.git(cls.sdk,'init','--quiet')
        cls.git(cls.sdk,'config','user.name','Canonical metadata fixture')
        cls.git(cls.sdk,'config','user.email','fixture@example.invalid')
        cls.git(cls.sdk,'config','core.autocrlf','false')
        for name in ['Bin','Rdk','Libraries/Nmsdk-PulseLib','Libraries/Nmsdk-MotionControlLib',
                     'Libraries/Rdk-BasicLib','Libraries/Rdk-CvBasicLib','Libraries/Rdk-HardwareLib']:
            child=cls.sdk/name;child.mkdir(parents=True)
            cls.git(child,'init','--quiet');cls.git(child,'config','user.name','Canonical metadata fixture')
            cls.git(child,'config','user.email','fixture@example.invalid')
            (child/'readme.txt').write_text(name+'\n',encoding='utf-8')
            cls.git(child,'add','readme.txt');cls.git(child,'commit','--quiet','-m','Actual fixture data')
            pin=cls.git(child,'rev-parse','HEAD').decode().strip()
            cls.git(cls.sdk,'update-index','--add','--cacheinfo','160000',pin,name)
        links=['Bin','Rdk','Libraries/Nmsdk-PulseLib','Libraries/Nmsdk-MotionControlLib',
               'Libraries/Rdk-BasicLib','Libraries/Rdk-CvBasicLib','Libraries/Rdk-HardwareLib']
        (cls.sdk/'.gitmodules').write_text(''.join('[submodule "'+name+'"]\n path = '+name+'\n url = ./'+name+'\n' for name in links),encoding='utf-8')
        cls.git(cls.sdk,'add','Scripts','Tests','.gitmodules');cls.git(cls.sdk,'commit','--quiet','-m','Whole production Scripts and literal metadata tests')
        cls.commit=cls.git(cls.sdk,'rev-parse','HEAD').decode().strip()
        cls.namespace={}
        for relative in ['', 'Bin','Rdk','Libraries/Nmsdk-PulseLib','Libraries/Nmsdk-MotionControlLib',
                         'Libraries/Rdk-BasicLib','Libraries/Rdk-CvBasicLib','Libraries/Rdk-HardwareLib']:
            repository=cls.sdk/relative
            for entry in cls.git(repository,'ls-tree','-r','-z','HEAD').split(b'\0'):
                if not entry:continue
                header,name=entry.split(b'\t',1);mode,kind,oid=header.decode().split()
                if kind!='blob':continue
                rel=name.decode();raw=(repository/rel).read_bytes();path=(Path(relative)/rel).as_posix()
                cls.namespace[path]={'git_mode':mode,'git_blob':oid,'bytes':len(raw),'sha256':digest(raw)}

    @classmethod
    def tearDownClass(cls):cls.temporary.cleanup()

    @staticmethod
    def git(root,*args,data=None):
        return subprocess.check_output(['git','-C',str(root),*args],input=data,stderr=subprocess.PIPE,
            env=dict(os.environ,GIT_NO_LAZY_FETCH='1',GIT_OPTIONAL_LOCKS='0'))

    def setUp(self):
        self.case=self.root/self._testMethodName;self.case.mkdir()
        self.external=self.case/'external';self.controls=self.case/'controls';self.controls.mkdir()
        for name in ('resources','framework'):(self.case/name).mkdir()
        self.job,_,_=declarations();self.job['workspace']=str(self.base)
        self.job['paths']={k:str(self.sdk if k=='source' else self.case/(self.case.name+'-native') if k=='output'
                                 else self.case/k) for k in self.job['paths']}
        native=Path(self.job['paths']['output']).name
        self.controller=self.base/'readbacks'/(native+'-controller')
        self.job['preparation']=str(self.controller/'inputs/preparation.json')
        self.cohort={'selections':[{'path':'Tests/actual.cpp','suites':['Suite'],
            'dialect':'literal-TEST-and-attempt-invalid-budget-v1'}],
            'selected_ids':['Suite/First','Suite/Second'],
            'runplan':[{'name':'leaf','expected_ids':['Suite/First','Suite/Second'],'wall_seconds':60}],
            'partitions':[{'name':'fixture','ids':['Suite/First','Suite/Second'],'count':2}]}
        self.plan={'kind':'timelearner_native_canonical_preparation','schema_version':1,
            'workspace':str(self.base),'source':{'path':str(self.sdk),'commit':self.commit,
                'namespace':self.binding('namespace.json',self.namespace)},
            'cohort':self.binding('cohort.json',self.cohort),'native_job':self.binding('job.json',self.job),
            'prior_bindings':[],'external_output':str(self.external),
            'native_tool':{'path':str(subject.ROOT),'commit':self.git(subject.ROOT,'rev-parse','HEAD').decode().strip()},
            'require_fresh_build':True}

    def binding(self,name,value):
        raw=encode(value);path=self.controls/name;path.write_bytes(raw)
        return {'path':str(path),'sha256':digest(raw)}

    def child(self,plan=None,commit=None):
        raw=encode(self.plan if plan is None else plan);path=self.controls/'plan.json';path.write_bytes(raw)
        return subprocess.run([sys.executable,'-I','-B',str(Path(subject.__file__).resolve()),'_child',
            str(path),str(self.sdk),commit or self.commit,digest(raw)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            timeout=180,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',GIT_NO_LAZY_FETCH='1'))

    def test_closed_schema_and_boolean_versions_refuse_without_outputs(self):
        for key,value in [('schema_version',True),('schema_version',2),('command','checkout'),('require_fresh_build',False)]:
            with self.subTest(key=key,value=value):
                plan=copy.deepcopy(self.plan);plan[key]=value
                with self.assertRaises(ValueError):subject.validate_plan(plan)
                self.assertFalse(self.external.exists());self.assertFalse(Path(self.job['paths']['build']).exists())

    def test_bound_input_hash_and_alias_are_checked_before_outputs(self):
        plan=copy.deepcopy(self.plan);plan['cohort']['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'canonical_input_changed'):subject.validate_plan(plan)
        alias=self.controls/'alias.json';alias.symlink_to(self.controls/'cohort.json')
        plan=copy.deepcopy(self.plan);plan['cohort']['path']=str(alias)
        with self.assertRaises(ValueError):subject.validate_plan(plan)
        self.assertFalse(self.external.exists())

    def test_external_output_and_internal_controller_layout_are_distinct(self):
        state=subject.validate_plan(self.plan)
        self.assertEqual(state['controller'],self.controller);self.assertFalse(self.controller.exists())
        changed=copy.deepcopy(self.job);changed['preparation']=str(self.external/'preparation.json')
        plan=copy.deepcopy(self.plan);plan['native_job']=self.binding('wrong-job.json',changed)
        with self.assertRaisesRegex(ValueError,'canonical_internal_copy_layout'):subject.validate_plan(plan)
        self.external.mkdir()
        with self.assertRaisesRegex(ValueError,'canonical_new_external_output'):subject.validate_plan(self.plan)

    def test_existing_build_is_not_silently_reused_by_fresh_policy(self):
        Path(self.job['paths']['build']).mkdir()
        with self.assertRaisesRegex(ValueError,'canonical_source_or_fresh_build'):subject.validate_plan(self.plan)
        self.assertFalse(self.external.exists())

    def test_real_Git_namespace_is_full_and_unchanged(self):
        closure,actual=subject.verify_namespace(self.sdk,self.namespace)
        self.assertEqual(actual,self.namespace);self.assertEqual(len(closure),8)
        self.assertEqual(closure['root']['head'],self.commit)
        self.assertFalse(self.external.exists())

    def test_extra_untracked_file_cannot_hide_outside_declared_projection(self):
        extra=self.sdk/'untracked-source.py';extra.write_bytes(b'# metadata-only corruption\n')
        try:
            with self.assertRaisesRegex(ValueError,'canonical_source_projection_changed'):
                subject.verify_namespace(self.sdk,self.namespace)
        finally:extra.unlink()

    def test_real_tracked_byte_change_is_not_a_valid_Git_namespace(self):
        path=self.sdk/'Tests/actual.cpp';before=path.read_bytes();path.write_bytes(before+b'// changed\n')
        try:
            with self.assertRaises((ValueError,RuntimeError)):subject.verify_namespace(self.sdk,self.namespace)
        finally:path.write_bytes(before)

    def test_independent_actual_SDK_child_uses_stock_preparation_and_raw_bytes(self):
        result=self.child();self.assertEqual(result.returncode,0,result.stderr.decode('utf-8'))
        observed=json.loads(result.stdout);spec=json.loads(observed['canonical_utf8'])
        self.assertTrue({'Scripts.StructTrain.TimeLearner.'+n for n in subject.MODULES}
                        <= set(observed['SDK_modules']))
        self.assertTrue(all(Path(r['path']).is_relative_to(self.sdk) for r in observed['SDK_modules'].values()))
        self.assertEqual(observed['actor']['path'],str(Path(subject.__file__).resolve()))
        self.assertEqual(observed['native_job_utf8'].encode('utf-8'),(self.controls/'job.json').read_bytes())
        self.assertEqual(spec['execution']['arguments'],['--job',str(self.controller/'inputs/job.json')])
        self.assertEqual(observed['selected_ids'],['Suite/First','Suite/Second'])
        self.assertFalse(observed['compiled_or_tests_or_models']);self.assertIsNone(observed['scientific_verdict'])
        self.assertFalse(self.external.exists());self.assertFalse(self.controller.exists())

    def extra_module_sdk(self, mode):
        # A separate real Git fixture, so the shared source and other cases stay
        # untouched. Whole production Scripts still execute in the clean child.
        sdk=self.case/'extended-sdk';shutil.copytree(self.sdk,sdk)
        self.sdk=sdk
        package=sdk/'Scripts/StructTrain/TimeLearner'
        extra=package/'closure_fixture_extra.py';extra.write_bytes(b'VALUE = "metadata only"\n')
        if mode=='valid':
            addition='\nfrom . import closure_fixture_extra\n'
        else:
            outside=self.case/'outside.py';outside.write_bytes(b'# outside SDK\n')
            alias='Scripts.StructTrain.TimeLearner.closure_fixture_alias'
            path=str(outside if mode=='foreign' else extra)
            addition=('\nimport sys as _s, types as _t\n_m=_t.ModuleType('+repr(alias)+')\n'
                      '_m.__file__='+repr(path)+'\n_s.modules['+repr(alias)+']=_m\n')
        init=package/'__init__.py';init.write_bytes(init.read_bytes()+addition.encode())
        self.git(sdk,'add','Scripts');self.git(sdk,'commit','--quiet','-m','Extra metadata import fixture')
        self.commit=self.git(sdk,'rev-parse','HEAD').decode().strip()
        namespace=copy.deepcopy(self.namespace)
        for path in [init,extra]:
            relative=path.relative_to(sdk).as_posix();raw=path.read_bytes()
            oid=self.git(sdk,'rev-parse','HEAD:'+relative).decode().strip()
            namespace[relative]={'git_mode':'100644','git_blob':oid,'bytes':len(raw),'sha256':digest(raw)}
        self.plan['source']={'path':str(sdk),'commit':self.commit,
                             'namespace':self.binding('extended-namespace.json',namespace)}
        self.job['paths']['source']=str(sdk)
        self.plan['native_job']=self.binding('extended-job.json',self.job)

    def test_extra_Git_bound_import_is_inventoried_without_magic_count(self):
        self.extra_module_sdk('valid');result=self.child()
        self.assertEqual(result.returncode,0,result.stderr.decode())
        modules=json.loads(result.stdout)['SDK_modules']
        self.assertIn('Scripts.StructTrain.TimeLearner.closure_fixture_extra',modules)
        self.assertTrue(all(Path(row['path']).is_relative_to(self.sdk) for row in modules.values()))
        self.assertFalse(self.external.exists())

    def test_extra_import_from_foreign_Tool_path_is_rejected(self):
        self.extra_module_sdk('foreign');result=self.child()
        self.assertNotEqual(result.returncode,0)
        self.assertIn(b'canonical_child_Tool_SDK_namespace_mix',result.stderr)
        self.assertFalse(self.external.exists())

    def test_alias_name_cannot_impersonate_a_different_bound_module(self):
        self.extra_module_sdk('alias');result=self.child()
        self.assertNotEqual(result.returncode,0)
        self.assertIn(b'canonical_child_module_name_path_changed',result.stderr)
        self.assertFalse(self.external.exists())

    def test_wrong_actual_child_head_refuses_without_canonical_sideeffects(self):
        result=self.child(commit='a'*40);self.assertNotEqual(result.returncode,0)
        self.assertIn(b'canonical_child_wrong_source',result.stderr)
        self.assertFalse(self.external.exists());self.assertFalse(self.controller.exists())

    def test_loaded_parent_Tool_namespace_cannot_be_reused_as_SDK_child(self):
        with self.assertRaisesRegex(ValueError,'canonical_child_not_clean_file_bootstrap'):
            subject._child('/unused',str(self.sdk),self.commit,'a'*64)

    def test_owner_operation_is_closed_and_uses_directory_resources(self):
        from .test_owned_python_job import request as owner_request
        # The existing request helper is declaration data, never a runner.
        request=owner_request();request['operation']={'kind':'native-canonical-preparation',
            'plan':{'path':str(self.controls/'plan.json'),'sha256':'a'*64}}
        owned_python_job.validate_request(request)
        request['operation']['command']='arbitrary'
        with self.assertRaises(ValueError):owned_python_job.validate_request(request)
        separate=self.case/'separate-plan';separate.mkdir()
        rows=subject.resources(self.plan,self.case/'owner-job',separate/'plan.json')
        self.assertIn({'path':str(self.external),'access':'write'},rows)
        self.assertIn({'path':str(separate),'access':'read'},rows)
        self.assertIn({'path':str(self.sdk),'access':'read'},rows)
        self.assertNotIn({'path':str(self.sdk),'access':'write'},rows)
        self.assertTrue(all(not str(r['path']).endswith('.json') for r in rows))

    def test_original_plan_and_control_bytes_are_refrozen_before_publication(self):
        raw=encode(self.plan);path=self.controls/'plan.json';path.write_bytes(raw)
        before=subject.capture_inputs(self.plan,path,digest(raw))
        self.assertIn(str(path),before);self.assertIn(str(self.controls/'cohort.json'),before)
        changed=self.controls/'cohort.json';old=changed.read_bytes();changed.write_bytes(old+b' ')
        with self.assertRaisesRegex(ValueError,'canonical_input_changed'):
            subject.capture_inputs(self.plan,path,digest(raw))
        changed.write_bytes(old);path.write_bytes(raw+b' ')
        with self.assertRaisesRegex(ValueError,'canonical_plan_changed'):
            subject.capture_inputs(self.plan,path,digest(raw))
        self.assertFalse(self.external.exists());self.assertFalse(self.controller.exists())

    def test_many_prior_directories_use_existing_declared_protected_read_scope(self):
        from ..resource_reservations import _resources
        parent=self.case/'closed-original';parent.mkdir()
        priors=[]
        for index in range(80):
            directory=parent/str(index);directory.mkdir()
            path=directory/'binding.json';raw=encode({'kind':'metadata-scope-fixture'})
            path.write_bytes(raw);priors.append({'path':str(path),'sha256':digest(raw)})
        self.plan['prior_bindings']=priors
        self.job['protected_runtimes'].append(str(parent))
        self.plan['native_job']=self.binding('job.json',self.job)
        rows=subject.resources(self.plan,self.case/'owner-job',self.controls/'plan.json')
        self.assertIn({'path':str(parent),'access':'read'},rows)
        self.assertTrue(all({'path':str(Path(p['path']).parent),'access':'read'} not in rows for p in priors))
        self.assertLessEqual(len(_resources(rows)),64)
        self.assertNotIn({'path':str(self.case),'access':'read'},rows)
        self.assertNotIn({'path':str(parent),'access':'write'},rows)
        self.assertFalse(self.external.exists());self.assertFalse(self.controller.exists())

    def test_uncovered_prior_directories_do_not_gain_an_undeclared_ancestor(self):
        from ..resource_reservations import _resources,ReservationError
        parent=self.case/'independent-originals';parent.mkdir()
        priors=[]
        for index in range(80):
            directory=parent/str(index);directory.mkdir()
            path=directory/'binding.json';raw=encode({'kind':'metadata-scope-fixture'})
            path.write_bytes(raw);priors.append({'path':str(path),'sha256':digest(raw)})
        self.plan['prior_bindings']=priors
        rows=subject.resources(self.plan,self.case/'owner-job',self.controls/'plan.json')
        self.assertNotIn({'path':str(parent),'access':'read'},rows)
        with self.assertRaisesRegex(ReservationError,'invalid_reservation_resources'):_resources(rows)
        self.assertFalse(self.external.exists());self.assertFalse(self.controller.exists())


if __name__=='__main__':unittest.main()
