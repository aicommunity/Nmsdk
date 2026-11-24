"""Explicit historical sequence definitions and cohort execution."""
from pathlib import Path
import sys,copy,json,argparse
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import ROOT,WORK,CONFIG,BASE,load,save,run_jobs,make_manifest,sha
from run import supervise
def scheme_jobs():
 data=load(BASE)['dataset'];p=lambda i:data[i-1]['pattern'];subset=list(range(41,61))+list(range(101,111));jobs=[]
 for scheme,count,ids,initial in [('3_4',7,subset,False),('0_1',17,subset,True),('0_1_4_subset',13,list(range(51,61)),True),('0_1_4_full',13,list(range(1,151)),True),('2_2',13,subset,True),('preliminary_1_4',6,subset,True),('preliminary_2_4',6,subset,True)]:
  job={'id':'scheme-'+scheme,'kind':'learner','target_id':51,'target_class':2,'scheme':scheme,'stages':[],'evaluate_initial':initial,'evaluation_ids':ids,
       'interpretation':'Documented schedule' if not scheme.startswith('preliminary') and scheme!='2_2' else 'Explicit reconstruction; cycle count for 2/2 is a declared study setting, not a recovered historical endpoint'}
  for cycle in range(1,count+1):
   if scheme in ['3_4','2_2']:
    n=3 if scheme=='3_4' else 2
    if cycle>1:job['stages'].append({'pattern':p(51),'target_id':51,'target_class':2,'iterations':n,'evaluate':False,'cycle':cycle})
    job['stages'].append({'pattern':p(61),'target_id':61,'target_class':2,'iterations':4 if scheme=='3_4' else 2,'evaluate':True,'cycle':cycle,'source_state_index':cycle if not initial else cycle+1})
   elif scheme=='0_1':job['stages'].append({'pattern':p(61),'target_id':61,'target_class':2,'iterations':1,'evaluate':True,'cycle':cycle,'source_state_index':cycle+1})
   else:
    joint=2 if scheme=='preliminary_2_4' else 1
    job['stages'].append({'pattern':p(61),'target_id':61,'target_class':2,'iterations':joint,'evaluate':False,'cycle':cycle})
    job['stages'].append({'pattern':p(61),'target_id':61,'target_class':2,'iterations':4,'synapses_only':True,'evaluate':True,'cycle':cycle,'source_state_index':cycle+1})
  jobs.append(job)
 return jobs
def warm_job():
 sequence=load(BASE)['warm_sequence'];first=sequence[0]
 return {'id':'warm-91','kind':'learner','target_id':first['id'],'target_class':(first['id']-1)//50+1,'pattern':first['pattern'],
  'stages':[{'pattern':s['pattern'],'target_id':s['id'],'target_class':(s['id']-1)//50+1,'iterations':0,'evaluate':False,'transition_index':i} for i,s in enumerate(sequence[1:],1)],'protocol':'Continuous archived 91-input file sequence including first rounded input, all 90 directed transitions'}
def execute(variant,cohort,workers):
 jobs=[warm_job()] if cohort=='warm' else scheme_jobs()
 save(WORK/'protocol-definitions.json',{'warm':warm_job(),'schemes':scheme_jobs(),
  'notes':['3/4 has seven evaluations after training cycles; its first archived snapshot is not the initial neuron for input 51.','0/1 has eighteen evaluations including the initial state, hence seventeen additional iterations.','The 2/2 evaluation count is a declared diagnostic continuation; source describes the learning ratio but supplies no uniquely aligned numerical curve.','Preliminary variants are explicit alternative reconstructions and are not selected by closeness to the historical curve.']})
 run_jobs(variant,jobs,cohort,workers)
def modes(variant,workers=1):
 v=load(WORK/'variants'/(variant+'.json'));m=make_manifest(variant,{'id':'modes','kind':'learner','target_id':22,'target_class':1})
 path=CONFIG/'Jobs'/variant/'modes.json';save(path,m)
 tasks=[]
 for repeat in range(1,4):
  out=WORK/'runs'/variant/'modes'/('modes-r'+str(repeat))
  if (out/'process.json').exists() and load(out/'process.json')['status']=='completed':continue
  tasks.append((out,repeat))
 with ThreadPoolExecutor(max_workers=workers) as pool:
  list(pool.map(lambda t:supervise(ROOT/v['binary'],path,t[0],'modes',t[1],0,660),tasks))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('cohort',choices=['warm','schemes','modes']);p.add_argument('--variant',default='VP');p.add_argument('--workers',type=int,default=1);a=p.parse_args()
 modes(a.variant,a.workers) if a.cohort=='modes' else execute(a.variant,a.cohort,a.workers)
