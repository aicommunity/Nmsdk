from pathlib import Path
import sys,json,subprocess,hashlib,tarfile,sqlite3,re,collections
from xml.etree import ElementTree as ET
base=Path('/media/user/Data/TimeLearnerRefactor');repo=base/'source-attempt-invalid-budget-evidence-a1';parent='a2df1eac50bfb53e5ce6c9220eed8b7da7b5ba0b';source=base/'source-attempt-invalid-budget-baseline-normal-a1';folder=base/'readbacks/s07-attempt-invalid-budget-baseline-normal-a1';controller=Path(str(folder)+'-container');prefix='Reports/StructTrain/TimeLearner/s07-attempt-invalid-budget-baseline-m40-a1';sys.dont_write_bytecode=True;sys.path.insert(0,str(repo));payloads={};updates={}
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.native_gate import audit_junit
c=sqlite3.connect('file:'+str(base/'resource-reservations.sqlite3')+'?mode=ro',uri=True);metadata=dict(c.execute('SELECT key,value FROM metadata'));c.close();registry=Reservations(base/'resource-reservations.sqlite3',**({'capacity':json.loads(metadata['capacity'])} if 'capacity' in metadata else {}));closed=inspect_worker_dependency(controller,registry,folder.name);assert closed['state']=='ready' and closed['reservation_state']=='released',closed
bundle=json.loads((folder/'bundle.json').read_text());archive=folder/'primary.tar.xz';assert archive.stat().st_size==bundle['archive_bytes'] and hashlib.sha256(archive.read_bytes()).hexdigest()==bundle['archive_sha256'];seen=set()
with tarfile.open(archive,'r:xz') as tf:
 for m in tf:
  assert m.isfile() and m.name not in seen;seen.add(m.name);raw=tf.extractfile(m).read();assert bundle['members'][m.name]=={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
assert seen==set(bundle['members'])
terminal=json.loads((folder/'terminal.json').read_text());assert terminal['build_passed'] and terminal['expected_baseline_failures_observed'] and terminal['native_gates_executed']
result=json.loads((folder/'baseline-verdict.json').read_text());runtime=json.loads((folder/'native-runtime.json').read_text());expected=['TrainingInvalidBudget/'+n for n in ['ClassicN0','ClassicN1','BranchN0','BranchN1']]
assert result['assertion_status']=='failed' and result['validity']=='valid' and result['inventory']==audit_junit(folder/'baseline-native/native.xml',expected)
assert result['inventory']['failed_test_ids']==expected
assert runtime['source_closure']['root']['head']=='7cc21bdd9e0904f8f5052466651e0682f2f1f1a3'
owner=json.loads((folder/'baseline-native/process/owned-process.json').read_text());process=json.loads((folder/'baseline-native/process/result.json').read_text());loaded=json.loads((folder/'baseline-native/process/loaded-files.json').read_text())
assert owner['executable_sha256']==runtime['executable']['sha256'] and owner['runtime_fingerprint']==runtime['runtime_fingerprint'] and process['returncode']==1 and process['runtime_provenance']=='loaded_files_captured' and any(r['sha256']==owner['executable_sha256'] for r in loaded)
header=(source/'Libraries/Nmsdk-PulseLib/Core/TimeLearner/BoundedTraining.h').read_text();enums=re.search(r'enum class TrainingStatus \{([^}]+)\}',header).group(1);values=[s.strip() for s in enums.split(',')];assert values.index('Exact')==2 and values.index('InvalidObservation')==6
cpp=source/'Tests/Integration/Libraries/Test_PulseLib_BoundedTraining.cpp';lines=cpp.read_text().splitlines();diagnostics=[]
for case in ET.parse(folder/'baseline-native/native.xml').getroot().iter('testcase'):
 failures=case.findall('failure');assert len(failures)==8
 combinations=collections.Counter()
 for f in failures:
  text=f.text or '';first=text.splitlines()[0];path,line=first.rsplit(':',1);assert path==str(cpp);statement=lines[int(line)-1]
  trace=re.search(r'scenario=([01]) invalidPreparation=(false|true)',text);assert trace,text
  if 'session.Status()' in text:
   assert 'EXPECT_EQ(session.Status(),TrainingStatus::InvalidObservation)' in statement
   assert '4-byte object <02-00 00-00>' in text and '4-byte object <06-00 00-00>' in text
   kind='exact_instead_of_invalid_observation'
  else:
   assert 'EXPECT_FALSE(session.Certificate())' in statement and 'Actual: true' in text and 'Expected: false' in text
   kind='certificate_present_after_budget_exceeded'
  combinations[(trace.group(1),trace.group(2),kind)]+=1
 assert len(combinations)==8 and set(combinations.values())=={1}
 diagnostics.append({'test_id':case.get('classname')+'/'+case.get('name'),'expected_budget_failures':len(failures),'only_over_budget_scenarios_failed':True,'single_retry_and_zero_budget_controls_have_no_assertion_failures':True})
for p in folder.iterdir():
 if p.is_file() and (p.suffix=='.json' or p.name in ['primary.tar.xz','producer.py']):payloads[prefix+'/'+p.name]=p.read_bytes()
for p in controller.iterdir():
 if p.is_file() and p.suffix=='.json':payloads[prefix+'/controller/'+p.name]=p.read_bytes()
payloads[prefix+'/originals-verification.json']=(json.dumps({'fresh_closed_released':closed,'archive_members_checked':len(seen),'actual_native_owner':owner,'loaded_files':len(loaded),'baseline_source_root':'7cc21bdd9e0904f8f5052466651e0682f2f1f1a3','unchanged_PulseLib':'12d8c8a41c998ae1516496f716a0ae0f3d312b3e','actual_failure_diagnostics':diagnostics,'fixed_controller_pass_attested':False,'whole_plan_complete':False,'scientific_verdict':None},indent=2)+'\n').encode();payloads[prefix+'/publisher-source.py']=PUBLISHER_SOURCE.encode()
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
t=tree(git('rev-parse',parent+'^{tree}'),updates);commit=git('-c','user.name=TimeLearner Agent','-c','user.email=timelearner@localhost','commit-tree',t,'-p',parent,data=b'Preserve original controller Exact results beyond shared invalid-observation budget\n');git('update-ref','refs/heads/codex/attempt-invalid-budget-baseline-m40-a1-evidence',commit,'0'*40);print(json.dumps({'commit':commit,'parent':parent,'repository':str(repo),'members':len(seen),'archive_bytes':bundle['archive_bytes'],'archive_sha256':bundle['archive_sha256'],'expected_original_test_failures':4,'failure_assertions':32,'origin_published':False}))
