from pathlib import Path
import json,subprocess,sys
base=Path('/media/user/Data/TimeLearnerRefactor');repo=base/'source-theory-retirement-a1';parent='4bd624d69d61f8f687c145325b50fbd2543234cb';sys.dont_write_bytecode=True;sys.path.insert(0,str(base/'source-native-partition-a2'))
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
registry=Reservations(base/'resource-reservations.sqlite3');receipt=(base/'readbacks/shared-asan-build-focused-a1-publisher-recovery.json').read_bytes();event=json.loads(receipt);assert event['completed_data_commit']==parent and not event['native_jobs_modified'];lease=registry.reserve('publish-shared-asan-focused-recovery-a1',[{'path':str(repo),'access':'write'}],ttl_seconds=120)
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






try:
 updates={}
 for label in ['s07-integrated-acceptance-asan-build-a2','s06-integrated-acceptance-asan-focused-a3']:
  prefix='Reports/StructTrain/TimeLearner/'+label+'/'
  updates[prefix+'publisher-lease-recovery.json']=('100644','blob',git('hash-object','-w','--stdin',data=receipt))
  updates[prefix+'recovery-collector-source.py']=('100644','blob',git('hash-object','-w','--stdin',data=PUBLISHER_SOURCE.encode()))
 t=tree(git('rev-parse',parent+'^{tree}'),updates);commit=git('-c','user.name=TimeLearner Agent','-c','user.email=timelearner@localhost','commit-tree',t,'-p',parent,data=b'Preserve explicit closure of completed evidence publisher lease without native changes\n');git('update-ref','refs/heads/codex/shared-asan-build-focused-recovery-a1-evidence',commit,'0'*40)
finally:registry.release(lease['token'],note='Completed evidence append; no native job modified')
print(json.dumps({'commit':commit,'parent':parent,'repository':str(repo),'publisher_lease_recovered':True,'origin_published':False}))
