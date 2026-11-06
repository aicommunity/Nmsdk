from pathlib import Path
import os,sys,json,subprocess,hashlib,stat,shutil,tarfile,threading,sqlite3,traceback
base=Path('/home/user/timelearner-refactor');out=base/'readbacks/s02-elder-normal304-expanded-duplicates-a2';out.mkdir(exist_ok=False);old=base/'readbacks/s07-integrated-native304-normal-a1';target=old/'native-result/native';archive=old/'primary.tar.xz';repo=base/'source-asymrm-driver-retirement-a1';tool=base/'source-pipeline-condition-a2';sys.dont_write_bytecode=True;sys.path.insert(0,str(tool));stop=threading.Event();thread=None;registry=None;token=None;passed=False;errors=[]
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.process_runner import verify_runtime

def write(name,value):(out/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as stream:
  for b in iter(lambda:stream.read(1024**2),b''):h.update(b)
 return h.hexdigest()
def identity(s):return [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_nlink]
write('owner.json',{'pid':os.getpid(),'start_ticks':Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19],'native_models_executed':0});(out/'producer.py').write_bytes(Path(__file__).read_bytes())
try:
 assert target.resolve(strict=True)==target.absolute() and target.is_relative_to(base.resolve()) and target.name=='native' and target.parent.name=='native-result'
 raw=subprocess.check_output(['git','-C',str(repo),'show','d3429a33209a9985a3d30164df69206713f8d724:Reports/StructTrain/TimeLearner/s07-integrated-native304-normal-a1/bundle.json']);canonical=json.loads(raw);assert (old/'bundle.json').read_bytes()==raw and canonical['archive_sha256']=='e95626641478c04131900bf17aebed1cca3264f8ad6e05499d4409d3e5a97414' and archive.stat().st_size==canonical['archive_bytes'] and sha(archive)==canonical['archive_sha256'];write('canonical-archive.json',{'data_commit':'d3429a33209a9985a3d30164df69206713f8d724','bundle_sha256':hashlib.sha256(raw).hexdigest(),'archive_path':str(archive),'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'archive_kept':True})
 c=sqlite3.connect('file:'+str(base/'resource-reservations.sqlite3')+'?mode=ro',uri=True)
 try:capacity=json.loads(dict(c.execute('SELECT key,value FROM metadata'))['capacity'])
 finally:c.close()
 registry=Reservations(base/'resource-reservations.sqlite3',capacity=capacity);closed=inspect_worker_dependency(Path(str(old)+'-container'),registry,old.name);assert closed['state']=='ready';write('original-worker-closure.json',closed)
 lease=registry.reserve(out.name,[{'path':str(target),'access':'write'},{'path':str(out),'access':'write'},{'path':str(old),'access':'read'},{'path':str(repo),'access':'read'},{'path':str(tool),'access':'read'}],ttl_seconds=120,demands={'slots':1,'memory_bytes':512*1024**2,'disk_bytes':8*1024**2});token=lease['token'];write('reservation.json',lease)
 def heartbeat():
  while not stop.wait(20):
   try:registry.heartbeat(token,ttl_seconds=120);registry.validate_paths(token)
   except BaseException as e:errors.append(str(e));return
 thread=threading.Thread(target=heartbeat,daemon=True);thread.start()
 runtime=json.loads((base/'readbacks/s10-pipeline-condition-native-a1/runtime.json').read_text());verify_runtime(runtime);critical=[runtime['executable'],runtime['app_ini'],runtime['compiler']]+runtime['resolved_libraries'];before={r['path']:sha(Path(r['path'])) for r in critical};write('runtime-before.json',before)
 expected={n.removeprefix('native-result/native/'):v for n,v in canonical['members'].items() if n.startswith('native-result/native/')};actual=[p for p in target.rglob('*') if not p.is_dir()];assert {p.relative_to(target).as_posix() for p in actual}==set(expected)
 rows=[]
 for p in sorted(actual):
  assert p.resolve(strict=True).is_relative_to(target) and not p.is_symlink();s=p.lstat();key=p.relative_to(target).as_posix();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_size==expected[key]['bytes'] and sha(p)==expected[key]['sha256'];rows.append({'path':str(p),'relative':key,'bytes':s.st_size,'sha256':expected[key]['sha256'],'identity':identity(s)})
 assert rows and not errors;write('prepared-files.json',rows)
 # Inspect user processes once; only named nondumpable login/session helpers
 # may be excluded, explicitly recorded. No unknown ownership is ignored.
 open_refs=[];excluded=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit():continue
  try:
   if p.stat().st_uid!=os.getuid():continue
   links=[]
   try:
    links.append(os.readlink(p/'cwd'))
    for fd in (p/'fd').iterdir():
     try:links.append(os.readlink(fd))
     except FileNotFoundError:pass
   except PermissionError:
    comm=(p/'comm').read_text().strip();parent=(p/'status').read_text().split('PPid:')[1].splitlines()[0].strip();parent_comm=(Path('/proc')/parent/'comm').read_text().strip();assert (comm,parent_comm) in [('(sd-pam)','systemd'),('ssh-agent','systemd'),('sshd','sshd')],(p.name,comm,parent_comm);excluded.append({'pid':p.name,'comm':comm,'parent':parent,'parent_comm':parent_comm,'cwd_fd_not_inspected':True});continue
   for name in links:
    if name.startswith(str(target)+'/') or name==str(target):open_refs.append({'pid':p.name,'path':name})
  except FileNotFoundError:pass
 assert not open_refs;write('open-reference-check.json',{'target':str(target),'open_references':open_refs,'excluded_nondumpable_helpers':excluded,'unknown_permission_ignored':False})
 free_before=shutil.disk_usage(base).free;removed=0
 with (out/'deletions.jsonl').open('x',encoding='utf-8') as journal:
  for row in rows:
   assert not errors;registry.validate_paths(token);p=Path(row['path']);assert p.resolve(strict=True).is_relative_to(target) and identity(p.lstat())==row['identity'] and sha(p)==row['sha256'] and identity(p.lstat())==row['identity'];journal.write(json.dumps({'state':'verified_before_unlink',**row})+'\n');journal.flush();os.fsync(journal.fileno());p.unlink();journal.write(json.dumps({'state':'removed','relative':row['relative'],'sha256':row['sha256']})+'\n');journal.flush();os.fsync(journal.fileno());removed+=1
 assert removed==len(rows) and not any(p.is_file() for p in target.rglob('*'));(target/'CACHE_RESTORATION.md').write_text('Expanded duplicates removed only after exact content verification. Restore native-result/native/* from ../../primary.tar.xz (relative to this marker directory) or Git data d3429a33209a9985a3d30164df69206713f8d724, Reports/StructTrain/TimeLearner/s07-integrated-native304-normal-a1. Archive SHA256 e95626641478c04131900bf17aebed1cca3264f8ad6e05499d4409d3e5a97414. No original archive, code, model evidence or runtime was deleted.\n')
 after={r['path']:sha(Path(r['path'])) for r in critical};assert after==before and sha(archive)==canonical['archive_sha256'];verify_runtime(runtime);write('result.json',{'removed_files':removed,'logical_bytes_removed':sum(r['bytes'] for r in rows),'free_bytes_before':free_before,'free_bytes_after':shutil.disk_usage(base).free,'runtime_critical_files_unchanged':len(before),'archive_kept_and_rehashed':True,'native_models_executed':0,'scientific_verdict':None});passed=True
except BaseException as e:write('exception.json',{'reason':str(e),'traceback':traceback.format_exc()})
finally:
 stop.set()
 if thread:thread.join(timeout=10)
 if token:registry.release(token,note='Exact expanded duplicate cleanup finished; canonical archive and runtime retained')
 write('terminal.json',{'cleanup_passed':passed,'native_models_executed':0,'whole_plan_complete':False,'scientific_verdict':None});members={}
 with tarfile.open(out/'primary.tar.xz','w:xz',preset=3) as tf:
  for p in sorted(out.iterdir()):
   if p.is_file() and p.name not in ['primary.tar.xz','bundle.json']:
    members[p.name]={'bytes':p.stat().st_size,'sha256':sha(p)};info=tarfile.TarInfo(p.name);info.size=p.stat().st_size
    with p.open('rb') as stream:tf.addfile(info,stream)
 write('bundle.json',{'cleanup_passed':passed,'members':members,'archive_bytes':(out/'primary.tar.xz').stat().st_size,'archive_sha256':sha(out/'primary.tar.xz'),'scientific_verdict':None});print('CLOSED',passed,flush=True)
