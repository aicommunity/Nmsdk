"""History-grounded causal controls and independent verification of study gates."""
from pathlib import Path
import sys,json,subprocess,copy,hashlib,statistics
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import ROOT,WORK,CONFIG,OLD,load,save,git,sha,run_jobs,make_manifest,VARIANTS
def rdk_auto_init():
 p=ROOT/'Rdk/Core/Engine/UContainer.cpp';t=p.read_text(encoding='utf8');needle='// Оптимизация: убрали избыточный вызов Init() - проверка InitFlag выполняется ниже'
 assert t.count(needle)==1
 t=t.replace(needle,'Init(); // Research control: restore the call removed by 35f7065ac on 2026-01-01.')
 p.write_text(t,encoding='utf8')
 old=subprocess.check_output(['git','show','7d761e2223fdd069ef501fd66f8d6ba70a77147c:Core/Engine/UContainer.cpp'],cwd=ROOT/'Rdk')
 start=old.index(b'bool UContainer::Calculate(void)');snippet=old[start:start+650]
 patch=subprocess.check_output(['git','show','35f7065ac','--','Core/Engine/UContainer.cpp'],cwd=ROOT/'Rdk')
 (WORK/'history/rdk-35f7065ac.patch').write_bytes(patch)
 save(WORK/'history/rdk-lifecycle.json',{'removal_commit':'35f7065ac480c431b91ece981afbf501a8516d56','removal_date':'2026-01-01','old_rdk_sha':'7d761e2223fdd069ef501fd66f8d6ba70a77147c',
  'old_root_sha':'bc635671441fe8842299aee86ce0c3bd37acaea9','old_source_sha256':hashlib.sha256(old).hexdigest(),
  'old_calculate_start':snippet.decode('cp1251'),'restored_statement':'Init();','causal_status':'Awaiting paired native control; history alone is insufficient'})
 print('Restored only the historical automatic Init call in Calculate')
def gate(variant):
 paths=list((WORK/'runs'/variant/'pilot').glob('*/results.jsonl'));records=[json.loads(p.read_text().splitlines()[0]) for p in paths if p.stat().st_size]
 own=[]
 for p in (WORK/'inference'/variant/'pilot/reference-own').glob('*/results.jsonl'):
  if p.stat().st_size:own.append(json.loads(p.read_text().splitlines()[-1]))
 result={'variant':variant,'training_records':len(records),'own_checks':len(own),
  'initialized':sum(not r['whole_initialization_audit']['uninitialized'] for r in records),'native_stopped':sum(not r['native_need_to_train'] for r in records),
  'own_recognized':sum(r.get('answers')==[1] for r in own),'inference_structure_unchanged':all(r['structure_unchanged'] for r in own),
  'passed':len(records)==27 and len(own)==27 and all(r['status']=='completed' and not r['native_need_to_train'] and not r['whole_initialization_audit']['uninitialized'] for r in records) and all(r.get('answers')==[1] and r['structure_unchanged'] for r in own)}
 times=[load(p.parent/'process.json')['elapsed_wall_seconds'] for p in paths if p.stat().st_size and 'elapsed_wall_seconds' in load(p.parent/'process.json')]
 if times:result['estimate']={'pilot_median_process_seconds':statistics.median(times),'cold_attempts_total':903,'reused_pilot_attempts':27,'cold_expected_worker_seconds':statistics.mean(times)*876,'note':'Estimate depends on concurrent load; excludes full inference and multi-input series'}
 if not result['passed']:result['reason']='Functional precondition was not met; retain pilot data and investigate instead of expanding to the complete matrix'
 save(WORK/'gates'/(variant+'.json'),result);print(json.dumps(result,ensure_ascii=False,indent=2));return result
def causal_jobs(variant,phase='causal'):
 # Same targets, three actual native repeats. The extra tick observes whether
 # the historical Rdk just-in-time initialization contract takes effect.
 from training_repro import BASE
 jobs=[{'id':k+'-'+str(i),'kind':k,'target_id':i,'target_class':(i-1)//50+1,'allow_initialization_grace_tick':True} for k in ['learner','trainer'] for i in [22,64,111]]
 run_jobs(variant,jobs,phase,workers=1)
def physical_after_inference():
 from legacy_recover import physical
 failures=[];count=0
 processes=list((WORK/'inference').glob('*/*/*/*/process.json'))+list((WORK/'engine-controls').glob('*/process.json'))+list((WORK/'geometry-engine-controls').glob('*/process.json'))
 for p in processes:
  meta=load(p)
  if meta['status']!='completed':continue
  manifest=load(meta['command'][meta['command'].index('--manifest')+1]);config=ROOT/manifest['legacy_job']['config']
  a=physical(__import__('xml.etree.ElementTree',fromlist=['parse']).parse(config.parent/'Model_00.xml').getroot())
  b=physical(__import__('xml.etree.ElementTree',fromlist=['parse']).parse(p.parent/'loaded/Model_00.xml').getroot())
  diff=[]
  if a['links']!=b['links']:diff.append('links')
  if a['nodes']!=b['nodes']:
   for name in a['nodes'].keys()|b['nodes'].keys():
    if a['nodes'].get(name)!=b['nodes'].get(name):diff.append(name)
  save(p.parent/'physical-load-audit.json',{'passed':not diff,'differences':diff,'nodes':len(a['nodes']),'links':len(a['links'])})
  count+=1
  if diff:failures.append({'process':str(p.relative_to(ROOT)),'differences':diff})
 save(WORK/'physical-load-audit.json',{'count':count,'failures':failures,'passed':not failures});print('Physical load checks',count,'failures',len(failures))
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('action',choices=['rdk-auto-init','gate','causal','physical-load']);p.add_argument('--variant',default='V1C');args=p.parse_args()
 if args.action=='rdk-auto-init':rdk_auto_init()
 elif args.action=='gate':gate(args.variant)
 elif args.action=='physical-load':physical_after_inference()
 else:causal_jobs(args.variant)
