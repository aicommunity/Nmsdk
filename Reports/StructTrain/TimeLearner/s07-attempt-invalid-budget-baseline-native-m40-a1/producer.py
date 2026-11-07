from pathlib import Path
import os,sys,json,hashlib,threading,tarfile,traceback,sqlite3
base=Path('/media/user/Data/TimeLearnerRefactor');source=base/'source-attempt-invalid-budget-baseline-normal-a1';tool=source;out=base/'readbacks/s07-attempt-invalid-budget-baseline-native-a1';out.mkdir(exist_ok=False);sys.dont_write_bytecode=True;sys.path.insert(0,str(source));stop=threading.Event();thread=None;registry=None;token=None;passed=False;errors=[]
from Scripts.StructTrain.TimeLearner.native_gate import run_native_gate
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):(out/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
root='7cc21bdd9e0904f8f5052466651e0682f2f1f1a3'
write('owner.json',{'pid':os.getpid(),'start_ticks':Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19],'compiled_root':root,'compiler_executed':False});(out/'producer.py').write_bytes(Path(__file__).read_bytes())
try:
 c=sqlite3.connect('file:'+str(base/'resource-reservations.sqlite3')+'?mode=ro',uri=True)
 try:metadata=dict(c.execute('SELECT key,value FROM metadata'))
 finally:c.close()
 registry=Reservations(base/'resource-reservations.sqlite3',**({'capacity':json.loads(metadata['capacity'])} if 'capacity' in metadata else {}))
 previous=base/'readbacks/s07-attempt-invalid-budget-baseline-normal-a1'
 dependency=inspect_worker_dependency(Path(str(previous)+'-container'),registry,previous.name)
 assert dependency['state']=='ready' and dependency['reservation_state']=='released',dependency
 assert json.loads((previous/'terminal.json').read_text())['expected_baseline_failures_observed']
 for n in ['baseline-verdict.json']:
  r=json.loads((previous/n).read_text());assert r['validity']=='valid' and r['assertion_status']=='failed',r
 write('fixed-normal-prerequisite.json',dependency)
 runtime=json.loads((previous/'native-runtime.json').read_text());assert runtime['source_closure']['root']['head']==root
 write('runtime.json',runtime)
 reads=[source,Path(runtime['executable']['path']).parent,base/'build-attempt-invalid-budget-baseline-normal-a1',Path(runtime['build_flags']['NMSDK_RESOURCE_ROOT']),previous];selected=[]
 for p in sorted(set(p.resolve(strict=True) for p in reads),key=lambda p:len(p.parts)):
  if not any(p.is_relative_to(q) for q in selected):selected.append(p)
 lease=registry.reserve(out.name,[{'path':str(out),'access':'write'}]+[{'path':str(p),'access':'read'} for p in selected],ttl_seconds=120,**({'demands':{'slots':1,'memory_bytes':8*1024**3,'disk_bytes':1024**3}} if 'capacity' in metadata else {}));token=lease['token'];write('reservation.json',lease)
 def heartbeat():
  while not stop.wait(20):
   try:registry.heartbeat(token,ttl_seconds=120);registry.validate_paths(token)
   except BaseException as error:errors.append(str(error));return
 thread=threading.Thread(target=heartbeat,daemon=True);thread.start()
 expected=['NativeTrainingService/ClassicN0SearchAndFreshNegativeFinalGate', 'NativeTrainingService/BranchN0SearchAndFreshNegativeFinalGate', 'NativeTrainingService/ClassicN1SearchAndFreshNegativeFinalGate', 'NativeTrainingService/BranchN1SearchAndFreshNegativeFinalGate', 'NativeTrainingService/ExactAutoCompletionResetWarmRestartAndRetarget', 'NativeTrainingService/ClassicExternalStopPreservesCensoredEvidence', 'NativeTrainingService/BranchExternalStopPreservesCensoredEvidence', 'NativeTrainingService/ModelTimeBudgetCannotManufactureConvergence', 'NativeLearnedState/ClassicN0', 'NativeLearnedState/BranchN0', 'NativeLearnedState/ClassicN1', 'NativeLearnedState/BranchN1', 'NativeLearnedState/ExactCertificateWithExplicitPointTwoTolerance', 'NativeLearnedState/ClassicConfiguredN1', 'NativeLearnedState/BranchConfiguredN0', 'NativeStoppedState/ClassicFinal', 'NativeStoppedState/BranchFinal', 'NativeStoppedState/ClassicInvalidProbe', 'NativeStoppedState/BranchInvalidProbe', 'NativeStoppedState/ClassicN0BudgetSearch', 'NativeStoppedState/BranchN0BudgetSearch', 'NativeStoppedState/ClassicN0RepeatedHalfCandidate', 'NativeStoppedState/BranchN0RepeatedHalfCandidate']
 write('specification.json',{'kind':'timelearner_native_test_gate','schema_version':2,'runtime_manifest':str(out/'runtime.json'),'source_root':str(source),'expected_test_ids':expected,'maximum_wall_seconds':10800,'asan_options':'','cooperative_runtime_capture':True})
 result=run_native_gate(out/'specification.json',out/'native-result');write('result.json',result)
 assert result['execution']=='process_error' and result['validity']=='valid' and result['assertion_status']=='failed' and result['inventory']['observed']==23 and not errors,result
 assert result['inventory']['failed_test_ids']==['NativeLearnedState/ClassicConfiguredN1','NativeLearnedState/BranchConfiguredN0'],result
 write('scope.json',{'actual_production_native_test_functions':23,'new_invalid_budget_scenarios_are_a_separate_gate':True,'full_model_learned_and_stopped_transport_controls':True,'expected_failed_cases_preserved':2,'all_native_matrix_complete':False,'scientific_verdict':None})
 passed=True
except BaseException as error:write('exception.json',{'reason':str(error),'traceback':traceback.format_exc()})
finally:
 stop.set()
 if thread:thread.join(timeout=10)
 write('tool-source-hashes.json',{p.relative_to(source).as_posix():sha(p) for p in (source/'Scripts/StructTrain/TimeLearner').rglob('*.py')})
 write('native-source-hashes.json',{p.relative_to(source).as_posix():sha(p) for folder in ['Tests/Integration/Libraries','Libraries/Nmsdk-PulseLib/Core'] for p in (source/folder).rglob('*') if p.is_file()})
 write('terminal.json',{'original_controller_native23_expected_failures_observed':passed,'compiled_root':root,'ASan_executed':False,'whole_plan_complete':False,'scientific_verdict':None});members={}
 with tarfile.open(out/'primary.tar.xz','w:xz',preset=3) as archive:
  for p in sorted(out.rglob('*')):
   if p.is_file() and p.name not in ['primary.tar.xz','bundle.json']:
    name=p.relative_to(out).as_posix();members[name]={'bytes':p.stat().st_size,'sha256':sha(p)};info=tarfile.TarInfo(name);info.size=p.stat().st_size
    with p.open('rb') as stream:archive.addfile(info,stream)
 write('bundle.json',{'original_controller_native23_expected_failures_observed':passed,'members':members,'archive_bytes':(out/'primary.tar.xz').stat().st_size,'archive_sha256':sha(out/'primary.tar.xz')});print('CLOSED',passed,flush=True)
