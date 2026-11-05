from pathlib import Path
import json,subprocess,hashlib,tarfile,io,sys
base=Path('/media/user/Data/TimeLearnerRefactor');repo=base/'source-theory-retirement-a1';parent='fe0eb83ed076a65ddf3a3b328213e31669def305';folder=base/'readbacks/s07-joint-asan-owner-readers-a3';controller=Path(str(folder)+'-container');prefix='Reports/StructTrain/TimeLearner/s07-joint-asan-owner-readers-a3';updates={};payloads={};sys.dont_write_bytecode=True;sys.path.insert(0,str(base/'source-integrated-owner-plots-a1'))
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.recognition_owner_replay import audit_case_replay
state=inspect_worker_dependency(controller,Reservations(base/'resource-reservations.sqlite3'),folder.name);assert state['state']=='ready',state
bundle=json.loads((folder/'bundle.json').read_text());raw=(folder/'primary.tar.xz').read_bytes();assert len(raw)==bundle['archive_bytes'] and hashlib.sha256(raw).hexdigest()==bundle['archive_sha256'];seen=set()
with tarfile.open(fileobj=io.BytesIO(raw),mode='r:xz') as tf:
 for member in tf:
  assert member.isfile() and member.name not in seen;seen.add(member.name);value=tf.extractfile(member).read();assert bundle['members'][member.name]=={'bytes':len(value),'sha256':hashlib.sha256(value).hexdigest()}
assert seen==set(bundle['members']) and len(seen)==195
terminal=json.loads((folder/'terminal.json').read_text());assert terminal['ASan_owner8_readers128_passed'] and not terminal['leak_absence_attested'];readers=json.loads((folder/'structured-readers/result.json').read_text());assert readers['assertion_status']=='passed' and readers['executed_tests']==len(readers['expected_test_ids'])==128 and not any(readers[k] for k in ['failures','errors','skipped'])
index=json.loads((folder/'fresh-owner-replay/index.json').read_text());assert index['passed'] and index['execution']=='completed' and len(index['cases'])==8 and index['source_archive_sha256']=='9e13eeaee1700e31b2ff86946b51667bcfa3a508453bc15bb703cbcd1a5d5ef6' and index['origin_evidence_commit']=='fe0eb83ed076a65ddf3a3b328213e31669def305';identities=set();observed=[]
for row in index['cases']:
 assert row['passed'] and row['reason']=='native_import_and_exact_waveform';original=base/'readbacks/s07-native-partition-full-asan-a2/native-result/native'/row['source_filename'];audit_case_replay(original,folder/'fresh-owner-replay');case=folder/'fresh-owner-replay'/row['id'];owner=json.loads((case/'gate/process/owned-process.json').read_text());process=json.loads((case/'gate/process/result.json').read_text());loaded=json.loads((case/'gate/process/loaded-files.json').read_text());key=(owner['boot_id'],owner['pid'],owner['start_ticks']);assert key not in identities;identities.add(key);assert process['returncode']==0 and process['execution']=='completed' and process['runtime_provenance']=='loaded_files_captured' and any('libasan' in item['path'] for item in loaded);observed.append({'case':row['id'],'native_process':owner,'source_model_file':row['source_filename'],'source_file_sha256':row['source_file_sha256'],'exact_waveform_verified':True})
for n in ['primary.tar.xz','bundle.json','terminal.json','reader-source-hashes.json','native304-published-origin.json','reader-suite.json','fixture-bindings.json']:payloads[n]=(folder/n).read_bytes()
payloads['owner-index.json']=(folder/'fresh-owner-replay/index.json').read_bytes();payloads['readers128-result.json']=(folder/'structured-readers/result.json').read_bytes()
for path in controller.iterdir():
 if path.is_file() and path.suffix=='.json':payloads['controller/'+path.name]=path.read_bytes()
payloads['owner-originals-verification.json']=(json.dumps({'unique_native_processes':len(identities),'cases':observed,'readers_executed':128,'scientific_verdict':None},indent=2)+'\n').encode();payloads['fresh-operational-dependency.json']=(json.dumps(state,indent=2)+'\n').encode();payloads['publisher-source.py']=PUBLISHER_SOURCE.encode();payloads['README.ru.md']=b'SDK802/Pulsecc ASan actual fresh owner8 and reader128 passed after published isolated304 prerequisite. Full195-member primary and exact input bindings preserved; actual imported graph and waveform checked by production audit,8 native identities/libasan mappings verified. Shared SDK2e/Pulse12d ASan build is separate and not accepted here. Leak absence/full science/full refactoring not claimed.\n';payloads['SHA256SUMS']=''.join(hashlib.sha256(v).hexdigest()+'  '+n+'\n' for n,v in sorted(payloads.items())).encode()
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
t=tree(git('rev-parse',parent+'^{tree}'),updates);commit=git('-c','user.name=TimeLearner Agent','-c','user.email=timelearner@localhost','commit-tree',t,'-p',parent,data=b'Preserve ASan fresh owner8 and reader128 after complete published304\n');git('update-ref','refs/heads/codex/joint-asan-owner-readers-a3-evidence',commit,'0'*40)
print(json.dumps({'commit':commit,'parent':parent,'repository':str(repo),'archive_members':len(seen),'archive_bytes':bundle['archive_bytes'],'archive_sha256':bundle['archive_sha256'],'native_owners':8,'readers':128,'origin_published':False}))
