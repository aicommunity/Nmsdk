from pathlib import Path
import os,sys,json,gzip,hashlib,subprocess,threading,time,shutil,sqlite3,tarfile,traceback,unittest,io
base=Path('/home/user/timelearner-refactor');source=base/'source-pipeline-condition-matrix-a1';out=base/'readbacks/s10-pipeline-condition-native-matrix-a2';out.mkdir(exist_ok=False);controller=Path(str(out)+'-container');sys.dont_write_bytecode=True;os.environ['PYTHONDONTWRITEBYTECODE']='1';sys.path.insert(0,str(source));os.chdir('/tmp')
from Scripts.StructTrain.TimeLearner.managed_pipeline import run_pipeline,audit_pipeline,signed
from Scripts.StructTrain.TimeLearner.pipeline_condition import build_binding
from Scripts.StructTrain.TimeLearner.native_process_policy import policy_for_reservation
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.process_runner import verify_runtime
from Scripts.StructTrain.TimeLearner.contained_process import inspect as inspect_contained
from Scripts.StructTrain.TimeLearner.native_evidence import load
stop=threading.Event();registry=None;global_token=None;case_registry=None;case_token=None;errors=[];passed=False;thread=None

def write(name,value):
 p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as stream:
  for b in iter(lambda:stream.read(1024**2),b''):h.update(b)
 return h.hexdigest()
write('owner.json',{'pid':os.getpid(),'start_ticks':Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19],'tool_root':'83a82844a6792e23f39106d1d3f41e8638920077','compiled_root':'2e0618110a9abb48b94f6edc6b63c51f829ec810'});(out/'producer.py').write_bytes(Path(__file__).read_bytes())
try:
 assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()=='83a82844a6792e23f39106d1d3f41e8638920077'
 old_declaration=load(base/'readbacks/s10-integrated-coordinator-normal-a3/declaration.json');runtime=load(Path(old_declaration['runtime']));verify_runtime(runtime);assert runtime['executable']['sha256']=='b2d98c8f85be0ff5d87769ddd4285bbc2ee2fc8b39609d2bd4833149865c5153';write('runtime.json',runtime)
 free=shutil.disk_usage(base).free;available=int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024;budget=1280*1024**2;assert free>=1024**3+budget and available>=6*1024**3
 write('resource-preflight.json',{'free_disk_bytes':free,'available_memory_bytes':available,'output_disk_budget_bytes':budget,'minimum_disk_headroom_bytes':1024**3,'budget_basis':'Two eight-case suites; expected40 actual native phase units. Same completed two-case primary253385299 bytes provides conservative roughly1.05GB full estimate plus compressed primary/log reserve. Accounting not filesystem quota.','parent_memory_cap':512*1024**2,'sequential_native_memory_cap':4*1024**3})
 calibration=base/'readbacks/s10-managed-native-calibration-normal-a1/actual-controls'
 c=sqlite3.connect('file:'+str(base/'resource-reservations.sqlite3')+'?mode=ro',uri=True)
 try:capacity=json.loads(dict(c.execute('SELECT key,value FROM metadata'))['capacity'])
 finally:c.close()
 registry=Reservations(base/'resource-reservations.sqlite3',capacity=capacity)
 reads=[source,base/'source-integrated-acceptance-normal-a1',base/'build-integrated-acceptance-normal-a1',Path(runtime['executable']['path']).parent,Path(runtime['build_flags']['NMSDK_RESOURCE_ROOT']),Path(old_declaration['templates']),Path(old_declaration['positive_templates']),calibration];selected=[]
 for p in sorted(set(p.resolve(strict=True) for p in reads),key=lambda p:len(p.parts)):
  if not any(p.is_relative_to(q) for q in selected):selected.append(p)
 lease=registry.reserve(out.name,[{'path':str(out),'access':'write'}]+[{'path':str(p),'access':'read'} for p in selected],ttl_seconds=120,demands={'slots':1,'memory_bytes':4*1024**3+512*1024**2,'disk_bytes':budget});global_token=lease['token'];write('global-reservation.json',lease)
 def watch():
  while not stop.wait(10):
   try:
    registry.heartbeat(global_token,ttl_seconds=120);registry.validate_paths(global_token)
    if shutil.disk_usage(base).free<1024**3:
     errors.append('disk_headroom_exhausted')
     for p in out.glob('suites/*/*/runs/pipeline/phases/*/process'):
      if (p/'contained/owned-unit.json').exists() and not(p/'cancel.request').exists():(p/'cancel.request').write_text('Owned matrix phase cancellation: less than1GiB free disk headroom.\n')
     return
   except BaseException as error:errors.append(str(error));return
 thread=threading.Thread(target=watch,daemon=True);thread.start()
 from Scripts.StructTrain.TimeLearner.tests.test_managed_pipeline_coordinator import ManagedPipelineCoordinatorTest
 from Scripts.StructTrain.TimeLearner.tests.test_managed_pipeline_condition_coordinator import ManagedPipelineConditionCoordinatorTest
 names=[]
 for version,cls in [(1,ManagedPipelineCoordinatorTest),(2,ManagedPipelineConditionCoordinatorTest)]:
  assert not errors
  declaration=dict(old_declaration,runtime=str(out/'runtime.json'),controller=str(controller),output=str(out/'suites'/('schema'+str(version))));write('declaration-schema'+str(version)+'.json',declaration);os.environ['TIMELEARNER_MANAGED_NATIVE_PIPELINE']=str(out/('declaration-schema'+str(version)+'.json'));os.environ['TIMELEARNER_COORDINATOR_CALIBRATION_TEMPLATES']=str(calibration)
  suite=unittest.defaultTestLoader.loadTestsFromTestCase(cls);ids=[t.id() for t in suite];assert len(ids)==8;write('progress.json',{'suite':version,'declared_tests':ids,'scientific_verdict':None});stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2,failfast=True).run(suite);(out/('schema'+str(version)+'-unittest.log')).write_text(stream.getvalue());r={'schema':version,'declared_ids':ids,'tests_run':result.testsRun,'failures':[{'id':t.id(),'traceback':e} for t,e in result.failures],'errors':[{'id':t.id(),'traceback':e} for t,e in result.errors],'skips':[{'id':t.id(),'reason':e} for t,e in result.skipped]};write('suite-schema'+str(version)+'-result.json',r);assert result.wasSuccessful() and result.testsRun==8 and not result.skipped and not errors;names.extend(ids)
 units=set();identities=set();compared=[]
 for name in ['Classic-v1','Classic-v2','Branch-v1','Branch-v2','Classic-N0','Classic-N1','Branch-N0','Branch-N1']:
  roots=[out/'suites'/('schema'+str(v))/name/'runs/pipeline' for v in [1,2]];positive='-v' in name;fps=[];csvs=[]
  for root in roots:
   job=load(root.parent.parent/'pipeline-job.json');fps.append(build_binding(job,runtime)['condition_fingerprint']);audit=audit_pipeline(root);assert audit['pipeline_complete']==positive
   records={p.relative_to(root).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in root.rglob('*.csv')};assert records;csvs.append(records)
   for phase in (root/'phases').iterdir():
    process=phase/'process';assert inspect_contained(process/'contained')['all_processes_closed'];unit=load(process/'contained/owned-unit.json')['unit'];owner=load(process/'owned-process.json');key=(owner['boot_id'],owner['pid'],owner['start_ticks']);assert unit not in units and key not in identities;units.add(unit);identities.add(key)
  assert fps[0]==fps[1] and csvs[0]==csvs[1];compared.append({'case':name,'positive':positive,'condition_fingerprint':fps[0],'byte_identical_csvs':csvs[0]})
 assert len(units)==len(identities)==40 and len(names)==16;write('schema-comparison.json',{'cases':compared,'actual_distinct_native_phase_units':40,'same_compiled_runtime':True,'independent_scientific_repetitions':False});write('result.json',{'tests_run':16,'actual_native_phase_units':sorted(units),'passed':True,'scientific_verdict':None});passed=True
except BaseException as error:write('exception.json',{'reason':str(error),'traceback':traceback.format_exc()})
finally:
 stop.set()
 if thread:thread.join(timeout=10)
 groups=list(out.glob('suites/*/*/runs/pipeline/phases/*/process/contained'));closed=all(inspect_contained(p)['all_processes_closed'] for p in groups);write('native-closure.json',{'all_native_groups_closed':closed,'groups':len(groups)})
 if closed and global_token is not None:registry.release(global_token,note='Full coordinator matrix every actual native group freshly closed; per-case reservations checked separately')
 write('terminal.json',{'matrix_passed':passed,'all_native_groups_closed':closed,'tool_root':'83a82844a6792e23f39106d1d3f41e8638920077','compiled_root':'2e0618110a9abb48b94f6edc6b63c51f829ec810','whole_plan_complete':False,'scientific_verdict':None})
 if closed:
  write('source-hashes.json',{p.relative_to(source).as_posix():sha(p) for p in (source/'Scripts/StructTrain/TimeLearner').rglob('*') if p.is_file() and (p.suffix=='.py' or '/tests/fixtures/' in p.as_posix())});members={}
  with tarfile.open(out/'primary.tar.xz','w:xz',preset=3) as tf:
   for p in sorted(out.rglob('*')):
    if p.is_file() and p.name not in ['primary.tar.xz','bundle.json'] and not p.name.endswith(('-wal','-shm')):
     name=p.relative_to(out).as_posix();members[name]={'bytes':p.stat().st_size,'sha256':sha(p)};info=tarfile.TarInfo(name);info.size=p.stat().st_size
     with p.open('rb') as stream:tf.addfile(info,stream)
  write('bundle.json',{'matrix_passed':passed,'members':members,'archive_bytes':(out/'primary.tar.xz').stat().st_size,'archive_sha256':sha(out/'primary.tar.xz'),'scientific_verdict':None})
 print('CLOSED',passed,closed,flush=True)
