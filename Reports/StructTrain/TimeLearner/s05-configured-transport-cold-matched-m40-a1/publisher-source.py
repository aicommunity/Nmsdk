from pathlib import Path
import sys,json,subprocess,hashlib,tarfile,sqlite3
base=Path('/media/user/Data/TimeLearnerRefactor');repo=base/'source-configured-transport-preconditions-evidence-a1';parent='d41fdb6efbef2c672229df55266be8acabc57ac7';folder=base/'readbacks/s05-configured-transport-cold-matched-a1';controller=Path(str(folder)+'-container');prefix='Reports/StructTrain/TimeLearner/s05-configured-transport-cold-matched-m40-a1';sys.dont_write_bytecode=True;sys.path.insert(0,str(repo));payloads={};updates={}
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.native_gate import audit_junit
c=sqlite3.connect('file:'+str(base/'resource-reservations.sqlite3')+'?mode=ro',uri=True);metadata=dict(c.execute('SELECT key,value FROM metadata'));c.close();registry=Reservations(base/'resource-reservations.sqlite3',**({'capacity':json.loads(metadata['capacity'])} if 'capacity' in metadata else {}));closed=inspect_worker_dependency(controller,registry,folder.name);assert closed['state']=='ready' and closed['reservation_state']=='released',closed
bundle=json.loads((folder/'bundle.json').read_text());archive=folder/'primary.tar.xz';assert archive.stat().st_size==bundle['archive_bytes'] and hashlib.sha256(archive.read_bytes()).hexdigest()==bundle['archive_sha256'];seen=set()
with tarfile.open(archive,'r:xz') as tf:
 for m in tf:
  assert m.isfile() and m.name not in seen;seen.add(m.name);raw=tf.extractfile(m).read();assert bundle['members'][m.name]=={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
assert seen==set(bundle['members']) and json.loads((folder/'terminal.json').read_text())['matched_cold_4_process_controls_passed']
matched=json.loads((folder/'matched-cold-comparison.json').read_text());owners=[];keys=set()
for case in matched['cases']:
 name=case['case'];assert name in ['ClassicConfiguredN1','BranchConfiguredN0']
 for mode in ['old','new']:
  p=folder/name/mode;r=json.loads((p/'result.json').read_text());runtime=json.loads((p/'runtime.json').read_text())
  assert r['validity']=='valid' and r['assertion_status']==('failed' if mode=='old' else 'passed')
  assert r['inventory']==audit_junit(p/'native/native.xml',['NativeLearnedState/'+name])
  owner=json.loads((p/'native/process/owned-process.json').read_text());process=json.loads((p/'native/process/result.json').read_text());loaded=json.loads((p/'native/process/loaded-files.json').read_text())
  assert owner['executable_sha256']==runtime['executable']['sha256'] and owner['runtime_fingerprint']==runtime['runtime_fingerprint'] and process['returncode']==(1 if mode=='old' else 0) and process['runtime_provenance']=='loaded_files_captured' and any(x['sha256']==owner['executable_sha256'] for x in loaded)
  key=(owner['boot_id'],owner['pid'],owner['start_ticks']);assert key not in keys;keys.add(key);owners.append({'case':name,'mode':mode,'actual_native_owner':owner,'loaded_files':len(loaded)})
  for n,value in case['cold_CSV_byte_identical'].items():
   raw=(p/'native/native'/n).read_bytes();assert value=={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
  for n,value in case['cold_precondition_byte_identical'].items():assert hashlib.sha256((p/'native/native'/n).read_bytes()).hexdigest()==value
for p in folder.iterdir():
 if p.is_file() and (p.suffix=='.json' or p.name in ['primary.tar.xz','producer.py']):payloads[prefix+'/'+p.name]=p.read_bytes()
for p in controller.iterdir():
 if p.is_file() and p.suffix=='.json':payloads[prefix+'/controller/'+p.name]=p.read_bytes()
payloads[prefix+'/originals-verification.json']=(json.dumps({'fresh_closed_released':closed,'archive_members_checked':len(seen),'actual_native_owners':owners,'four_fresh_native_processes':True,'cold_csv_byte_identical_count':sum(len(c['cold_CSV_byte_identical']) for c in matched['cases']),'cold_preconditions_byte_identical_count':sum(len(c['cold_precondition_byte_identical']) for c in matched['cases']),'absolute_timestamps_compared_without_translation':True,'original_two_failed_verdicts_preserved':True,'new_two_diagnostic_transport_controls_passed':True,'ASan_executed':False,'whole_plan_complete':False,'scientific_verdict':None},indent=2)+'\n').encode();payloads[prefix+'/publisher-source.py']=PUBLISHER_SOURCE.encode()
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
t=tree(git('rev-parse',parent+'^{tree}'),updates);commit=git('-c','user.name=TimeLearner Agent','-c','user.email=timelearner@localhost','commit-tree',t,'-p',parent,data=b'Preserve isolated configured cold conditions before and after transport expectation repair\n');git('update-ref','refs/heads/codex/configured-transport-cold-matched-m40-a1-evidence',commit,'0'*40);print(json.dumps({'commit':commit,'parent':parent,'repository':str(repo),'members':len(seen),'archive_bytes':bundle['archive_bytes'],'archive_sha256':bundle['archive_sha256'],'actual_native_processes':4,'matched_cold_csv_files':sum(len(c['cold_CSV_byte_identical']) for c in matched['cases']),'origin_published':False}))
