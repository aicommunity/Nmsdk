from pathlib import Path
import json,subprocess,hashlib,tarfile,sys,io,sqlite3
base=Path('/home/user/timelearner-refactor');repo=base/'source-pipeline-condition-a2';parent='d43780822a7b9e2b7c0229c323cda174abc7fce8';folder=base/'readbacks/s10-pipeline-condition-native-a1';controller=Path(str(folder)+'-container');prefix='Reports/StructTrain/TimeLearner/s10-pipeline-condition-native-elder-a1';sys.dont_write_bytecode=True;sys.path.insert(0,str(repo));updates={};payloads={}
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.contained_process import inspect as inspect_contained
from Scripts.StructTrain.TimeLearner.managed_pipeline import audit_pipeline
from Scripts.StructTrain.TimeLearner.pipeline_condition import audit_binding
c=sqlite3.connect('file:'+str(base/'resource-reservations.sqlite3')+'?mode=ro',uri=True)
try:capacity=json.loads(dict(c.execute('SELECT key,value FROM metadata'))['capacity'])
finally:c.close()
state=inspect_worker_dependency(controller,Reservations(base/'resource-reservations.sqlite3',capacity=capacity),folder.name);assert state['state']=='ready',state
bundle=json.loads((folder/'bundle.json').read_text());archive=folder/'primary.tar.xz';assert archive.stat().st_size==bundle['archive_bytes'] and hashlib.sha256(archive.read_bytes()).hexdigest()==bundle['archive_sha256'];seen=set()
with tarfile.open(archive,mode='r:xz') as tf:
 for m in tf:
  assert m.isfile() and m.name not in seen;seen.add(m.name);h=hashlib.sha256();size=0;stream=tf.extractfile(m)
  for part in iter(lambda:stream.read(1024**2),b''):h.update(part);size+=len(part)
  assert bundle['members'][m.name]=={'bytes':size,'sha256':h.hexdigest()}
assert seen==set(bundle['members']) and json.loads((folder/'terminal.json').read_text())['pilot_passed'];identities=set();units=set();cases=[];runtime=json.loads((folder/'runtime.json').read_text())
for name in ['Classic-v1','Branch-v2']:
 case=folder/'cases'/name;root=case/'runs/pipeline';spec=json.loads((case/'job.json').read_text());binding=json.loads((root/'condition-binding.json').read_text());fingerprint=audit_binding(binding,spec,runtime);audit=audit_pipeline(root);assert audit['pipeline_complete'] and audit['condition_declaration_bound'] and audit['condition_fingerprint']==fingerprint and not audit['condition_identity_attested'];result=json.loads((case/'result.json').read_text());assert result['audit']==audit and result['completed_continue_started_no_new_unit'] and result['learned_state_unchanged_on_continue'] and result['condition_binding_unchanged_on_continue'];observed=[]
 for phase in ['train','export','calibrate','evaluate']:
  process=root/'phases'/phase/'process';closure=inspect_contained(process/'contained');assert closure['all_processes_closed'];owner=json.loads((process/'owned-process.json').read_text());execution=json.loads((process/'result.json').read_text());loaded=json.loads((process/'loaded-files.json').read_text());unit=json.loads((process/'contained/owned-unit.json').read_text())['unit'];assert unit not in units;units.add(unit);key=(owner['boot_id'],owner['pid'],owner['start_ticks']);assert key not in identities;identities.add(key);assert owner['executable_sha256']==runtime['executable']['sha256'] and owner['runtime_fingerprint']==runtime['runtime_fingerprint'] and execution['execution']=='completed' and execution['returncode']==0 and execution['ownership_scope']=='bound_cgroup' and execution['all_processes_closed'] and execution['runtime_provenance']=='loaded_files_captured' and any(x['sha256']==owner['executable_sha256'] for x in loaded);observed.append({'phase':phase,'native_process':owner,'unit':unit,'fresh_closure':closure,'loaded_files':len(loaded)})
 c=sqlite3.connect('file:'+str(case/'leases.sqlite3')+'?mode=ro&immutable=1',uri=True)
 try:states=c.execute('SELECT state FROM leases').fetchall();assert states==[('released',)],states
 finally:c.close()
 cases.append({'case':name,'condition_fingerprint':fingerprint,'actual_phase_processes':observed,'portable_pipeline_audit':audit,'managed_case_lease_released':True})
assert len(units)==len(identities)==8
for path in folder.iterdir():
 if path.is_file() and (path.suffix=='.json' or path.name in ['primary.tar.xz','producer.py']):payloads[path.name]=path.read_bytes()
for path in controller.iterdir():
 if path.is_file() and path.suffix=='.json':payloads['controller/'+path.name]=path.read_bytes()
proof={'kind':'timelearner_schema2_condition_pilot_original_verification','cases':cases,'unique_actual_native_phase_processes':8,'archive_members_checked':len(seen),'fresh_closed_released':state,'condition_declaration_bound':True,'full_effective_factor_attestation':False,'whole_plan_complete':False,'scientific_verdict':None};payloads['originals-verification.json']=(json.dumps(proof,indent=2)+'\n').encode();payloads['publisher-source.py']=PUBLISHER_SOURCE.encode()
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
t=tree(git('rev-parse',parent+'^{tree}'),updates);commit=git('-c','user.name=TimeLearner Agent','-c','user.email=timelearner@localhost','commit-tree',t,'-p',parent,data=b'Preserve actual schema2 ConditionSpec Classic Branch cold continuation calibration frozen pilot\n');git('update-ref','refs/heads/codex/pipeline-condition-native-elder-a1-evidence',commit,'0'*40)
print(json.dumps({'commit':commit,'parent':parent,'repository':str(repo),'members':len(seen),'archive_bytes':bundle['archive_bytes'],'archive_sha256':bundle['archive_sha256'],'actual_native_phase_units':8,'origin_published':False}))
