"""Finish isolated criterion controls while immutable protocol binaries execute."""
import sys,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import ROOT,WORK,load,save,git,run_jobs,inference
from training_post_controls import build,engine_controls
from training_stop_variants import apply
PULSE=ROOT/'Libraries/Nmsdk-PulseLib'
def main():
 for variant,crossing in [('FZ',False),('FZC',True)]:
  if not (WORK/'variants'/(variant+'.json')).exists():
   branch='classic-training-repro-stop-'+('crossing' if crossing else 'strict')
   exists=subprocess.run(['git','show-ref','--verify','--quiet','refs/heads/'+branch],cwd=PULSE).returncode==0
   assert not git('status','--porcelain',repo=PULSE)
   subprocess.run(['git','switch',branch] if exists else ['git','switch','-c',branch,'8710978'],cwd=PULSE,check=True)
   if git('rev-parse','--short=7','HEAD',repo=PULSE)=='8710978':
    apply(crossing);subprocess.run(['git','add','--','Core'],cwd=PULSE,check=True);subprocess.run(['git','commit','-m','Research isolate '+('crossing-aware' if crossing else 'strict')+' amplitude stopping in Trainer'],cwd=PULSE,check=True)
   build(variant)
  run_jobs(variant,[{'id':'trainer-22','kind':'trainer','target_id':22,'target_class':1}],'stopping',3)
  inference(variant,'stopping',self_only=True,workers=1)
 subprocess.run(['git','switch','classic-training-repro-initialization'],cwd=PULSE,check=True)
 run_jobs('VB',[{'id':kind+'-22','kind':kind,'target_id':22,'target_class':1} for kind in ['learner','trainer']],'factor-reversal',1)
 inference('VB','factor-reversal',self_only=True,workers=1)
 engine_controls()
 save(WORK/'stopping-engine-controls-completion.json',{'completed':True,'variants':['FZ','FZC'],'engine_controls':12})
if __name__=='__main__':main()
