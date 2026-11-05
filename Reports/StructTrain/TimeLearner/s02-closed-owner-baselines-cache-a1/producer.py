audit={'targets': ['/home/user/timelearner-refactor/build-shared-recognition-normal-a3', '/home/user/timelearner-refactor/build-shared-lifecycle-corrected-normal-a2', '/home/user/timelearner-refactor/readbacks/s06-shared-recognition-ab-a1/baseline-result', '/home/user/timelearner-refactor/readbacks/s06-shared-recognition-ab-a1/candidate-result', '/home/user/timelearner-refactor/readbacks/s06-shared-recognition-ab-a1/full-result'], 'checked_processes': 292, 'hits': [], 'errors': [], 'read_only_audit': True, 'time_ns': 1793862276252560159}
cache={'commit': '1ed9bb55c7e56fda8e117391943b07b66372dca1', 'cache': '/media/user/Data/TimeLearnerRefactor/ReportsCache/shared-recognition-ab-a1/source', 'regular_files': 2056, 'expanded_bytes': 809241644, 'archive_sha256': '23b8ffbfdda712470dc50b9726040167af8a4fb5990a5ac77d9f2a71568f18b5', 'source_transport': 'Git only', 'archive_retained_in_origin_develop': True, 'all_files_written_and_rehashed': True}

from pathlib import Path
import json,sys,hashlib,shutil,subprocess,time,threading
b=Path('/home/user/timelearner-refactor').resolve();out=b/'readbacks/s02-closed-owner-baselines-cache-a1';out.mkdir(exist_ok=False);sys.path.insert(0,str(b/'source-worker-dependency-normal-a2'))
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
r=Reservations(b/'resource-reservations.sqlite3',capacity={'slots':1,'memory_bytes':24*1024**3,'disk_bytes':14*1024**3});token=None
assert audit['read_only_audit'] and not audit['hits'] and not audit['errors'] and time.time_ns()-audit['time_ns']<900*10**9
assert cache['all_files_written_and_rehashed'] and cache['regular_files']==2056 and cache['expanded_bytes']==809241644
paths=[Path(n) for n in audit['targets']];assert all(p.resolve()==p and p.is_relative_to(b) and p!=b and p.exists() for p in paths)
expected=[b/n for n in ['build-shared-recognition-normal-a3','build-shared-lifecycle-corrected-normal-a2','readbacks/s06-shared-recognition-ab-a1/baseline-result','readbacks/s06-shared-recognition-ab-a1/candidate-result','readbacks/s06-shared-recognition-ab-a1/full-result']];assert paths==expected
states={n:inspect_worker_dependency(b/'readbacks'/(n+'-container'),r,n) for n in ['s06-shared-recognition-ab-a1','s06-recognition-owner-burst-normal-a1']};assert all(v['state']=='ready' and v['reservation_state']=='released' for v in states.values())
for l in r.inspect()['leases']:
 if l['state']=='held':
  for v in l['resources']:
   q=Path(v['canonical_path']);assert all(not p.is_relative_to(q) and not q.is_relative_to(p) for p in paths)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(1024**2),b''):h.update(x)
 return h.hexdigest()
original=b/'readbacks/s06-shared-recognition-ab-a1';bundle=json.loads((original/'bundle.json').read_text());assert sha(original/'primary.tar.xz')==cache['archive_sha256']==bundle['archive_sha256']
records={};builds={}
for directory in paths:
 for f in directory.rglob('*'):
  if f.is_symlink():records[str(f.relative_to(b))]={'symlink':str(f.readlink())};continue
  if not f.is_file():continue
  assert f.resolve().is_relative_to(directory)
  record={'bytes':f.stat().st_size,'sha256':sha(f)};records[str(f.relative_to(b))]=record
  if directory in paths[2:]:assert bundle['members'][f.relative_to(original).as_posix()]==record
for directory,source_root in [(paths[0],'4f3db1160cda9bad59974af2bff01c023832248d'),(paths[1],'1eab24decb6432947afc928e7f049f3a07de2709')]:
 text=(directory/'CMakeCache.txt').read_text();values=dict(s.split('=',1) for s in text.splitlines() if '=' in s and not s.startswith(('#','//')));home=Path(values['CMAKE_HOME_DIRECTORY:INTERNAL']);runtime=Path(values['NMSDK_DEPLOY_ROOT:PATH']);assert home.is_relative_to(b) and runtime.is_relative_to(b) and not runtime.is_relative_to(directory)
 assert subprocess.check_output(['git','-C',str(home),'rev-parse','HEAD'],text=True).strip()==source_root
 (out/(directory.name+'-CMakeCache.txt')).write_bytes((directory/'CMakeCache.txt').read_bytes());builds[directory.name]={'root':source_root,'source_retained':str(home),'runtime_retained':str(runtime)}
lease=r.reserve(out.name,[{'path':str(out),'access':'write'}]+[{'path':str(p),'access':'write'} for p in paths],demands={'slots':1,'memory_bytes':512*1024**2,'disk_bytes':64*1024**2},ttl_seconds=300);token=lease['token'];(out/'reservation.json').write_text(json.dumps(lease,indent=2))
proof={'read_only_process_audit':audit,'M40_full_cache_verification':cache,'fresh_dependencies':states,'removed_path_inventory':records,'builds':builds,'free_before':shutil.disk_usage(b).free,'unique_primaries_lost':False,'source_runtime_resources_retained':True}
(out/'predelete-verification.json').write_text(json.dumps(proof,indent=2)+'\n')
try:
 r.validate_paths(token)
 for directory in paths:
  assert directory.resolve()==directory and directory in expected and directory.is_relative_to(b)
  shutil.rmtree(directory)
 proof['free_after']=shutil.disk_usage(b).free;proof['bytes_freed']=proof['free_after']-proof['free_before'];proof['completed']=True
 (out/'result.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:proof[k] for k in ['free_before','free_after','bytes_freed','unique_primaries_lost','completed']}))
finally:
 if token:r.release(token,note='Closed obsolete build caches and byte-verified duplicate expanded AB corpus removed; all primary data preserved in Git and M40 full cache.')
