from pathlib import Path
import os,sys,json,hashlib,subprocess,sqlite3,shutil,threading,time,traceback,tarfile
base=Path('/home/user/timelearner-refactor');out=base/'readbacks/s07-integrated-native304-normal-a1';out.mkdir(exist_ok=False);source=base/'source-integrated-acceptance-normal-a1';build=base/'build-integrated-acceptance-normal-a1';runtime=base/'runtime-integrated-acceptance-normal-a1';tool=base/'source-publication-lock-recovery-a2';root='2e0618110a9abb48b94f6edc6b63c51f829ec810';tool_root='10d45ed93f08928a9992a3cf569c6a4938cdcd64';stop=threading.Event();monitor_stop=threading.Event();thread=None;monitor=None;registry=None;token=None;errors=[];passed=False;memory_group=None
sys.dont_write_bytecode=True;os.environ['PYTHONDONTWRITEBYTECODE']='1';sys.path.insert(0,str(tool));os.chdir(tool)
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.runtime import snapshot
from Scripts.StructTrain.TimeLearner.native_gate import run_native_gate

def write(n,v):
 p=out/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for part in iter(lambda:f.read(1024**2),b''):h.update(part)
 return h.hexdigest()
def git(p,*a):return subprocess.check_output(['git','-C',str(p),*a],text=True).strip()
write('owner.json',{'pid':os.getpid(),'start_ticks':Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19],'compiled_root':root,'tool_root':tool_root});(out/'producer.py').write_bytes(Path(__file__).read_bytes())
try:
 c=sqlite3.connect('file:'+str(base/'resource-reservations.sqlite3')+'?mode=ro',uri=True)
 try:metadata=dict(c.execute('SELECT key,value FROM metadata'))
 finally:c.close()
 registry=Reservations(base/'resource-reservations.sqlite3',capacity=json.loads(metadata['capacity']));previous=inspect_worker_dependency(base/'readbacks/s02-elder-verified-cache-release-a3-container',registry,'s02-elder-verified-cache-release-a3');assert previous['state']=='ready';assert json.loads((base/'readbacks/s02-elder-verified-cache-release-a3/terminal.json').read_text())['verified_cache_release_passed'];write('cleanup-closed.json',previous)
 disk=shutil.disk_usage(base).free;memory=int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024;budget=7*1024**3//4;assert disk>=1024**3+budget and memory>=8*1024**3
 write('resource-preflight.json',{'disk_free_bytes':disk,'memory_available_bytes':memory,'disk_output_budget_bytes':budget,'minimum_disk_headroom_bytes':1024**3,'budget_basis':'Prior exact304 native corpus3932 files1489572707 bytes; declared1.75GiB includes margin, source hashes, logs and compressed archive. Accounting budget, with owned native cancellation below1GiB free.','memory_cap_bytes':8*1024**3,'whole_wall_seconds':86400,'native_wall_seconds':82800,'compilation_disabled':True})
 lease=registry.reserve(out.name,[{'path':str(out),'access':'write'}]+[{'path':str(p),'access':'read'} for p in [source,build,runtime,tool]],ttl_seconds=120,demands={'slots':1,'memory_bytes':8*1024**3,'disk_bytes':budget});token=lease['token'];write('reservation.json',lease)
 def heartbeat():
  while not stop.wait(20):
   try:registry.heartbeat(token,ttl_seconds=120);registry.validate_paths(token)
   except BaseException as e:errors.append(str(e));return
 thread=threading.Thread(target=heartbeat,daemon=True);thread.start()
 assert git(source,'rev-parse','HEAD')==root and not git(source,'status','--porcelain','--untracked-files=no') and git(tool,'rev-parse','HEAD')==tool_root
 children={}
 for line in git(source,'config','-f','.gitmodules','--get-regexp','^submodule.*.path$').splitlines():
  _,p=line.split(None,1);wanted=git(source,'rev-parse','HEAD:'+p);assert git(source/p,'rev-parse','HEAD')==wanted and not git(source/p,'status','--porcelain','--untracked-files=no');children[p]=wanted
 assert len(children)==7 and children['Libraries/Nmsdk-PulseLib']=='12d8c8a41c998ae1516496f716a0ae0f3d312b3e';write('source-closure.json',{'root':root,'children':children,'clean':True,'tool_root':tool_root,'source_build_runtime_updated':False})
 os.environ['QT_QPA_PLATFORM']='offscreen';os.environ['ASAN_OPTIONS']=''
 for key in ['LD_LIBRARY_PATH','QT_PLUGIN_PATH']:os.environ.pop(key,None)
 manifest=snapshot(source,runtime/'Test_PulseLib_StorageComponents',runtime/'NeuroModelerConsole.ini',build/'CMakeCache.txt');old=json.loads((base/'readbacks/s06-integrated-acceptance-normal-a1/native-runtime.json').read_text())
 for field in ['executable','app_ini','source_closure','build_flags']:assert manifest[field]==old[field],field
 assert manifest['executable']['sha256']=='bcc51673ce59f1605567e7d8c998e6785ab978e0ff33c82aa116af39f52c9291';write('native-runtime.json',manifest);write('runtime-comparison.json',{'same_binary_app_ini_source_closure_build_flags':True,'compiler_record_same':manifest['compiler']==old['compiler'],'full_manifest_equal':manifest==old,'old_manifest_not_modified':True})
 spec=json.loads((source/'Scripts/StructTrain/TimeLearner/specs/native-csearch-threshold-regression-v1.json').read_text());assert len(spec['expected_test_ids'])==len(set(spec['expected_test_ids']))==304 and spec['schema_version']==2;write('original-native-specification.json',spec);spec.update(source_root=str(source),runtime_manifest=str(out/'native-runtime.json'),maximum_wall_seconds=82800);write('native-specification.json',spec)
 binding=json.loads((Path(str(out)+'-container')/'owned-unit.json').read_text());memory_group=Path('/sys/fs/cgroup')/binding['control_group'].lstrip('/');assert int((memory_group/'memory.max').read_text())==8*1024**3
 def watch():
  iteration=0
  while not monitor_stop.wait(1):
   try:
    free=shutil.disk_usage(base).free;process=out/'native-result/process'
    if free<1024**3 and (process/'owned-process.json').is_file() and not (process/'cancel.request').exists():
     (process/'cancel.request').write_text('Owned native cancellation: less than1GiB disk headroom.\n');write('disk-cancellation.json',{'free_bytes':free,'owned_process':json.loads((process/'owned-process.json').read_text()),'cancel_file':str(process/'cancel.request')})
    if iteration%5==0:
     row={'monotonic':time.monotonic(),'disk_free_bytes':free,'memory_current':int((memory_group/'memory.current').read_text()),'memory_peak':int((memory_group/'memory.peak').read_text())}
     with (out/'resource-history.jsonl').open('a') as stream:stream.write(json.dumps(row)+'\n')
    iteration+=1
   except BaseException as e:errors.append('resource_monitor:'+str(e));return
 monitor=threading.Thread(target=watch,daemon=True);monitor.start();result=run_native_gate(out/'native-specification.json',out/'native-result');write('native-verdict.json',result)
 assert not errors,errors;assert result['execution']=='completed' and result['validity']=='valid' and result['assertion_status']=='passed' and result['inventory']['expected']==result['inventory']['observed']==304;passed=True
except BaseException as e:write('exception.json',{'reason':str(e),'traceback':traceback.format_exc()})
finally:
 monitor_stop.set()
 if monitor:monitor.join(timeout=10)
 try:
  write('terminal.json',{'native304_normal_passed':passed,'compiled_root':root,'tool_root':tool_root,'monolithic_normal_batch':True,'asan_equivalence_attested':False,'whole_plan_complete':False,'scientific_verdict':None})
  if memory_group:write('memory-before-archive.json',{'current':int((memory_group/'memory.current').read_text()),'peak':int((memory_group/'memory.peak').read_text()),'events':(memory_group/'memory.events').read_text()})
  hashes={}
  for prefix in ['App/NeuroModelerConsole','Tests/Integration/Libraries','Scripts/StructTrain/TimeLearner','Libraries/Nmsdk-PulseLib/Core']:
   for p in (source/prefix).rglob('*'):
    if p.is_file() and '__pycache__' not in p.parts:hashes[p.relative_to(source).as_posix()]=sha(p)
  write('compiled-source-hashes.json',hashes);write('tool-source-hashes.json',{p.relative_to(tool).as_posix():sha(p) for p in (tool/'Scripts/StructTrain/TimeLearner').rglob('*.py') if '__pycache__' not in p.parts})
  files={p.relative_to(out).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in out.rglob('*') if p.is_file() and p.name not in ['primary.tar.xz','bundle.json']};assert sum(v['bytes'] for v in files.values())<=7*1024**3//4
  with tarfile.open(out/'primary.tar.xz','w:xz',preset=3) as archive:
   for name,record in sorted(files.items()):
    p=out/name;assert sha(p)==record['sha256'];info=tarfile.TarInfo(name);info.size=record['bytes']
    with p.open('rb') as stream:archive.addfile(info,stream)
  write('bundle.json',{'kind':'timelearner_integrated_native304_normal','compiled_root':root,'pulselib':'12d8c8a41c998ae1516496f716a0ae0f3d312b3e','tool_root':tool_root,'members':files,'archive_bytes':(out/'primary.tar.xz').stat().st_size,'archive_sha256':sha(out/'primary.tar.xz'),'native304_normal_passed':passed,'scientific_verdict':None})
 except BaseException as e:write('archive-exception.json',{'reason':str(e),'traceback':traceback.format_exc()})
 stop.set()
 if thread:thread.join(timeout=30)
 if monitor:monitor.join(timeout=10)
 print('CLOSED',passed,flush=True)
