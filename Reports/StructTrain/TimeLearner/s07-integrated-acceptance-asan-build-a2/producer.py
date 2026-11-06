from pathlib import Path
import os,sys,json,subprocess,hashlib,threading,time,traceback,shutil,tarfile,io
base=Path('/media/user/Data/TimeLearnerRefactor');root='2e0618110a9abb48b94f6edc6b63c51f829ec810';label='integrated-acceptance-asan-build-a2'
out=base/('readbacks/s07-'+label);out.mkdir(exist_ok=False)
source=base/'source-integrated-acceptance-asan-a1';build=base/'build-integrated-acceptance-asan-a1';runtime=base/'runtime-integrated-acceptance-asan-a1'
bootstrap=base/'source-closed-worker-recovery-a3';donor=base/'source-csearch-threshold-joint-asan-build-a1'
framework=base/'framework-configured-probe-ownership-asan-h14';vendor=base/'build-configured-probe-ownership-asan-h14/_deps/llama_cpp-src'
stop=threading.Event();thread=None;registry=None;token=None;errors=[];passed=False

def write(name,value):
 p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def ticks(pid):return Path('/proc',str(pid),'stat').read_text().rsplit(') ',1)[1].split()[19]
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
def run(args,name):
 if token:registry.validate_paths(token)
 assert not errors,errors
 with (out/name).open('xb') as log:
  p=subprocess.Popen(list(map(str,args)),stdout=log,stderr=subprocess.STDOUT)
  write('owned-'+name+'.json',{'pid':p.pid,'start_ticks':ticks(p.pid),'arguments':list(map(str,args))});status=p.wait()
 assert status==0,(name,status)
write('owned-supervisor.json',{'pid':os.getpid(),'start_ticks':ticks(os.getpid()),'root':root,'source':str(source),'build':str(build),'runtime':str(runtime),'contained_supervisor':str(base/('readbacks/s07-'+label+'-container'))})
(out/'producer.py').write_bytes(Path(__file__).read_bytes())
try:
 assert source.is_dir() and not build.exists() and not runtime.exists()
 memory=int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024
 disk=shutil.disk_usage(base);assert disk.free>=24*1024**3 and memory>=36*1024**3
 write('resource-preflight.json',{'memory_available_bytes':memory,'disk_free_bytes':disk.free,'compiler_parallelism':1,'worker_memory_max_bytes':4*1024**3,'worker_tasks_max':128,'maximum_wall_seconds':21600,'native_gates_disabled':True,'minimum_available_memory_before_start':36*1024**3})
 sys.path.insert(0,str(base/'source-worker-dependency-normal-a2'))
 from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
 registry=Reservations(base/'resource-reservations.sqlite3')
 reservation=registry.reserve('s07-'+label,[{'path':str(p),'access':'write'} for p in [out,source,build,runtime]]+[{'path':str(p),'access':'read'} for p in [bootstrap,donor,framework,vendor,base/'source-worker-dependency-normal-a2']],ttl_seconds=120)
 token=reservation['token'];write('reservation.json',dict(reservation,ledger_schema=1,live_K1_ledger_not_migrated=True,scope='Read/write paths only; actual memory/task cap enforced by the enclosing cgroup. Build only.'))
 def heartbeat():
  while not stop.wait(20):
   try:registry.heartbeat(token,ttl_seconds=120);registry.validate_paths(token)
   except BaseException as error:errors.append(str(error));return
 thread=threading.Thread(target=heartbeat,daemon=True);thread.start()
 from Scripts.StructTrain.TimeLearner.contained_process import inspect as inspect_contained
 from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
 prior=base/'readbacks/s07-joint-asan-owner-readers-a3'
 prior_state=inspect_worker_dependency(Path(str(prior)+'-container'),registry,prior.name)
 assert prior_state['state']=='ready' and prior_state['reservation_state']=='released',prior_state
 assert json.loads((prior/'terminal.json').read_text())['ASan_owner8_readers128_passed']
 write('predecessor-owner-reader-closure.json',prior_state)
 assert git(donor,'rev-parse','HEAD')=='8021301e894368aefd045f9d77274fcce9f60245'
 assert git(source,'rev-parse','HEAD')==root
 children={}
 for line in git(source,'config','-f','.gitmodules','--get-regexp','^submodule.*.path$').splitlines():
  key,path=line.split(None,1);wanted=git(source,'rev-parse','HEAD:'+path);destination=source/path
  assert destination.resolve().is_relative_to(source.resolve()) and not destination.is_symlink()
  if not (destination/'.git').exists():
   origin=donor/path;assert git(origin,'rev-parse','HEAD')==wanted and not git(origin,'status','--porcelain','--untracked-files=no')
   assert not destination.exists() or not any(destination.iterdir()), str(destination)
   destination.mkdir(parents=True,exist_ok=True);subprocess.run(['git','init','--quiet',str(destination)],check=True)
   objects={wanted,git(origin,'rev-parse',wanted+'^{tree}')}
   for entry in subprocess.check_output(['git','-C',str(origin),'ls-tree','-r','-t','-z',wanted]).split(b'\0'):
    if not entry:continue
    meta,name=entry.split(b'\t',1);mode,kind,oid=meta.split()
    if kind==b'tree' or (kind==b'blob' and (name==b'.gitignore' if path=='Bin' else name.split(b'/',1)[0] not in [b'Docs',b'Reports'])):objects.add(oid.decode())
   packet=subprocess.check_output(['git','-C',str(origin),'pack-objects','--stdout'],input=('\n'.join(sorted(objects))+'\n').encode())
   subprocess.run(['git','-C',str(destination),'index-pack','--stdin','--promisor'],input=packet,stdout=subprocess.DEVNULL,check=True)
   (destination/'.git/shallow').write_text(wanted+'\n')
   for setting,value in [('core.repositoryformatversion','1'),('extensions.partialClone','origin'),('remote.origin.promisor','true')]:subprocess.run(['git','-C',str(destination),'config',setting,value],check=True)
   subprocess.run(['git','-C',str(destination),'sparse-checkout','init','--no-cone'],check=True)
   subprocess.run(['git','-C',str(destination),'sparse-checkout','set','--no-cone',*(['/.gitignore'] if path=='Bin' else ['/*','!/Docs/','!/Reports/'])],check=True)
   subprocess.run(['git','-C',str(destination),'-c','submodule.recurse=false','checkout','--detach',wanted],stdout=subprocess.DEVNULL,check=True)
  assert git(destination,'rev-parse','HEAD')==wanted and not git(destination,'status','--porcelain','--untracked-files=no') and not (destination/'.git/objects/info/alternates').exists()
  children[path]=wanted
 subprocess.run(['git','-C',str(source),'submodule','init'],check=True)
 assert len(children)==7 and not git(source,'status','--porcelain','--untracked-files=no')
 assert children['Libraries/Nmsdk-PulseLib']=='12d8c8a41c998ae1516496f716a0ae0f3d312b3e'
 resources=donor/'Bin';assert git(resources,'rev-parse','HEAD')=='99f58da9296a794374cef679bbb878cb62af979a'
 def bin_entries(repo):
  return {entry.split(b'\t',1)[1].decode():entry.split(b'\t',1)[0].decode() for entry in subprocess.check_output(['git','-C',str(repo),'ls-tree','-r','-z','HEAD']).split(b'\0') if entry}
 old_bin=bin_entries(resources);new_bin=bin_entries(source/'Bin');changed=sorted(n for n in old_bin.keys()|new_bin.keys() if old_bin.get(n)!=new_bin.get(n))
 assert len(changed)==33 and all(Path(n).suffix.lower() in ['.py','.sh','.md'] for n in changed),changed
 write('shared-resource-binding.json',{'resource_root':str(resources),'actual_resource_Bin_commit':git(resources,'rev-parse','HEAD'),'recorded_Bin_gitlink':children['Bin'],'differing_paths':changed,'resource_config_physics_data_unchanged':True,'active_sdk_or_runtime_changed':False})
 write('source-closure.json',{'root':root,'children':children,'clean':True,'all_repositories_without_alternates':True,'source_delivery':'private Git stores; source2e/Pulse12d/Bin11ad delivered from exact published objects, other5 imported read-only from immutable SDK802'})
 assert git(framework,'rev-parse','HEAD')=='58d77fa8070e8cec2dc1ed015d66b454c8d78850' and not git(framework,'status','--porcelain','--untracked-files=no')
 assert git(vendor,'rev-parse','HEAD')=='1971adf55e3ebbfab83771d6174d37b77c352c71' and not git(vendor,'status','--porcelain','--untracked-files=no')
 write('offline-vendor.json',{'path':str(vendor),'commit':git(vendor,'rev-parse','HEAD'),'tracked_clean':True})
 args=['cmake','-S',source,'-B',build,'-DCMAKE_BUILD_TYPE=RelWithDebInfo','-DNMSDK_BUILD_PARALLEL_JOBS=1','-DCMAKE_CXX_FLAGS_RELWITHDEBINFO=-O1 -g1 -fsanitize=address -fno-omit-frame-pointer','-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address','-DBUILD_TESTING=ON','-DCMAKE_DISABLE_FIND_PACKAGE_GTest=ON','-DRDK_BUILD_LEGACY_ENGINE_UNIT_TESTS=OFF','-DFETCHCONTENT_SOURCE_DIR_GOOGLETEST='+str(framework),'-DFETCHCONTENT_UPDATES_DISCONNECTED=ON','-DRDK_LLM_LLAMA_CPP_DIR='+str(vendor),'-DNMSDK_DEPLOY_ROOT='+str(runtime),'-DNMSDK_RESOURCE_ROOT='+str(resources)]
 os.environ['CMAKE_BUILD_PARALLEL_LEVEL']='1'
 write('configure-arguments.json',{'arguments':list(map(str,args))});run(args,'configure.log')
 run(['cmake','--build',build,'--target','Test_PulseLib_StorageComponents','NeuroModelerConsole','--parallel','1'],'build.log')
 (out/'CMakeCache.txt').write_bytes((build/'CMakeCache.txt').read_bytes());write('build-terminal.json',{'execution':'completed','root':root,'native_gates_executed':False})
 for name in list(sys.modules):
  if name=='Scripts' or name.startswith('Scripts.'):del sys.modules[name]
 sys.path.insert(0,str(source));os.chdir(source)
 from Scripts.StructTrain.TimeLearner.runtime import snapshot
 os.environ['QT_QPA_PLATFORM']='offscreen';os.environ['ASAN_OPTIONS']='detect_leaks=0'
 for key in ['LD_LIBRARY_PATH','QT_PLUGIN_PATH']:os.environ.pop(key,None)
 write('native-runtime.json',snapshot(source,runtime/'Test_PulseLib_StorageComponents',runtime/'NeuroModelerConsole.ini',build/'CMakeCache.txt'))
 write('pending-gates.json',{'status':'not_started','root':root,'declared_focused_tests':8,'declared_full_tests':133,'reason':'Build only; new shared-control native8+133 require separate post-build resource/fixture decision. Prior SDK802 ASan304/owner/readers are prerequisites, not passes for this SDK.','scientific_verdict':None})
 passed=True
except BaseException as error:write('exception.json',{'reason':str(error),'traceback':traceback.format_exc()})
finally:
 stop.set()
 if thread:thread.join(timeout=30)
 write('terminal.json',{'build_passed':passed,'native_gates_executed':False,'native_models_executed':0,'scientific_verdict':None,'whole_plan_complete':False})
 hashes={}
 if source.exists():
  for prefix in ['App/NeuroModelerConsole','Tests/Integration/Libraries','Scripts/StructTrain/TimeLearner','Libraries/Nmsdk-PulseLib/Core']:
   for p in (source/prefix).rglob('*'):
    if p.is_file() and '__pycache__' not in p.parts:hashes[p.relative_to(source).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
 write('source-hashes.json',hashes)
 files={p.relative_to(out).as_posix():p.read_bytes() for p in out.rglob('*') if p.is_file()}
 with tarfile.open(out/'primary.tar.xz','w:xz',preset=3) as archive:
  for name,raw in files.items():info=tarfile.TarInfo(name);info.size=len(raw);archive.addfile(info,io.BytesIO(raw))
 raw=(out/'primary.tar.xz').read_bytes();write('bundle.json',{'kind':'integrated_shared_controller_asan_build_only','root':root,'build_passed':passed,'native_gates_executed':False,'members':{n:{'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()} for n,v in files.items()},'archive_bytes':len(raw),'archive_sha256':hashlib.sha256(raw).hexdigest(),'scientific_verdict':None})
 print('CLOSED',passed,flush=True)
