"""Versioned training reproducibility study; preserve prior evidence and native states."""
from pathlib import Path
import argparse,copy,hashlib,json,os,shutil,subprocess,sys,zipfile,time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run import supervise
ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/'Reports/StructTrainClassic/TrainingReproducibility-20261123'
CONFIG=ROOT/'Bin/Configs/StructTrainClassic/TrainingReproducibility'
DELIVERY=ROOT/'Reports/StructTrainClassic/outputs/01a20798-0fce-7661-bd9d-b3506770ffc9/TrainingReproducibility'
OLD=ROOT/'Reports/StructTrainClassic/LegacyChecks-20261123'
SOURCE=ROOT/'Docs/ClassicStructTrainExperiments'
RUNTIME=ROOT/'Bin/Platform/Win'
BASE=ROOT/'Bin/Configs/StructTrainClassic/Prepared/manifest.json'
VARIANTS={'V0':'Исходный autoPreset','V1':'Инициализация; предварительный контроль остановки','V1C':'Исправлена только инициализация','V2':'Инициализация и параметры синапсов 2022 года','V3':'Архивный цикл обучения на современной инфраструктуре'}
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def component_order(root):
 result=[]
 def walk(node,path):
  children=node.find('Components')
  if children is None:return
  result.append((path,[child.tag for child in children]))
  for child in children:walk(child,path+'.'+child.tag)
 walk(root.find('Model'),'Model');return result

def state_identity(folder,stage=0):
 ident=folder.name+('-s'+str(stage) if stage else '')
 return ('warm-file-exact--'+ident) if folder.parent.name=='warm-file-exact' else ident
def git(*args,repo=ROOT):return subprocess.check_output(['git',*args],cwd=repo,encoding='utf8',errors='replace').strip()
def setup():
 WORK.mkdir(parents=True,exist_ok=True);CONFIG.mkdir(parents=True,exist_ok=True);DELIVERY.mkdir(parents=True,exist_ok=True)
 locked=[OLD/'scientific-comparison-data.json',OLD/'assessment.json',OLD/'final-audit.json']
 locked+=list((DELIVERY.parent/'ScientificComparisons').glob('*'))
 locked+=list((ROOT/'Bin/Configs/StructTrainClassic/Prepared').rglob('*'))
 record={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in locked if p.is_file()}
 lock=WORK/'prior-evidence-lock.json'
 if lock.exists():assert load(lock)==record,'Prior evidence changed'
 else:save(lock,record)
 for kind in ['learner','trainer']:
  source=ROOT/'Bin/Configs/StructTrainClassic/Prepared'/kind;target=CONFIG/'Inputs'/kind
  if not target.exists():shutil.copytree(source,target)
 for name in ['ClassicStructTrainReplay','ClassicSavedStateCheck']:
  dest=RUNTIME/(name+'-reference.exe')
  if not dest.exists():shutil.copy2(RUNTIME/(name+'.exe'),dest)
  ini=RUNTIME/(name+'.ini')
  if ini.exists() and not dest.with_suffix('.ini').exists():shutil.copy2(ini,dest.with_suffix('.ini'))
 save(WORK/'reference.json',{'root':'e719215c26','bin':'2c187306','pulselib':'9f3c5131192521d23b77be062ebd9b97298f50d9',
  'native_reference':str((RUNTIME/'ClassicSavedStateCheck-reference.exe').relative_to(ROOT)),
  'native_sha256':sha(RUNTIME/'ClassicSavedStateCheck-reference.exe'),'prior_lock_count':len(record)})
 history()
 print('Prepared study, immutable reference lock and history register')
def history():
 rows=[]
 for p in sorted(SOURCE.rglob('*')):
  if not p.is_file():continue
  if p.suffix.lower() in ['.docx','.xlsx','.pptx'] and ('Эксперименты' in p.parts or p.name=='ВКР_ЕременкоЕА.docx'):
   with zipfile.ZipFile(p) as z:
    if 'docProps/core.xml' not in z.namelist():continue
    props=ET.fromstring(z.read('docProps/core.xml'));dates={n.tag.split('}')[-1]:n.text for n in props if n.tag.split('}')[-1] in ['created','modified']}
    rows.append({'path':str(p.relative_to(SOURCE)),'sha256':sha(p),**dates,'evidence':'Office internal metadata; not the exact experiment date'})
  if p.name=='History.xml':
   h=ET.parse(p).getroot();rows.append({'path':str(p.relative_to(SOURCE)),'sha256':sha(p),'saves':[n.attrib.get('Time') for n in h],'evidence':'Native configuration save history'})
 commits=[]
 for c,factor in [('5f3f06d','synapse defaults'),('0be546f','synapse defaults restored'),('1e1a1c9','internal links'),('8f47c01','computation order'),('0b03edb','learner first Git appearance'),('ff77ca4','learner output'),('7cf11a1','LTZone potential'),('59ece28','threshold and timing'),('805fda1','computation order and links'),('fcaa969','initialization plus stop criterion'),('aec0302','subtree initialization'),('b99714c','saved trainer inference')]:
  full=git('rev-parse',c,repo=ROOT/'Libraries/Nmsdk-PulseLib');description=git('show','-s','--format=%H%n%aI%n%cI%n%s',full,repo=ROOT/'Libraries/Nmsdk-PulseLib').splitlines()
  patch=subprocess.check_output(['git','show','--format=fuller',full,'--','Core'],cwd=ROOT/'Libraries/Nmsdk-PulseLib')
  target=WORK/'history'/(full[:10]+'.patch');target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(patch)
  commits.append({'sha':full,'author_date':description[1],'commit_date':description[2],'subject':description[3],'factor':factor,'patch_sha256':sha(target),'patch':str(target.relative_to(ROOT)),'status':'candidate; effect requires measurement'})
 save(WORK/'history.json',{'documents':rows,'commits':commits,'notes':['Office dates are bounds on document editing, not run dates.','Learner code in 2022 archive predates its first available Git commit in 2023.','Git dates alone do not establish causality.']})
def package(variant):
 (WORK/'variants').mkdir(parents=True,exist_ok=True)
 source=RUNTIME/'ClassicTrainingRepro.exe';target=RUNTIME/('ClassicTrainingRepro-'+variant+'.exe')
 assert source.exists()
 if (WORK/'last-build.json').exists():
  built=load(WORK/'last-build.json');assert built['binary_sha256'].lower()==sha(source)
  for name,h in built['sources'].items():assert sha(ROOT/name).upper()==h,'Sources differ from the completed build'
 record={'id':variant,'label':VARIANTS.get(variant,variant),'binary':str(target.relative_to(ROOT)).replace('\\','/'),'binary_sha256':sha(source),
  'root_sha':git('rev-parse','HEAD'),'pulselib_sha':git('rev-parse','HEAD',repo=ROOT/'Libraries/Nmsdk-PulseLib'),'rdk_sha':git('rev-parse','HEAD',repo=ROOT/'Rdk'),
  'controller_sha256':sha(ROOT/'Scripts/ClassicStructTrain/replay.cpp'),'training_adapter_sha256':sha(ROOT/'Scripts/ClassicStructTrain/training_replay.inc'),
  'build':'Release /O2 /Ob2 /DNDEBUG','packaged_utc':datetime.now(timezone.utc).isoformat()}
 path=WORK/'variants'/(variant+'.json')
 if path.exists():assert load(path)['binary_sha256']==record['binary_sha256'],'Variant ID already has a different binary'
 shutil.copy2(source,target)
 shutil.copy2(RUNTIME/'ClassicStructTrainReplay.ini',target.with_suffix('.ini'))
 patch=subprocess.check_output(['git','diff','HEAD','--','Scripts/ClassicStructTrain','Tests/Integration/Libraries/CMakeLists.txt'],cwd=ROOT)
 record['controller_patch_sha256']=hashlib.sha256(patch).hexdigest();(WORK/'variants'/(variant+'-controller.patch')).write_bytes(patch)
 source_files=['replay.cpp','legacy_replay.inc','training_replay.inc']
 if '#include "training_file_protocol.inc"' in (ROOT/'Scripts/ClassicStructTrain/replay.cpp').read_text(encoding='utf8'):source_files.append('training_file_protocol.inc')
 record['source_snapshots']={}
 for name in source_files:
  source_file=ROOT/'Scripts/ClassicStructTrain'/name;copy_file=WORK/'variants/controller-sources'/variant/name
  copy_file.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source_file,copy_file)
  record['source_snapshots'][str(copy_file.relative_to(ROOT)).replace('\\','/')]=sha(copy_file)
 save(path,record);print('Packaged',variant,record['binary_sha256'])
def make_manifest(variant,job):
 m=copy.deepcopy(load(BASE));m['variant']=load(WORK/'variants'/(variant+'.json'));m['repro_job']=job
 m['allow_initialization_grace_tick']=job.get('allow_initialization_grace_tick',False)
 for t in m['templates']:t['config']=str((CONFIG/'Inputs'/t['kind']/'project.ini').relative_to(ROOT)).replace('\\','/')
 return m
def pilot_jobs():
 data=load(BASE)['dataset'];jobs=[]
 for kind in ['learner','trainer']:
  for target in [22,64,111]:jobs.append({'id':kind+'-'+str(target),'kind':kind,'target_id':target,'target_class':(target-1)//50+1})
 for target in [51,61]:jobs.append({'id':'learner-'+str(target),'kind':'learner','target_id':target,'target_class':2})
 jobs.append({'id':'learner-mean51-61','kind':'learner','target_id':0,'target_class':2,'pattern':[(a+b)/2 for a,b in zip(data[50]['pattern'],data[60]['pattern'])]})
 return jobs
def run_jobs(variant,jobs,phase='pilot',workers=4):
 v=load(WORK/'variants'/(variant+'.json'));binary=ROOT/v['binary'];assert sha(binary)==v['binary_sha256']
 tasks=[]
 for job in jobs:
  for repeat in range(1,4):
   folder=WORK/'runs'/variant/phase/(job['id']+'-r'+str(repeat));path=folder/'process.json'
   if path.exists() and load(path)['status']=='completed':continue
   if folder.exists() and any(folder.iterdir()):raise ValueError('Incomplete attempt must be preserved under its original ID: '+str(folder))
   manifest=CONFIG/'Jobs'/variant/(phase+'-'+job['id']+'-r'+str(repeat)+'.json');save(manifest,make_manifest(variant,job));tasks.append((manifest,folder,repeat))
 def execute(t):return supervise(binary,t[0],t[1],'repro',t[2],0,660)
 with ThreadPoolExecutor(max_workers=workers) as pool:results=list(pool.map(execute,tasks))
 save(WORK/'runs'/variant/(phase+'-run.json'),{'variant':v,'phase':phase,'new_processes':results,'jobs':[j['id'] for j in jobs]})
 summarize()
def summarize():
 from collections import Counter
 rows=[]
 for path in sorted((WORK/'runs').glob('*/*/*/results.jsonl')):
  process=load(path.parent/'process.json')
  for line in path.read_text(encoding='utf8').splitlines():
   r=json.loads(line);r['directory']=str(path.parent.relative_to(ROOT)).replace('\\','/');r['process_status']=process['status'];rows.append(r)
 summary={}
 for v in sorted({r['variant']['id'] for r in rows}):
  rs=[r for r in rows if r['variant']['id']==v];summary[v]={'records':len(rs),'statuses':dict(Counter(r['status'] for r in rs)),
   'initialized':sum(not r.get('whole_initialization_audit',{}).get('uninitialized',[True]) for r in rs),
   'wall_seconds':sum(r.get('elapsed_wall_seconds',0) for r in rs)}
 save(WORK/'training-assessment.json',{'summary':summary,'records':rows});print(json.dumps(summary,ensure_ascii=False))
def verify_lock():
 errors=[p for p,h in load(WORK/'prior-evidence-lock.json').items() if sha(ROOT/p)!=h]
 assert not errors,errors
 print('Prior evidence remains unchanged')
def inference(variant,phase='pilot',backend=None,self_only=False,workers=4,only_unplanned=False):
 from legacy_execute import write_config,internal_links
 from legacy_recover import physical
 binary=ROOT/(load(WORK/'variants'/(backend+'.json'))['binary'] if backend else load(WORK/'reference.json')['native_reference'])
 jobs=[];records=[];cache={};reuse=[]
 binary_hash=sha(binary)
 def cache_key(physical_state,dataset,job,pattern,order):
  return hashlib.sha256(json.dumps({'physical':physical_state,'component_order':order,'dataset':dataset,'class':job['target_class'],'initial_pattern':pattern,'binary':binary_hash,'protocol':'continuous'},sort_keys=True).encode()).hexdigest()
 if not self_only:
  for prior in (WORK/'inference').glob('*/*/*/*/process.json'):
   meta=load(prior)
   if meta['status']!='completed' or meta['binary_sha256']!=binary_hash:continue
   mf=load(meta['command'][meta['command'].index('--manifest')+1])
   if len(mf['dataset'])!=150:continue
   cfg=ROOT/mf['legacy_job']['config'];pstate=physical(ET.parse(cfg.parent/'Model_00.xml').getroot())
   pattern=[float(v) for v in ET.parse(cfg.parent/'Model_00.xml').getroot().findtext('Model/Components/Subject/Parameters/InputPattern').split()]
   cache[cache_key(pstate,mf['dataset'],mf['legacy_job'],pattern,component_order(ET.parse(cfg.parent/'Model_00.xml').getroot()))]=prior.parent
 files=sorted((WORK/'runs'/variant).glob('*/*/results.jsonl')) if phase=='all' else sorted((WORK/'runs'/variant/phase).glob('*/results.jsonl'))
 if variant=='VP1' and phase=='all':files=[p for p in files if p.parent.parent.name in ['warm-file-exact','schemes']]
 # Historical comparisons first. This changes only scheduling, never a stimulus.
 files.sort(key=lambda p:({'pilot':0,'ten':1}.get(p.parent.parent.name,2),str(p)))
 for file in files:
  for line in file.read_text(encoding='utf8').splitlines():
   try:r=json.loads(line)
   except json.JSONDecodeError:
    if load(file.parent/'process.json')['status']=='running':continue
    raise
   if r.get('record_type','training')!='training':continue
   if r['status']!='completed' or r.get('whole_initialization_audit',{}).get('uninitialized'):continue
   stage=r.get('stage_index',0);source=file.parent/('stage-'+str(stage) if stage else 'trained')
   job=copy.deepcopy(r['job'])
   # Joint intermediate phases are not archived evaluation checkpoints. Warm
   # training endpoints remain eligible; scheme checkpoints have an explicit map.
   if job.get('scheme') and stage and not r.get('stage',{}).get('evaluate',False):continue
   if r.get('stage'):
    for field in ['target_id','target_class']:
     if field in r['stage']:job[field]=r['stage'][field]
   state_id=state_identity(file.parent,stage)
   if only_unplanned:
    backend_key=(backend or 'reference')+('-own' if self_only else '')
    if (CONFIG/'InferenceJobs'/variant/phase/backend_key/(state_id+'.json')).exists():continue
   folder=CONFIG/'States'/variant/phase/state_id
   source_root=ET.parse(source/'Model_00.xml').getroot();subject=source_root.find('Model/Components/Subject')
   provenance=folder/'state-provenance.json';source_hash=sha(source/'Model_00.xml')
   if provenance.exists():assert load(provenance)['source_model_sha256']==source_hash,'Saved training source changed under an existing state identity'
   folder.parent.mkdir(parents=True,exist_ok=True);lock=folder.parent/(state_id+'.prepare.lock');wait_start=time.monotonic()
   while True:
    try:
     descriptor=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(descriptor,str(os.getpid()).encode());os.close(descriptor);break
    except FileExistsError:
     if time.monotonic()-wait_start>120:raise RuntimeError('Saved-state preparation lock did not clear: '+str(lock))
     time.sleep(.1)
   try:
    if not all((folder/name).exists() for name in ['Model_00.xml','Parameters_00.xml','project.ini']):
     frozen=write_config(folder,source_root,subject,internal_links(source_root,'Model.Subject'),(source/'project.ini').read_text(encoding='utf-8-sig'))
    else:frozen=ET.parse(folder/'Model_00.xml').getroot()
   finally:lock.unlink()
   original,prepared=physical(source_root),physical(frozen)
   assert original['links']==prepared['links'] and original['nodes'].keys()==prepared['nodes'].keys(),'Frozen adapter changed physical topology'
   allowed={('Subject','StructureBuildMode'):[0.0],('Subject','IsNeedToTrain'):[0.0],('Subject','LTZThreshold'):[float(subject.findtext('Parameters/FixedLTZThreshold'))],
            ('Subject.Neuron','StructureBuildMode'):[0.0],('Subject.Neuron.LTZone','Threshold'):[float(subject.findtext('Parameters/FixedLTZThreshold'))]}
   changes=[]
   for node,before in original['nodes'].items():
    after=prepared['nodes'][node];assert before['class']==after['class']
    for name in before['parameters'].keys()|after['parameters'].keys():
     a,b=before['parameters'].get(name),after['parameters'].get(name)
     if a!=b:
      assert (node,name) in allowed and b==allowed[(node,name)],'Unexpected physical parameter change: '+node+'.'+name
      changes.append({'node':node,'parameter':name,'before':a,'after':b,'reason':'Disable training, freeze construction and restore recorded inference threshold'})
   save(folder/'adapter-audit.json',{'passed':True,'nodes':len(original['nodes']),'links':len(original['links']),'explicit_mode_changes':changes,
       'physical_sha256':hashlib.sha256(json.dumps(prepared,sort_keys=True).encode()).hexdigest()})
   save(provenance,{'source_model':str((source/'Model_00.xml').relative_to(ROOT)).replace('\\','/'),'source_model_sha256':source_hash,'state_identity':state_id})
   key={'id':variant+'-'+phase+'-'+state_id,'kind':job['kind'],'target_id':job.get('target_id',0),'target_class':job['target_class'],
        'config':str((folder/'project.ini').relative_to(ROOT)).replace('\\','/'),'dendrites':r['dendrites'],'synapses':r['synapses']}
   for repeat in [1]:
    backend_key=(backend or 'reference')+('-own' if self_only else '')
    name=state_id;output=WORK/'inference'/variant/phase/backend_key/name
    if (output/'process.json').exists() and load(output/'process.json')['status']=='completed':continue
    m=make_manifest(variant,job);m['legacy_job']=key
    if self_only:m['dataset']=[{'id':job.get('target_id',0),'class':job['target_class'],'pattern':r['pattern']}]
    path=CONFIG/'InferenceJobs'/variant/phase/backend_key/(name+'.json');save(path,m)
    # legacyLoad starts from the serialized configuration. Use its actual
    # serialized input, including native numeric precision, for cross-batch keys.
    initial_pattern=[float(v) for v in frozen.findtext('Model/Components/Subject/Parameters/InputPattern').split()]
    ck=cache_key(prepared,m['dataset'],key,initial_pattern,component_order(frozen))
    if not self_only and ck in cache and cache[ck]!=output:
     save(output/'reuse.json',{'source':str(cache[ck].relative_to(ROOT)).replace('\\','/'),'reason':'Identical physical graph, parameters, initial pattern, test sequence and binary; training repeats remain independently executed','cache_key':ck})
     reuse.append((output,cache[ck]))
    else:
     if (output/'reuse.json').exists():
      save(output/'reuse-before-recompute.json',load(output/'reuse.json'));(output/'reuse.json').unlink()
     jobs.append((path,output,r['repeat']))
     if not self_only:cache[ck]=output
   records.append({'state_id':state_id,'source':str(source.relative_to(ROOT)),'config':key['config'],'job':key,'variant':variant,'phase':phase,'backend':backend or 'reference','training':r})
 def run_one(t):return supervise(binary,t[0],t[1],'legacy',t[2],0,660)
 with ThreadPoolExecutor(max_workers=workers) as pool:results=list(pool.map(run_one,jobs))
 for output,original in reuse:assert (original/'process.json').exists() and load(original/'process.json')['status']=='completed','Inference reuse source failed'
 suffix='-unplanned-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') if only_unplanned else ''
 save(WORK/'inference'/variant/phase/((backend or 'reference')+('-own' if self_only else '')+'-index'+suffix+'.json'),{'states':records,'processes':results,'reused_states':len(reuse),'only_previously_unplanned':only_unplanned})
 print('Inference states:',len(records))
def ten_jobs():
 return [{'id':kind+'-'+str(i),'kind':kind,'target_id':i,'target_class':(i-1)//50+1} for kind in ['learner','trainer'] for i in load(BASE)['selected_ids']]
def complete_cold(variant,workers):
 pilot={j['id'] for j in pilot_jobs()}
 run_jobs(variant,[j for j in ten_jobs() if j['id'] not in pilot],'ten',workers)
 completed=pilot|{j['id'] for j in ten_jobs()}
 full=[{'id':kind+'-'+str(i),'kind':kind,'target_id':i,'target_class':(i-1)//50+1} for kind in ['learner','trainer'] for i in range(1,151)]
 run_jobs(variant,[j for j in full if j['id'] not in completed],'full',workers)
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['setup','package','pilot','summarize','verify','inference','full']);p.add_argument('--variant',default='V0');p.add_argument('--phase',default='pilot');p.add_argument('--backend');p.add_argument('--self-only',action='store_true');p.add_argument('--only-unplanned',action='store_true');p.add_argument('--workers',type=int,default=4);args=p.parse_args()
 if args.action=='setup':setup()
 elif args.action=='package':package(args.variant)
 elif args.action=='pilot':run_jobs(args.variant,pilot_jobs(),workers=args.workers)
 elif args.action=='summarize':summarize()
 elif args.action=='inference':inference(args.variant,args.phase,args.backend,args.self_only,args.workers,args.only_unplanned)
 elif args.action=='full':complete_cold(args.variant,args.workers)
 else:verify_lock()
if __name__=='__main__':main()
