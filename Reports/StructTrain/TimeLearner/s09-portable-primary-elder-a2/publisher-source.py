from pathlib import Path
import sys,json,subprocess,hashlib,tarfile,sqlite3
base=Path('/home/user/timelearner-refactor');repo=base/'source-portable-primary-a1';parent='f1af8480406b3d1c1cfdb4b62f2b501e1117c5b6';folder=base/'readbacks/s09-portable-primary-readers-a2';controller=Path(str(folder)+'-container');prefix='Reports/StructTrain/TimeLearner/s09-portable-primary-elder-a2';sys.dont_write_bytecode=True;sys.path.insert(0,str(repo));payloads={};updates={}
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
c=sqlite3.connect('file:'+str(base/'resource-reservations.sqlite3')+'?mode=ro',uri=True);capacity=json.loads(dict(c.execute('SELECT key,value FROM metadata'))['capacity']);c.close();closed=inspect_worker_dependency(controller,Reservations(base/'resource-reservations.sqlite3',capacity=capacity),folder.name);assert closed['state']=='ready',closed
bundle=json.loads((folder/'bundle.json').read_text());archive=folder/'primary.tar.xz';assert archive.stat().st_size==bundle['archive_bytes'] and hashlib.sha256(archive.read_bytes()).hexdigest()==bundle['archive_sha256'];seen=set()
with tarfile.open(archive,'r:xz') as tf:
 for m in tf:
  assert m.isfile() and m.name not in seen;seen.add(m.name);raw=tf.extractfile(m).read();assert bundle['members'][m.name]=={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
assert seen==set(bundle['members']);result=json.loads((folder/'result.json').read_text());assert result['tests_run']==len(result['expected_ids'])==len(set(result['expected_ids']))==14 and not any(result[k] for k in ['failures','errors','skips']) and json.loads((folder/'terminal.json').read_text())['checks_passed']
for p in folder.iterdir():
 if p.is_file() and (p.suffix=='.json' or p.name in ['primary.tar.xz','producer.py']):payloads[prefix+'/'+p.name]=p.read_bytes()
for p in controller.iterdir():
 if p.is_file() and p.suffix=='.json':payloads[prefix+'/controller/'+p.name]=p.read_bytes()
failed=base/'readbacks/s09-portable-primary-readers-a1';assert not (failed/'result.json').exists() and json.loads((failed/'terminal.json').read_text())['checks_passed'] is False
for p in failed.iterdir():
 if p.is_file() and (p.suffix=='.json' or p.name in ['primary.tar.xz','producer.py']):payloads[prefix+'/previous-a1/'+p.name]=p.read_bytes()
payloads[prefix+'/originals-verification.json']=(json.dumps({'fresh_closed_released':closed,'archive_members_checked':len(seen),'tests_run':14,'native_models_executed':0,'whole_plan_complete':False},indent=2)+'\n').encode();payloads[prefix+'/publisher-source.py']=PUBLISHER_SOURCE.encode()
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
t=tree(git('rev-parse',parent+'^{tree}'),updates);commit=git('-c','user.name=TimeLearner Agent','-c','user.email=timelearner@localhost','commit-tree',t,'-p',parent,data=b'Preserve Elder fourteen production portable primary restoration regressions\n');git('update-ref','refs/heads/codex/portable-primary-elder-a2-evidence',commit,'0'*40);print(json.dumps({'commit':commit,'parent':parent,'repository':str(repo),'members':len(seen),'archive_bytes':bundle['archive_bytes'],'archive_sha256':bundle['archive_sha256'],'origin_published':False}))
