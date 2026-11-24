"""Build and measure one-factor research branches; binaries remain immutable."""
from pathlib import Path
import sys,subprocess,shutil
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import ROOT,WORK,load,save,git,package,run_jobs,inference
from training_variants import single_factor
SHELL=shutil.which('pwsh') or 'powershell.exe'
def run():
 results=[]
 for variant,factor in [('FS','secretion'),('FD','dissociation'),('FR','resistance'),('FO','order')]:
  repo=ROOT/'Libraries/Nmsdk-PulseLib';branch='classic-training-repro-'+factor
  if not (WORK/'variants'/(variant+'.json')).exists():
   assert not git('status','--porcelain',repo=repo),'PulseLib has uncommitted changes'
   exists=subprocess.run(['git','show-ref','--verify','--quiet','refs/heads/'+branch],cwd=repo).returncode==0
   subprocess.run(['git','switch',branch] if exists else ['git','switch','-c',branch,'8710978'],cwd=repo,check=True)
   if exists:
    assert git('log','-1','--format=%s',repo=repo)=='Research isolated '+factor+' factor in classic training','Unexpected existing research branch'
   else:
    single_factor(factor)
    subprocess.run(['git','add','--','Core'],cwd=repo,check=True)
    subprocess.run(['git','commit','--quiet','-m','Research isolated '+factor+' factor in classic training'],cwd=repo,check=True)
   log=WORK/('build-factor-'+variant+'.log')
   with log.open('w',encoding='utf8') as out:
    result=subprocess.run([SHELL,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'Scripts/ClassicStructTrain/training_build.ps1')],cwd=ROOT,stdout=out,stderr=subprocess.STDOUT)
   if result.returncode:
    save(WORK/'factors'/(variant+'-build.json'),{'status':'failed','log':str(log.relative_to(ROOT))});raise RuntimeError('Factor build failed: '+variant)
   package(variant)
  jobs=[{'id':kind+'-22','kind':kind,'target_id':22,'target_class':1} for kind in ['learner','trainer']]
  run_jobs(variant,jobs,'factor',workers=1)
  inference(variant,'factor',self_only=True,workers=1)
  results.append({'variant':variant,'factor':factor,'metadata':load(WORK/'variants'/(variant+'.json'))})
  save(WORK/'factors/index.json',results)
 subprocess.run(['git','switch','classic-training-repro-initialization'],cwd=ROOT/'Libraries/Nmsdk-PulseLib',check=True)
if __name__=='__main__':run()
