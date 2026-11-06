from pathlib import Path
import json,subprocess,hashlib,tarfile,sys,io,sqlite3
base=Path('/home/user/timelearner-refactor');repo=base/'source-asymrm-driver-retirement-a1';parent='f8ef0f2187f30cf18eed12af8ae3a0de98aee1e9';label='s07-integrated-native304-normal-a1';prefix='Reports/StructTrain/TimeLearner/'+label;folder=base/'readbacks'/label;controller=Path(str(folder)+'-container');updates={};payloads={};sys.dont_write_bytecode=True
sys.path.insert(0,str(base/'source-publication-lock-recovery-a2'))
from Scripts.StructTrain.TimeLearner.native_gate import audit_junit
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
connection=sqlite3.connect('file:'+str(base/'resource-reservations.sqlite3')+'?mode=ro',uri=True);capacity=json.loads(dict(connection.execute('SELECT key,value FROM metadata'))['capacity']);connection.close();state=inspect_worker_dependency(controller,Reservations(base/'resource-reservations.sqlite3',capacity=capacity),label);assert state['state']=='ready',state
bundle=json.loads((folder/'bundle.json').read_text());archive=folder/'primary.tar.xz';assert archive.stat().st_size==bundle['archive_bytes'] and hashlib.sha256(archive.read_bytes()).hexdigest()==bundle['archive_sha256'];seen=set()
with tarfile.open(archive,mode='r:xz') as tf:
 for member in tf:
  assert member.isfile() and member.name not in seen and not member.name.startswith('/') and '..' not in Path(member.name).parts;seen.add(member.name);stream=tf.extractfile(member);h=hashlib.sha256();size=0
  for block in iter(lambda:stream.read(1024**2),b''):h.update(block);size+=len(block)
  assert bundle['members'][member.name]=={'bytes':size,'sha256':h.hexdigest()}
assert seen==set(bundle['members'])
terminal=json.loads((folder/'terminal.json').read_text());assert terminal['native304_normal_passed'];runtime=json.loads((folder/'native-runtime.json').read_text());spec=json.loads((folder/'native-specification.json').read_text());expected=spec['expected_test_ids'];assert len(expected)==len(set(expected))==304;assert runtime['source_closure']['root']['head']=='2e0618110a9abb48b94f6edc6b63c51f829ec810'
verdict=json.loads((folder/'native-verdict.json').read_text());assert verdict['execution']=='completed' and verdict['validity']=='valid' and verdict['assertion_status']=='passed';inventory=audit_junit(folder/'native-result/native.xml',expected);assert inventory==verdict['inventory']
process=json.loads((folder/'native-result/process/result.json').read_text());owner=json.loads((folder/'native-result/process/owned-process.json').read_text());loaded=json.loads((folder/'native-result/process/loaded-files.json').read_text());assert process['execution']=='completed' and process['returncode']==0 and process['runtime_provenance']=='loaded_files_captured';assert owner['executable_sha256']==runtime['executable']['sha256']=='bcc51673ce59f1605567e7d8c998e6785ab978e0ff33c82aa116af39f52c9291' and owner['runtime_fingerprint']==runtime['runtime_fingerprint'] and any(item['sha256']==owner['executable_sha256'] for item in loaded)
assert not (folder/'disk-cancellation.json').exists() and not (folder/'exception.json').exists() and not (folder/'archive-exception.json').exists()
memory=json.loads((folder/'memory-before-archive.json').read_text());events=dict(line.split() for line in memory['events'].splitlines());assert all(int(events[k])==0 for k in ['max','oom','oom_kill'])
for path in folder.iterdir():
 if path.is_file() and (path.suffix=='.json' or path.name in ['primary.tar.xz','producer.py']):payloads[path.name]=path.read_bytes()
for path in controller.iterdir():
 if path.is_file() and path.suffix=='.json':payloads['controller/'+path.name]=path.read_bytes()
proof={'kind':'timelearner_native304_normal_original_verification','schema_version':1,'inventory':inventory,'native_process':owner,'process_result':process,'loaded_files_checked':len(loaded),'archive_members_checked':len(seen),'monolithic_native_batch':True,'fresh_operational_state':state,'whole_plan_complete':False,'scientific_verdict':None};payloads['originals-verification.json']=(json.dumps(proof,indent=2)+'\n').encode();payloads['fresh-operational-dependency.json']=(json.dumps(state,indent=2)+'\n').encode();payloads['publisher-source.py']=PUBLISHER_SOURCE.encode();payloads['README.ru.md']=b'SDK2e/Pulse12d full monolithic normal304 completed. All declared original JUnit IDs, native process/runtime and full primary checked. Not scientific classification or whole-plan completion. ASan is separate.\n';payloads['SHA256SUMS']=''.join(hashlib.sha256(v).hexdigest()+'  '+n+'\n' for n,v in sorted(payloads.items())).encode()
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






for name,raw in payloads.items():updates[prefix+'/'+name]=('100644','blob',git('hash-object','-w','--stdin',data=raw))
t=tree(git('rev-parse',parent+'^{tree}'),updates);commit=git('-c','user.name=TimeLearner Agent','-c','user.email=timelearner@localhost','commit-tree',t,'-p',parent,data=b'Preserve shared SDK2e full monolithic normal304 primary and native identity\n');git('update-ref','refs/heads/codex/integrated-native304-normal-a1-evidence',commit,'0'*40)
print(json.dumps({'commit':commit,'parent':parent,'repository':str(repo),'members':len(seen),'archive_bytes':bundle['archive_bytes'],'archive_sha256':bundle['archive_sha256'],'native_wall_seconds':process['wall_seconds'],'origin_published':False}))
