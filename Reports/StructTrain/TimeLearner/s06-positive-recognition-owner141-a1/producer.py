from pathlib import Path
import os,sys,json,subprocess,hashlib,tarfile,io,shutil,threading,traceback,time
base=Path('/home/user/timelearner-refactor');label='recognition-owner-burst-normal-a1';out=base/('readbacks/s06-'+label);out.mkdir(exist_ok=False);source=base/'source-recognition-owner-burst-normal-a1';build=base/'build-recognition-owner-burst-normal-a1';runtime=base/'runtime-recognition-owner-burst-normal-a1';candidate=source;bootstrap=base/'source-closed-worker-recovery-a3';stop=threading.Event();thread=None;registry=None;token=None;errors=[];passed=False
root='2cb855677f3e7160cd01837f62c649b18803ebf0';candidate_root=root;capacity={'slots':1,'memory_bytes':24*1024**3,'disk_bytes':14*1024**3}
def write(n,v):(out/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as stream:
  for b in iter(lambda:stream.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def git(repo,*a):return subprocess.check_output(['git','-C',str(repo),*a],text=True).strip()
write('owned-supervisor.json',{'pid':os.getpid(),'start_ticks':Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19],'root':root,'candidate_root':candidate_root,'contained_supervisor':str(Path(str(out)+'-container'))});(out/'producer.py').write_bytes(Path(__file__).read_bytes())
try:
 dependency_source=base/'source-worker-dependency-normal-a2'
 for name in list(sys.modules):
  if name=='Scripts' or name.startswith('Scripts.'):del sys.modules[name]
 sys.path.insert(0,str(dependency_source))
 from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
 from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
 dependency_registry=Reservations(base/'resource-reservations.sqlite3',capacity=capacity)
 baseline=base/'readbacks/s06-live-cold-fixture-baseline-normal-a1'
 value=inspect_worker_dependency(Path(str(baseline)+'-container'),dependency_registry,'s06-live-cold-fixture-baseline-normal-a1')
 assert value['state']=='ready' and json.loads((baseline/'terminal.json').read_text())['corrected_baseline133_passed']
 write('baseline-prerequisite.json',{'resource_state':value,'terminal':json.loads((baseline/'terminal.json').read_text()),'native_verdict':json.loads((baseline/'native-verdict.json').read_text())})
 lifecycle=base/'readbacks/s06-shared-lifecycle-corrected-normal-a2'
 old_state=inspect_worker_dependency(Path(str(lifecycle)+'-container'),dependency_registry,'s06-shared-lifecycle-corrected-normal-a2')
 assert old_state['state']=='ready' and old_state['reservation_state']=='released' and json.loads((lifecycle/'terminal.json').read_text())['candidate133_passed']
 write('previous-lifecycle-prerequisite.json',{'resource_state':old_state,'terminal':json.loads((lifecycle/'terminal.json').read_text()),'native_verdict':json.loads((lifecycle/'native-verdict.json').read_text())})
 predecessor=base/'readbacks/s06-shared-recognition-ab-a1-container'
 observation=inspect_worker_dependency(predecessor,dependency_registry,'s06-shared-recognition-ab-a1',reservation_optional=True)
 assert observation['state']=='ready',observation
 previous=json.loads((base/'readbacks/s06-shared-recognition-ab-a1/terminal.json').read_text());assert previous['baseline_candidate8_comparison_complete'] and previous['candidate133_passed'];write('old-source-ab-result.json',previous)
 write('queue-prerequisite.json',observation)
 memory=int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024;assert memory>=10*1024**3 and shutil.disk_usage(base).free>=2*1024**3
 write('disk-budget-basis.json',{'reserved_disk_bytes':2*1024**3,'baseline_build_KiB':201192,'baseline_runtime_KiB':147060,'shared_immutable_Bin_resources':True,'Bin_materialized_files':['.gitignore'],'no_duplicate_historical_Bin_configs':True,'test_inventory_reduced':False})
 write('resource-preflight.json',{'memory_available_bytes':memory,'disk_free_bytes':shutil.disk_usage(base).free,'worker_memory_max_bytes':8*1024**3,'tasks_max':128,'compilation_disabled':False,'baseline_source_build_runtime_immutable':True,'candidate_cpp_executed':None})
 sys.path.insert(0,str(bootstrap))
 from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
 registry=Reservations(base/'resource-reservations.sqlite3',capacity=capacity);reservation=registry.reserve('s06-'+label,[{'path':str(v),'access':'write'} for v in [out,source,build,runtime]]+[{'path':str(v),'access':'read'} for v in [bootstrap,dependency_source,base/'source-shared-recognition-normal-a1',lifecycle,baseline,base/'framework-initial-threshold-normal-a4',base/'build-initial-threshold-normal-a4/_deps/llama_cpp-src',base/'readbacks/s05-model-spec-production-normal-a4/corpus',base/'readbacks/s10-managed-native-calibration-normal-a1']],demands={'slots':1,'memory_bytes':8*1024**3,'disk_bytes':2*1024**3},ttl_seconds=120);token=reservation['token'];write('reservation.json',reservation)
 def heartbeat():
  while not stop.wait(20):
   try:registry.heartbeat(token,ttl_seconds=120);registry.validate_paths(token)
   except BaseException as e:errors.append(str(e));return
 thread=threading.Thread(target=heartbeat,daemon=True);thread.start()
 assert git(source,'rev-parse','HEAD')==root and git(candidate,'rev-parse','HEAD')==candidate_root
 donor=base/'source-shared-recognition-normal-a1';assert git(donor,'rev-parse','HEAD')=='4f3db1160cda9bad59974af2bff01c023832248d'
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
 def tree_entries(repository):
  return {line.split('\t',1)[1]:line.split('\t',1)[0] for line in git(repository,'ls-tree','-r','HEAD','--','Tests','App','CMakeLists.txt').splitlines()}
 baseline_entries=tree_entries(donor);current_entries=tree_entries(source)
 differences={path for path in baseline_entries.keys()|current_entries.keys() if baseline_entries.get(path)!=current_entries.get(path)}
 assert differences=={'Tests/Integration/Libraries/Test_PulseLib_NativeModelEditor.cpp'},differences
 def core_entries(repository):
  return {line.split('\t',1)[1]:line.split('\t',1)[0] for line in git(repository,'ls-tree','-r','HEAD','--','Core').splitlines()}
 before=core_entries(donor/'Libraries/Nmsdk-PulseLib');after=core_entries(source/'Libraries/Nmsdk-PulseLib')
 pulse_differences={path for path in before.keys()|after.keys() if before.get(path)!=after.get(path)}
 assert not pulse_differences,pulse_differences
 write('scope-verification.json',{'baseline_root':git(donor,'rev-parse','HEAD'),'candidate_root':root,'Tests_App_CMake_changed_paths':sorted(differences),'change_kind':'test-only shorter initial burst for8 owner cases; no algorithm change','pulse_core_changed_paths':sorted(pulse_differences),'mathematical_goals_and_tolerances_unchanged':True,'baseline_sdk_unchanged':True})
 assert len(children)==7 and not git(source,'status','--porcelain','--untracked-files=no')
 write('source-closure.json',{'root':root,'children':children,'clean':True,'alternates':False,'baseline_sdk_unchanged':True})
 assert not build.exists() and not runtime.exists()
 assert children['Bin']==git(donor/'Bin','rev-parse','HEAD') and not git(donor/'Bin','status','--porcelain','--untracked-files=no')
 write('shared-resource-binding.json',{'resource_root':str(donor/'Bin'),'recorded_Bin_gitlink':children['Bin'],'source_Bin_materialization':'Git commit/all trees/root .gitignore; other files sparse','historical_resources_omitted_from_runtime':False,'source_runtime_or_resources_mutated':False})
 framework=base/'framework-initial-threshold-normal-a4';vendor=base/'build-initial-threshold-normal-a4/_deps/llama_cpp-src'
 assert git(framework,'rev-parse','HEAD')=='58d77fa8070e8cec2dc1ed015d66b454c8d78850' and git(vendor,'rev-parse','HEAD')=='1971adf55e3ebbfab83771d6174d37b77c352c71'
 def run(arguments,name):
  assert not errors;registry.validate_paths(token)
  with (out/name).open('xb') as log:
   process=subprocess.Popen(list(map(str,arguments)),stdout=log,stderr=subprocess.STDOUT)
   write('owned-'+name+'.json',{'pid':process.pid,'start_ticks':Path('/proc',str(process.pid),'stat').read_text().rsplit(') ',1)[1].split()[19],'arguments':list(map(str,arguments))});status=process.wait()
  assert status==0,(name,status)
 args=['cmake','-S',source,'-B',build,'-DCMAKE_BUILD_TYPE=Release','-DBUILD_TESTING=ON','-DCMAKE_DISABLE_FIND_PACKAGE_GTest=ON','-DRDK_BUILD_LEGACY_ENGINE_UNIT_TESTS=OFF','-DFETCHCONTENT_SOURCE_DIR_GOOGLETEST='+str(framework),'-DFETCHCONTENT_UPDATES_DISCONNECTED=ON','-DRDK_LLM_LLAMA_CPP_DIR='+str(vendor),'-DNMSDK_DEPLOY_ROOT='+str(runtime),'-DNMSDK_RESOURCE_ROOT='+str(donor/'Bin')]
 write('configure-arguments.json',{'arguments':list(map(str,args))});run(args,'configure.log')
 run(['cmake','--build',build,'--target','Test_PulseLib_StorageComponents','NeuroModelerConsole','--parallel','1'],'build.log')
 (out/'CMakeCache.txt').write_bytes((build/'CMakeCache.txt').read_bytes());write('build-terminal.json',{'execution':'completed','root':root})
 pulse=candidate/'Libraries/Nmsdk-PulseLib';assert git(pulse,'rev-parse','HEAD')=='f6a917d395b21610f6bf6cbb0ed945e6cdee31dd' and not git(pulse,'status','--porcelain','--untracked-files=no')
 specfile=candidate/'Scripts/StructTrain/TimeLearner/specs/native-shared-lifecycle-regression-v1.json';spec=json.loads(specfile.read_text());assert len(spec['expected_test_ids'])==133;write('declaration-source.json',{'root':candidate_root,'spec_sha256':sha(specfile),'candidate_materialized_sdk':True,'candidate_cpp_root':root})
 original=json.loads((baseline/'fixture-restoration.json').read_text());restored={}
 for name,record in original['restored'].items():
  relative=Path(name);assert not relative.is_absolute() and '..' not in relative.parts
  content=(baseline/relative).read_bytes();assert len(content)==record['bytes'] and hashlib.sha256(content).hexdigest()==record['sha256']
  destination=out/relative;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(content);restored[name]=record
 assert (out/'fixtures/Classic-auto_metric/input/job.json').is_file() and (out/'fixtures/Branch-synthetic/input/job.json').is_file()
 write('fixture-restoration.json',{**original,'copied_from_verified_baseline':str(baseline),'restored':restored})
 for name in list(sys.modules):
  if name=='Scripts' or name.startswith('Scripts.'):del sys.modules[name]
 sys.path.insert(0,str(source));os.chdir(source)
 from Scripts.StructTrain.TimeLearner.runtime import snapshot
 from Scripts.StructTrain.TimeLearner.native_gate import run_native_gate
 os.environ['QT_QPA_PLATFORM']='offscreen';os.environ.pop('ASAN_OPTIONS',None)
 for key in ['LD_LIBRARY_PATH','QT_PLUGIN_PATH']:os.environ.pop(key,None)
 current=snapshot(source,runtime/'Test_PulseLib_StorageComponents',runtime/'NeuroModelerConsole.ini',build/'CMakeCache.txt');write('native-runtime.json',current)
 cold=base/'readbacks/s05-model-spec-production-normal-a4/corpus/runs';calibration=base/'readbacks/s10-managed-native-calibration-normal-a1/actual-controls';declarations={}
 for topology in ['Classic','Branch']:
  paths=[cold/(topology+'-v1-train/input/job.json'),cold/(topology+'-v1-frozen/input/job.json'),calibration/(topology+'-v1/measured-grid-job.json')]
  for path in paths:declarations[str(path)]={'bytes':path.stat().st_size,'sha256':sha(path)}
 write('live-declaration-sources.json',{'sources':declarations,'cold_model_installed':False,'original_negative_source_preserved':True})
 os.environ['TIMELEARNER_LIVE_COLD_SOURCE']=str(cold);os.environ['TIMELEARNER_LIVE_CALIBRATION_SOURCE']=str(calibration)
 os.environ['TIMELEARNER_POSTTUNE_FIXED_SOURCE']=str(out/'fixtures');spec.update(source_root=str(source),runtime_manifest=str(out/'native-runtime.json'),asan_options='');write('native-specification.json',spec)
 corefile=candidate/'Scripts/StructTrain/TimeLearner/specs/native-shared-recognition-v1.json';focused=json.loads(corefile.read_text());assert len(focused['expected_test_ids'])==8
 focused.update(source_root=str(source),runtime_manifest=str(out/'native-runtime.json'),asan_options='')
 write('focused-specification.json',focused);focused_result=run_native_gate(out/'focused-specification.json',out/'focused-result');write('focused-verdict.json',focused_result)
 assert focused_result['execution']=='completed' and focused_result['validity']=='valid' and focused_result['assertion_status']=='passed' and focused_result['inventory']['observed']==focused_result['inventory']['expected']==8
 result=run_native_gate(out/'native-specification.json',out/'native-result');write('native-verdict.json',result);assert result['execution']=='completed' and result['validity']=='valid' and result['assertion_status']=='passed' and result['inventory']['observed']==result['inventory']['expected']==133;assert not errors;passed=True
except BaseException as error:write('exception.json',{'reason':str(error),'traceback':traceback.format_exc()})
finally:
 try:
  write('terminal.json',{'recognition8_and_lifecycle133_passed':passed,'candidate_cpp_executed':(out/'focused-result').is_dir() or (out/'native-result').is_dir(),'candidate_build_pending':not (out/'build-terminal.json').is_file(),'whole_plan_complete':False,'scientific_verdict':None})
  hashes={}
  for prefix in ['App/NeuroModelerConsole','Tests/Integration/Libraries','Libraries/Nmsdk-PulseLib/Core']:
   for path in (source/prefix).rglob('*'):
    if path.is_file() and path.suffix in ['.cpp','.h','.c']:hashes[path.relative_to(source).as_posix()]=sha(path)
  write('source-hashes.json',hashes);files={p.relative_to(out).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in out.rglob('*') if p.is_file()}
  with tarfile.open(out/'primary.tar.xz','w:xz',preset=3) as archive:
   for name,record in files.items():
    entry=tarfile.TarInfo(name);entry.size=record['bytes']
    with (out/name).open('rb') as stream:archive.addfile(entry,stream)
  write('bundle.json',{'kind':'shared_recognition_candidate_controls','root':root,'candidate_root':candidate_root,'recognition8_and_lifecycle133_passed':passed,'members':files,'archive_bytes':(out/'primary.tar.xz').stat().st_size,'archive_sha256':sha(out/'primary.tar.xz'),'candidate_cpp_executed':None,'scientific_verdict':None})
 finally:
  stop.set()
  if thread:thread.join(timeout=30)
 print('CLOSED',passed,flush=True)
