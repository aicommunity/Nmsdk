from pathlib import Path
import os,sys,json,subprocess,hashlib,threading,traceback,tarfile,shutil
base=Path('/media/user/Data/TimeLearnerRefactor');reader=base/'source-integrated-owner-plots-a1';sdk=base/'source-csearch-threshold-joint-asan-build-a1';original=base/'readbacks/s07-native-partition-full-asan-a2';fixtures=base/'readbacks/s07-joint-asan-followup-fixtures-a1';out=base/'readbacks/s07-joint-asan-owner-readers-a3';out.mkdir(exist_ok=False);sys.path.insert(0,str(reader));sys.dont_write_bytecode=True
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.validation import package_fingerprint,fixture_fingerprint
from Scripts.StructTrain.TimeLearner.process_runner import verify_runtime
r=Reservations(base/'resource-reservations.sqlite3');token=None;stop=threading.Event();thread=None;errors=[];passed=False

def write(n,v):(out/n).write_bytes(json.dumps(v,indent=2,allow_nan=False).encode()+bytes([10]))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
(out/'producer.py').write_bytes(Path(__file__).read_bytes());write('owned-supervisor.json',{'pid':os.getpid(),'start_ticks':Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19],'reader_root':'0bebed450eb2f9bfc69e6c428ac2b2331dc6fd7d','native_root':'8021301e894368aefd045f9d77274fcce9f60245','new_SDK_build':False})
try:
 state=inspect_worker_dependency(Path(str(original)+'-container'),r,original.name);assert state['state']=='ready' and state['reservation_state']=='released';write('native304-resource-prerequisite.json',state)
 assert json.loads((original/'terminal.json').read_text())['native304_asan_passed']
 verdict=json.loads((original/'native-verdict.json').read_text());assert verdict['execution']=='completed' and verdict['validity']=='valid' and verdict['assertion_status']=='passed' and verdict['inventory']['observed']==verdict['inventory']['expected']==304
 assert shutil.disk_usage(base).free>=2*1024**3
 assert subprocess.check_output(['git','-C',str(reader),'rev-parse','HEAD'],text=True).strip()=='0bebed450eb2f9bfc69e6c428ac2b2331dc6fd7d';assert subprocess.check_output(['git','-C',str(sdk),'rev-parse','HEAD'],text=True).strip()=='8021301e894368aefd045f9d77274fcce9f60245'
 runtime=json.loads((original/'native-runtime.json').read_text());verify_runtime(runtime);write('native-runtime.json',runtime)
 lease=r.reserve(out.name,[{'path':str(out),'access':'write'}]+[{'path':str(p),'access':'read'} for p in [reader,sdk,original,fixtures,Path(runtime['executable']['path']).parent]],ttl_seconds=120);token=lease['token'];write('reservation.json',lease)
 def heartbeat():
  while not stop.wait(20):
   try:r.heartbeat(token,ttl_seconds=120);r.validate_paths(token)
   except BaseException as e:errors.append(str(e));return
 thread=threading.Thread(target=heartbeat,daemon=True);thread.start()
 native=original/'native-result/native';rows=[];cohort=set()
 for f in sorted(native.glob('*_owner_recognition_state.json')):
  package=json.loads(f.read_text());c=package['source_solo']['configuration'];m=c['model']
  if m['schema_version']!=2 or m['initial_threshold']!=100. or c['schema_version'] not in (3,4):continue
  mode='On' if c['schema_version']==4 else 'Off';key=(m['branch'],m['normalization'],mode);assert key not in cohort;cohort.add(key);rows.append({'id':('Branch' if m['branch'] else 'Classic')+'_'+m['normalization']+'_C'+mode,'package':f.name,'file_sha256':sha(f)})
 assert cohort=={(b,n,c) for b in (False,True) for n in ('N0','N1') for c in ('Off','On')} and len(rows)==8
 evidence=json.loads((base/'readbacks/s07-joint-asan-owner-readers-a3-queue/native304-published-origin.json').read_text());assert evidence['origin_published'] is True and evidence['native_source_commit']=='8021301e894368aefd045f9d77274fcce9f60245' and evidence['native_archive_sha256']==sha(original/'primary.tar.xz')
 receipt_repo=base/'source-theory-retirement-a1';published_bundle=subprocess.check_output(['git','-C',str(receipt_repo),'show',evidence['evidence_commit']+':'+evidence['report_prefix'].rstrip('/')+'/bundle.json']);assert published_bundle==(original/'bundle.json').read_bytes()
 write('native304-published-origin.json',evidence)
 spec={'kind':'timelearner_recognition_owner_replay','schema_version':1,'source_directory':str(native),'source_bundle':str(original/'bundle.json'),'source_archive':str(original/'primary.tar.xz'),'source_prefix':'native-result/native','origin_evidence_commit':evidence['evidence_commit'],'native_source_root':str(sdk),'runtime_manifest':str(out/'native-runtime.json'),'maximum_wall_seconds':180,'asan_options':'detect_leaks=0','cases':rows}
 write('replay-specification.json',spec)
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',QT_QPA_PLATFORM='offscreen');env.pop('ASAN_OPTIONS',None)
 args=[sys.executable,'-m','Scripts.StructTrain.TimeLearner.recognition_owner_replay',str(out/'replay-specification.json'),'--output',str(out/'fresh-owner-replay')]
 with (out/'owner-cli.log').open('wb') as log:process=subprocess.run(args,cwd=reader,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=3000)
 index=json.loads((out/'fresh-owner-replay/index.json').read_text());assert process.returncode==0 and index['passed'] and len(index['cases'])==8 and all(v['passed'] for v in index['cases'])
 old=json.loads((fixtures/'normal/reader-suite.json').read_text());assert len(old['expected_test_ids'])==128
 bindings={k:(original/'native-result' if k=='TIMELEARNER_NATIVE_GATE_DIR' else native) for k in old['fixtures']};bindings.update(TIMELEARNER_DOMAIN_EVIDENCE_DIR=fixtures/'domain/fixture',TIMELEARNER_MODELSPEC2_FRESH_OWNER_REPLAY=out/'fresh-owner-replay',TIMELEARNER_MODELSPEC2_OWNER_SOURCE=native);declarations={}
 for key,folder in bindings.items():
  pattern='**/*.json' if key=='TIMELEARNER_MODELSPEC2_FRESH_OWNER_REPLAY' else '*.json';count,digest=fixture_fingerprint(folder,pattern);declarations[key]={'pattern':pattern,'files':count,'fingerprint':digest}
 suite={'kind':'timelearner_python_validation_suite','schema_version':1,'suite_id':'joint304-ASan-real-owner8-and-reader128','package_fingerprint':package_fingerprint(),'modules':old['modules'],'expected_test_ids':old['expected_test_ids'],'fixtures':declarations};write('reader-suite.json',suite);write('fixture-bindings.json',{k:str(v) for k,v in bindings.items()});args=[sys.executable,'-m','Scripts.StructTrain.TimeLearner.validation',str(out/'reader-suite.json'),'--output',str(out/'structured-readers')]
 for k,v in bindings.items():args+=['--fixture',k+'='+str(v)]
 with (out/'reader-cli.log').open('wb') as log:process=subprocess.run(args,cwd=reader,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=3000)
 result=json.loads((out/'structured-readers/result.json').read_text());assert process.returncode==0 and result['executed_tests']==128 and result['assertion_status']=='passed' and not any(result[k] for k in ['failures','errors','skipped']);assert not errors;passed=True
except BaseException as e:write('exception.json',{'reason':str(e),'traceback':traceback.format_exc()})
finally:
 write('reader-source-hashes.json',{str(p.relative_to(reader)):sha(p) for p in (reader/'Scripts/StructTrain/TimeLearner').rglob('*.py') if '__pycache__' not in p.parts});write('terminal.json',{'ASan_owner8_readers128_passed':passed,'native304_prerequisite_not_inferred_from_this_job':True,'leak_absence_attested':False,'exact_published_origin_verified':True,'whole_plan_complete':False,'scientific_verdict':None})
 members={str(p.relative_to(out)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in out.rglob('*') if p.is_file() and not p.is_symlink()}
 with tarfile.open(out/'primary.tar.xz','w:xz',preset=3) as a:
  for n,v in members.items():
   info=tarfile.TarInfo(n);info.size=v['bytes']
   with (out/n).open('rb') as f:a.addfile(info,f)
 write('bundle.json',{'members':members,'archive_bytes':(out/'primary.tar.xz').stat().st_size,'archive_sha256':sha(out/'primary.tar.xz'),'scientific_verdict':None});stop.set()
 if thread:thread.join(timeout=30)
 print('CLOSED',passed,flush=True)
