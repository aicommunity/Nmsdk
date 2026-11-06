from pathlib import Path
import sys,json,subprocess,hashlib,tarfile,sqlite3,re,collections
from xml.etree import ElementTree as ET
base=Path('/media/user/Data/TimeLearnerRefactor');repo=base/'source-attempt-invalid-budget-evidence-a1';parent='a2df1eac50bfb53e5ce6c9220eed8b7da7b5ba0b';source=base/'source-attempt-invalid-budget-baseline-normal-a1';folder=base/'readbacks/s07-attempt-invalid-budget-baseline-native-a1';controller=Path(str(folder)+'-container');prefix='Reports/StructTrain/TimeLearner/s07-attempt-invalid-budget-baseline-native-m40-a1';sys.dont_write_bytecode=True;sys.path.insert(0,str(repo));payloads={};updates={}
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.native_gate import audit_junit
c=sqlite3.connect('file:'+str(base/'resource-reservations.sqlite3')+'?mode=ro',uri=True);metadata=dict(c.execute('SELECT key,value FROM metadata'));c.close();registry=Reservations(base/'resource-reservations.sqlite3',**({'capacity':json.loads(metadata['capacity'])} if 'capacity' in metadata else {}));closed=inspect_worker_dependency(controller,registry,folder.name);assert closed['state']=='ready' and closed['reservation_state']=='released',closed
bundle=json.loads((folder/'bundle.json').read_text());archive=folder/'primary.tar.xz';assert archive.stat().st_size==bundle['archive_bytes'] and hashlib.sha256(archive.read_bytes()).hexdigest()==bundle['archive_sha256'];seen=set()
with tarfile.open(archive,'r:xz') as tf:
 for m in tf:
  assert m.isfile() and m.name not in seen;seen.add(m.name);raw=tf.extractfile(m).read();assert bundle['members'][m.name]=={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
assert seen==set(bundle['members'])
terminal=json.loads((folder/'terminal.json').read_text());assert terminal['original_controller_native23_expected_failures_observed'] is True
runtime=json.loads((folder/'runtime.json').read_text());assert runtime['source_closure']['root']['head']=='7cc21bdd9e0904f8f5052466651e0682f2f1f1a3'
result=json.loads((folder/'result.json').read_text());spec=json.loads((folder/'specification.json').read_text());expected=spec['expected_test_ids'];assert len(expected)==23
assert result['execution']=='process_error' and result['validity']=='valid' and result['assertion_status']=='failed'
assert result['inventory']==audit_junit(folder/'native-result/native.xml',expected)
assert result['inventory']['failed_test_ids']==['NativeLearnedState/ClassicConfiguredN1','NativeLearnedState/BranchConfiguredN0']
owner=json.loads((folder/'native-result/process/owned-process.json').read_text());process=json.loads((folder/'native-result/process/result.json').read_text());loaded=json.loads((folder/'native-result/process/loaded-files.json').read_text())
assert owner['executable_sha256']==runtime['executable']['sha256'] and owner['runtime_fingerprint']==runtime['runtime_fingerprint'] and process['returncode']==1 and process['runtime_provenance']=='loaded_files_captured' and any(r['sha256']==owner['executable_sha256'] for r in loaded)
checks=[]
for case in ET.parse(folder/'native-result/native.xml').getroot().iter('testcase'):
 failures=case.findall('failure')
 if not failures:continue
 assert len(failures)==1 and 'service.Certificate()' in failures[0].text and 'Actual: false' in failures[0].text and 'maximum_sweeps_exhausted' in failures[0].text
 checks.append({'test_id':case.get('classname')+'/'+case.get('name'),'failure_kind':'certificate_expected_after_actual_sweep_budget_exhaustion','original_failure':failures[0].text})
assert len(checks)==2
fixed=base/'readbacks/s07-attempt-invalid-budget-fixed-native-a1'
fixed_closed=inspect_worker_dependency(Path(str(fixed)+'-container'),registry,fixed.name)
assert fixed_closed['state']=='ready' and fixed_closed['reservation_state']=='released',fixed_closed
fixed_spec=json.loads((fixed/'specification.json').read_text());fixed_result=json.loads((fixed/'result.json').read_text());fixed_runtime=json.loads((fixed/'runtime.json').read_text())
assert fixed_spec['expected_test_ids']==expected and fixed_result['inventory']['failed_test_ids']==result['inventory']['failed_test_ids']
assert fixed_runtime['source_closure']['root']['head']==parent
assert runtime['compiler']==fixed_runtime['compiler']
for key in ['CMAKE_BUILD_TYPE','CMAKE_CXX_FLAGS_RELWITHDEBINFO','NMSDK_RESOURCE_ROOT']:
 assert key in runtime['build_flags'] and runtime['build_flags'][key]==fixed_runtime['build_flags'][key],key
fixed_loaded=json.loads((fixed/'native-result/process/loaded-files.json').read_text())
assert {(r['path'],r['sha256']) for r in loaded if r['sha256']!=owner['executable_sha256']}=={(r['path'],r['sha256']) for r in fixed_loaded if r['sha256']!=fixed_runtime['executable']['sha256']}
def contents(root,pattern):return {p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob(pattern) if p.is_file()}
csv_old=contents(folder/'native-result/native','*.csv');csv_new=contents(fixed/'native-result/native','*.csv')
assert csv_old and set(csv_old)==set(csv_new)
assert all(csv_old[n]==csv_new[n] for n in csv_old)
pre_old=contents(folder/'native-result/native','*transport_training_precondition.json');pre_new=contents(fixed/'native-result/native','*transport_training_precondition.json')
assert pre_old and set(pre_old)==set(pre_new) and all(pre_old[n]==pre_new[n] for n in pre_old)
ab={'kind':'timelearner_native_budget_original_fixed_AB','schema_version':1,'baseline_root':runtime['source_closure']['root']['head'],'fixed_root':parent,'exact_same_23_test_ids':expected,'failed_test_ids_on_both':result['inventory']['failed_test_ids'],'both_original_negative_verdicts_preserved':True,'same_compiler_flags_resource_root_and_loaded_shared_files':True,'CSV_files_byte_identical':{n:{'bytes':len(csv_old[n]),'sha256':hashlib.sha256(csv_old[n]).hexdigest()} for n in csv_old},'training_precondition_summaries_byte_identical':{n:hashlib.sha256(pre_old[n]).hexdigest() for n in pre_old},'fixed_fresh_closed_released':fixed_closed,'interpretation':'The two configured precondition assertion failures reproduce on the original controller with byte-identical recorded curves and summaries; this experiment does not attribute them to the budget fix.','whole_plan_complete':False,'scientific_verdict':None}
payloads[prefix+'/native-ab-verification.json']=(json.dumps(ab,indent=2)+'\n').encode()
for p in folder.iterdir():
 if p.is_file() and (p.suffix=='.json' or p.name in ['primary.tar.xz','producer.py']):payloads[prefix+'/'+p.name]=p.read_bytes()
for p in controller.iterdir():
 if p.is_file() and p.suffix=='.json':payloads[prefix+'/controller/'+p.name]=p.read_bytes()
payloads[prefix+'/originals-verification.json']=(json.dumps({'fresh_closed_released':closed,'archive_members_checked':len(seen),'compiled_source_root':'7cc21bdd9e0904f8f5052466651e0682f2f1f1a3','PulseLib':'12d8c8a41c998ae1516496f716a0ae0f3d312b3e','original_cpp_functions_observed':23,'passed':21,'failed':2,'original_failures':checks,'actual_native_owner':owner,'loaded_files':len(loaded),'same_case_fixed_comparison_available':True,'ASan_executed':False,'whole_plan_complete':False,'scientific_verdict':None},indent=2)+'\n').encode();payloads[prefix+'/publisher-source.py']=PUBLISHER_SOURCE.encode()

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
t=tree(git('rev-parse',parent+'^{tree}'),updates);commit=git('-c','user.name=TimeLearner Agent','-c','user.email=timelearner@localhost','commit-tree',t,'-p',parent,data=b'Preserve original native 21 plus 2 and byte-exact fixed controller AB traces\n');git('update-ref','refs/heads/codex/attempt-invalid-budget-baseline-native-m40-a1-evidence',commit,'0'*40);print(json.dumps({'commit':commit,'parent':parent,'repository':str(repo),'members':len(seen),'archive_bytes':bundle['archive_bytes'],'archive_sha256':bundle['archive_sha256'],'native_functions_observed':23,'native_functions_passed':21,'native_functions_failed':2,'byte_identical_CSV_files':len(csv_old),'byte_identical_preconditions':len(pre_old),'origin_published':False}))
