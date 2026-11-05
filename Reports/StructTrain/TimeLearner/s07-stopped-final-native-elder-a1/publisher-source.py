from pathlib import Path
import json,subprocess,hashlib,tarfile,io,sys,sqlite3,xml.etree.ElementTree as ET
base=Path('/home/user/timelearner-refactor');repo=base/'source-stopped-final-diagnostics-a1';parent='ff409ba3a5107ca9a3931657ecb65e69aa2199ef';prefix='Reports/StructTrain/TimeLearner/s07-stopped-final-native-elder-a1';updates={};payloads={}
sys.path.insert(0,str(repo))
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
c=sqlite3.connect('file:'+str(base/'resource-reservations.sqlite3')+'?mode=ro',uri=True)
try:metadata=dict(c.execute('SELECT key,value FROM metadata'))
finally:c.close()
registry=Reservations(base/'resource-reservations.sqlite3',capacity=json.loads(metadata['capacity']) if metadata['schema_version']=='2' else None)
folder=base/'readbacks/s07-stopped-final-native-elder-a1';controller=Path(str(folder)+'-container');state=inspect_worker_dependency(controller,registry,folder.name);assert state['state']=='ready',state
bundle=json.loads((folder/'bundle.json').read_text());raw=(folder/'primary.tar.xz').read_bytes();assert len(raw)==bundle['archive_bytes'] and hashlib.sha256(raw).hexdigest()==bundle['archive_sha256'];seen=set()
with tarfile.open(fileobj=io.BytesIO(raw),mode='r:xz') as tf:
 for member in tf:
  assert member.isfile() and member.name not in seen;seen.add(member.name);value=tf.extractfile(member).read();assert bundle['members'][member.name]=={'bytes':len(value),'sha256':hashlib.sha256(value).hexdigest()}
assert seen==set(bundle['members'])
terminal=json.loads((folder/'terminal.json').read_text());assert terminal['native4_passed'] and not terminal['readers10_and_cli4_passed']
native=json.loads((folder/'native-verdict.json').read_text());assert native['execution']=='completed' and native['validity']=='valid' and native['assertion_status']=='passed' and native['inventory']['expected']==native['inventory']['observed']==4
junit=ET.parse(folder/'native-result/native.xml').getroot();assert junit.get('tests')=='4' and junit.get('failures')=='0' and junit.get('errors')=='0'
checks=json.loads((folder/'checks.json').read_text());assert checks['tests']==10 and checks['returncode']==1
for name in ['primary.tar.xz','bundle.json','terminal.json','native-verdict.json','native-specification.json','runtime.json','runtime-comparison.json','checks.json','exception.json','reader-inputs.json','reader-source-hashes.json']:
 payloads[name]=(folder/name).read_bytes()
for path in controller.iterdir():
 if path.is_file() and path.suffix=='.json':payloads['controller/'+path.name]=path.read_bytes()
payloads['fresh-operational-closure.json']=(json.dumps(state,indent=2)+'\n').encode()
payloads['publisher-source.py']=PUBLISHER_SOURCE.encode()
payloads['README.ru.md']=b'Actual four NativeTrainingTermination Classic/Branch N0/N1 native cases passed on unchanged SDK2e. All32 raw probe pairs retained. Reader A1 ran10 checks, nine passed and one CLI test errored due to reading the standard analysis envelope incorrectly. This is not reader acceptance; models are not rerun for metadata corrections. Whole group freshly closed and lease released. No scientific recognition or full-plan completion verdict.\n'
payloads['SHA256SUMS']=''.join(hashlib.sha256(value).hexdigest()+'  '+name+'\n' for name,value in sorted(payloads.items())).encode()
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
t=tree(git('rev-parse',parent+'^{tree}'),updates);commit=git('-c','user.name=TimeLearner Agent','-c','user.email=timelearner@localhost','commit-tree',t,'-p',parent,data=b'Preserve native final-pass4 success and reader A1 CLI-test error\n');git('update-ref','refs/heads/codex/stopped-final-native-elder-a1-evidence',commit,'0'*40)
print(json.dumps({'commit':commit,'parent':parent,'repository':str(repo),'files':len(payloads),'archive_bytes':bundle['archive_bytes'],'archive_sha256':bundle['archive_sha256'],'native4_passed':True,'readers_accepted':False,'origin_published':False}))
