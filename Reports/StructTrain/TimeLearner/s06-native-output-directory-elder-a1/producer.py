from pathlib import Path
import os,sys,json,hashlib,threading,tarfile,traceback,sqlite3
base=Path('/home/user/timelearner-refactor');tool=base/'source-native-gate-output-a1';source=base/'source-integrated-acceptance-normal-a1';out=base/'readbacks/s06-native-output-directory-a1';out.mkdir(exist_ok=False);sys.dont_write_bytecode=True;sys.path.insert(0,str(tool));stop=threading.Event();thread=None;registry=None;token=None;passed=False;errors=[]
from Scripts.StructTrain.TimeLearner.native_gate import run_native_gate
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):(out/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
write('owner.json',{'pid':os.getpid(),'start_ticks':Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19],'tool_root':'642a9c875c5cc4790fbef2854195b184bb1fefdf','compiled_root':'2e0618110a9abb48b94f6edc6b63c51f829ec810'});(out/'producer.py').write_bytes(Path(__file__).read_bytes())
try:
 c=sqlite3.connect('file:'+str(base/'resource-reservations.sqlite3')+'?mode=ro',uri=True)
 try:metadata=dict(c.execute('SELECT key,value FROM metadata'))
 finally:c.close()
 registry=Reservations(base/'resource-reservations.sqlite3',**({'capacity':json.loads(metadata['capacity'])} if 'capacity' in metadata else {}));dependency=inspect_worker_dependency(base/'readbacks/s10-pipeline-condition-native-matrix-a2-container',registry,'s10-pipeline-condition-native-matrix-a2');assert dependency['state']=='ready',dependency;write('prior-closure.json',dependency)
 previous=base/'readbacks/s07-integrated-native304-normal-a1/native-runtime.json';runtime=json.loads(previous.read_text());write('runtime.json',runtime)
 reads=[source,tool,Path(runtime['executable']['path']).parent,base/'build-integrated-acceptance-normal-a1',Path(runtime['build_flags']['NMSDK_RESOURCE_ROOT'])];selected=[]
 for p in sorted(set(p.resolve(strict=True) for p in reads),key=lambda p:len(p.parts)):
  if not any(p.is_relative_to(q) for q in selected):selected.append(p)
 lease=registry.reserve(out.name,[{'path':str(out),'access':'write'}]+[{'path':str(p),'access':'read'} for p in selected],ttl_seconds=120,**({'demands':{'slots':1,'memory_bytes':4*1024**3,'disk_bytes':16*1024**2}} if 'capacity' in metadata else {}));token=lease['token'];write('reservation.json',lease)
 def heartbeat():
  while not stop.wait(20):
   try:registry.heartbeat(token,ttl_seconds=120);registry.validate_paths(token)
   except BaseException as e:errors.append(str(e));return
 thread=threading.Thread(target=heartbeat,daemon=True);thread.start();spec={'kind':'timelearner_native_test_gate','schema_version':2,'runtime_manifest':str(out/'runtime.json'),'source_root':str(source),'expected_test_ids':['NativeBranchAliasing/CoincidentLabelsExposeOneEffectivePhysicalBank'],'maximum_wall_seconds':600,'asan_options':'','cooperative_runtime_capture':True};write('specification.json',spec);result=run_native_gate(out/'specification.json',out/'native-result');write('result.json',result);assert result['execution']=='completed' and result['validity']=='valid' and result['assertion_status']=='passed' and result['inventory']['observed']==1 and not errors
 values=[]
 for n in [0,1]:
  p=out/'native-result/native'/('BranchAlias_N'+str(n)+'.json');assert p.is_file();values.append(json.loads(p.read_text()))
 write('native-readback.json',{'two_original_cpp_outputs':values,'same_original_test_body':True,'no_recompiled_binary':True,'scientific_verdict':None});passed=True
except BaseException as e:write('exception.json',{'reason':str(e),'traceback':traceback.format_exc()})
finally:
 stop.set()
 if thread:thread.join(timeout=10)
 write('tool-source-hashes.json',{p.relative_to(tool).as_posix():sha(p) for p in (tool/'Scripts/StructTrain/TimeLearner').rglob('*.py')});write('terminal.json',{'control_passed':passed,'compiled_root':'2e0618110a9abb48b94f6edc6b63c51f829ec810','full_asan133_attested':False,'whole_plan_complete':False,'scientific_verdict':None});members={}
 with tarfile.open(out/'primary.tar.xz','w:xz',preset=3) as tf:
  for p in sorted(out.rglob('*')):
   if p.is_file() and p.name not in ['primary.tar.xz','bundle.json']:
    name=p.relative_to(out).as_posix();members[name]={'bytes':p.stat().st_size,'sha256':sha(p)};i=tarfile.TarInfo(name);i.size=p.stat().st_size
    with p.open('rb') as s:tf.addfile(i,s)
 write('bundle.json',{'control_passed':passed,'members':members,'archive_bytes':(out/'primary.tar.xz').stat().st_size,'archive_sha256':sha(out/'primary.tar.xz')});print('CLOSED',passed,flush=True)
