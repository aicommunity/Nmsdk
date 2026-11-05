from pathlib import Path
import os,sys,json,subprocess,hashlib,threading,traceback,tarfile,shutil
base=Path('/home/user/timelearner-refactor');source=base/'source-integrated-historical-replay-a1';out=base/'readbacks/s06-recognition-shared-saved-ab-a2';out.mkdir(exist_ok=False);sys.path.insert(0,str(source));sys.dont_write_bytecode=True
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.process_runner import verify_runtime
r=Reservations(base/'resource-reservations.sqlite3',capacity={'slots':1,'memory_bytes':24*1024**3,'disk_bytes':14*1024**3});token=None;stop=threading.Event();thread=None;errors=[];passed=False
origin=base/'readbacks/s06-recognition-owner-burst-normal-a1';old=base/'readbacks/s06-shared-recognition-ab-a1'
def write(n,v):(out/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
(out/'producer.py').write_bytes(Path(__file__).read_bytes());write('owned-supervisor.json',{'pid':os.getpid(),'start_ticks':Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19],'package_root':'f3af229da421c27f0c8e2756dc858d6af90c6092','native_roots':['1eab24decb6432947afc928e7f049f3a07de2709','2cb855677f3e7160cd01837f62c649b18803ebf0'],'cold_train':False})
try:
 assert shutil.disk_usage(base).free>=2*1024**3
 assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()=='f3af229da421c27f0c8e2756dc858d6af90c6092'
 for name in ['s06-shared-recognition-ab-a1','s06-recognition-owner-burst-normal-a1']:
  state=inspect_worker_dependency(base/'readbacks'/(name+'-container'),r,name);assert state['state']=='ready' and state['reservation_state']=='released';write(name+'-prerequisite.json',state)
 assert json.loads((origin/'terminal.json').read_text())['recognition8_and_lifecycle133_passed']
 prior=base/'readbacks/s06-recognition-shared-saved-ab-a1';assert not (prior/'reservation.json').exists();write('previous-failed-preflight.json',{'terminal':json.loads((prior/'terminal.json').read_text()),'exception':json.loads((prior/'exception.json').read_text()),'native_processes_launched':0,'reason':'source_closure intentionally stores content identity without absolute root path; use explicit verified native source binding'})
 native_sources={'baseline':base/'source-shared-lifecycle-corrected-normal-a2','candidate':base/'source-recognition-owner-burst-normal-a1'}
 runtimes={'baseline':json.loads((old/'baseline-runtime.json').read_text()),'candidate':json.loads((origin/'native-runtime.json').read_text())}
 paths=[source,origin,old]
 for name,runtime in runtimes.items():
  assert subprocess.check_output(['git','-C',str(native_sources[name]),'rev-parse','HEAD'],text=True).strip()==runtime['source_closure']['root']['head']
  verify_runtime(runtime);write(name+'-runtime.json',runtime);paths.extend([Path(str(native_sources[name])),Path(runtime['executable']['path']).parent])
 # Repeated paths are harmless scientifically, but a reservation requires an exact unique declaration.
 paths=list(dict.fromkeys(paths));lease=r.reserve(out.name,[{'path':str(out),'access':'write'}]+[{'path':str(p),'access':'read'} for p in paths],demands={'slots':1,'memory_bytes':8*1024**3,'disk_bytes':1024**3},ttl_seconds=120);token=lease['token'];write('reservation.json',lease)
 def heartbeat():
  while not stop.wait(20):
   try:r.heartbeat(token,ttl_seconds=120);r.validate_paths(token)
   except BaseException as e:errors.append(str(e));return
 thread=threading.Thread(target=heartbeat,daemon=True);thread.start()
 native=origin/'focused-result/native';rows=[{'id':'Owner'+str(i+1).zfill(2),'package':f.name,'file_sha256':sha(f)} for i,f in enumerate(sorted(native.glob('*_owner_recognition_state.json')))];assert len(rows)==8
 before={f.name:sha(f) for f in native.iterdir() if f.is_file()};write('source-primary-before.json',before)
 for name,runtime in runtimes.items():
  spec={'kind':'timelearner_recognition_owner_replay','schema_version':1,'source_directory':str(native),'source_bundle':str(origin/'bundle.json'),'source_archive':str(origin/'primary.tar.xz'),'source_prefix':'focused-result/native','origin_evidence_commit':'b411dbf1eb469f83442dc816f77563f82bdfb5ea','native_source_root':str(native_sources[name]),'runtime_manifest':str(out/(name+'-runtime.json')),'maximum_wall_seconds':120,'asan_options':'','cases':rows};write(name+'-specification.json',spec)
  env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',QT_QPA_PLATFORM='offscreen');env.pop('ASAN_OPTIONS',None)
  for k in ['LD_LIBRARY_PATH','QT_PLUGIN_PATH']:env.pop(k,None)
  args=[sys.executable,'-m','Scripts.StructTrain.TimeLearner.recognition_owner_replay',str(out/(name+'-specification.json')),'--output',str(out/name)]
  with (out/(name+'-cli.log')).open('wb') as log:result=subprocess.run(args,cwd=source,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=3000)
  index=json.loads((out/name/'index.json').read_text());assert result.returncode==0 and index['passed'] and len(index['cases'])==8 and all(v['passed'] for v in index['cases'])
 pairs={}
 for row in rows:
  a=out/'baseline'/row['id']/'actual.json.csv';b=out/'candidate'/row['id']/'actual.json.csv';assert a.read_bytes()==b.read_bytes();pairs[row['id']]={'bytes':a.stat().st_size,'sha256':sha(a),'source_package_file':row['package'],'source_package_file_sha256':row['file_sha256']}
 after={f.name:sha(f) for f in native.iterdir() if f.is_file()};assert after==before;write('source-primary-after.json',after);write('comparison.json',{'same_source_packages':8,'separate_native_processes':16,'byte_equal_actual_soma_input_CSV':pairs,'new_cold_train':False,'scientific_verdict':None});assert not errors;passed=True
except BaseException as e:write('exception.json',{'reason':str(e),'traceback':traceback.format_exc()})
finally:
 stop.set()
 if thread:thread.join(timeout=30)
 write('source-hashes.json',{p.relative_to(source).as_posix():sha(p) for p in (source/'Scripts/StructTrain/TimeLearner').rglob('*.py') if '__pycache__' not in p.parts});write('terminal.json',{'saved_state_AB16_passed':passed,'new_training_executed':False,'integrated_CPP_runtime_built':False,'source_package':'f3af229da421c27f0c8e2756dc858d6af90c6092','whole_plan_complete':False,'scientific_verdict':None})
 members={p.relative_to(out).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in out.rglob('*') if p.is_file() and not p.is_symlink()}
 with tarfile.open(out/'primary.tar.xz','w:xz',preset=3) as a:
  for n,v in members.items():
   info=tarfile.TarInfo(n);info.size=v['bytes']
   with (out/n).open('rb') as f:a.addfile(info,f)
 write('bundle.json',{'members':members,'archive_bytes':(out/'primary.tar.xz').stat().st_size,'archive_sha256':sha(out/'primary.tar.xz'),'scientific_verdict':None});print('CLOSED',passed,flush=True)
