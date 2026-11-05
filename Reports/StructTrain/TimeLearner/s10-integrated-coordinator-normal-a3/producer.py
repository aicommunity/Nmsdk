from pathlib import Path
import os,sys,json,subprocess,hashlib,tarfile,threading,traceback,unittest,shutil,time
base=Path('/home/user/timelearner-refactor');label='integrated-coordinator-normal-a3';out=base/('readbacks/s10-'+label);out.mkdir(exist_ok=False);source=base/'source-integrated-acceptance-normal-a1';bootstrap=base/'source-closed-worker-recovery-a3';root='2e0618110a9abb48b94f6edc6b63c51f829ec810';container=Path(str(out)+'-container')
runtime_path=out/'console-runtime.json';templates=base/'readbacks/s09-native-pipeline-cli-normal-a2';stop=threading.Event();thread=None;errors=[];passed=False;token=None
capacity={'slots':1,'memory_bytes':24*1024**3,'disk_bytes':14*1024**3}
def write(name,value):(out/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
write('owned-supervisor.json',{'pid':os.getpid(),'start_ticks':Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19],'source':str(source),'root':root,'contained_supervisor':str(container)});(out/'producer.py').write_bytes(Path(__file__).read_bytes())
try:
 dependency_source=base/'source-worker-dependency-normal-a2'
 for name in list(sys.modules):
  if name=='Scripts' or name.startswith('Scripts.'):del sys.modules[name]
 sys.path.insert(0,str(dependency_source))
 from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
 from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
 dependency_registry=Reservations(base/'resource-reservations.sqlite3',capacity=capacity)
 prerequisite=base/'readbacks/s06-integrated-acceptance-normal-a1'
 ready=inspect_worker_dependency(Path(str(prerequisite)+'-container'),dependency_registry,prerequisite.name)
 assert ready['state']=='ready' and ready['reservation_state']=='released',ready
 assert json.loads((prerequisite/'terminal.json').read_text())['recognition8_and_lifecycle133_passed']
 write('preceding-resource-state.json',ready)
 sys.path.insert(0,str(source))
 from Scripts.StructTrain.TimeLearner.runtime import snapshot
 runtime_root=base/'runtime-integrated-acceptance-normal-a1';build=base/'build-integrated-acceptance-normal-a1'
 runtime=snapshot(source,runtime_root/'NeuroModelerConsole',runtime_root/'NeuroModelerConsole.ini',build/'CMakeCache.txt');write('console-runtime.json',runtime)
 memory=int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024;assert memory>=8*1024**3 and shutil.disk_usage(base).free>=2*1024**3
 runtime=json.loads(runtime_path.read_text());assert runtime['source_closure']['root']['head']==root
 write('resource-preflight.json',{'memory_available_bytes':memory,'disk_free_bytes':shutil.disk_usage(base).free,'controller_cap_bytes':512*1024**2,'native_process_cap_bytes':4*1024**3,'cold_training_expected':True,'same_matrix_frozen':True,'runtime_immutable':True,'compilation_disabled':True})
 sys.path.insert(0,str(bootstrap))
 from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
 registry=Reservations(base/'resource-reservations.sqlite3',capacity=capacity)
 positive_templates=base/'readbacks/s05-model-spec-production-normal-a4/corpus/runs'
 calibration_templates=base/'readbacks/s10-managed-native-calibration-normal-a1/actual-controls';os.environ['TIMELEARNER_COORDINATOR_CALIBRATION_TEMPLATES']=str(calibration_templates)
 paths=[source,bootstrap,dependency_source,templates,positive_templates,calibration_templates,Path(runtime['executable']['path']).parent,Path(runtime['build_flags']['NMSDK_RESOURCE_ROOT'])]
 write('reservation-resources.json',{'write':[str(out)],'read':[str(v.resolve()) for v in paths]})
 assert len({str(v.resolve()) for v in paths})==len(paths) and out.resolve() not in [v.resolve() for v in paths], 'worker_resource_list_not_unique'
 reserved=registry.reserve('s10-'+label,[{'path':str(out),'access':'write'}]+[{'path':str(v),'access':'read'} for v in paths],demands={'slots':1,'memory_bytes':4*1024**3+512*1024**2,'disk_bytes':1024**3},ttl_seconds=120);token=reserved['token'];write('reservation.json',reserved)
 def heartbeat():
  while not stop.wait(20):
   try:registry.heartbeat(token,ttl_seconds=120);registry.validate_paths(token)
   except BaseException as e:errors.append(str(e));return
 thread=threading.Thread(target=heartbeat,daemon=True);thread.start()
 assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()==root and not subprocess.check_output(['git','-C',str(source),'status','--porcelain','--untracked-files=no']).strip()
 for name in list(sys.modules):
  if name=='Scripts' or name.startswith('Scripts.'):del sys.modules[name]
 sys.path.insert(0,str(source));os.chdir(source)
 from Scripts.StructTrain.TimeLearner.process_runner import verify_runtime
 verify_runtime(runtime);(out/'native-runtime.json').write_bytes(runtime_path.read_bytes())
 for key in ['LD_LIBRARY_PATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM']:
  if key in runtime['loader_environment']:os.environ[key]=runtime['loader_environment'][key]
  else:os.environ.pop(key,None)
 os.environ.pop('ASAN_OPTIONS',None)
 write('declaration.json',{'runtime':str(out/'native-runtime.json'),'templates':str(templates),'positive_templates':str(positive_templates),'controller':str(container),'output':str(out/'actual-controls')});os.environ['TIMELEARNER_MANAGED_NATIVE_PIPELINE']=str(out/'declaration.json')
 suite=unittest.defaultTestLoader.loadTestsFromName('Scripts.StructTrain.TimeLearner.tests.test_managed_pipeline_coordinator');assert suite.countTestCases()==8
 with (out/'tests.log').open('w') as log:result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
 write('tests.json',{'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'expected':8});assert result.testsRun==8 and result.wasSuccessful() and not result.skipped and not errors;passed=True
except BaseException as e:write('exception.json',{'reason':str(e),'traceback':traceback.format_exc()})
finally:
 try:
  write('terminal.json',{'tests_passed':passed,'actual_managed_native_phases':None,'phase_count_derived_from_actual_artifacts_required':True,'calibration_and_owned_posttune_pending':True,'independent_partition_verified':False,'scientific_verdict':None,'whole_plan_complete':False})
  write('source-hashes.json',{p.relative_to(source).as_posix():sha(p) for p in (source/'Scripts/StructTrain/TimeLearner').rglob('*.py') if '__pycache__' not in p.parts})
  files={p.relative_to(out).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in out.rglob('*') if p.is_file() and not p.is_symlink()}
  with tarfile.open(out/'primary.tar.xz','w:xz',preset=3) as archive:
   for name,v in files.items():
    entry=tarfile.TarInfo(name);entry.size=v['bytes']
    with (out/name).open('rb') as f:archive.addfile(entry,f)
  write('bundle.json',{'kind':'managed_actual_cold_pipeline_checks','source_commit':root,'passed':passed,'members':files,'archive_bytes':(out/'primary.tar.xz').stat().st_size,'archive_sha256':sha(out/'primary.tar.xz'),'scientific_verdict':None})
 finally:
  stop.set()
  if thread:thread.join(timeout=30)
 print('CLOSED',passed,flush=True)
