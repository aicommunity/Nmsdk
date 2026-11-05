from pathlib import Path
import json,subprocess,hashlib,tarfile,io,sys
base=Path('/media/user/Data/TimeLearnerRefactor');repo=base/'source-psi-retirement-a1';parent='554c45786cc2d0203ac5199cc7df568828f66e58';prefix='Reports/StructTrain/TimeLearner/s09-psi-retirement-m40-a1';updates={};payloads={}
sys.path.insert(0,str(base/'source-psi-retirement-a1'))
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
registry=Reservations(base/'psi-metadata-reservations.sqlite3');states={}
for attempt in ['a1']:
 folder=base/('readbacks/s09-psi-retirement-'+attempt);controller=Path(str(folder)+'-container')
 state=inspect_worker_dependency(controller,registry,folder.name,reservation_optional=attempt!='a1');assert state['state']=='ready',state;states[attempt]=state
 bundle=json.loads((folder/'bundle.json').read_text());raw=(folder/'primary.tar.xz').read_bytes();assert len(raw)==bundle['archive_bytes'] and hashlib.sha256(raw).hexdigest()==bundle['archive_sha256'];seen=set()
 with tarfile.open(fileobj=io.BytesIO(raw),mode='r:xz') as a:
  for m in a:
   assert m.isfile() and m.name not in seen;seen.add(m.name);v=a.extractfile(m).read();assert bundle['members'][m.name]=={'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()}
 assert seen==set(bundle['members'])
 terminal=json.loads((folder/'terminal.json').read_text());assert terminal['checks_passed']==(attempt=='a1')
 sub='' if attempt=='a1' else 'prior/'+attempt+'/'
 for n in ['primary.tar.xz','bundle.json','terminal.json']:
  payloads[sub+n]=(folder/n).read_bytes()
 if attempt=='a1':
  for n in ['positive.json','negative.json','scope.json','source-hashes.json']:payloads[n]=(folder/n).read_bytes()
 for p in controller.iterdir():
  if p.is_file() and p.suffix=='.json':payloads[sub+'controller/'+p.name]=p.read_bytes()
assert json.loads(payloads['positive.json'])['source_records_verified']==205
payloads['fresh-operational-closure.json']=(json.dumps(states,indent=2)+'\n').encode()
payloads['README.ru.md']=b'Historical19 PSI campaign tools retired: production history205 and restored-path negative passed; exact Bin19 deletions+7 historical documentation prefixes, Root3 paths. All other config/data/native/code objects and original report bodies unchanged. No model or old script executed; full migration and science completion not claimed.\n'
payloads['publisher-source.py']=PUBLISHER_SOURCE.encode('utf-8')
payloads['SHA256SUMS']=''.join(hashlib.sha256(v).hexdigest()+'  '+n+'\n' for n,v in sorted(payloads.items())).encode()
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
t=tree(git('rev-parse',parent+'^{tree}'),updates);commit=git('-c','user.name=TimeLearner Agent','-c','user.email=timelearner@localhost','commit-tree',t,'-p',parent,data=b'Preserve PSI migration205 and restored-path negative controls\n');git('update-ref','refs/heads/codex/psi-retirement-m40-a1-evidence',commit,'0'*40)
print(json.dumps({'commit':commit,'parent':parent,'repository':str(repo),'source':'554c45786cc2d0203ac5199cc7df568828f66e58','files':len(payloads),'archive_bytes':len(payloads['primary.tar.xz']),'origin_published':False}))
