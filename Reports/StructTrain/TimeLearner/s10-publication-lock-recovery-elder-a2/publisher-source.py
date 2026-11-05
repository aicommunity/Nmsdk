from pathlib import Path
import sys,json,subprocess,hashlib,tarfile,io
base=Path('/home/user/timelearner-refactor');repo=base/'source-publication-lock-recovery-a2';parent='10d45ed93f08928a9992a3cf569c6a4938cdcd64';prefix='Reports/StructTrain/TimeLearner/s10-publication-lock-recovery-elder-a2';updates={};payloads={};states={}
sys.path.insert(0,str(repo))
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
registry=Reservations(base/'publication-lock-metadata-reservations.sqlite3')
for attempt,expected in [('a1',False),('a2',True)]:
 folder=base/('readbacks/s10-publication-lock-recovery-'+attempt);controller=Path(str(folder)+'-container');state=inspect_worker_dependency(controller,registry,folder.name);assert state['state']=='ready',state;states[attempt]=state
 bundle=json.loads((folder/'bundle.json').read_text());raw=(folder/'primary.tar.xz').read_bytes();assert bundle['checks_passed'] is expected and len(raw)==bundle['archive_bytes'] and hashlib.sha256(raw).hexdigest()==bundle['archive_sha256'];seen=set()
 with tarfile.open(fileobj=io.BytesIO(raw),mode='r:xz') as tf:
  for member in tf:
   assert member.isfile() and member.name not in seen;seen.add(member.name);value=tf.extractfile(member).read();assert bundle['members'][member.name]=={'bytes':len(value),'sha256':hashlib.sha256(value).hexdigest()}
 assert seen==set(bundle['members']);terminal=json.loads((folder/'terminal.json').read_text());assert terminal['checks_passed'] is expected and terminal['native_models_executed']==0
 sub='' if expected else 'prior/a1/'
 for n in ['primary.tar.xz','bundle.json','terminal.json','checks.json']:payloads[sub+n]=(folder/n).read_bytes()
 if not expected:payloads[sub+'exception.json']=(folder/'exception.json').read_bytes()
 else:
  checks=json.loads((folder/'checks.json').read_text());assert checks['tests']==checks['expected']==20 and not checks['failures'] and not checks['errors'] and not checks['skipped']
  for n in ['fault-evidence/frontend-crash-recovery.json','source-hashes.json','source-unchanged.json','test-inventory.json']:payloads[n]=(folder/n).read_bytes()
 for path in controller.iterdir():
  if path.is_file() and path.suffix=='.json':payloads[sub+'controller/'+path.name]=path.read_bytes()
fault=json.loads(payloads['fault-evidence/frontend-crash-recovery.json']);assert fault['frontend_returncode']==-9 and fault['public_cli_recovery']['recovery']=='recovered' and fault['resumed_publication']['publication']=='published' and fault['root_remote_commit']==fault['expected_root_commit']
payloads['fresh-operational-closures.json']=(json.dumps(states,indent=2)+'\n').encode();payloads['publisher-source.py']=PUBLISHER_SOURCE.encode();payloads['README.ru.md']=b'Publisher20 real local Git cases passed, including frontend kill during live receive hook, kernel guard refusal, explicit public CLI recovery preserving old owner, and resumed children-first publication. Prior A1 code NameError and launcher CWD error preserved separately. No neural model executed; whole stage10 and remote distributed transaction not claimed.\n';payloads['SHA256SUMS']=''.join(hashlib.sha256(v).hexdigest()+'  '+n+'\n' for n,v in sorted(payloads.items())).encode()
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
t=tree(git('rev-parse',parent+'^{tree}'),updates);commit=git('-c','user.name=TimeLearner Agent','-c','user.email=timelearner@localhost','commit-tree',t,'-p',parent,data=b'Preserve publication20 kernel lock recovery and actual Git fault evidence\n');git('update-ref','refs/heads/codex/publication-lock-recovery-elder-a2-evidence',commit,'0'*40)
print(json.dumps({'commit':commit,'parent':parent,'repository':str(repo),'files':len(payloads),'primary_bytes':len(payloads['primary.tar.xz']),'prior_bytes':len(payloads['prior/a1/primary.tar.xz']),'origin_published':False}))
