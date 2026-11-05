from pathlib import Path,PurePosixPath
import os,sys,json,subprocess,hashlib,tarfile,io,unittest,traceback,threading,shutil
venv='/media/user/Data/TimeLearnerRefactor/plot-venv-a1'
if sys.prefix!=venv:os.execv(venv+'/bin/python',[venv+'/bin/python',str(Path(__file__))])
base=Path('/media/user/Data/TimeLearnerRefactor');source=base/'source-integrated-owner-plots-a1';out=base/'readbacks/s11-shared-saved-ab-visual-a1';out.mkdir(exist_ok=False);cache=base/'ReportsCache/shared-saved-ab16-a1';sys.path.insert(0,str(source));sys.dont_write_bytecode=True;os.nice(15)
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
r=Reservations(base/'shared-recognition-report-reservations.sqlite3');stop=threading.Event();thread=None;token=None;errors=[];passed=False
def write(n,v):(out/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def blob(c,n):return subprocess.check_output(['git','-C',str(source),'show',c+':'+n])
(out/'producer.py').write_bytes(Path(__file__).read_bytes());write('owner.json',{'pid':os.getpid(),'start_ticks':Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19],'source':'0bebed450eb2f9bfc69e6c428ac2b2331dc6fd7d','native_model_runs':0})
try:
 assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()=='0bebed450eb2f9bfc69e6c428ac2b2331dc6fd7d';assert not cache.exists() and shutil.disk_usage(base).free>=2*1024**3
 bind=json.loads((base/'readbacks/s07-csearch-threshold-joint-full-asan-a2-container/owned-unit.json').read_text());group=Path('/sys/fs/cgroup'+bind['control_group']);current=int((group/'memory.current').read_text()) if group.exists() else 0;maximum=int((group/'memory.max').read_text()) if group.exists() else 0;available=int(next(s.split()[1] for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:')))*1024
 assert available>=max(0,maximum-current)+2*1024**3
 write('resource-preflight.json',{'MemAvailable':available,'ASan_current':current,'ASan_limit':maximum,'renderer_limit':1024**3,'extra_margin':1024**3,'heavy_SDK_build':False})
 lease=r.reserve(out.name,[{'path':str(out),'access':'write'},{'path':str(cache),'access':'write'},{'path':str(source),'access':'read'}],ttl_seconds=120);token=lease['token'];write('reservation.json',lease)
 def heartbeat():
  while not stop.wait(20):
   try:r.heartbeat(token,ttl_seconds=120);r.validate_paths(token)
   except BaseException as e:errors.append(str(e));return
 thread=threading.Thread(target=heartbeat,daemon=True);thread.start();cache.mkdir();restored=[]
 for name,c,prefix,selection in [('native','b411dbf1eb469f83442dc816f77563f82bdfb5ea','Reports/StructTrain/TimeLearner/s06-positive-recognition-owner141-a1/','focused-result/native/'),('replay','87ea825ae4d2a1e91414b8e30cd00827d4f7ea25','Reports/StructTrain/TimeLearner/s06-recognition-shared-saved-ab-a2/','')]:
  bundle=json.loads(blob(c,prefix+'bundle.json'));raw=blob(c,prefix+'primary.tar.xz');assert len(raw)==bundle['archive_bytes'] and hashlib.sha256(raw).hexdigest()==bundle['archive_sha256'];dest=cache/name;dest.mkdir();seen=set();written=0
  with tarfile.open(fileobj=io.BytesIO(raw),mode='r:xz') as a:
   for member in a:
    n=PurePosixPath(member.name);assert member.isfile() and not n.is_absolute() and '..' not in n.parts and member.name not in seen;seen.add(member.name);value=a.extractfile(member).read();assert bundle['members'][member.name]=={'bytes':len(value),'sha256':hashlib.sha256(value).hexdigest()}
    if member.name.startswith(selection):
     f=dest/member.name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(value);assert sha(f)==bundle['members'][member.name]['sha256'];written+=1
  assert seen==set(bundle['members']);restored.append({'commit':c,'prefix':prefix,'archive_sha256':bundle['archive_sha256'],'all_members_verified':len(seen),'selected_members_restored':written})
 write('restoration.json',restored);original=cache/'native/focused-result/native';replay=cache/'replay';before={str(f.relative_to(cache)):sha(f) for folder in [cache/'native',replay] for f in folder.rglob('*') if f.is_file()};write('primary-before.json',before)
 from Scripts.StructTrain.TimeLearner.tests.test_recognition_owner_replay_reports import RecognitionOwnerReplayReportsTest
 results={};inventories={}
 for name in ['baseline','candidate']:
  report=cache/('reports-'+name);os.environ.update(TIMELEARNER_MODELSPEC2_OWNER_SOURCE=str(original),TIMELEARNER_MODELSPEC2_FRESH_OWNER_REPLAY=str(replay/name),TIMELEARNER_MODELSPEC2_REPLAY_REPORT_CACHE=str(report))
  with (out/(name+'-tests.log')).open('w') as log:result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RecognitionOwnerReplayReportsTest))
  results[name]={'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped)};assert result.testsRun==1 and result.wasSuccessful() and not result.skipped
  manifest=json.loads((report/'manifest.json').read_text());write(name+'-report-manifest.json',manifest);inventories[name]={str(f.relative_to(report)):{'bytes':f.stat().st_size,'sha256':sha(f)} for f in report.rglob('*') if f.is_file()}
 after={str(f.relative_to(cache)):sha(f) for folder in [cache/'native',replay] for f in folder.rglob('*') if f.is_file()};assert before==after;write('primary-after.json',after);write('tests.json',results);write('full-cache-inventory.json',inventories);write('source-hashes.json',{str(f.relative_to(source)):sha(f) for f in (source/'Scripts/StructTrain/TimeLearner').rglob('*.py') if '__pycache__' not in f.parts});assert not errors;passed=True
except BaseException as e:write('exception.json',{'reason':str(e),'traceback':traceback.format_exc()})
finally:
 stop.set()
 if thread:thread.join(timeout=30)
 write('terminal.json',{'reports_checked':passed,'new_native_model_runs':0,'source':'0bebed450eb2f9bfc69e6c428ac2b2331dc6fd7d','cache':str(cache),'selected_images_pending':True,'manual_QA_complete':False,'scientific_verdict':None})
 members={str(f.relative_to(out)):{'bytes':f.stat().st_size,'sha256':sha(f)} for f in out.rglob('*') if f.is_file()}
 with tarfile.open(out/'metadata.tar.xz','w:xz',preset=3) as a:
  for n,v in members.items():
   info=tarfile.TarInfo(n);info.size=v['bytes']
   with (out/n).open('rb') as f:a.addfile(info,f)
 write('bundle.json',{'members':members,'archive_bytes':(out/'metadata.tar.xz').stat().st_size,'archive_sha256':sha(out/'metadata.tar.xz'),'full_images_kept_only_in_M40_cache':True,'scientific_verdict':None});print('CLOSED',passed,flush=True)
