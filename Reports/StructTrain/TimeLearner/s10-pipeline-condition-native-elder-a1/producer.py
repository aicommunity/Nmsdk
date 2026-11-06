from pathlib import Path
import os,sys,json,gzip,hashlib,subprocess,threading,time,shutil,sqlite3,tarfile,traceback
base=Path('/home/user/timelearner-refactor');source=base/'source-pipeline-condition-a2';out=base/'readbacks/s10-pipeline-condition-native-a1';out.mkdir(exist_ok=False);controller=Path(str(out)+'-container');sys.dont_write_bytecode=True;os.environ['PYTHONDONTWRITEBYTECODE']='1';sys.path.insert(0,str(source));os.chdir('/tmp')
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
write('owner.json',{'pid':os.getpid(),'start_ticks':Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19],'tool_root':'d43780822a7b9e2b7c0229c323cda174abc7fce8','compiled_root':'2e0618110a9abb48b94f6edc6b63c51f829ec810'});(out/'producer.py').write_bytes(Path(__file__).read_bytes())
try:
 assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()=='d43780822a7b9e2b7c0229c323cda174abc7fce8'
 fixture=source/'Scripts/StructTrain/TimeLearner/tests/fixtures/pipeline_condition';manifest=load(fixture/'source.json');records={}
 for row in manifest['members']:
  p=fixture/row['path'];assert sha(p)==row['gzip_sha256'];raw=gzip.decompress(p.read_bytes());assert len(raw)==row['raw_bytes'] and hashlib.sha256(raw).hexdigest()==row['raw_sha256'];records[row['path']]=json.loads(raw)
 runtime=records['runtime.json.gz'];assert runtime['executable']['sha256']=='b2d98c8f85be0ff5d87769ddd4285bbc2ee2fc8b39609d2bd4833149865c5153';verify_runtime(runtime);write('runtime.json',runtime)
 free=shutil.disk_usage(base).free;available=int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024;budget=384*1024**2;assert free>=1024**3+budget and available>=6*1024**3
 write('resource-preflight.json',{'free_disk_bytes':free,'available_memory_bytes':available,'output_disk_budget_bytes':budget,'minimum_disk_headroom_bytes':1024**3,'old_same_two_case_raw_bytes':139154751+111844884,'budget_basis':'Two previously published exact declarations250999635 bytes plus new condition bindings, logs and compressed primary; cancellation below1GiB headroom. Accounting, not filesystem quota.','parent_memory_cap':512*1024**2,'sequential_native_memory_cap':4*1024**3})
 c=sqlite3.connect('file:'+str(base/'resource-reservations.sqlite3')+'?mode=ro',uri=True)
 try:metadata=dict(c.execute('SELECT key,value FROM metadata'))
 finally:c.close()
 registry=Reservations(base/'resource-reservations.sqlite3',capacity=json.loads(metadata['capacity']))
 reads=[source,base/'source-integrated-acceptance-normal-a1',base/'build-integrated-acceptance-normal-a1',Path(runtime['executable']['path']).parent,Path(runtime['build_flags']['NMSDK_RESOURCE_ROOT'])];reads=sorted(set(p.resolve(strict=True) for p in reads),key=lambda p:len(p.parts));selected=[]
 for p in reads:
  if not any(p.is_relative_to(q) for q in selected):selected.append(p)
 lease=registry.reserve(out.name,[{'path':str(out),'access':'write'}]+[{'path':str(p),'access':'read'} for p in selected],ttl_seconds=120,demands={'slots':1,'memory_bytes':4*1024**3+512*1024**2,'disk_bytes':budget});global_token=lease['token'];write('global-reservation.json',lease)
 def watch():
  while not stop.wait(5):
   try:
    registry.heartbeat(global_token,ttl_seconds=120);registry.validate_paths(global_token)
    if case_token is not None:case_registry.heartbeat(case_token,ttl_seconds=120);case_registry.validate_paths(case_token)
    free=shutil.disk_usage(base).free
    if free<1024**3:
     for p in out.glob('cases/*/runs/pipeline/phases/*/process'):
      if (p/'contained/owned-unit.json').exists() and not(p/'cancel.request').exists():(p/'cancel.request').write_text('Owned phase cancellation: less than1GiB free disk headroom.\n')
     errors.append('disk_headroom_exhausted');return
   except BaseException as error:errors.append(str(error));return
 thread=threading.Thread(target=watch,daemon=True);thread.start();results=[];all_units=set()
 for name in ['Classic-v1','Branch-v2']:
  assert not errors and shutil.disk_usage(base).free>=1024**3
  case=out/'cases'/name;case.mkdir(parents=True);spec=records[name+'.json.gz'];baseline=build_binding(spec,runtime)['condition_fingerprint'];spec['schema_version']=2
  def rename(value):
   if isinstance(value,dict):
    for key,child in value.items():
     if key in ['run_id','trial_id','attempt_id']:value[key]='condition-native-a1/'+child
     else:rename(child)
   elif isinstance(value,list):
    for child in value:rename(child)
  rename(spec);spec['phases'][0]['job']=signed(spec['phases'][0]['job']);assert build_binding(spec,runtime)['condition_fingerprint']==baseline;declaration=case/'job.json';declaration.write_text(json.dumps(spec));runtime_path=out/'runtime.json'
  case_registry=Reservations(case/'leases.sqlite3',capacity={'slots':1,'memory_bytes':6*1024**3,'disk_bytes':512*1024**2,'tasks':512},managed_units=True)
  lease=case_registry.reserve('condition-native-a1-'+name,[{'path':str(case/'runs'),'access':'write'}],demands={'slots':1,'memory_bytes':4*1024**3+512*1024**2,'disk_bytes':budget,'tasks':256},controller_directory=str(controller),ttl_seconds=120);case_token=lease['token'];write('cases/'+name+'/reservation.json',lease);policy=policy_for_reservation(case_registry,case_token,memory_bytes=4*1024**3,tasks=64);write('cases/'+name+'/policy.json',policy);write('progress.json',{'case':name,'phase':'cold_train','scientific_verdict':None})
  root=case/'runs/pipeline';paused=run_pipeline(declaration,runtime_path,policy,root,stop_after='train');assert paused['completed_phases']==['train'] and paused['condition_declaration_bound'] and not paused['pipeline_complete'];state=root/'phases/train/native/train_learned_state.json';state_sha=sha(state);binding_sha=sha(root/'condition-binding.json');write('cases/'+name+'/paused-audit.json',paused)
  assert not errors and shutil.disk_usage(base).free>=1024**3;write('progress.json',{'case':name,'phase':'continue_calibration_frozen','scientific_verdict':None});complete=run_pipeline(declaration,runtime_path,policy,root,resume=True);assert complete['pipeline_complete'] and complete['completed_phases']==['train','export','calibrate','evaluate'] and complete['condition_fingerprint']==baseline and not complete['condition_identity_attested'];assert sha(state)==state_sha and sha(root/'condition-binding.json')==binding_sha
  units={p.name:load(p/'process/contained/owned-unit.json')['unit'] for p in (root/'phases').iterdir()};assert len(units)==4 and len(set(units.values()))==4 and not all_units.intersection(units.values());all_units.update(units.values());assert all(inspect_contained(p/'process/contained')['all_processes_closed'] for p in (root/'phases').iterdir());again=run_pipeline(declaration,runtime_path,policy,root,resume=True);assert again==complete and units=={p.name:load(p/'process/contained/owned-unit.json')['unit'] for p in (root/'phases').iterdir()};metrics=complete['evaluation']['pooled_counts'];assert {k:metrics[k] for k in ['TP','FP','FN','TN']}=={'TP':2,'FP':0,'FN':0,'TN':2}
  write('cases/'+name+'/result.json',{'audit':complete,'phase_units':units,'completed_continue_started_no_new_unit':True,'learned_state_unchanged_on_continue':True,'condition_binding_unchanged_on_continue':True,'same_matrix_engineering_fixture':True,'stock_scientific_result':False,'scientific_verdict':None});case_registry.release(case_token,note='All four actual native phase groups freshly closed; completed continuation did not rerun phases');case_token=None;results.append(name)
 assert not errors and len(all_units)==8;write('result.json',{'cases':results,'actual_native_phase_units':sorted(all_units),'passed':True,'scientific_verdict':None});passed=True
except BaseException as error:write('exception.json',{'reason':str(error),'traceback':traceback.format_exc()})
finally:
 stop.set()
 if thread:thread.join(timeout=10)
 groups=list(out.glob('cases/*/runs/pipeline/phases/*/process/contained'));closed=all(inspect_contained(p)['all_processes_closed'] for p in groups);write('native-closure.json',{'all_native_groups_closed':closed,'groups':len(groups)})
 if closed:
  if case_token is not None:case_registry.release(case_token,note='Aborted pilot; every registered native group freshly closed')
  if global_token is not None:registry.release(global_token,note='Pilot native groups freshly closed; source/runtime unchanged')
 write('terminal.json',{'pilot_passed':passed,'all_native_groups_closed':closed,'tool_root':'d43780822a7b9e2b7c0229c323cda174abc7fce8','compiled_root':'2e0618110a9abb48b94f6edc6b63c51f829ec810','whole_plan_complete':False,'scientific_verdict':None})
 if closed:
  write('source-hashes.json',{p.relative_to(source).as_posix():sha(p) for p in (source/'Scripts/StructTrain/TimeLearner').rglob('*') if p.is_file() and (p.suffix=='.py' or '/tests/fixtures/' in p.as_posix())});members={}
  with tarfile.open(out/'primary.tar.xz','w:xz',preset=3) as tf:
   for p in sorted(out.rglob('*')):
    if p.is_file() and p.name not in ['primary.tar.xz','bundle.json'] and not p.name.endswith(('-wal','-shm')):
     name=p.relative_to(out).as_posix();members[name]={'bytes':p.stat().st_size,'sha256':sha(p)};info=tarfile.TarInfo(name);info.size=p.stat().st_size
     with p.open('rb') as stream:tf.addfile(info,stream)
  write('bundle.json',{'pilot_passed':passed,'members':members,'archive_bytes':(out/'primary.tar.xz').stat().st_size,'archive_sha256':sha(out/'primary.tar.xz'),'scientific_verdict':None})
 print('CLOSED',passed,closed,flush=True)
