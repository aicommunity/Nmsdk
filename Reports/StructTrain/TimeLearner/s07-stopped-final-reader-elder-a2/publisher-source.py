from pathlib import Path
import sys,json,subprocess,hashlib,tarfile,io
base=Path('/home/user/timelearner-refactor');repo=base/'source-stopped-final-diagnostics-a2';parent='297bcbb42105396d83c3eecf52ad98613afaef0f';prefix='Reports/StructTrain/TimeLearner/s07-stopped-final-reader-elder-a2';updates={};payloads={}
sys.path.insert(0,str(repo))
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
registry=Reservations(base/'stopped-final-metadata-reservations.sqlite3');folder=base/'readbacks/s07-stopped-final-reader-elder-a2';controller=Path(str(folder)+'-container');state=inspect_worker_dependency(controller,registry,folder.name);assert state['state']=='ready',state
bundle=json.loads((folder/'bundle.json').read_text());raw=(folder/'primary.tar.xz').read_bytes();assert bundle['checks_passed'] and bundle['native_models_executed']==0 and len(raw)==bundle['archive_bytes'] and hashlib.sha256(raw).hexdigest()==bundle['archive_sha256'];seen=set()
with tarfile.open(fileobj=io.BytesIO(raw),mode='r:xz') as tf:
 for member in tf:
  assert member.isfile() and member.name not in seen;seen.add(member.name);value=tf.extractfile(member).read();assert bundle['members'][member.name]=={'bytes':len(value),'sha256':hashlib.sha256(value).hexdigest()}
assert seen==set(bundle['members'])
terminal=json.loads((folder/'terminal.json').read_text());assert terminal['readers13_and_cli4_passed'] and terminal['native_models_executed']==0
checks=json.loads((folder/'checks.json').read_text());assert checks['returncode']==0 and checks['tests']==checks['expected']==13
for name in ['primary.tar.xz','bundle.json','terminal.json','checks.json','restoration.json','source-unchanged.json','reader-source-hashes.json']:
 payloads[name]=(folder/name).read_bytes()
measurements=[]
for path in sorted((folder/'diagnostics').glob('*.json')):
 value=json.loads(path.read_text());v=value['analysis'];assert value['kind']=='timelearner_analysis' and value['evaluation_verdict'] is None and v['complete_measured_final_pass'] and not v['training_completed'] and not v['certificate_present']
 payloads['diagnostics/'+path.name]=path.read_bytes();measurements.append({'case':path.stem,'tolerances':v['tolerances'],'residuals':v['residuals']})
assert len(measurements)==4
for path in controller.iterdir():
 if path.is_file() and path.suffix=='.json':payloads['controller/'+path.name]=path.read_bytes()
payloads['fresh-operational-closure.json']=(json.dumps(state,indent=2)+'\n').encode();payloads['publisher-source.py']=PUBLISHER_SOURCE.encode();payloads['README.ru.md']=b'Exact297bcbb reader passed13 checks and production CLI4 on published native4 corpusd080310f. Primary116 source files restored through Git and rehashed unchanged. No models executed by this metadata group. Native4 was executed on Elder only, same CPP source/executable/AppIni/build flags as SDK2e; fresh runtime manifest recorded. Negative final residuals remain diagnostics, without convergence certificate or scientific recognition verdict.\n';payloads['SHA256SUMS']=''.join(hashlib.sha256(value).hexdigest()+'  '+name+'\n' for name,value in sorted(payloads.items())).encode()
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
t=tree(git('rev-parse',parent+'^{tree}'),updates);commit=git('-c','user.name=TimeLearner Agent','-c','user.email=timelearner@localhost','commit-tree',t,'-p',parent,data=b'Preserve negative final-pass reader13 and CLI4 acceptance\n');git('update-ref','refs/heads/codex/stopped-final-reader-elder-a2-evidence',commit,'0'*40)
print(json.dumps({'commit':commit,'parent':parent,'repository':str(repo),'files':len(payloads),'archive_bytes':bundle['archive_bytes'],'archive_sha256':bundle['archive_sha256'],'measurements':measurements,'origin_published':False}))
