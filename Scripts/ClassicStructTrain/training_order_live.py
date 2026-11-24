"""Paired order control: real training followed by inference in the same live model."""
from pathlib import Path
import sys,argparse
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import WORK,run_jobs,save
def main(kind=None):
 jobs=[{'id':k+'-22-live','kind':k,'target_id':22,'target_class':1,'evaluate_initial':True,
  'interpretation':'Controlled order factor; actual cold learning and continuous inference without saving or loading between them; compare separately with frozen common-reference inference'} for k in ([kind] if kind else ['learner','trainer'])]
 with ThreadPoolExecutor(max_workers=2) as pool:
  futures=[pool.submit(run_jobs,v,jobs,'order-live',1) for v in ['VB','FO']]
  for future in futures:future.result()
 save(WORK/('order-live-'+(kind or 'all')+'-completion.json'),{'completed':True,'variants':['VB','FO'],'real_training_attempts':len(jobs)*6,'live_evaluations':len(jobs)*6})
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--kind',choices=['learner','trainer']);a=p.parse_args();main(a.kind)
