from pathlib import Path
import os,sys,json,hashlib,tarfile,traceback,unittest,io,sqlite3
base=Path('/media/user/Data/TimeLearnerRefactor');source=base/'source-portable-primary-a1';out=base/'readbacks/s09-portable-primary-readers-a1';out.mkdir(exist_ok=False);sys.dont_write_bytecode=True;os.environ['PYTHONDONTWRITEBYTECODE']='1';sys.path.insert(0,str(source));passed=False;token=None;registry=None
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.tests.test_portable_primary import PortablePrimaryTest

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):(out/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
write('owner.json',{'pid':os.getpid(),'start_ticks':Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19],'source_commit':'f1af8480406b3d1c1cfdb4b62f2b501e1117c5b6','native_models_executed':0});(out/'producer.py').write_bytes(Path(__file__).read_bytes())
try:
 c=sqlite3.connect('file:'+str(base/'resource-reservations.sqlite3')+'?mode=ro',uri=True)
 try:metadata=dict(c.execute('SELECT key,value FROM metadata'))
 finally:c.close()
 registry=Reservations(base/'resource-reservations.sqlite3',**({'capacity':json.loads(metadata['capacity'])} if 'capacity' in metadata else {}));lease=registry.reserve(out.name,[{'path':str(source),'access':'read'},{'path':str(out),'access':'write'}],ttl_seconds=300,**({'demands':{'slots':1,'memory_bytes':512*1024**2,'disk_bytes':8*1024**2}} if 'capacity' in metadata else {}));token=lease['token'];write('reservation.json',lease)
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(PortablePrimaryTest);ids=[t.id() for t in suite];assert len(ids)==14;write('expected-tests.json',ids);stream=io.StringIO();r=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite);(out/'unittest.log').write_text(stream.getvalue());result={'tests_run':r.testsRun,'expected_ids':ids,'failures':[{'id':t.id(),'traceback':e} for t,e in r.failures],'errors':[{'id':t.id(),'traceback':e} for t,e in r.errors],'skips':[{'id':t.id(),'reason':e} for t,e in r.skipped]};write('result.json',result);assert r.wasSuccessful() and r.testsRun==14 and not r.skipped;passed=True
except BaseException as e:write('exception.json',{'reason':str(e),'traceback':traceback.format_exc()})
finally:
 if token:registry.release(token,note='Completed14 production archive restoration regression checks; no native models or old scripts executed')
 write('source-hashes.json',{p.relative_to(source).as_posix():sha(p) for p in (source/'Scripts/StructTrain/TimeLearner').rglob('*') if p.is_file() and (p.suffix=='.py' or '/tests/fixtures/' in p.as_posix())});write('terminal.json',{'checks_passed':passed,'native_models_executed':0,'whole_plan_complete':False,'scientific_verdict':None});members={}
 with tarfile.open(out/'primary.tar.xz','w:xz',preset=3) as tf:
  for p in sorted(out.iterdir()):
   if p.is_file() and p.name not in ['primary.tar.xz','bundle.json']:
    members[p.name]={'bytes':p.stat().st_size,'sha256':sha(p)};info=tarfile.TarInfo(p.name);info.size=p.stat().st_size
    with p.open('rb') as s:tf.addfile(info,s)
 write('bundle.json',{'checks_passed':passed,'members':members,'archive_bytes':(out/'primary.tar.xz').stat().st_size,'archive_sha256':sha(out/'primary.tar.xz'),'scientific_verdict':None});print('CLOSED',passed,flush=True)
