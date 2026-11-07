from pathlib import Path
import sys,json,subprocess,hashlib,tarfile
base=Path('/media/user/Data/TimeLearnerRefactor');repo=base/'source-native-partition-a2';parent='86118630da6fed4763715209e4405980cad59f0d';folder=base/'readbacks/s06-integrated-acceptance-asan-lifecycle-a3';controller=Path(str(folder)+'-container');prefix='Reports/StructTrain/TimeLearner/s06-integrated-acceptance-asan-lifecycle-a3';sys.dont_write_bytecode=True;sys.path.insert(0,str(repo));payloads={};updates={}
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
from Scripts.StructTrain.TimeLearner.native_gate import audit_junit
closed=inspect_worker_dependency(controller,Reservations(base/'resource-reservations.sqlite3'),folder.name);assert closed['state']=='ready',closed
bundle=json.loads((folder/'bundle.json').read_text());archive=folder/'primary.tar.xz';h=hashlib.sha256()
with archive.open('rb') as s:
 for b in iter(lambda:s.read(1024**2),b''):h.update(b)
assert archive.stat().st_size==bundle['archive_bytes'] and h.hexdigest()==bundle['archive_sha256']=='ed89a8239f6e67efeab37fbba5aa493d0a69ed29ca4a1c7465a217a48e35e5dc';seen=set()
with tarfile.open(archive,'r:xz') as tf:
 for m in tf:
  assert m.isfile() and m.name not in seen;seen.add(m.name);h=hashlib.sha256();size=0
  with tf.extractfile(m) as s:
   for b in iter(lambda:s.read(1024**2),b''):h.update(b);size+=len(b)
  assert bundle['members'][m.name]=={'bytes':size,'sha256':h.hexdigest()}
assert seen==set(bundle['members']) and len(seen)==4883;spec=json.loads((folder/'native-specification.json').read_text());ids=spec['expected_test_ids'];assert len(ids)==len(set(ids))==133;result=json.loads((folder/'native-verdict.json').read_text());assert result['execution']=='completed' and result['validity']=='valid' and result['assertion_status']=='failed' and result['executed_partitions']==133 and result['inventory']==audit_junit(folder/'native-result/native.xml',ids);assert result['inventory']['failed_test_ids']==['NativeBranchAliasing/CoincidentLabelsExposeOneEffectivePhysicalBank'];runtime=json.loads((folder/'native-runtime.json').read_text());identities=set();cases=[]
for i,identity in enumerate(ids):
 case=folder/'native-result/cases'/f'{i:04d}';inventory=audit_junit(case/'native.xml',[identity]);owner=json.loads((case/'process/owned-process.json').read_text());execution=json.loads((case/'process/result.json').read_text());loaded=json.loads((case/'process/loaded-files.json').read_text());key=(owner['boot_id'],owner['pid'],owner['start_ticks']);assert key not in identities;identities.add(key);assert owner['executable_sha256']==runtime['executable']['sha256'] and owner['runtime_fingerprint']==runtime['runtime_fingerprint'] and execution['runtime_provenance']=='loaded_files_captured' and any('libasan' in r['path'] for r in loaded) and any(r['sha256']==owner['executable_sha256'] for r in loaded);failed=identity in result['inventory']['failed_test_ids'];assert inventory['assertion_status']==('failed' if failed else 'passed') and execution['returncode']==(1 if failed else 0);cases.append({'test_id':identity,'owner':owner,'assertion_status':inventory['assertion_status'],'returncode':execution['returncode'],'libasan_mapping_present':True})
case=folder/'native-result/cases/0090';assert not (case/'native').exists();assert b'file.open(QIODevice::WriteOnly|QIODevice::NewOnly)' in (case/'process/stdout.log').read_bytes();terminal=json.loads((folder/'terminal.json').read_text());assert terminal['shared_integrated_ASan_lifecycle133_passed'] is False
for p in folder.iterdir():
 if p.is_file() and (p.suffix=='.json' or p.name in ['primary.tar.xz','producer.py']):payloads[prefix+'/'+p.name]=p.read_bytes()
for p in controller.iterdir():
 if p.is_file() and p.suffix=='.json':payloads[prefix+'/controller/'+p.name]=p.read_bytes()
proof={'kind':'timelearner_original_failed_shared_asan133_verification','fresh_closed_released':closed,'archive_members_checked':len(seen),'cases':cases,'passed_tests':132,'failed_tests':1,'original_verdict_preserved':True,'observed_missing_output_directory':True,'asan_finding_causal_claim':False,'full_asan133_pass_attested':False,'whole_plan_complete':False};payloads[prefix+'/originals-verification.json']=(json.dumps(proof,indent=2)+'\n').encode();payloads[prefix+'/publisher-source.py']=PUBLISHER_SOURCE.encode()
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
t=tree(git('rev-parse',parent+'^{tree}'),updates);commit=git('-c','user.name=TimeLearner Agent','-c','user.email=timelearner@localhost','commit-tree',t,'-p',parent,data=b'Preserve all original shared ASan133 results including missing-directory assertion failure\n');git('update-ref','refs/heads/codex/shared-asan133-original-failure-a3-evidence',commit,'0'*40);print(json.dumps({'commit':commit,'parent':parent,'repository':str(repo),'members':len(seen),'archive_bytes':bundle['archive_bytes'],'archive_sha256':bundle['archive_sha256'],'passed':132,'failed':1,'origin_published':False}))
