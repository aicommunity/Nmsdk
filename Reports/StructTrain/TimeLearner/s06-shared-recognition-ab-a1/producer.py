from pathlib import Path
import os,sys,json,subprocess,hashlib,tarfile,threading,traceback,time,shutil
base=Path('/home/user/timelearner-refactor');out=base/'readbacks/s06-shared-recognition-ab-a1';out.mkdir(exist_ok=False);bootstrap=base/'source-closed-worker-recovery-a3';source=base/'source-shared-recognition-normal-a1';prior=base/'readbacks/s06-shared-recognition-normal-a3';baseline=base/'readbacks/s06-shared-lifecycle-corrected-normal-a2'
capacity={'slots':1,'memory_bytes':24*1024**3,'disk_bytes':14*1024**3};stop=threading.Event();thread=None;errors=[];token=None;comparison_ok=False;regression_passed=False
sys.path.insert(0,str(source))
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.native_gate import run_native_gate
from Scripts.StructTrain.TimeLearner.runtime import snapshot
registry=Reservations(base/'resource-reservations.sqlite3',capacity=capacity)
def write(n,v):(out/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
write('owned-supervisor.json',{'pid':os.getpid(),'start_ticks':Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19],'baseline_root':'1eab24decb6432947afc928e7f049f3a07de2709','candidate_root':'4f3db1160cda9bad59974af2bff01c023832248d'});(out/'producer.py').write_bytes(Path(__file__).read_bytes())
try:
 assert shutil.disk_usage(base).free>=3*1024**3
 paths=[source,base/'source-shared-lifecycle-corrected-normal-a2',prior,baseline,base/'runtime-shared-recognition-normal-a3',base/'runtime-shared-lifecycle-corrected-normal-a2',base/'readbacks/s05-model-spec-production-normal-a4/corpus/runs',base/'readbacks/s10-managed-native-calibration-normal-a1/actual-controls']
 lease=registry.reserve(out.name,[{'path':str(out),'access':'write'}]+[{'path':str(p),'access':'read'} for p in paths],demands={'slots':1,'memory_bytes':8*1024**3,'disk_bytes':1024**3},ttl_seconds=120);token=lease['token'];write('reservation.json',lease)
 def heartbeat():
  while not stop.wait(20):
   try:registry.heartbeat(token,ttl_seconds=120);registry.validate_paths(token)
   except BaseException as e:errors.append(str(e));return
 thread=threading.Thread(target=heartbeat,daemon=True);thread.start()
 os.environ['QT_QPA_PLATFORM']='offscreen';os.environ.pop('ASAN_OPTIONS',None)
 for k in ['LD_LIBRARY_PATH','QT_PLUGIN_PATH']:os.environ.pop(k,None)
 os.environ['TIMELEARNER_LIVE_COLD_SOURCE']=str(base/'readbacks/s05-model-spec-production-normal-a4/corpus/runs')
 os.environ['TIMELEARNER_LIVE_CALIBRATION_SOURCE']=str(base/'readbacks/s10-managed-native-calibration-normal-a1/actual-controls')
 os.environ['TIMELEARNER_POSTTUNE_FIXED_SOURCE']=str(prior/'fixtures')
 focused=json.loads((prior/'focused-specification.json').read_text());assert len(focused['expected_test_ids'])==8 and focused['maximum_wall_seconds']==21600
 verdicts={};csvs={}
 for name,folder in [('baseline',baseline),('candidate',prior)]:
  runtime=json.loads((folder/'native-runtime.json').read_text());rootdir=Path(runtime['source_closure']['root']['path']) if 'path' in runtime['source_closure']['root'] else (base/'source-shared-lifecycle-corrected-normal-a2' if name=='baseline' else source)
  wanted='1eab24decb6432947afc928e7f049f3a07de2709' if name=='baseline' else '4f3db1160cda9bad59974af2bff01c023832248d'
  assert runtime['source_closure']['root']['head']==wanted
  executable=Path(runtime['executable']['path']);cache=base/('build-shared-lifecycle-corrected-normal-a2' if name=='baseline' else 'build-shared-recognition-normal-a3')/'CMakeCache.txt'
  actual=snapshot(rootdir,executable,Path(runtime['app_ini']['path']),cache);assert actual==runtime
  write(name+'-runtime.json',runtime);spec=dict(focused,source_root=str(rootdir),runtime_manifest=str(out/(name+'-runtime.json')));write(name+'-specification.json',spec)
  v=run_native_gate(out/(name+'-specification.json'),out/(name+'-result'));write(name+'-verdict.json',v);verdicts[name]=v
  assert v['validity']=='valid' and v['inventory']['expected']==v['inventory']['observed']==8
  csvs[name]={p.relative_to(out/(name+'-result')).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in (out/(name+'-result')).rglob('*.csv')}
 assert verdicts['baseline']['inventory']['failed_test_ids']==verdicts['candidate']['inventory']['failed_test_ids']
 assert csvs['baseline'] and csvs['baseline']==csvs['candidate']
 comparison_ok=True;write('comparison.json',{'same_failure_ids':verdicts['baseline']['inventory']['failed_test_ids'],'same_csv_count':len(csvs['baseline']),'all_csv':csvs['baseline'],'owner_positive_contract_exercised':not verdicts['baseline']['inventory']['failed_test_ids'],'no_expected_failures_reclassified_as_success':True})
 full=json.loads((prior/'native-specification.json').read_text());assert len(full['expected_test_ids'])==133 and full['maximum_wall_seconds']==21600
 # The full regression has independent valid fixtures. Same failed training precondition in8 is not a reason to omit it.
 full['runtime_manifest']=str(out/'candidate-runtime.json');write('full-specification.json',full)
 v=run_native_gate(out/'full-specification.json',out/'full-result');write('full-verdict.json',v)
 assert v['execution']=='completed' and v['validity']=='valid' and v['assertion_status']=='passed' and v['inventory']['observed']==v['inventory']['expected']==133
 assert not errors;regression_passed=True
except BaseException as e:write('exception.json',{'reason':str(e),'traceback':traceback.format_exc()})
finally:
 stop.set()
 if thread:thread.join(timeout=30)
 write('terminal.json',{'baseline_candidate8_comparison_complete':comparison_ok,'candidate133_passed':regression_passed,'positive_recognition_owner_gate_passed':False,'whole_controller_accepted':False,'scientific_verdict':None})
 members={}
 with tarfile.open(out/'primary.tar.xz','w:xz',preset=3) as t:
  for p in sorted(out.rglob('*')):
   if p.is_file() and p.name not in ['primary.tar.xz','bundle.json']:
    name=p.relative_to(out).as_posix();members[name]={'bytes':p.stat().st_size,'sha256':sha(p)};info=tarfile.TarInfo(name);info.size=p.stat().st_size
    with p.open('rb') as f:t.addfile(info,f)
 write('bundle.json',{'members':members,'archive_bytes':(out/'primary.tar.xz').stat().st_size,'archive_sha256':sha(out/'primary.tar.xz'),'scientific_verdict':None})
 print('CLOSED',comparison_ok,regression_passed,flush=True)
