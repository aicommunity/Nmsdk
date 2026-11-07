from pathlib import Path
import sys,json,subprocess,hashlib,tarfile,sqlite3,re,collections
from xml.etree import ElementTree as ET
base=Path('/media/user/Data/TimeLearnerRefactor');repo=base/'source-configured-transport-preconditions-evidence-a1';parent='d41fdb6efbef2c672229df55266be8acabc57ac7';source=base/'source-configured-transport-preconditions-normal-a1';folder=base/'readbacks/s07-configured-transport-preconditions-normal-a1';controller=Path(str(folder)+'-container');prefix='Reports/StructTrain/TimeLearner/s05-configured-transport-preconditions-m40-a1';sys.dont_write_bytecode=True;sys.path.insert(0,str(repo));payloads={};updates={}
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.native_gate import audit_junit
c=sqlite3.connect('file:'+str(base/'resource-reservations.sqlite3')+'?mode=ro',uri=True);metadata=dict(c.execute('SELECT key,value FROM metadata'));c.close();registry=Reservations(base/'resource-reservations.sqlite3',**({'capacity':json.loads(metadata['capacity'])} if 'capacity' in metadata else {}));closed=inspect_worker_dependency(controller,registry,folder.name);assert closed['state']=='ready' and closed['reservation_state']=='released',closed
bundle=json.loads((folder/'bundle.json').read_text());archive=folder/'primary.tar.xz';assert archive.stat().st_size==bundle['archive_bytes'] and hashlib.sha256(archive.read_bytes()).hexdigest()==bundle['archive_sha256'];seen=set()
with tarfile.open(archive,'r:xz') as tf:
 for m in tf:
  assert m.isfile() and m.name not in seen;seen.add(m.name);raw=tf.extractfile(m).read();assert bundle['members'][m.name]=={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
assert seen==set(bundle['members'])
terminal=json.loads((folder/'terminal.json').read_text());assert terminal['build_passed'] and terminal['configured_transport25_passed'] and terminal['native_gates_executed']
runtime=json.loads((folder/'native-runtime.json').read_text());assert runtime['source_closure']['root']['head']==parent
result=json.loads((folder/'transport-verdict.json').read_text());spec=json.loads((folder/'transport-gate-specification.json').read_text());expected=spec['expected_test_ids'];assert len(expected)==25
assert result['execution']=='completed' and result['validity']=='valid' and result['assertion_status']=='passed'
assert result['inventory']==audit_junit(folder/'native25/native.xml',expected) and result['inventory']['failed_test_ids']==[]
owner=json.loads((folder/'native25/process/owned-process.json').read_text());process=json.loads((folder/'native25/process/result.json').read_text());loaded=json.loads((folder/'native25/process/loaded-files.json').read_text())
assert owner['executable_sha256']==runtime['executable']['sha256'] and owner['runtime_fingerprint']==runtime['runtime_fingerprint'] and process['returncode']==0 and process['runtime_provenance']=='loaded_files_captured' and any(r['sha256']==owner['executable_sha256'] for r in loaded)
# A new criterion version cannot retroactively change the two old failed runs.
previous=base/'readbacks/s07-attempt-invalid-budget-fixed-native-a1';old=json.loads((previous/'result.json').read_text());assert old['assertion_status']=='failed' and len(old['inventory']['failed_test_ids'])==2
old_csv={p.relative_to(previous/'native-result/native').as_posix():p for p in (previous/'native-result/native').rglob('*.csv')}
new_root=folder/'native25/native';unchanged={};different=[];missing=[]
for name,path in old_csv.items():
 new=new_root/name
 if not new.is_file():missing.append(name)
 elif path.read_bytes()!=new.read_bytes():different.append(name)
 else:unchanged[name]={'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
comparison={'prior_23_original_verdict':'21 passed / 2 failed','new_25_criterion_version':'two stopped diagnostic expectations; two additional explicit-0.2 completed controls','prior_csv_files':len(old_csv),'unchanged_prior_csv':unchanged,'different_prior_csv':different,'missing_prior_csv':missing,'scientific_verdict':None}
payloads[prefix+'/cold-evidence-comparison.json']=(json.dumps(comparison,indent=2)+'\n').encode()
for p in folder.iterdir():
 if p.is_file() and (p.suffix=='.json' or p.name in ['primary.tar.xz','producer.py']):payloads[prefix+'/'+p.name]=p.read_bytes()
for p in controller.iterdir():
 if p.is_file() and p.suffix=='.json':payloads[prefix+'/controller/'+p.name]=p.read_bytes()
payloads[prefix+'/originals-verification.json']=(json.dumps({'fresh_closed_released':closed,'archive_members_checked':len(seen),'compiled_source_root':parent,'PulseLib':'2c7e0144a902795cb6287ee677cff5aa08998847','original_cpp_functions_observed':25,'passed':25,'failed':0,'actual_native_owner':owner,'loaded_files':len(loaded),'old_negative_23_case_verdict_preserved':True,'new_candidate_recovery_mode_tested':False,'ASan_executed':False,'whole_plan_complete':False,'scientific_verdict':None},indent=2)+'\n').encode();payloads[prefix+'/publisher-source.py']=PUBLISHER_SOURCE.encode()

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







for name,raw in payloads.items():updates[name]=('100644','blob',git('hash-object','-w','--stdin',data=raw))
t=tree(git('rev-parse',parent+'^{tree}'),updates);commit=git('-c','user.name=TimeLearner Agent','-c','user.email=timelearner@localhost','commit-tree',t,'-p',parent,data=b'Preserve separate configured diagnostic and completed transport 25-case native evidence\n');git('update-ref','refs/heads/codex/configured-transport-preconditions-m40-a1-evidence',commit,'0'*40);print(json.dumps({'commit':commit,'parent':parent,'repository':str(repo),'members':len(seen),'archive_bytes':bundle['archive_bytes'],'archive_sha256':bundle['archive_sha256'],'native_functions_observed':25,'native_functions_passed':25,'old_csv_files_unchanged':len(unchanged),'old_csv_files_different':len(different),'old_csv_files_missing':len(missing),'origin_published':False}))
