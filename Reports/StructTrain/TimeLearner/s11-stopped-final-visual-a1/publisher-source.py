from pathlib import Path
import sys,json,subprocess,hashlib,tarfile,io,time
base=Path('/media/user/Data/TimeLearnerRefactor');repo=base/'source-stopped-final-diagnostics-a2';parent='297bcbb42105396d83c3eecf52ad98613afaef0f';prefix='Reports/StructTrain/TimeLearner/s11-stopped-final-visual-a1';updates={};payloads={}
sys.path.insert(0,str(repo))
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
folder=base/'readbacks/s11-stopped-final-visual-a1';cache=base/'ReportsCache/stopped-final-visual-a1';controller=Path(str(folder)+'-container');state=inspect_worker_dependency(controller,Reservations(base/'report-reservations.sqlite3'),folder.name);assert state['state']=='ready',state
terminal=json.loads((folder/'terminal.json').read_text());assert terminal['report_and_checks_passed'] and terminal['native_models_executed']==0
coverage=json.loads((folder/'coverage.json').read_text());assert coverage['trials']==32 and coverage['trial_soma_pairs']==48 and coverage['source_members_unchanged']==116
members={}
for path in sorted(folder.iterdir()):
 if path.is_file():members['worker/'+path.name]=path.read_bytes()
for path in sorted((cache/'reports').rglob('*.json')):
 if 'primary' not in path.relative_to(cache/'reports').parts:members['reports/'+path.relative_to(cache/'reports').as_posix()]=path.read_bytes()
for path in sorted((cache/'inputs').rglob('report-spec.json')):members['input-specs/'+path.parent.name+'.json']=path.read_bytes()
buffer=io.BytesIO()
with tarfile.open(fileobj=buffer,mode='w:xz',preset=6) as archive:
 for name,raw in sorted(members.items()):
  info=tarfile.TarInfo(name);info.size=len(raw);info.mtime=0;archive.addfile(info,io.BytesIO(raw))
raw=buffer.getvalue();bundle={'kind':'timelearner_stopped_final_temporal_metadata','schema_version':1,'members':{n:{'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()} for n,v in members.items()},'archive_bytes':len(raw),'archive_sha256':hashlib.sha256(raw).hexdigest(),'native_primary_commit':'d080310f241c994bca1231cbb38a3cb290ca2f36','reader_commit':parent,'full_reports_cache':str(cache/'reports'),'native_models_executed':0,'manual_visual_review_complete':False,'scientific_verdict':None}
payloads['metadata.tar.xz']=raw;payloads['bundle.json']=(json.dumps(bundle,indent=2)+'\n').encode()
for n in ['coverage.json','selection.json','terminal.json','progress.json']:payloads[n]=(folder/n).read_bytes()
selection=json.loads(payloads['selection.json']);assert len(selection['images'])==24
for index,row in enumerate(selection['images']):
 image=cache/row['png'];assert image.resolve().is_relative_to(cache.resolve());value=image.read_bytes();assert hashlib.sha256(value).hexdigest()==row['sha256'];payloads['selected/'+str(index+1).zfill(2)+'.png']=value
for path in controller.iterdir():
 if path.is_file() and path.suffix=='.json':payloads['controller/'+path.name]=path.read_bytes()
payloads['fresh-operational-closure.json']=(json.dumps(state,indent=2)+'\n').encode();payloads['publisher-source.py']=PUBLISHER_SOURCE.encode();payloads['SHA256SUMS']=''.join(hashlib.sha256(v).hexdigest()+'  '+n+'\n' for n,v in sorted(payloads.items())).encode()
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
t=tree(git('rev-parse',parent+'^{tree}'),updates);commit=git('-c','user.name=TimeLearner Agent','-c','user.email=timelearner@localhost','commit-tree',t,'-p',parent,data=b'Preserve actual32 stopped final probes temporal reports and24 selected originals\n');git('update-ref','refs/heads/codex/stopped-final-visual-a1-evidence',commit,'0'*40)
print(json.dumps({'commit':commit,'parent':parent,'repository':str(repo),'files':len(payloads),'archive_members':len(members),'archive_bytes':bundle['archive_bytes'],'archive_sha256':bundle['archive_sha256'],'coverage':coverage,'origin_published':False}))
