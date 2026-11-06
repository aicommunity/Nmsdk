from pathlib import Path
import json,subprocess,hashlib,tarfile,sys,io
base=Path('/home/user/timelearner-refactor');repo=base/'source-statistic-traces-a1';parent='f096b7a854b95b04c08720dcc8c9610de85f1bf2';folder=base/'readbacks/s09-statistic-traces-a1';controller=Path(str(folder)+'-container');prefix='Reports/StructTrain/TimeLearner/s09-statistic-traces-elder-a1';sys.dont_write_bytecode=True;sys.path.insert(0,str(repo));updates={};payloads={}
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
state=inspect_worker_dependency(controller,Reservations(base/'statistic-trace-checks-reservations.sqlite3'),folder.name);assert state['state']=='ready',state
bundle=json.loads((folder/'bundle.json').read_text());raw=(folder/'primary.tar.xz').read_bytes();assert len(raw)==bundle['archive_bytes'] and hashlib.sha256(raw).hexdigest()==bundle['archive_sha256'];seen=set()
with tarfile.open(fileobj=io.BytesIO(raw),mode='r:xz') as tf:
 for m in tf:
  assert m.isfile() and m.name not in seen;seen.add(m.name);value=tf.extractfile(m).read();assert bundle['members'][m.name]=={'bytes':len(value),'sha256':hashlib.sha256(value).hexdigest()}
assert seen==set(bundle['members']);result=json.loads((folder/'result.json').read_text());expected=json.loads((folder/'expected-tests.json').read_text());assert result['passed'] and result['executed']==len(expected)==len(set(expected))==12 and expected==result['expected'] and not any(result[k] for k in ['failures','errors','skipped']) and result['native_models_executed']==0;assert json.loads((folder/'terminal.json').read_text())['checks_passed']
for path in folder.iterdir():
 if path.is_file():payloads[path.name]=path.read_bytes()
for path in controller.iterdir():
 if path.is_file() and path.suffix=='.json':payloads['controller/'+path.name]=path.read_bytes()
payloads['fresh-operational-dependency.json']=(json.dumps(state,indent=2)+'\n').encode();payloads['publisher-source.py']=PUBLISHER_SOURCE.encode()
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
t=tree(git('rev-parse',parent+'^{tree}'),updates);commit=git('-c','user.name=TimeLearner Agent','-c','user.email=timelearner@localhost','commit-tree',t,'-p',parent,data=b'Preserve strict StatisticLog reader actual fixture and production CLI checks elder\n');git('update-ref','refs/heads/codex/statistic-traces-elder-a1-evidence',commit,'0'*40)
print(json.dumps({'commit':commit,'parent':parent,'repository':str(repo),'members':len(seen),'archive_bytes':bundle['archive_bytes'],'archive_sha256':bundle['archive_sha256'],'passed':12,'origin_published':False}))
