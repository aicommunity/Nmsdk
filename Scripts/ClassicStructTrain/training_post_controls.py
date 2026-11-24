"""Sequential source-stable diagnostic builds after the one-factor sweep."""
from pathlib import Path
import sys,time,subprocess,shutil,copy,json
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import ROOT,WORK,CONFIG,BASE,load,save,git,package,run_jobs,inference,make_manifest
from training_stop_variants import apply
from training_variants import span
from training_protocols import modes
from run import supervise
SHELL=shutil.which('pwsh') or 'powershell.exe'
PULSE=ROOT/'Libraries/Nmsdk-PulseLib'

def build(variant):
 with (WORK/('build-control-'+variant+'.log')).open('w',encoding='utf8') as out:
  result=subprocess.run([SHELL,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'Scripts/ClassicStructTrain/training_build.ps1')],cwd=ROOT,stdout=out,stderr=subprocess.STDOUT)
 assert result.returncode==0,'Diagnostic build failed: '+variant
 package(variant)

def prepare_controller():
 p=ROOT/'Scripts/ClassicStructTrain/replay.cpp';t=p.read_text(encoding='utf8')
 if 'static void resetCount' not in t:
  token=' static int count(const NNeuronLearner& n)';index=t.index(token)
  t=t[:index]+' static void resetCount(NNeuronLearner& n) { n.*(&LearnerAccess::CountIteration)=0; }\n'+t[index:]
 if 'cold_mode_override' not in t:
  t=t.replace('learner->CalculateMode=fixedIterations ? 1 : (cold ? 0 : 1);','learner->CalculateMode=fixedIterations ? 1 : (cold ? (suite=="repro"?manifest.at("repro_job").value("cold_mode_override",0):0) : 1);')
 if '#include "training_file_protocol.inc"' not in t:t=t.replace('#include "training_replay.inc"','#include "training_file_protocol.inc"\n#include "training_replay.inc"')
 a,b=span(t,'void modes()');body=t[a:b]
 if 'training_precondition' not in body:
  body=body.replace('key=test["case"];','json precondition=nullptr; key=test["case"];')
  body=body.replace('auto trained=train(p[0],true);','''auto trained=train(p[0],true);
    if(trained["status"]=="completed" && needs() && learner->CalculateMode.GetData()==0
       && zero(LearnerAccess::ds(*learner)) && zero(LearnerAccess::ss(*learner))) step();
    if(trained["status"]=="completed" && needs()) trained["status"]="native_completion_failed";
    precondition=state();''')
  body=body.replace('writeResult({{"status","recorded"}', 'writeResult({{"training_precondition",precondition},{"status","recorded"}')
  t=t[:a]+body+t[b:]
 p.write_text(t,encoding='utf8')
 p=ROOT/'Scripts/ClassicStructTrain/training_replay.inc';t=p.read_text(encoding='utf8')
 if 'file_controller' not in t:t=t.replace(' const auto job=manifest.at("repro_job");\n kind=', ' const auto job=manifest.at("repro_job");\n if(job.value("file_controller",false)){reproFileProtocol();return;}\n kind=')
 p.write_text(t,encoding='utf8')

def file_jobs():
 dataset=load(BASE)['dataset'];seq=[dataset[i-1] for i in [22,64,111]]
 common={'kind':'learner','target_id':22,'target_class':1,'cold_mode_override':1,'file_sequence':seq,
  'interpretation':'Archived boundary conditions with explicitly assumed file hook before environment tick; missing historical ACalculate call chain is a limitation'}
 jobs=[]
 external={**common,'id':'file-external','file_controller':False,'stages':[{'pattern':s['pattern'],'target_id':s['id'],'target_class':s['class'],'iterations':0} for s in seq[1:]]}
 jobs.append(external)
 for ident,trailing,truncate in [('file-trailing',True,False),('file-no-trailing',False,False),('file-truncated',True,True)]:
  jobs.append({**common,'id':ident,'file_controller':True,'trailing_newline':trailing,'truncate_last':truncate})
 save(WORK/'file-protocol-definitions.json',jobs);return jobs

def engine_controls():
 tasks=[]
 for kind,target in [('learner',22),('trainer',111)]:
  source=CONFIG/'InferenceJobs/V1C/pilot/reference-own'/(kind+'-'+str(target)+'-r1.json')
  original=load(source)
  for label,backend,reset,preserve in [('baseline','VB',False,False),('reset','VB',True,False),('native-order','VB',False,True),('order-disabled','FO',False,True),('order-explicit','FO',False,False),('reversal','VB',False,False)]:
   name=kind+'-'+str(target)+'-'+label;out=WORK/'engine-controls'/name
   if (out/'process.json').exists() and load(out/'process.json')['status']=='completed':continue
   manifest=copy.deepcopy(original);manifest['variant']=load(WORK/'variants'/(backend+'.json'));manifest['dataset']=load(BASE)['dataset']
   manifest['legacy_job'].update(id=name,independent_reset=reset,preserve_native_order=preserve,roundtrip=True)
   path=CONFIG/'EngineControls'/(name+'.json');save(path,manifest)
   tasks.append((ROOT/manifest['variant']['binary'],path,out))
 # Sequential within each measured controller choice; the immutable state does
 # not carry runtime activity from one process into another.
 for binary,manifest,out in tasks:supervise(binary,manifest,out,'legacy',1,0,660)

def run():
 start=time.monotonic()
 while not ((WORK/'factors/index.json').exists() and len(load(WORK/'factors/index.json'))==4 and git('branch','--show-current',repo=PULSE)=='classic-training-repro-initialization'):
  assert time.monotonic()-start<1800,'Factor sweep has not completed; no sources were edited'
  time.sleep(5)
 assert not git('status','--porcelain',repo=PULSE)
 prepare_controller()
 if not (WORK/'variants/VB.json').exists():build('VB')
 # These controls use immutable executables while later criterion binaries build.
 with ThreadPoolExecutor(max_workers=3) as pool:
  files=pool.submit(run_jobs,'VB',file_jobs(),'file-protocol',1)
  observer=pool.submit(run_jobs,'VB',[{'id':'learner-111-observer-off','kind':'learner','target_id':111,'target_class':3}],'observer',1)
  mode_checks=pool.submit(modes,'VB',3)
  for variant,crossing in [('FZ',False),('FZC',True)]:
   if not (WORK/'variants'/(variant+'.json')).exists():
    branch='classic-training-repro-stop-'+('crossing' if crossing else 'strict')
    exists=subprocess.run(['git','show-ref','--verify','--quiet','refs/heads/'+branch],cwd=PULSE).returncode==0
    subprocess.run(['git','switch',branch] if exists else ['git','switch','-c',branch,'8710978'],cwd=PULSE,check=True)
    if not exists:
     apply(crossing);subprocess.run(['git','add','--','Core'],cwd=PULSE,check=True);subprocess.run(['git','commit','-m','Research isolate '+('crossing-aware' if crossing else 'strict')+' amplitude stopping in Trainer'],cwd=PULSE,check=True)
    build(variant)
   run_jobs(variant,[{'id':'trainer-22','kind':'trainer','target_id':22,'target_class':1}],'stopping',3)
   inference(variant,'stopping',self_only=True,workers=1)
  subprocess.run(['git','switch','classic-training-repro-initialization'],cwd=PULSE,check=True)
  files.result();observer.result();mode_checks.result()
 run_jobs('VB',[{'id':kind+'-22','kind':kind,'target_id':22,'target_class':1} for kind in ['learner','trainer']],'factor-reversal',1)
 inference('VB','factor-reversal',self_only=True,workers=1)
 engine_controls()
 save(WORK/'post-controls-completion.json',{'completed':True,'file_jobs':4,'file_repeats':3,'observer_repeats':3,'stop_variants':['FZ','FZC'],'engine_controls':12})
 print('Completed file, observer, criterion, reversal and fixed-state engine controls')
if __name__=='__main__':run()
