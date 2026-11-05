from pathlib import Path
import os,sys,json,hashlib,subprocess,unittest,time,traceback,shutil,tarfile,threading
base=Path('/home/user/timelearner-refactor');source=base/'source-integrated-controller-python-a1';original=base/'readbacks/s10-managed-pipeline-coordinator-normal-a4';primary=original/'actual-controls';out=base/'readbacks/s10-integrated-recovery-declaration-a3';out.mkdir(exist_ok=False);root='d9363446203bdc41c762c81d47deffc835057148';sys.dont_write_bytecode=True;sys.path.insert(0,str(source));os.nice(15)
r=None;global_r=None;token=None;passed=False;stop=threading.Event();thread=None;errors=[]
def write(n,v):(out/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for data in iter(lambda:f.read(1024**2),b''):h.update(data)
 return h.hexdigest()
def inventory(folder):
 result={}
 for p in sorted(folder.rglob('*')):
  name=p.relative_to(folder).as_posix()
  if p.is_symlink():result[name]={'symlink':os.readlink(p)}
  elif p.is_file():result[name]={'bytes':p.stat().st_size,'sha256':sha(p)}
  else:assert p.is_dir()
 return result
def walk(suite):
 for child in suite:
  if isinstance(child,unittest.TestSuite):yield from walk(child)
  else:yield child
(out/'producer.py').write_bytes(Path(__file__).read_bytes());write('owner.json',{'pid':os.getpid(),'start_ticks':Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19],'source_package':root,'native_model_work':False})
try:
 dependency_source=base/'source-worker-dependency-normal-a2';sys.path.insert(0,str(dependency_source))
 from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
 from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
 r=Reservations(base/'metadata-regression-reservations.sqlite3');global_r=Reservations(base/'resource-reservations.sqlite3',capacity={'slots':1,'memory_bytes':24*1024**3,'disk_bytes':14*1024**3})
 prior=base/'readbacks/s10-integrated-recovery-declaration-a3-container'
 from Scripts.StructTrain.TimeLearner.contained_process import inspect
 previous_launch=inspect(prior);assert previous_launch['all_processes_closed'];cleanup=json.loads((base/'readbacks/s10-integrated-recovery-declaration-a3/failed-attempt-cleanup.json').read_text());assert cleanup['execution']=='timeout';write('previous-failed-launch.json',{'closure':previous_launch,'tests_completed':6,'whole20_passed':False,'reason':'previous immutable8c metadata/control suite exhausted1800s outer wall budget; no assertion failure or memory OOM established','temporary_cleanup':cleanup})
 assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()==root
 dep=inspect_worker_dependency(Path(str(original)+'-container'),global_r,original.name);assert dep['state']=='ready' and dep['reservation_state']=='released'
 assert json.loads((original/'terminal.json').read_text())['tests_passed'];write('actual-corpus-prerequisite.json',dep)
 previous=inventory(primary);write('source-primary-inventory-before.json',previous)
 sizes={p.name:sum(v.get('bytes',0) for n,v in previous.items() if n.startswith(p.name+'/')) for p in primary.iterdir() if p.is_dir()};maximum_copy=2*max(sizes.values());assert maximum_copy<1024**3
 assert shutil.disk_usage(base).free>=2*1024**3;write('disk-preflight.json',{'case_regular_bytes':sizes,'maximum_two_case_copy_bytes':maximum_copy,'free_bytes':shutil.disk_usage(base).free,'minimum_free_bytes':2*1024**3,'temporary_copy_budget_bytes':1024**3,'budget_basis':'only metadata/control suite; measured maximum278298262 bytes of temporary copies; lower2GiB free floor leaves more than1GiB margin;7200s wall budget, assertions and20-case inventory unchanged','copies_removed_by_each_test_cleanup':True})
 held=[v for lease in global_r.inspect()['leases'] if lease['state']=='held' for v in lease['resources']]
 for p in [out,source,original]:
  for v in held:
   q=Path(v['canonical_path']);assert not p.is_relative_to(q) and not q.is_relative_to(p),str(q)
 temp=out/'temporary';temp.mkdir();os.environ.update(TMPDIR=str(temp),TIMELEARNER_MANAGED_COORDINATOR_PRIMARY=str(primary),PYTHONDONTWRITEBYTECODE='1');import tempfile;tempfile.tempdir=str(temp)
 lease=r.reserve(out.name,[{'path':str(out),'access':'write'},{'path':str(source),'access':'read'},{'path':str(original),'access':'read'}],ttl_seconds=120);token=lease['token'];write('reservation.json',lease)
 def heartbeat():
  while not stop.wait(20):
   try:r.heartbeat(token,ttl_seconds=120);r.validate_paths(token)
   except BaseException as e:errors.append(str(e));return
 thread=threading.Thread(target=heartbeat,daemon=True);thread.start()
 for n in list(sys.modules):
  if n=='Scripts' or n.startswith('Scripts.'):del sys.modules[n]
 sys.path.insert(0,str(source))
 modules=['Scripts.StructTrain.TimeLearner.tests.test_managed_pipeline_reconciliation','Scripts.StructTrain.TimeLearner.tests.test_managed_declaration'];suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(n) for n in modules);ids=[t.id() for t in walk(suite)];assert len(ids)==len(set(ids))==20 and all('_FailedTest' not in n for n in ids);write('expected-test-ids.json',ids)
 with (out/'tests.log').open('w') as log:result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
 write('tests.json',{'executed':result.testsRun,'expected':20,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped)})
 assert result.testsRun==20 and result.wasSuccessful() and not result.skipped
 assert not list(temp.iterdir());temp.rmdir();after=inventory(primary);assert after==previous;write('source-primary-inventory-after.json',after)
 write('source-hashes.json',{p.relative_to(source).as_posix():sha(p) for p in (source/'Scripts/StructTrain/TimeLearner').rglob('*.py') if '__pycache__' not in p.parts});assert not errors;passed=True
except BaseException as e:write('exception.json',{'reason':str(e),'traceback':traceback.format_exc()})
finally:
 stop.set()
 if thread:thread.join(timeout=30)
 write('terminal.json',{'tests_passed':passed,'native_models_executed':0,'source_package':root,'corpus_origin_evidence':'2776bd89fb53a4c32324a445d771e75d010a30d0','whole_fault_matrix_complete':False,'scientific_verdict':None})
 members={p.relative_to(out).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in out.rglob('*') if p.is_file() and not p.is_symlink()}
 with tarfile.open(out/'primary.tar.xz','w:xz',preset=3) as a:
  for n,record in members.items():
   info=tarfile.TarInfo(n);info.size=record['bytes']
   with (out/n).open('rb') as f:a.addfile(info,f)
 write('bundle.json',{'members':members,'archive_bytes':(out/'primary.tar.xz').stat().st_size,'archive_sha256':sha(out/'primary.tar.xz'),'scientific_verdict':None});print('CLOSED',passed,flush=True)
