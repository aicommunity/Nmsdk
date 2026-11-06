from pathlib import Path
import os,sys,json,hashlib,threading,tarfile,traceback,sqlite3
base=Path('/media/user/Data/TimeLearnerRefactor');tool=base/'source-configured-transport-preconditions-normal-a1';out=base/'readbacks/s05-configured-transport-cold-matched-a1';out.mkdir(exist_ok=False);sys.dont_write_bytecode=True;sys.path.insert(0,str(tool));stop=threading.Event();thread=None;registry=None;token=None;passed=False;errors=[]
from Scripts.StructTrain.TimeLearner.native_gate import run_native_gate
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):p=out/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
write('owner.json',{'pid':os.getpid(),'start_ticks':Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19],'compilation_disabled':True});(out/'producer.py').write_bytes(Path(__file__).read_bytes())
try:
 c=sqlite3.connect('file:'+str(base/'resource-reservations.sqlite3')+'?mode=ro',uri=True)
 try:metadata=dict(c.execute('SELECT key,value FROM metadata'))
 finally:c.close()
 registry=Reservations(base/'resource-reservations.sqlite3',**({'capacity':json.loads(metadata['capacity'])} if 'capacity' in metadata else {}))
 jobs={'old':base/'readbacks/s07-attempt-invalid-budget-fixed-normal-a1','new':base/'readbacks/s07-configured-transport-preconditions-normal-a1'}
 runtimes={};sources={};reads=[tool]
 for mode,p in jobs.items():
  dependency=inspect_worker_dependency(Path(str(p)+'-container'),registry,p.name);assert dependency['state']=='ready' and dependency['reservation_state']=='released',dependency
  write('dependencies/'+mode+'.json',dependency);runtimes[mode]=json.loads((p/'native-runtime.json').read_text());sources[mode]=base/('source-attempt-invalid-budget-fixed-normal-a1' if mode=='old' else 'source-configured-transport-preconditions-normal-a1')
  reads.extend([p,sources[mode],Path(runtimes[mode]['executable']['path']).parent,Path(runtimes[mode]['build_flags']['NMSDK_RESOURCE_ROOT'])])
 selected=[]
 for p in sorted(set(p.resolve(strict=True) for p in reads),key=lambda p:len(p.parts)):
  if not any(p.is_relative_to(q) for q in selected):selected.append(p)
 lease=registry.reserve(out.name,[{'path':str(out),'access':'write'}]+[{'path':str(p),'access':'read'} for p in selected],ttl_seconds=120);token=lease['token'];write('reservation.json',lease)
 def heartbeat():
  while not stop.wait(20):
   try:registry.heartbeat(token,ttl_seconds=120);registry.validate_paths(token)
   except BaseException as e:errors.append(str(e));return
 thread=threading.Thread(target=heartbeat,daemon=True);thread.start();comparison=[]
 for case in ['ClassicConfiguredN1','BranchConfiguredN0']:
  dirs={}
  for mode in ['old','new']:
   folder=out/case/mode;folder.mkdir(parents=True,exist_ok=False);write(case+'/'+mode+'/runtime.json',runtimes[mode]);spec={'kind':'timelearner_native_test_gate','schema_version':2,'runtime_manifest':str(folder/'runtime.json'),'source_root':str(sources[mode]),'expected_test_ids':['NativeLearnedState/'+case],'maximum_wall_seconds':600,'asan_options':'','cooperative_runtime_capture':True};write(case+'/'+mode+'/specification.json',spec)
   result=run_native_gate(folder/'specification.json',folder/'native');write(case+'/'+mode+'/result.json',result)
   assert result['validity']=='valid' and result['assertion_status']==('failed' if mode=='old' else 'passed'),result
   dirs[mode]=folder/'native/native'
  old={p.relative_to(dirs['old']).as_posix():p.read_bytes() for p in dirs['old'].rglob('*.csv')};new={p.relative_to(dirs['new']).as_posix():p.read_bytes() for p in dirs['new'].rglob('*.csv')}
  assert old and set(old)<=set(new) and all(old[n]==new[n] for n in old),case
  a={p.relative_to(dirs['old']).as_posix():p.read_bytes() for p in dirs['old'].rglob('*transport_training_precondition.json')};z={p.relative_to(dirs['new']).as_posix():p.read_bytes() for p in dirs['new'].rglob('*transport_training_precondition.json')}
  assert a and set(a)==set(z) and all(a[n]==z[n] for n in a),case
  comparison.append({'case':case,'old_original_verdict':'failed','new_diagnostic_transport_verdict':'passed','cold_CSV_byte_identical':{n:{'bytes':len(old[n]),'sha256':hashlib.sha256(old[n]).hexdigest()} for n in old},'cold_precondition_byte_identical':{n:hashlib.sha256(a[n]).hexdigest() for n in a},'additional_new_csv_count':len(set(new)-set(old))})
 write('matched-cold-comparison.json',{'cases':comparison,'scientific_verdict':None,'absolute_timestamps_compared_without_translation':True});assert not errors;passed=True
except BaseException as e:write('exception.json',{'reason':str(e),'traceback':traceback.format_exc()})
finally:
 stop.set()
 if thread:thread.join(timeout=10)
 write('tool-source-hashes.json',{p.relative_to(tool).as_posix():sha(p) for p in (tool/'Scripts/StructTrain/TimeLearner').rglob('*.py')});write('terminal.json',{'matched_cold_4_process_controls_passed':passed,'compilation_disabled':True,'scientific_verdict':None,'whole_plan_complete':False});members={}
 with tarfile.open(out/'primary.tar.xz','w:xz',preset=3) as archive:
  for p in sorted(out.rglob('*')):
   if p.is_file() and p.name not in ['primary.tar.xz','bundle.json']:
    n=p.relative_to(out).as_posix();members[n]={'bytes':p.stat().st_size,'sha256':sha(p)};i=tarfile.TarInfo(n);i.size=p.stat().st_size
    with p.open('rb') as stream:archive.addfile(i,stream)
 write('bundle.json',{'matched_cold_4_process_controls_passed':passed,'members':members,'archive_bytes':(out/'primary.tar.xz').stat().st_size,'archive_sha256':sha(out/'primary.tar.xz')});print('CLOSED',passed,flush=True)
