from pathlib import Path
import json,subprocess,hashlib,tarfile,sys,io,xml.etree.ElementTree as ET
base=Path('/media/user/Data/TimeLearnerRefactor');repo=base/'source-theory-retirement-a1';parent='523e5d35d46619c4cf86b3482142905925d79ead';label='s07-native-partition-full-asan-a2';prefix='Reports/StructTrain/TimeLearner/s07-native-partition-full-asan-a2';folder=base/'readbacks'/label;controller=Path(str(folder)+'-container');updates={};payloads={};sys.dont_write_bytecode=True
sys.path.insert(0,str(base/'source-native-partition-a2'))
from Scripts.StructTrain.TimeLearner.native_gate import audit_junit
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
state=inspect_worker_dependency(controller,Reservations(base/'resource-reservations.sqlite3'),folder.name);assert state['state']=='ready',state
bundle=json.loads((folder/'bundle.json').read_text());archive=(folder/'primary.tar.xz').read_bytes();assert len(archive)==bundle['archive_bytes'] and hashlib.sha256(archive).hexdigest()==bundle['archive_sha256'];seen=set()
with tarfile.open(fileobj=io.BytesIO(archive),mode='r:xz') as tf:
 for member in tf:
  assert member.isfile() and member.name not in seen;seen.add(member.name);stream=tf.extractfile(member);h=hashlib.sha256();size=0
  for block in iter(lambda:stream.read(1024**2),b''):h.update(block);size+=len(block)
  assert bundle['members'][member.name]=={'bytes':size,'sha256':h.hexdigest()}
assert seen==set(bundle['members']) and len(seen)==12095
terminal=json.loads((folder/'terminal.json').read_text());assert terminal['native304_asan_passed'] and not terminal['leak_absence_attested'];runtime=json.loads((folder/'native-runtime.json').read_text());spec=json.loads((folder/'native-specification.json').read_text());expected=spec['expected_test_ids'];assert len(expected)==len(set(expected))==304 and spec['asan_options']=='detect_leaks=0';assert runtime['source_closure']['root']['head']=='8021301e894368aefd045f9d77274fcce9f60245'
result=json.loads((folder/'native-verdict.json').read_text());assert result['execution']=='completed' and result['validity']=='valid' and result['assertion_status']=='passed' and result['executed_partitions']==result['inventory']['observed']==304
aggregate=audit_junit(folder/'native-result/native.xml',expected);assert aggregate==result['inventory'];owners=set();originals=[]
for index,identity in enumerate(expected):
 case=folder/'native-result/cases'/f'{index:04d}';verdict=json.loads((case/'result.json').read_text());inventory=audit_junit(case/'native.xml',[identity]);assert inventory==verdict['inventory'] and verdict['assertion_status']=='passed' and verdict['validity']=='valid'
 process=json.loads((case/'process/result.json').read_text());owner=json.loads((case/'process/owned-process.json').read_text());loaded=json.loads((case/'process/loaded-files.json').read_text());assert process['execution']=='completed' and process['returncode']==0 and process['runtime_provenance']=='loaded_files_captured';assert owner['executable_sha256']==runtime['executable']['sha256'] and owner['runtime_fingerprint']==runtime['runtime_fingerprint'];key=(owner['boot_id'],owner['pid'],owner['start_ticks']);assert key not in owners;owners.add(key);assert any('libasan' in item['path'] for item in loaded);assert any(item['sha256']==owner['executable_sha256'] for item in loaded)
 stderr=(case/'process/stderr.log').read_bytes();assert b'ERROR: AddressSanitizer' not in stderr and b'SUMMARY: AddressSanitizer' not in stderr
 originals.append({'test_id':identity,'native_process':owner,'junit_sha256':hashlib.sha256((case/'native.xml').read_bytes()).hexdigest(),'loaded_maps_files':len(loaded),'libasan_mapping_present':True})
assert not (folder/'native-result/process/result.json').exists()
projection=json.loads((folder/'native-result/native-projection.json').read_text());assert projection
for name,row in projection.items():
 target=folder/'native-result/native'/name;assert target.resolve().is_relative_to((folder/'native-result/native').resolve());assert target.stat().st_size==row['content']['bytes'] and hashlib.sha256(target.read_bytes()).hexdigest()==row['content']['sha256']
 for origin in row['sources']:assert bundle['members']['native-result/'+origin]==row['content']
memory=json.loads((folder/'native-memory-result.json').read_text());assert memory['cgroup_after_native']['memory.max']==42*1024**3 and all(memory['cgroup_after_native']['events'][k]==0 for k in ['max','oom','oom_kill'])
for path in folder.iterdir():
 if path.is_file() and (path.suffix=='.json' or path.name in ['primary.tar.xz','producer.py']):payloads[path.name]=path.read_bytes()
for path in controller.iterdir():
 if path.is_file() and path.suffix=='.json':payloads['controller/'+path.name]=path.read_bytes()
proof={'kind':'timelearner_native304_original_partition_verification','schema_version':1,'independent_original_junits':304,'unique_process_identities':len(owners),'cases':originals,'aggregate_matches_original_inventory':True,'native_projection_files_verified':len(projection),'no_fabricated_aggregate_process_result':True,'archive_members_verified':len(seen),'fresh_operational_state':state,'leak_absence_attested':False,'whole_plan_complete':False,'scientific_verdict':None};payloads['originals-verification.json']=(json.dumps(proof,indent=2)+'\n').encode();payloads['fresh-operational-dependency.json']=(json.dumps(state,indent=2)+'\n').encode();payloads['publisher-source.py']=PUBLISHER_SOURCE.encode();payloads['README.ru.md']=b'Actual isolated ASan304 completed on SDK802/Pulsecc97149c. Every original case JUnit, native process identity, loaded executable/libasan mapping and unchanged projection validated. Full12095-member primary preserved. Owner8/readers128, shared SDK2e ASan gates and full scientific/refactoring acceptance remain separate. Leak detection disabled.\n';payloads['SHA256SUMS']=''.join(hashlib.sha256(v).hexdigest()+'  '+n+'\n' for n,v in sorted(payloads.items())).encode()
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
t=tree(git('rev-parse',parent+'^{tree}'),updates);commit=git('-c','user.name=TimeLearner Agent','-c','user.email=timelearner@localhost','commit-tree',t,'-p',parent,data=b'Preserve full isolated ASan304 original processes JUnits runtime and primary\n');git('update-ref','refs/heads/codex/native-partition-full-asan-a2-evidence',commit,'0'*40)
print(json.dumps({'commit':commit,'parent':parent,'repository':str(repo),'files':len(payloads),'members':len(seen),'archive_bytes':bundle['archive_bytes'],'archive_sha256':bundle['archive_sha256'],'memory_peak':memory['cgroup_after_native']['memory.peak'],'wall_seconds':result['wall_seconds'],'origin_published':False}))
