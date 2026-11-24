"""Exhaustive result or reason ledger and objective evidence completion gate."""
from pathlib import Path
import sys,json,collections,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import ROOT,WORK,BASE,load,save,sha,verify_lock,pilot_jobs,state_identity
from training_protocols import scheme_jobs,warm_job
from training_report_data import lines,inference_result

def main():
 verify_lock();base=load(BASE);ledger=[];pending=[];errors=[];evidence=[]
 unavailable={'V0':'Исходный вариант не инициализирует динамический граф в пилоте; зависимые массовые серии не запускались',
  'V2':'Пилот: 0 из 27 собственных входов распознаны после сохранения и загрузки; функциональное предусловие расширения не выполнено',
  'V3':'Частичная архивная реконструкция: 0 из 27 собственных входов распознаны; функциональное предусловие расширения не выполнено'}
 cache={}
 def read(folder):
  key=str(folder)
  if key not in cache:cache[key]=lines(folder/'results.jsonl')
  return cache[key]
 coldjobs=[{'id':k+'-'+str(i),'kind':k,'target_id':i,'target_class':(i-1)//50+1} for k in ['learner','trainer'] for i in range(1,151)]
 coldjobs.append(next(j for j in pilot_jobs() if j['target_id']==0))
 def find_training(variant,cohort,job,repeat,stage=0):
  phases=['pilot','ten','full'] if cohort=='cold' else ['warm-file-exact'] if variant=='VP1' and cohort=='warm' else [cohort]
  for phase in phases:
   folder=WORK/'runs'/variant/phase/(job+'-r'+str(repeat))
   rs=[r for r in read(folder) if r.get('record_type','training')=='training' and 'iterations' in r and r.get('stage_index',0)==stage]
   if rs:return rs[-1],folder,phase
  return None,None,None
 def result_row(family,cohort,job,repeat,stage=0,needs_inference=False):
  variant='VP1' if family=='V1C' and cohort in ['warm','schemes'] else 'VB' if family=='V1C' and cohort=='modes' else family
  row={'variant_family':family,'actual_variant':variant,'cohort':cohort,'job':job,'repeat':repeat,'stage':stage}
  r,folder,phase=find_training(variant,cohort,job,repeat,stage)
  if r:
   row.update(status=r['status'],iterations=r['iterations'],native_need_to_train=r.get('native_need_to_train'),directory=str(folder.relative_to(ROOT)).replace('\\','/'))
   meta=load(folder/'process.json');row['process_status']=meta['status']
   row['initialized']=not r.get('whole_initialization_audit',{}).get('uninitialized',[True])
   if meta['status']=='running':row['status']='pending_process_completion'
   elif r['status']=='completed' and not row['initialized']:errors.append({'row':row,'reason':'Completed training has an uninitialized graph'})
   if needs_inference and r['status']=='completed' and row['initialized']:
    ident=state_identity(folder,stage)
    for backend,label,length in [('reference-own','own',1),('reference','full',150)]:
     found=None
     for searchphase in [phase,'all']:
      candidate=WORK/'inference'/variant/searchphase/backend/ident
      inf,origin=inference_result(candidate)
      if inf is not None and len(inf.get('answers',[]))==length:found=(inf,origin);break
     if found:
      inf,origin=found;row[label+'_source']=origin;row[label+'_status']='completed';row[label+'_recognized']=inf['answers'][0] if length==1 else None
      if not inf.get('training_disabled') or not inf.get('structure_unchanged'):errors.append({'row':row,'reason':'Inference changed structure or enabled training'})
     else:row[label+'_status']='pending';pending.append({**row,'reason':'Missing '+label+' inference of completed saved checkpoint'})
   if row['status'].startswith('pending'):pending.append(row)
  elif family in unavailable:
   row.update(status='not_run_precondition',reason=unavailable[family])
  else:
   # An unsuccessful earlier stage legitimately prevents later stages; it does
   # not turn an otherwise still-running protocol into a completed negative.
   attempt=WORK/'runs'/variant/('warm-file-exact' if variant=='VP1' and cohort=='warm' else cohort)/(job+'-r'+str(repeat));rs=read(attempt)
   failure=next((x for x in rs if x.get('record_type')=='training' and x.get('status')!='completed'),None)
   if failure:row.update(status='not_run_previous_stage_failed',reason=failure['status'],failed_stage=failure.get('stage_index',0))
   else:row['status']='pending';pending.append(row)
  ledger.append(row);return row
 for family in ['V0','V1C','V2','V3']:
  for job in coldjobs:
   for repeat in range(1,4):result_row(family,'cold',job['id'],repeat,needs_inference=family=='V1C')
  warm=warm_job()
  for repeat in range(1,4):
   for stage in range(91):result_row(family,'warm',warm['id'],repeat,stage,needs_inference=family=='V1C')
  for job in scheme_jobs():
   for repeat in range(1,4):
    for stage in range(len(job['stages'])+1):
     checkpoint=stage==0 or job['stages'][stage-1].get('evaluate',False)
     row=result_row(family,'schemes',job['id'],repeat,stage,needs_inference=family=='V1C' and checkpoint)
     row['checkpoint']=checkpoint
     if not checkpoint:row['inference_plan']='Промежуточная совместная полуфаза; измеряется следующий предусмотренный протоколом контрольный снимок'
    if family=='V1C':
     attempt=WORK/'runs/VP1/schemes'/(job['id']+'-r'+str(repeat));rs=read(attempt)
     for stage in ([0] if job.get('evaluate_initial') else [])+[i+1 for i,s in enumerate(job['stages']) if s.get('evaluate')]:
      row={'variant_family':family,'actual_variant':'VP1','cohort':'in_protocol_inference','job':job['id'],'repeat':repeat,'stage':stage}
      inf=next((r for r in rs if r.get('record_type')=='evaluation_in_protocol' and r['stage_index']==stage),None)
      if inf:
       row.update(status='completed',TP=inf['TP'],FP=inf['FP'],FN=inf['FN'],TN=inf['TN'],directory=str(attempt.relative_to(ROOT)).replace('\\','/'))
       if not inf['training_disabled'] or not inf['structure_unchanged']:errors.append({'row':row,'reason':'In-protocol test changed structure or enabled training'})
      else:
       failure=next((r for r in rs if r.get('record_type')=='training' and r['status']!='completed'),None)
       if failure:row.update(status='not_run_previous_stage_failed',reason=failure['status'])
       else:row['status']='pending';pending.append(row)
      ledger.append(row)
  for repeat in range(1,4):
   actual='VB' if family=='V1C' else family
   for case in base['mode_cases']:
    attempt=WORK/'runs'/actual/('modes-isolated' if family=='V1C' else 'modes')/((case['case']+'-r'+str(repeat)) if family=='V1C' else 'modes-r'+str(repeat));rs=read(attempt)
    row={'variant_family':family,'actual_variant':actual,'cohort':'modes','job':case['case'],'repeat':repeat,'stage':0}
    r=next((r for r in rs if r['case']==case['case']),None)
    if r:
     row.update(status=r['status'],directory=str(attempt.relative_to(ROOT)).replace('\\','/'))
     if r.get('training_precondition') and r['training_precondition']['is_need_to_train']:errors.append({'row':row,'reason':'Mode precondition was not natively finalized'})
    elif family in unavailable:row.update(status='not_run_precondition',reason=unavailable[family])
    else:row['status']='pending';pending.append(row)
    ledger.append(row)
 # Process evidence and all actual terminal diagnostics, including negative
 # controls, are retained in addition to the planned matrix.
 binary_hashes={}
 all_processes=list((WORK/'runs').glob('*/*/*/process.json'))+list((WORK/'inference').glob('*/*/*/*/process.json'))+list((WORK/'engine-controls').glob('*/process.json'))+list((WORK/'geometry-engine-controls').glob('*/process.json'))+list((WORK/'prior-order-controls').glob('*/process.json'))
 for p in all_processes:
  m=load(p);binary=Path(m['command'][0]);
  if binary.parent.resolve()!=(ROOT/'Bin/Platform/Win').resolve() or Path(m['cwd']).resolve()!=binary.parent.resolve():errors.append({'process':str(p),'reason':'Unexpected runtime or CWD'})
  if binary not in binary_hashes:binary_hashes[binary]=sha(binary)
  if binary_hashes[binary]!=m['binary_sha256']:errors.append({'process':str(p),'reason':'Native executable changed'})
  if m['status']=='running':pending.append({'process':str(p),'reason':'Native process still running'})
  evidence.append({'file':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':sha(p),'status':m['status']})
 for name,key in [('post-controls-completion.json','completed'),('factor-inference-completion.json','completed'),('trace-controls-completion.json','completed'),('geometry-engine-completion.json','completed'),('prior-order-completion.json','completed'),('inference-reuse-audit.json','passed'),('physical-load-audit.json','passed')]:
  path=WORK/name
  if not path.exists() or not load(path).get(key):pending.append({'evidence':name,'reason':'Required independent diagnostic or audit is incomplete'})
 controls=load(WORK/'control-analysis.json') if (WORK/'control-analysis.json').exists() else {}
 if len(controls.get('order_live',[]))!=12:pending.append({'evidence':'order_live','reason':'Need twelve terminal NT/NL order-control attempts, with live inference or a concrete failed-training precondition'})
 counter=collections.Counter((r['variant_family'],r['cohort'],r['status']) for r in ledger)
 summary={'planned_rows':len(ledger),'pending_items':len(pending),'errors':len(errors),'by_group':[{'variant':v,'cohort':c,'status':s,'count':n} for (v,c,s),n in sorted(counter.items())],
  'all_planned_cases_have_result_or_reason':not pending,'note':'A negative result is complete evidence; a pending process or missing required inference is not.'}
 save(WORK/'coverage-ledger.json',ledger);save(WORK/'coverage-summary.json',summary)
 save(WORK/'completion-audit.json',{'passed':not pending and not errors,'pending':pending,'errors':errors,'process_evidence':evidence,'prior_evidence_unchanged':True})
 print(json.dumps({'planned_rows':len(ledger),'pending':len(pending),'errors':len(errors)},ensure_ascii=False))
if __name__=='__main__':main()
