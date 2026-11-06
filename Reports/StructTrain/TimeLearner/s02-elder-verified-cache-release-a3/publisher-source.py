from pathlib import Path
import os,sys,json,subprocess,hashlib,tarfile,io,sqlite3
base=Path('/home/user/timelearner-refactor');repo=base/'source-asymrm-driver-retirement-a1';parent='617d80919a5cbb6c38ac0d56188243d8bf66a801';prefix='Reports/StructTrain/TimeLearner/s02-elder-verified-cache-release-a3';updates={};payloads={};states={};members={};sys.dont_write_bytecode=True;sys.path.insert(0,str(base/'source-publication-lock-recovery-a2'))
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
c=sqlite3.connect('file:'+str(base/'resource-reservations.sqlite3')+'?mode=ro',uri=True)
try:metadata=dict(c.execute('SELECT key,value FROM metadata'))
finally:c.close()
registry=Reservations(base/'resource-reservations.sqlite3',capacity=json.loads(metadata['capacity']))
for attempt,passed in [('a1',False),('a2',False),('a3',True)]:
 folder=base/('readbacks/s02-elder-verified-cache-release-'+attempt);controller=Path(str(folder)+'-container');state=inspect_worker_dependency(controller,registry,folder.name);assert state['state']=='ready',state;states[attempt]=state
 terminal=json.loads((folder/'terminal.json').read_text());assert terminal['verified_cache_release_passed'] is passed and terminal['native_models_executed']==0
 if not passed:assert terminal['already_deleted']==0
 for path in folder.iterdir():
  if path.is_file():members[attempt+'/'+path.name]=path.read_bytes()
 for path in controller.iterdir():
  if path.is_file() and path.suffix=='.json':payloads['controller-'+attempt+'/'+path.name]=path.read_bytes()
folder=base/'readbacks/s02-elder-verified-cache-release-a3';plan=json.loads((folder/'plan.json').read_text());result=json.loads((folder/'result.json').read_text());deleted=[json.loads(line) for line in (folder/'deleted.jsonl').read_text().splitlines()];assert len(plan['files'])==len(deleted)==result['deleted_files']==5159 and result['logical_bytes_removed']==1788657942
for wanted,actual in zip(plan['files'],deleted):
 assert all(wanted[k]==actual[k] for k in ['path','bytes','sha256']) and not Path(actual['path']).exists()
archive=Path(plan['archive_preserved']);assert archive.is_file();assert hashlib.sha256(archive.read_bytes()).hexdigest()==plan['archive_sha256']=='e0b4dbc2ba7f34f1f0579b19309240842c7d31c0a1624656f61010d1fae2f94c'
buffer=io.BytesIO()
with tarfile.open(fileobj=buffer,mode='w:xz',preset=3) as tf:
 for name,raw in sorted(members.items()):
  info=tarfile.TarInfo(name);info.size=len(raw);tf.addfile(info,io.BytesIO(raw))
raw=buffer.getvalue();bundle={'kind':'timelearner_verified_duplicate_and_object_cache_release','schema_version':1,'members':{n:{'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()} for n,v in members.items()},'archive_bytes':len(raw),'archive_sha256':hashlib.sha256(raw).hexdigest(),'published_original_data_commit':plan['published_data_commit'],'native_models_executed':0,'scientific_verdict':None};payloads['primary.tar.xz']=raw;payloads['bundle.json']=(json.dumps(bundle,indent=2)+'\n').encode();payloads['result.json']=(folder/'result.json').read_bytes();payloads['process-scan-exclusions.json']=(folder/'process-scan-exclusions.json').read_bytes();payloads['fresh-operational-closures.json']=(json.dumps(states,indent=2)+'\n').encode();payloads['publisher-source.py']=PUBLISHER_SOURCE.encode();payloads['README.ru.md']=b'Only3907 expanded files matching published original archive and1252 obsolete compiled object cache files removed. Original archive remains locally and in Git25bb;5159 file hashes and deletion journal retained.19 current runtime file hashes unchanged. A1/A2 refused protected PAM/SSH proc inspection before any deletion; A3 records explicit helper exclusions and original native group closure. No model executed by cleanup.\n';payloads['SHA256SUMS']=''.join(hashlib.sha256(v).hexdigest()+'  '+n+'\n' for n,v in sorted(payloads.items())).encode()
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
t=tree(git('rev-parse',parent+'^{tree}'),updates);commit=git('-c','user.name=TimeLearner Agent','-c','user.email=timelearner@localhost','commit-tree',t,'-p',parent,data=b'Preserve verified duplicate/cache cleanup exact file hashes and original archive source\n');git('update-ref','refs/heads/codex/elder-verified-cache-release-a3-evidence',commit,'0'*40)
print(json.dumps({'commit':commit,'parent':parent,'repository':str(repo),'archive_members':len(members),'archive_bytes':len(payloads['primary.tar.xz']),'archive_sha256':bundle['archive_sha256'],'result':result,'origin_published':False}))
