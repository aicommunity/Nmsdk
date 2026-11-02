from pathlib import Path
import subprocess,sys,os,json,hashlib,tarfile,io,traceback
def publish_git_evidence(repo,parent,report,branch,out,files,message):
 import subprocess,os,hashlib,json
 subprocess.run(['git','-C',str(repo),'fetch','--no-recurse-submodules','https://github.com/aicommunity/Nmsdk.git',parent],check=True,capture_output=True)
 env=dict(os.environ,GIT_INDEX_FILE=str(out/'publish.index'))
 def git(*a,raw=None):return subprocess.check_output(['git','-C',str(repo),*a],input=raw,env=env).decode().strip()
 files['SHA256SUMS.json']=(json.dumps({k:hashlib.sha256(v).hexdigest() for k,v in files.items()},indent=2)+'\n').encode()
 git('read-tree',parent)
 for name,raw in files.items():git('update-index','--add','--cacheinfo','100644',git('hash-object','-w','--stdin',raw=raw),report+'/'+name)
 commit=git('commit-tree',git('write-tree'),'-p',parent,raw=(message+'\n').encode())
 git('update-ref','refs/heads/'+branch,commit,'0'*40)
 git('push','--recurse-submodules=no','git@github.com:aicommunity/Nmsdk.git','refs/heads/'+branch+':refs/heads/'+branch)
 assert git('ls-remote','git@github.com:aicommunity/Nmsdk.git','refs/heads/'+branch).split()[0]==commit
 print(json.dumps({'commit':commit,'report':report}),flush=True)
 return commit

base=Path("/media/user/Data/TimeLearnerRefactor");worker='asan';root='12649b3a6f1da80d5898a6744ab7f7b35f47ac49'
out=Path(__file__).resolve().parent
assert out==base/'readbacks/s03-inherited-review-selection-asan-a2'
def write(n,v):
 with (out/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def run(args,n,env=None,timeout=600):
 with (out/n).open('xb') as f:r=subprocess.run(list(map(str,args)),env=env,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
 assert r.returncode==0,(n,r.returncode)
try:
 repo=out/'repo'
 run(['git','clone','--shared','--no-checkout','--origin','local-source',base/'source-n1-measured-refinement-asan-a1',repo],'clone.log')
 run(['git','-C',repo,'fetch','--no-tags','--no-recurse-submodules','https://github.com/aicommunity/Nmsdk.git',root],'fetch.log')
 run(['git','-C',repo,'sparse-checkout','set','Scripts/StructTrain/TimeLearner'],'sparse.log')
 run(['git','-C',repo,'-c','submodule.recurse=false','checkout','--detach',root],'checkout.log')
 def blob(commit,path):return subprocess.check_output(['git','-C',str(repo),'show',commit+':'+path])
 visual='Reports/StructTrain/TimeLearner/s01-inherited-native-visual-normal-a1/'
 primary='Reports/StructTrain/TimeLearner/s01-inherited-native-gate-normal-a1/'
 visualProof='e8ecd698cd00c4a4a7c696c6687be888f0bfc5c6';primaryProof='cc7d8b66d1ee4552e6bff8cd2d49bba63507e0af'
 vm=json.loads(blob(visualProof,visual+'manifest.json'));pm=json.loads(blob(primaryProof,primary+'manifest.json'))
 meta=blob(visualProof,visual+'metadata.tar.xz');data=blob(primaryProof,primary+'primary.tar.xz')
 sha=lambda b:hashlib.sha256(b).hexdigest()
 assert sha(meta)==vm['metadata_sha256'] and sha(data)==pm['archive_sha256']
 cache=out/'review-cache';cache.mkdir()
 with tarfile.open(fileobj=io.BytesIO(meta),mode='r:xz') as t,tarfile.open(fileobj=io.BytesIO(data),mode='r:xz') as raw:
  manifest=json.load(t.extractfile('cache/manifest.json'));sums=json.load(t.extractfile('cache/SHA256SUMS.json'))
  (cache/'manifest.json').write_bytes(t.extractfile('cache/manifest.json').read())
  copied={}
  for i,g in enumerate(manifest['groups']):
   entry=g['trials'][0]
   if not entry['source_packet'].endswith('_inherited_activity_probe_2_evidence.json'):continue
   folder=cache/f'group-{i:03d}'/'probe-0000';(folder/'primary').mkdir(parents=True)
   probeManifest=t.extractfile(f'cache/group-{i:03d}/probe-0000/manifest.json').read()
   packet=json.load(raw.extractfile('native-run/native/'+entry['source_packet']))
   packetBytes=(json.dumps(packet,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
   traces=raw.extractfile('native-run/native/'+entry['source_trace']).read()
   for dest,b in [('manifest.json',probeManifest),('primary/probe.json',packetBytes),('primary/trace.csv',traces)]:
    p=folder/dest;rel=str(p.relative_to(cache));assert sha(b)==sums[rel],rel;p.write_bytes(b);copied[rel]=sha(b)
  assert len(copied)==24
  write('bound-cache-files.json',copied)
 env=dict(os.environ,PYTHONPATH=str(repo),TIMELEARNER_INHERITED_REPORT_CACHE=str(cache))
 run([sys.executable,'-m','unittest','Scripts.StructTrain.TimeLearner.tests.test_review_views','-v'],'tests.log',env,1200)
 sys.path.insert(0,str(repo))
 from Scripts.StructTrain.TimeLearner.review_views import select_review_views
 from Scripts.StructTrain.TimeLearner.probe_reports import _read_probe_data
 selected=[];files={}
 for i,g in enumerate(manifest['groups']):
  name=g['trials'][0]['source_packet']
  if not name.endswith('_inherited_activity_probe_2_evidence.json'):continue
  folder=cache/f'group-{i:03d}'/'probe-0000'
  probe=json.loads((folder/'manifest.json').read_text())
  samples=_read_probe_data(folder/'primary/probe.json',folder/'primary/trace.csv',True)[5]
  chosen=select_review_views(probe['figures'][0]['views'],samples,0)
  for choice in chosen:
   view=choice['view'];relative=f'group-{i:03d}/probe-0000/'+view['files'][0]
   selected.append({'packet':name,'purpose':choice['purpose'],'anchor_time':choice['anchor_time'],'cache_path':relative,'view':view,'png_sha256':sums[relative],'directly_reviewed':False})
   if worker=='asan':
    path=base/'report-cache/s01-inherited-normal-a1'/relative
    b=path.read_bytes();assert sha(b)==sums[relative]
    filename='selected/'+name.removesuffix('_evidence.json')+'-'+view['view']+'.png'
    files[filename]=b;selected[-1]['file']=filename
 assert len(selected)==24
 write('selection.json',{'source':root,'primary_proof':primaryProof,'render_proof':visualProof,'selected_anchors':selected,'unique_views':len({r['cache_path'] for r in selected}),'whole_visual_acceptance':False,'scientific_verdict':None})
 metadata={n:(out/n).read_bytes() for n in ['job.py','tests.log','bound-cache-files.json','selection.json','clone.log','fetch.log','sparse.log','checkout.log']}
 files.update(metadata)
 files['README.md']=b'Corrective review selection from actual first input pulse and first-response excursion; overview retained; response uses existing labelled local-detail amplitude scale when available. Old fixed first zoom was blank before stimulus in all4 20000Hz cases. Seven actual-data tests,8 configurations,24 source-bound cache files and24 named anchors;20 unique views expected. Model/primary traces and full cache unchanged. No scientific score/peak assignment inferred. PNG only on M40 publication; direct visual QA pending.\n'
 commit=publish_git_evidence(repo,root,'Reports/StructTrain/TimeLearner/s03-inherited-review-selection-asan-a2','codex/timelearner-inherited-review-selection-asan-a1',out,files,'Verify informative inherited review view selection on asan')
 write('terminal.json',{'execution':'completed','commit':commit,'tests':7,'actual_cases':8,'selected_anchors':24,'unique_views':len({r['cache_path'] for r in selected}),'selected_png':len([k for k in files if k.endswith('.png')]),'scientific_verdict':None})
except BaseException as error:
 write('exception.json',{'error':str(error),'traceback':traceback.format_exc()});raise
