from pathlib import Path
import sys,os,json,subprocess,hashlib,threading,traceback,shutil,tarfile,time
base=Path('/media/user/Data/TimeLearnerRefactor');root='8021301e894368aefd045f9d77274fcce9f60245';label='csearch-threshold-joint-full-asan-a2'
out=base/('readbacks/s07-'+label);out.mkdir(exist_ok=False)
source=base/'source-csearch-threshold-joint-asan-build-a1';build=base/'build-csearch-threshold-joint-asan-build-a1';runtime=base/'runtime-csearch-threshold-joint-asan-build-a2';bootstrap=base/'source-closed-worker-recovery-a3'
stop=threading.Event();thread=None;registry=None;token=None;errors=[];passed=False

def write(name,value):
 p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for part in iter(lambda:f.read(1024*1024),b''):h.update(part)
 return h.hexdigest()
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
def ticks(pid):return Path('/proc',str(pid),'stat').read_text().rsplit(') ',1)[1].split()[19]
write('owned-supervisor.json',{'pid':os.getpid(),'start_ticks':ticks(os.getpid()),'root':root,'source':str(source),'build':str(build),'runtime':str(runtime),'contained_supervisor':str(base/('readbacks/s07-'+label+'-container'))})
(out/'producer.py').write_bytes(Path(__file__).read_bytes())
memory_stop=threading.Event();memory_thread=None;memory_group=None
def memory_sample():
 group=memory_group
 record={'monotonic_seconds':time.monotonic(),'cgroup':str(group)}
 for field in ['memory.current','memory.peak','memory.max','memory.swap.current']:
  path=group/field
  if path.exists():
   value=path.read_text().strip();record[field]=int(value) if value!='max' else value
 path=group/'memory.events'
 if path.exists():record['events']={line.split()[0]:int(line.split()[1]) for line in path.read_text().splitlines()}
 return record
def memory_watch():
 while not memory_stop.is_set():
  try:
   with (out/'memory-history.jsonl').open('ab') as f:f.write((json.dumps(memory_sample(),allow_nan=False)+'\n').encode());f.flush();os.fsync(f.fileno())
  except BaseException as error:errors.append('memory_monitor:'+str(error));return
  memory_stop.wait(5)

try:
 memory=int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024;disk=shutil.disk_usage(base)
 assert disk.free>=14*1024**3 and memory>=42*1024**3
 write('resource-preflight.json',{'memory_available_bytes':memory,'disk_free_bytes':disk.free,'worker_memory_max_bytes':42*1024**3,'worker_tasks_max':128,'maximum_wall_seconds':86400,'compilation_disabled':True})
 sys.path.insert(0,str(bootstrap))
 from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
 from Scripts.StructTrain.TimeLearner.contained_process import inspect as inspect_contained
 capacity=None;registry=Reservations(base/'resource-reservations.sqlite3')
 reservation=registry.reserve('s07-'+label,[{'path':str(out),'access':'write'}]+[{'path':str(p),'access':'read'} for p in [source,build,runtime,bootstrap,base/'readbacks/s07-csearch-threshold-joint-asan-gate-a3']],ttl_seconds=120)
 token=reservation['token'];write('reservation.json',dict(reservation,capacity=capacity,release_policy='Hold through archive creation and worker exit; outside controller recovers only after fresh kernel closure and exact owner binding.'))
 def heartbeat():
  while not stop.wait(20):
   try:registry.heartbeat(token,ttl_seconds=120);registry.validate_paths(token)
   except BaseException as error:errors.append(str(error));return
 thread=threading.Thread(target=heartbeat,daemon=True);thread.start()
 previous=inspect_contained(base/'readbacks/s07-csearch-threshold-joint-asan-gate-a3-container');assert previous['all_processes_closed'];write('previous-worker-closure.json',previous)
 assert git(source,'rev-parse','HEAD')==root and not git(source,'status','--porcelain','--untracked-files=no')
 children={}
 for line in git(source,'config','-f','.gitmodules','--get-regexp','^submodule.*.path$').splitlines():
  _,path=line.split(None,1);wanted=git(source,'rev-parse','HEAD:'+path);assert git(source/path,'rev-parse','HEAD')==wanted and not git(source/path,'status','--porcelain','--untracked-files=no');assert not (source/path/'.git/objects/info/alternates').exists();children[path]=wanted
 assert len(children)==7 and children['Libraries/Nmsdk-PulseLib']=='cc97149c90ce98ff24ca688452f4a40d54e0e63d' and not (source/'.git/objects/info/alternates').exists()
 write('source-closure.json',{'root':root,'children':children,'clean':True,'read_only_reuse':True,'new_checkout_build_or_runtime_update':False})
 for name in list(sys.modules):
  if name=='Scripts' or name.startswith('Scripts.'):del sys.modules[name]
 sys.path.insert(0,str(source));os.chdir(source)
 from Scripts.StructTrain.TimeLearner.runtime import snapshot
 from Scripts.StructTrain.TimeLearner.native_gate import run_native_gate
 os.environ['QT_QPA_PLATFORM']='offscreen';os.environ['ASAN_OPTIONS']='detect_leaks=0'
 for key in ['LD_LIBRARY_PATH','QT_PLUGIN_PATH']:os.environ.pop(key,None)
 current=snapshot(source,runtime/'Test_PulseLib_StorageComponents',runtime/'NeuroModelerConsole.ini',build/'CMakeCache.txt');previous_runtime=json.loads((base/'readbacks/s07-csearch-threshold-joint-asan-gate-a3/native-runtime.json').read_text());assert current==previous_runtime
 write('native-runtime.json',current);write('runtime-identity-readback.json',{'unchanged_against_asan44':True,'runtime_fingerprint':current['runtime_fingerprint']})
 specification=json.loads((source/'Scripts/StructTrain/TimeLearner/specs/native-csearch-threshold-regression-v1.json').read_text());assert len(specification['expected_test_ids'])==len(set(specification['expected_test_ids']))==304 and specification['maximum_wall_seconds']==86400
 specification.update(source_root=str(source),runtime_manifest=str(out/'native-runtime.json'),asan_options='detect_leaks=0');write('native-specification.json',specification)
 binding=json.loads((base/('readbacks/s07-'+label+'-container/owned-unit.json')).read_text());memory_group=Path('/sys/fs/cgroup')/binding['control_group'].lstrip('/')
 assert memory_sample()['memory.max']==42*1024**3
 memory_thread=threading.Thread(target=memory_watch,daemon=True);memory_thread.start()
 result=run_native_gate(out/'native-specification.json',out/'native-result');write('native-verdict.json',result)
 memory_stop.set();memory_thread.join(timeout=10)
 import resource
 write('native-memory-result.json',{'cgroup_after_native':memory_sample(),'largest_reaped_child_maxrss_kib':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,'rusage_scope':'largest individual reaped child in this worker; cgroup peak is whole job through native completion','legacy_K1_final_peak_known':False})
 assert not errors,errors
 assert result['execution']=='completed' and result['validity']=='valid' and result['assertion_status']=='passed' and result['inventory']['expected']==result['inventory']['observed']==304
 passed=True
except BaseException as error:write('exception.json',{'reason':str(error),'traceback':traceback.format_exc()})
finally:
 memory_stop.set()
 if memory_thread:memory_thread.join(timeout=10)
 if memory_group is not None:
  try:write('memory-before-archive.json',memory_sample())
  except BaseException as error:write('memory-readback-error.json',{'reason':str(error)})
 try:
  write('terminal.json',{'execution':'completed','native304_asan_passed':passed,'additional_readers_pending':True,'owner_replay_pending':True,'leak_absence_attested':False,'whole_plan_complete':False,'scientific_verdict':None})
  hashes={}
  for prefix in ['App/NeuroModelerConsole','Tests/Integration/Libraries','Scripts/StructTrain/TimeLearner','Libraries/Nmsdk-PulseLib/Core']:
   for p in (source/prefix).rglob('*'):
    if p.is_file() and '__pycache__' not in p.parts:hashes[p.relative_to(source).as_posix()]=sha(p)
  write('source-hashes.json',hashes)
  files={}
  for p in sorted(out.rglob('*')):
   if not p.is_file():continue
   assert p.resolve().is_relative_to(out.resolve()),str(p)
   files[p.relative_to(out).as_posix()]={'bytes':p.stat().st_size,'sha256':sha(p)}
  with tarfile.open(out/'primary.tar.xz','w:xz',preset=3) as archive:
   for name,record in files.items():
    p=out/name;assert p.stat().st_size==record['bytes'] and sha(p)==record['sha256'];info=tarfile.TarInfo(name);info.size=record['bytes']
    with p.open('rb') as f:archive.addfile(info,f)
  write('bundle.json',{'kind':'joint_csearch_threshold_full_native_regression','schema_version':1,'root':root,'pulselib':children.get('Libraries/Nmsdk-PulseLib') if 'children' in globals() else None,'acceptance_status':'native_checks_passed_readers_pending' if passed else 'not_accepted','members':files,'archive_bytes':(out/'primary.tar.xz').stat().st_size,'archive_sha256':sha(out/'primary.tar.xz'),'scientific_verdict':None})
 finally:
  stop.set()
  if thread:thread.join(timeout=30)
 print('CLOSED',passed,flush=True)
