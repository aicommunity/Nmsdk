from pathlib import Path
import sys,os,json,hashlib,threading,time,traceback,tarfile,unittest,shutil,subprocess
base=Path('/media/user/Data/TimeLearnerRefactor');label='native-partition-addressed-asan-a1';out=base/('readbacks/s07-'+label);out.mkdir(exist_ok=False)
tool=base/'source-native-partition-a1';sdk=base/'source-csearch-threshold-joint-asan-build-a1';runtime=base/'runtime-csearch-threshold-joint-asan-build-a2';build=base/'build-csearch-threshold-joint-asan-build-a1';bootstrap=base/'source-worker-dependency-normal-a2'
stop=threading.Event();thread=None;errors=[];passed=False;token=None

def write(n,v):(out/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
write('owned-supervisor.json',{'pid':os.getpid(),'start_ticks':Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19],'tool_commit':'8ba66bad772aa716e6dc85c94e86c395d6d63c1d','native_sdk':'8021301e894368aefd045f9d77274fcce9f60245'});(out/'producer.py').write_bytes(Path(__file__).read_bytes())
try:
 sys.path.insert(0,str(bootstrap))
 from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
 from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
 registry=Reservations(base/'resource-reservations.sqlite3');dependency=inspect_worker_dependency(base/'readbacks/s07-csearch-threshold-joint-full-asan-a2-container',registry,'s07-csearch-threshold-joint-full-asan-a2');assert dependency['state']=='ready' and dependency['reservation_state']=='released';write('predecessor-closure.json',dependency)
 lease=registry.reserve(out.name,[{'path':str(out),'access':'write'}]+[{'path':str(p),'access':'read'} for p in [tool,sdk,runtime,build,bootstrap]],ttl_seconds=120);token=lease['token'];write('reservation.json',lease)
 def heartbeat():
  while not stop.wait(20):
   try:registry.heartbeat(token,ttl_seconds=120);registry.validate_paths(token)
   except BaseException as e:errors.append(str(e));return
 thread=threading.Thread(target=heartbeat,daemon=True);thread.start()
 for name in list(sys.modules):
  if name=='Scripts' or name.startswith('Scripts.'):del sys.modules[name]
 sys.path.insert(0,str(tool));os.chdir(tool);sys.dont_write_bytecode=True
 from Scripts.StructTrain.TimeLearner.runtime import snapshot
 from Scripts.StructTrain.TimeLearner.process_runner import verify_runtime
 assert subprocess.check_output(['git','-C',str(tool),'rev-parse','HEAD'],text=True).strip()=='8ba66bad772aa716e6dc85c94e86c395d6d63c1d'
 os.environ['QT_QPA_PLATFORM']='offscreen';os.environ['ASAN_OPTIONS']='detect_leaks=0'
 for k in ['LD_LIBRARY_PATH','QT_PLUGIN_PATH']:os.environ.pop(k,None)
 current=snapshot(sdk,runtime/'Test_PulseLib_StorageComponents',runtime/'NeuroModelerConsole.ini',build/'CMakeCache.txt');old=json.loads((base/'readbacks/s07-csearch-threshold-joint-full-asan-a2/native-runtime.json').read_text())
 for k in ['executable','app_ini','compiler','source_closure','build_flags']:assert current[k]==old[k],k
 changed={p['path']:{'previous':p,'current':next((q for q in current['resolved_libraries'] if q['path']==p['path']),None)} for p in old['resolved_libraries'] if p not in current['resolved_libraries']}
 write('runtime-delta.json',{'native_code_unchanged':True,'compiler_unchanged':True,'system_dependency_changes':changed,'new_attempt_not_repair_of_old_manifest':True});write('native-runtime.json',current)
 native=json.loads((sdk/'Scripts/StructTrain/TimeLearner/specs/native-csearch-threshold-regression-v1.json').read_text());native.update(source_root=str(sdk),runtime_manifest=str(out/'native-runtime.json'),asan_options='detect_leaks=0',expected_test_ids=['NativeCapacitanceModelSpec2Codec/ClassicN0_2000','NativeCapacitanceModelSpec2Codec/BranchN0_2000'])
 spec={'kind':'timelearner_partitioned_native_gate','schema_version':1,'native_gate':native,'maximum_total_wall_seconds':1800,'maximum_case_wall_seconds':600};write('partition-specification.json',spec)
 os.environ['TIMELEARNER_PARTITION_SPEC']=str(out/'partition-specification.json');os.environ['TIMELEARNER_PARTITION_OUTPUT']=str(out/'actual-two-processes')
 suite=unittest.defaultTestLoader.loadTestsFromName('Scripts.StructTrain.TimeLearner.tests.test_native_partition');assert suite.countTestCases()==5
 with (out/'tests.log').open('w') as log:result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
 write('tests.json',{'expected':5,'executed':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped)});verify_runtime(current);assert result.testsRun==5 and result.wasSuccessful() and not result.skipped and not errors;passed=True
except BaseException as e:write('exception.json',{'reason':str(e),'traceback':traceback.format_exc()})
finally:
 stop.set()
 if thread:thread.join(timeout=30)
 write('terminal.json',{'addressed_real_ASan_partitions_passed':passed,'full304_passed':False,'whole_plan_complete':False,'scientific_verdict':None})
 write('tool-source-hashes.json',{str(p.relative_to(tool)):sha(p) for p in (tool/'Scripts/StructTrain/TimeLearner').rglob('*.py') if '__pycache__' not in p.parts})
 members={str(p.relative_to(out)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in out.rglob('*') if p.is_file() and not p.is_symlink()}
 with tarfile.open(out/'primary.tar.xz','w:xz',preset=3) as archive:
  for n,v in members.items():
   e=tarfile.TarInfo(n);e.size=v['bytes']
   with (out/n).open('rb') as f:archive.addfile(e,f)
 write('bundle.json',{'members':members,'archive_bytes':(out/'primary.tar.xz').stat().st_size,'archive_sha256':sha(out/'primary.tar.xz'),'scientific_verdict':None});print('CLOSED',passed,flush=True)
