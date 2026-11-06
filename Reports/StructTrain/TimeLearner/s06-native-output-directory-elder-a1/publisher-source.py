from pathlib import Path
import sys,json,subprocess,hashlib,tarfile,sqlite3
base=Path('/home/user/timelearner-refactor');repo=base/'source-native-gate-output-a1';parent='642a9c875c5cc4790fbef2854195b184bb1fefdf';folder=base/'readbacks/s06-native-output-directory-a1';controller=Path(str(folder)+'-container');prefix='Reports/StructTrain/TimeLearner/s06-native-output-directory-elder-a1';sys.dont_write_bytecode=True;sys.path.insert(0,str(repo));payloads={};updates={}
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.native_gate import audit_junit
c=sqlite3.connect('file:'+str(base/'resource-reservations.sqlite3')+'?mode=ro',uri=True);metadata=dict(c.execute('SELECT key,value FROM metadata'));c.close();registry=Reservations(base/'resource-reservations.sqlite3',**({'capacity':json.loads(metadata['capacity'])} if 'capacity' in metadata else {}));closed=inspect_worker_dependency(controller,registry,folder.name);assert closed['state']=='ready',closed
bundle=json.loads((folder/'bundle.json').read_text());archive=folder/'primary.tar.xz';assert archive.stat().st_size==bundle['archive_bytes'] and hashlib.sha256(archive.read_bytes()).hexdigest()==bundle['archive_sha256'];seen=set()
with tarfile.open(archive,'r:xz') as tf:
 for m in tf:
  assert m.isfile() and m.name not in seen;seen.add(m.name);raw=tf.extractfile(m).read();assert bundle['members'][m.name]=={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
assert seen==set(bundle['members']);result=json.loads((folder/'result.json').read_text());runtime=json.loads((folder/'runtime.json').read_text());identity='NativeBranchAliasing/CoincidentLabelsExposeOneEffectivePhysicalBank';assert result['assertion_status']=='passed' and result['validity']=='valid' and result['inventory']==audit_junit(folder/'native-result/native.xml',[identity]);owner=json.loads((folder/'native-result/process/owned-process.json').read_text());process=json.loads((folder/'native-result/process/result.json').read_text());loaded=json.loads((folder/'native-result/process/loaded-files.json').read_text());assert owner['executable_sha256']==runtime['executable']['sha256'] and owner['runtime_fingerprint']==runtime['runtime_fingerprint'] and process['returncode']==0 and process['runtime_provenance']=='loaded_files_captured' and any(r['sha256']==owner['executable_sha256'] for r in loaded);readback=json.loads((folder/'native-readback.json').read_text());assert len(readback['two_original_cpp_outputs'])==2 and readback['no_recompiled_binary']
if 'elder'=='m40':assert any('libasan' in r['path'] for r in loaded)
for p in folder.iterdir():
 if p.is_file() and (p.suffix=='.json' or p.name in ['primary.tar.xz','producer.py']):payloads[prefix+'/'+p.name]=p.read_bytes()
for p in controller.iterdir():
 if p.is_file() and p.suffix=='.json':payloads[prefix+'/controller/'+p.name]=p.read_bytes()
payloads[prefix+'/originals-verification.json']=(json.dumps({'fresh_closed_released':closed,'archive_members_checked':len(seen),'actual_native_owner':owner,'loaded_files':len(loaded),'full_asan133_attested':False,'whole_plan_complete':False},indent=2)+'\n').encode();payloads[prefix+'/publisher-source.py']=PUBLISHER_SOURCE.encode()
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
t=tree(git('rev-parse',parent+'^{tree}'),updates);commit=git('-c','user.name=TimeLearner Agent','-c','user.email=timelearner@localhost','commit-tree',t,'-p',parent,data=b'Preserve actual isolated native Branch alias fixture after owned output directory preparation\n');git('update-ref','refs/heads/codex/native-output-elder-a1-evidence',commit,'0'*40);print(json.dumps({'commit':commit,'parent':parent,'repository':str(repo),'members':len(seen),'archive_bytes':bundle['archive_bytes'],'archive_sha256':bundle['archive_sha256'],'origin_published':False}))
