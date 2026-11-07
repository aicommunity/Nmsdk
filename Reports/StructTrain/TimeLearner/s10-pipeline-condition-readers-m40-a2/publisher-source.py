from pathlib import Path
import json,subprocess,hashlib,tarfile,sys,io
base=Path('/media/user/Data/TimeLearnerRefactor');repo=base/'source-pipeline-condition-a2';parent='d43780822a7b9e2b7c0229c323cda174abc7fce8';sys.dont_write_bytecode=True;sys.path.insert(0,str(repo));updates={};payloads={};proofs={}
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
for attempt in ['a1','a2']:
 folder=base/('readbacks/s10-pipeline-condition-readers-'+attempt);controller=Path(str(folder)+'-container');prefix='Reports/StructTrain/TimeLearner/s10-pipeline-condition-readers-m40-'+attempt
 state=inspect_worker_dependency(controller,Reservations(base/'statistic-trace-checks-reservations.sqlite3'),folder.name);assert state['state']=='ready',state
 bundle=json.loads((folder/'bundle.json').read_text());archive=(folder/'primary.tar.xz').read_bytes();assert len(archive)==bundle['archive_bytes'] and hashlib.sha256(archive).hexdigest()==bundle['archive_sha256'];seen=set()
 with tarfile.open(fileobj=io.BytesIO(archive),mode='r:xz') as tf:
  for m in tf:
   assert m.isfile() and m.name not in seen;seen.add(m.name);raw=tf.extractfile(m).read();assert bundle['members'][m.name]=={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
 assert seen==set(bundle['members']);terminal=json.loads((folder/'terminal.json').read_text());assert terminal['native_models_executed']==0
 if attempt=='a1':
  assert not terminal['checks_passed'] and not(folder/'result.json').exists();exception=json.loads((folder/'exception.json').read_text());assert 'not JSON serializable' in exception['reason']
 else:
  result=json.loads((folder/'result.json').read_text());suite=json.loads((folder/'structured-suite/suite.json').read_text());assert terminal['checks_passed'] and result['execution']=='completed' and result['assertion_status']=='passed' and result['executed_tests']==len(set(result['expected_test_ids']))==36 and not any(result[k] for k in ['failures','errors','skipped']);assert result['expected_test_ids']==suite['expected_test_ids'] and result['package_fingerprint']==suite['package_fingerprint'] and (folder/'result.json').read_bytes()==(folder/'structured-suite/result.json').read_bytes()
 for path in folder.iterdir():
  if path.is_file():payloads[prefix+'/'+path.name]=path.read_bytes()
 for path in controller.iterdir():
  if path.is_file() and path.suffix=='.json':payloads[prefix+'/controller/'+path.name]=path.read_bytes()
 proof={'attempt':attempt,'archive_members_checked':len(seen),'archive_bytes':len(archive),'archive_sha256':bundle['archive_sha256'],'accepted_python_suite':attempt=='a2','native_models_executed':0,'fresh_closed_released':state,'scientific_verdict':None};proofs[attempt]=proof;payloads[prefix+'/originals-verification.json']=(json.dumps(proof,indent=2)+'\n').encode();payloads[prefix+'/publisher-source.py']=PUBLISHER_SOURCE.encode()
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
t=tree(git('rev-parse',parent+'^{tree}'),updates);commit=git('-c','user.name=TimeLearner Agent','-c','user.email=timelearner@localhost','commit-tree',t,'-p',parent,data=b'Preserve ConditionSpec projection initial failed control and corrected production36 m40\n');git('update-ref','refs/heads/codex/pipeline-condition-readers-m40-a2-evidence',commit,'0'*40)
print(json.dumps({'commit':commit,'parent':parent,'repository':str(repo),'attempts':{k:{key:value for key,value in proof.items() if key!='fresh_closed_released'} for k,proof in proofs.items()},'origin_published':False}))
