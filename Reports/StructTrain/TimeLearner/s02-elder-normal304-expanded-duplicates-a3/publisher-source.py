from pathlib import Path
import json,subprocess,hashlib,tarfile,sys,sqlite3
base=Path('/home/user/timelearner-refactor');repo=base/'source-pipeline-condition-a2';parent='bd10072c73d7c8296f1a4d02c051459f29f8c039';sys.dont_write_bytecode=True;sys.path.insert(0,str(repo));updates={};payloads={};proof=[]
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
c=sqlite3.connect('file:'+str(base/'resource-reservations.sqlite3')+'?mode=ro',uri=True)
try:capacity=json.loads(dict(c.execute('SELECT key,value FROM metadata'))['capacity'])
finally:c.close()
registry=Reservations(base/'resource-reservations.sqlite3',capacity=capacity)
for attempt in [1,2,3]:
 folder=base/('readbacks/s02-elder-normal304-expanded-duplicates-a'+str(attempt));controller=Path(str(folder)+'-container');closed=inspect_worker_dependency(controller,registry,folder.name);assert closed['closure']['all_processes_closed'] and ((attempt==1 and closed['reservation_state']=='not_created' and closed['reason']=='dependency_required_reservation_missing') or (attempt>1 and closed['state']=='ready')),closed
 bundle=json.loads((folder/'bundle.json').read_text());archive=folder/'primary.tar.xz';assert archive.stat().st_size==bundle['archive_bytes'] and hashlib.sha256(archive.read_bytes()).hexdigest()==bundle['archive_sha256'];seen=set()
 with tarfile.open(archive,'r:xz') as tf:
  for m in tf:
   assert m.isfile() and m.name not in seen;seen.add(m.name);raw=tf.extractfile(m).read();assert bundle['members'][m.name]=={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
 assert seen==set(bundle['members']);terminal=json.loads((folder/'terminal.json').read_text());assert terminal['cleanup_passed']==(attempt==3)
 if attempt<3:assert not (folder/'deletions.jsonl').exists()
 else:
  rows=json.loads((folder/'prepared-files.json').read_text());journal=[json.loads(x) for x in (folder/'deletions.jsonl').read_text().splitlines()];assert len(journal)==2*len(rows)
  for i,row in enumerate(rows):
   assert journal[2*i]==dict(state='verified_before_unlink',**row);assert journal[2*i+1]=={'state':'removed','relative':row['relative'],'sha256':row['sha256']};assert not Path(row['path']).exists()
  result=json.loads((folder/'result.json').read_text());assert result['removed_files']==len(rows)==3907 and result['logical_bytes_removed']==sum(r['bytes'] for r in rows)==1489206262 and result['archive_kept_and_rehashed'] and result['runtime_critical_files_unchanged']==28
 prefix='Reports/StructTrain/TimeLearner/s02-elder-normal304-expanded-duplicates-a'+str(attempt)
 for p in folder.iterdir():
  if p.is_file() and (p.suffix=='.json' or p.name in ['primary.tar.xz','producer.py']):payloads[prefix+'/'+p.name]=p.read_bytes()
 for p in controller.iterdir():
  if p.is_file() and p.suffix=='.json':payloads[prefix+'/controller/'+p.name]=p.read_bytes()
 proof.append({'attempt':attempt,'fresh_closed_released':closed,'archive_members_checked':len(seen),'terminal':terminal,'archive_sha256':bundle['archive_sha256'],'archive_bytes':bundle['archive_bytes']})
old=base/'readbacks/s07-integrated-native304-normal-a1';canonical=json.loads((old/'bundle.json').read_text());assert hashlib.sha256((old/'primary.tar.xz').read_bytes()).hexdigest()==canonical['archive_sha256']=='e95626641478c04131900bf17aebed1cca3264f8ad6e05499d4409d3e5a97414'
prefix='Reports/StructTrain/TimeLearner/s02-elder-normal304-expanded-duplicates-a3';payloads[prefix+'/originals-verification.json']=(json.dumps({'attempts':proof,'removed_files':3907,'logical_bytes_removed':1489206262,'canonical_archive_kept':True,'native_models_executed':0,'whole_plan_complete':False},indent=2)+'\n').encode();payloads[prefix+'/publisher-source.py']=PUBLISHER_SOURCE.encode();payloads[prefix+'/CACHE_RESTORATION.md']=(old/'native-result/native/CACHE_RESTORATION.md').read_bytes()
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
t=tree(git('rev-parse',parent+'^{tree}'),updates);commit=git('-c','user.name=TimeLearner Agent','-c','user.email=timelearner@localhost','commit-tree',t,'-p',parent,data=b'Preserve verified Elder expanded native304 duplicate cleanup and both refused attempts\n');git('update-ref','refs/heads/codex/elder-normal304-expanded-duplicates-a3-evidence',commit,'0'*40)
print(json.dumps({'commit':commit,'parent':parent,'repository':str(repo),'removed_files':3907,'logical_bytes_removed':1489206262,'attempts_preserved':3,'origin_published':False}))
