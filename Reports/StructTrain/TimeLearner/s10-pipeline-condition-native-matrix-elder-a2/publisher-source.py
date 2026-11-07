from pathlib import Path
import sys,json,subprocess,hashlib,tarfile,sqlite3
base=Path('/home/user/timelearner-refactor');repo=base/'source-pipeline-condition-matrix-a1';parent='83a82844a6792e23f39106d1d3f41e8638920077';folder=base/'readbacks/s10-pipeline-condition-native-matrix-a2';controller=Path(str(folder)+'-container');prefix='Reports/StructTrain/TimeLearner/s10-pipeline-condition-native-matrix-elder-a2';sys.dont_write_bytecode=True;sys.path.insert(0,str(repo));payloads={};updates={}
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.contained_process import inspect as inspect_contained
from Scripts.StructTrain.TimeLearner.pipeline_condition import audit_binding
c=sqlite3.connect('file:'+str(base/'resource-reservations.sqlite3')+'?mode=ro',uri=True);capacity=json.loads(dict(c.execute('SELECT key,value FROM metadata'))['capacity']);c.close();registry=Reservations(base/'resource-reservations.sqlite3',capacity=capacity);closed=inspect_worker_dependency(controller,registry,folder.name);assert closed['state']=='ready',closed
bundle=json.loads((folder/'bundle.json').read_text());archive=folder/'primary.tar.xz';h=hashlib.sha256()
with archive.open('rb') as s:
 for b in iter(lambda:s.read(1024**2),b''):h.update(b)
assert archive.stat().st_size==bundle['archive_bytes'] and h.hexdigest()==bundle['archive_sha256'];seen=set()
with tarfile.open(archive,'r:xz') as tf:
 for m in tf:
  assert m.isfile() and m.name not in seen;seen.add(m.name);h=hashlib.sha256();size=0
  with tf.extractfile(m) as s:
   for b in iter(lambda:s.read(1024**2),b''):h.update(b);size+=len(b)
  assert bundle['members'][m.name]=={'bytes':size,'sha256':h.hexdigest()}
assert seen==set(bundle['members']) and json.loads((folder/'terminal.json').read_text())['matrix_passed'];runtime=json.loads((folder/'runtime.json').read_text());assert runtime['executable']['sha256']=='b2d98c8f85be0ff5d87769ddd4285bbc2ee2fc8b39609d2bd4833149865c5153';suite_results=[]
for version in [1,2]:
 r=json.loads((folder/('suite-schema'+str(version)+'-result.json')).read_text());assert r['tests_run']==len(r['declared_ids'])==len(set(r['declared_ids']))==8 and not any(r[k] for k in ['failures','errors','skips']);suite_results.append(r)
comparison=json.loads((folder/'schema-comparison.json').read_text());assert comparison['actual_distinct_native_phase_units']==40 and len(comparison['cases'])==8 and comparison['same_compiled_runtime'] and not comparison['independent_scientific_repetitions'];units=set();identities=set();processes=[];compared_files=0
for row in comparison['cases']:
 for version in [1,2]:
  case=folder/'suites'/('schema'+str(version))/row['case'];root=case/'runs/pipeline'
  if version==2:
   binding=json.loads((root/'condition-binding.json').read_text());assert audit_binding(binding,json.loads((case/'pipeline-job.json').read_text()),runtime)==row['condition_fingerprint']
  actual_csv={p.relative_to(root).as_posix():{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in root.rglob('*.csv')};assert actual_csv==row['byte_identical_csvs'];compared_files+=len(actual_csv)
  for phase in (root/'phases').iterdir():
   p=phase/'process';state=inspect_contained(p/'contained');assert state['all_processes_closed'];unit=json.loads((p/'contained/owned-unit.json').read_text())['unit'];owner=json.loads((p/'owned-process.json').read_text());execution=json.loads((p/'result.json').read_text());loaded=json.loads((p/'loaded-files.json').read_text());key=(owner['boot_id'],owner['pid'],owner['start_ticks']);assert unit not in units and key not in identities;units.add(unit);identities.add(key);assert owner['executable_sha256']==runtime['executable']['sha256'] and owner['runtime_fingerprint']==runtime['runtime_fingerprint'] and execution['runtime_provenance']=='loaded_files_captured' and execution['ownership_scope']=='bound_cgroup' and execution['all_processes_closed'] and execution['returncode'] in [0,2] and any(x['sha256']==owner['executable_sha256'] for x in loaded);processes.append({'case':row['case'],'schema':version,'phase':phase.name,'owner':owner,'process_result':execution,'fresh_closure':state})
  c=sqlite3.connect('file:'+str(case/'leases.sqlite3')+'?mode=ro&immutable=1',uri=True)
  try:assert c.execute('SELECT state FROM leases').fetchall()==[('released',)]
  finally:c.close()
assert len(units)==len(identities)==40
for p in folder.iterdir():
 if p.is_file() and (p.suffix=='.json' or p.name in ['primary.tar.xz','producer.py']):payloads[prefix+'/'+p.name]=p.read_bytes()
for p in controller.iterdir():
 if p.is_file() and p.suffix=='.json':payloads[prefix+'/controller/'+p.name]=p.read_bytes()
failed=base/'readbacks/s10-pipeline-condition-native-matrix-a1';assert json.loads((failed/'terminal.json').read_text())['matrix_passed'] is False and not list(failed.glob('suites/*/*/runs/pipeline/phases/*/process/owned-process.json'))
for p in failed.iterdir():
 if p.is_file() and (p.suffix=='.json' or p.name in ['primary.tar.xz','producer.py']):payloads[prefix+'/previous-a1/'+p.name]=p.read_bytes()
proof={'kind':'timelearner_full_coordinator_original_verification','fresh_closed_released':closed,'archive_members_checked':len(seen),'native_phase_units':40,'actual_original_processes':processes,'suite_results':suite_results,'csv_files_rehashed_across_schemas':compared_files,'full_effective_factor_attestation':False,'whole_plan_complete':False};payloads[prefix+'/originals-verification.json']=(json.dumps(proof,indent=2)+'\n').encode();payloads[prefix+'/publisher-source.py']=PUBLISHER_SOURCE.encode()
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







for name,raw in payloads.items():updates[name]=('100644','blob',git('hash-object','w' if False else '-w','--stdin',data=raw))
t=tree(git('rev-parse',parent+'^{tree}'),updates);commit=git('-c','user.name=TimeLearner Agent','-c','user.email=timelearner@localhost','commit-tree',t,'-p',parent,data=b'Preserve complete actual schema1 schema2 coordinator sixteen tests forty native phases\n');git('update-ref','refs/heads/codex/pipeline-condition-native-matrix-elder-a2-evidence',commit,'0'*40);print(json.dumps({'commit':commit,'parent':parent,'repository':str(repo),'members':len(seen),'archive_bytes':bundle['archive_bytes'],'archive_sha256':bundle['archive_sha256'],'native_phases':40,'csv_files_rehashed':compared_files,'origin_published':False}))
