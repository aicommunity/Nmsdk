from pathlib import Path
import json,subprocess,hashlib,tarfile,sys,io
base=Path('/media/user/Data/TimeLearnerRefactor');repo=base/'source-theory-retirement-a1';parent='b15569b6030b82be92e733562aba9b739aa6def8';updates={};payloads={};sys.dont_write_bytecode=True;sys.path.insert(0,str(base/'source-native-partition-a2'))
from Scripts.StructTrain.TimeLearner.native_gate import audit_junit
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
registry=Reservations(base/'resource-reservations.sqlite3');proofs={}
for label in ['s07-integrated-acceptance-asan-build-a2','s06-integrated-acceptance-asan-focused-a3']:
 folder=base/'readbacks'/label;controller=Path(str(folder)+'-container');prefix='Reports/StructTrain/TimeLearner/'+label
 state=inspect_worker_dependency(controller,registry,label);assert state['state']=='ready',state
 bundle=json.loads((folder/'bundle.json').read_text());archive=(folder/'primary.tar.xz').read_bytes();assert len(archive)==bundle['archive_bytes'] and hashlib.sha256(archive).hexdigest()==bundle['archive_sha256'];seen=set()
 with tarfile.open(fileobj=io.BytesIO(archive),mode='r:xz') as tf:
  for member in tf:
   assert member.isfile() and member.name not in seen and not member.name.startswith('/') and '..' not in Path(member.name).parts;seen.add(member.name);value=tf.extractfile(member).read();assert bundle['members'][member.name]=={'bytes':len(value),'sha256':hashlib.sha256(value).hexdigest()}
 assert seen==set(bundle['members'])
 terminal=json.loads((folder/'terminal.json').read_text());runtime=json.loads((folder/'native-runtime.json').read_text());assert runtime['source_closure']['root']['head']=='2e0618110a9abb48b94f6edc6b63c51f829ec810' and runtime['executable']['sha256']=='051c7cdc4fff8c59efee6a5b7f59c50fabb73492f6881b57755f67271236fae3'
 assert '-fsanitize=address' in runtime['build_flags']['CMAKE_CXX_FLAGS_RELWITHDEBINFO'] and '-fsanitize=address' in runtime['build_flags']['CMAKE_EXE_LINKER_FLAGS']
 cases=[]
 if 'build' in label:
  assert terminal['build_passed'] and terminal['native_models_executed']==0 and not terminal['native_gates_executed']
 else:
  assert terminal['shared_integrated_ASan_focused8_passed'] and terminal['native_cpp_executed'] and not terminal['leak_absence_attested']
  spec=json.loads((folder/'focused-specification.json').read_text());expected=spec['expected_test_ids'];assert len(expected)==len(set(expected))==8 and spec['asan_options']=='detect_leaks=0'
  verdict=json.loads((folder/'focused-verdict.json').read_text());assert verdict['execution']=='completed' and verdict['validity']=='valid' and verdict['assertion_status']=='passed' and verdict['executed_partitions']==8 and audit_junit(folder/'focused-result/native.xml',expected)==verdict['inventory'];identities=set()
  for i,identity in enumerate(expected):
   case=folder/'focused-result/cases'/f'{i:04d}';audit=audit_junit(case/'native.xml',[identity]);assert audit['assertion_status']=='passed';owner=json.loads((case/'process/owned-process.json').read_text());process=json.loads((case/'process/result.json').read_text());loaded=json.loads((case/'process/loaded-files.json').read_text());assert process['execution']=='completed' and process['returncode']==0 and process['runtime_provenance']=='loaded_files_captured';assert owner['executable_sha256']==runtime['executable']['sha256'] and owner['runtime_fingerprint']==runtime['runtime_fingerprint'] and any('libasan' in x['path'] for x in loaded) and any(x['sha256']==owner['executable_sha256'] for x in loaded);key=(owner['boot_id'],owner['pid'],owner['start_ticks']);assert key not in identities;identities.add(key);cases.append({'test_id':identity,'owner':owner,'loaded_files':len(loaded),'libasan_present':True})
  fixtures=json.loads((folder/'fixture-provenance.json').read_text());assert fixtures['all_109_fixture_files_rehashed'] and len(fixtures['cold_live_declaration_restoration']['restored'])==6 and len(fixtures['posttune_saved_state_binding']['members'])==103
 for path in folder.iterdir():
  if path.is_file() and (path.suffix=='.json' or path.name in ['primary.tar.xz','producer.py','CMakeCache.txt']):payloads[prefix+'/'+path.name]=path.read_bytes()
 for path in controller.iterdir():
  if path.is_file() and path.suffix=='.json':payloads[prefix+'/controller/'+path.name]=path.read_bytes()
 proof={'archive_members_checked':len(seen),'archive_bytes':len(archive),'archive_sha256':bundle['archive_sha256'],'fresh_closed_released':state,'cases':cases,'scientific_verdict':None,'whole_plan_complete':False};proofs[label]=proof;payloads[prefix+'/originals-verification.json']=(json.dumps(proof,indent=2)+'\n').encode();payloads[prefix+'/publisher-source.py']=PUBLISHER_SOURCE.encode()
def git(*args,data=None):return subprocess.check_output(['git','-C',str(repo),*args],input=data).decode().strip()
def tree(base_tree,changes):
 entries={}
 if base_tree:
  raw=subprocess.check_output(['git','-C',str(repo),'ls-tree','-z',base_tree])
  for item in raw.split(b'\0'):
   if not item:continue
   header,name=item.split(b'\t',1);mode,kind,sha=header.decode().split();entries[name.decode()]=(mode,kind,sha)
 groups={}
 for path,value in changes.items():
  head,sep,tail=path.partition('/')
  if sep:groups.setdefault(head,{})[tail]=value
  else:entries[head]=value
 for name,sub in groups.items():
  previous=entries.get(name);assert previous is None or previous[1]=='tree'
  entries[name]=('040000','tree',tree(previous[2] if previous else None,sub))
 content=b''.join((entries[n][0].lstrip('0')+' '+n).encode()+b'\0'+bytes.fromhex(entries[n][2]) for n in sorted(entries,key=lambda n:n+('/' if entries[n][1]=='tree' else '')))
 return git('hash-object','-w','-t','tree','--stdin',data=content)






lease=registry.reserve('publish-shared-asan-build-focused-a1',[{'path':str(repo),'access':'write'}],ttl_seconds=120)
try:
 for name,raw in payloads.items():updates[name]=('100644','blob',git('hash-object','-w','--stdin',data=raw))
 t=tree(git('rev-parse',parent+'^{tree}'),updates);commit=git('-c','user.name=TimeLearner Agent','-c','user.email=timelearner@localhost','commit-tree',t,'-p',parent,data=b'Preserve shared SDK2e ASan build and actual focused8 original primary\n');git('update-ref','refs/heads/codex/shared-asan-build-focused-a1-evidence',commit,'0'*40)
finally:registry.release(lease['token'])
print(json.dumps({'commit':commit,'parent':parent,'repository':str(repo),'proofs':{k:{n:v for n,v in d.items() if n not in ['cases','fresh_closed_released']} for k,d in proofs.items()},'origin_published':False}))
