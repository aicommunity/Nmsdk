from pathlib import Path
import os,sys,json,subprocess,hashlib,tarfile,traceback,unittest,contextlib,sqlite3,shutil
base=Path('/home/user/timelearner-refactor');source=base/'source-statistic-traces-a1';out=base/'readbacks/s09-statistic-traces-a1';out.mkdir(exist_ok=False);sys.dont_write_bytecode=True;os.environ['PYTHONDONTWRITEBYTECODE']='1';sys.path.insert(0,str(source));os.chdir('/tmp')
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
registry=Reservations(base/'statistic-trace-checks-reservations.sqlite3');lease=None;passed=False

def write(name,value):(out/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
write('owner.json',{'pid':os.getpid(),'start_ticks':Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19],'source_commit':'f096b7a854b95b04c08720dcc8c9610de85f1bf2','native_models_executed':0});(out/'producer.py').write_bytes(Path(__file__).read_bytes())
try:
 assert shutil.disk_usage(base).free>=256*1024**2
 assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()=='f096b7a854b95b04c08720dcc8c9610de85f1bf2'
 assert not subprocess.check_output(['git','-C',str(source),'status','--porcelain','--untracked-files=no'],text=True).strip()
 c=sqlite3.connect('file:'+str(base/'resource-reservations.sqlite3')+'?mode=ro',uri=True)
 try:held=[r for row in c.execute("SELECT resources FROM leases WHERE state='held'") for r in json.loads(row[0])]
 finally:c.close()
 for p in [source,out]:
  for record in held:
   q=Path(record['canonical_path']);assert not p.is_relative_to(q) and not q.is_relative_to(p)
 write('isolation.json',{'no_held_resource_overlap':True,'global_policy_not_modified':True,'held_resources':held,'native_models_executed':0,'old_scripts_executed':False})
 lease=registry.reserve(out.name,[{'path':str(source),'access':'read'},{'path':str(out),'access':'write'}],ttl_seconds=120);write('reservation.json',lease)
 suite=unittest.defaultTestLoader.loadTestsFromName('Scripts.StructTrain.TimeLearner.tests.test_statistic_traces')
 def ids(suite):
  for value in suite:
   if isinstance(value,unittest.TestSuite):yield from ids(value)
   else:yield value.id()
 expected=list(ids(suite));assert len(expected)==len(set(expected))==12;write('expected-tests.json',expected)
 with (out/'unittest.log').open('w') as log,(out/'test-stdout.log').open('w') as stdout,(out/'test-stderr.log').open('w') as stderr,contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
 write('result.json',{'executed':result.testsRun,'expected':expected,'failures':result.failures,'errors':result.errors,'skipped':result.skipped,'passed':result.wasSuccessful(),'native_models_executed':0,'scientific_verdict':None});assert result.testsRun==12 and result.wasSuccessful() and not result.skipped;passed=True
except BaseException as error:write('exception.json',{'reason':str(error),'traceback':traceback.format_exc()})
finally:
 if lease:registry.release(lease['token'],note='Finished isolated reader and production CLI checks; no native models or historical scripts executed')
 write('source-hashes.json',{p.relative_to(source).as_posix():sha(p) for p in (source/'Scripts/StructTrain/TimeLearner').rglob('*') if p.is_file() and (p.suffix=='.py' or 'fixtures/statistic_traces' in p.as_posix())})
 write('terminal.json',{'checks_passed':passed,'native_models_executed':0,'whole_plan_complete':False,'scientific_verdict':None})
 members={}
 with tarfile.open(out/'primary.tar.xz','w:xz',preset=3) as tf:
  for p in sorted(out.iterdir()):
   if p.is_file() and p.name not in ['primary.tar.xz','bundle.json']:
    members[p.name]={'bytes':p.stat().st_size,'sha256':sha(p)};info=tarfile.TarInfo(p.name);info.size=p.stat().st_size
    with p.open('rb') as stream:tf.addfile(info,stream)
 write('bundle.json',{'source_commit':'f096b7a854b95b04c08720dcc8c9610de85f1bf2','checks_passed':passed,'members':members,'archive_bytes':(out/'primary.tar.xz').stat().st_size,'archive_sha256':sha(out/'primary.tar.xz'),'scientific_verdict':None});print('CLOSED',passed,flush=True)
