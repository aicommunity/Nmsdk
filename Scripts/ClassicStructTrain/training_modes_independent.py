"""Run a historical mode case in a fresh process, isolating project-loader state."""
from pathlib import Path
import sys,argparse,copy
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import ROOT,WORK,CONFIG,BASE,load,save,make_manifest
from run import supervise
def main(case=None,repeat=None,workers=3):
 variant=load(WORK/'variants/VB.json');base=load(BASE);tasks=[]
 for item in base['mode_cases']:
  if case and item['case']!=case:continue
  for rep in ([repeat] if repeat else [1,2,3]):
   name=item['case']+'-r'+str(rep);output=WORK/'runs/VB/modes-isolated'/name
   if (output/'process.json').exists() and load(output/'process.json')['status']=='completed':continue
   assert not output.exists() or not any(output.iterdir()),'Unfinished case is preserved'
   manifest=make_manifest('VB',{'id':name,'kind':'learner','target_id':22,'target_class':1});manifest['mode_cases']=[item]
   path=CONFIG/'ModesIndependent'/(name+'.json');save(path,manifest);tasks.append((path,output,rep))
 with ThreadPoolExecutor(max_workers=workers) as pool:
  list(pool.map(lambda t:supervise(ROOT/variant['binary'],t[0],t[1],'modes',t[2],0,660),tasks))
 print('Completed fresh-process mode attempts:',len(tasks))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--case');p.add_argument('--repeat',type=int);p.add_argument('--workers',type=int,default=3);a=p.parse_args();main(a.case,a.repeat,a.workers)
