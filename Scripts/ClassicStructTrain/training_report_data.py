"""Collect measured training, common inference and historical references without filling gaps."""
from pathlib import Path
import sys,json,statistics,hashlib,math
from collections import Counter,defaultdict
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import ROOT,WORK,OLD,SOURCE,load,save,verify_lock,state_identity
def lines(path):
 if not path.exists():return []
 result=[]
 for line in path.read_text(encoding='utf-8-sig').splitlines():
  try:result.append(json.loads(line))
  except json.JSONDecodeError:continue
 return result
def inference_result(folder):
 seen=set()
 while (folder/'reuse.json').exists() and not ((folder/'process.json').exists() and load(folder/'process.json')['status']=='completed' and (folder/'results.jsonl').exists()):
  assert folder not in seen,'Inference reuse cycle';seen.add(folder);folder=ROOT/load(folder/'reuse.json')['source']
 rs=lines(folder/'results.jsonl')
 return (rs[-1] if rs else None),str(folder.relative_to(ROOT)).replace('\\','/')
def metrics(r):
 tp,fp,fn,tn=[r.get(k,0) for k in ['TP','FP','FN','TN']]
 return {'TP':tp,'FP':fp,'FN':fn,'TN':tn,'Q':fp+fn,'precision':tp/(tp+fp) if tp+fp else None,
  'recall':tp/(tp+fn) if tp+fn else None,'BAcc':.5*(tp/(tp+fn)+tn/(tn+fp)) if tp+fn and tn+fp else None,
  'risk':(fp+fn)/(tp+fp+fn+tn) if tp+fp+fn+tn else None}
def collect():
 verify_lock();science=load(OLD/'scientific-comparison-data.json');history=load(WORK/'history.json');records=[];processes=[]
 archive=load(ROOT/'Reports/StructTrainClassic/archive-evidence.json');previous_assessment=load(OLD/'assessment.json')
 previous_jobs={j['id']:j for p in (ROOT/'Bin/Configs/StructTrainClassic/LegacyInference').glob('*-jobs.json') for j in load(p) if isinstance(j,dict) and 'id' in j}
 for p in sorted((WORK/'runs').glob('*/*/*/process.json')):
  meta=load(p);variant=p.parents[2].name;phase=p.parents[1].name
  processes.append({'variant':variant,'phase':phase,'directory':str(p.parent.relative_to(ROOT)).replace('\\','/'),**meta})
  for r in lines(p.parent/'results.jsonl'):
   r['variant_id']=variant;r['phase']=phase;r['directory']=str(p.parent.relative_to(ROOT)).replace('\\','/');records.append(r)
 training=[r for r in records if r.get('record_type','training')=='training' and 'iterations' in r]
 cold=[r for r in training if r['variant_id']=='V1C' and r['phase'] in ['pilot','ten','full']]
 evaluations=[r for r in records if r.get('record_type')=='evaluation_in_protocol' and r['variant_id']=='VP1' and r['phase']=='schemes']
 modes=[r for r in records if r.get('suite')=='modes' and r['variant_id']=='VB' and r['phase']=='modes-isolated']
 for r in modes:
  source=next((x for x in archive['modes'] if x['case']==r['case']),None)
  r['historical_cells']=source['values'] if source else None
 for r in evaluations:
  ident=state_identity(ROOT/r['directory'],r['stage_index'])
  inf,origin=inference_result(WORK/'inference/VP1/all/reference'/ident)
  if inf and len(inf.get('answers',[]))==150:
   ids=r.get('input_ids',r['job']['evaluation_ids']);answers=[inf['answers'][i-1] for i in ids];counts={k:0 for k in ['TP','FP','FN','TN']}
   for i,answer in zip(ids,answers):counts[('T' if answer==int((i-1)//50+1==r['job']['target_class']) else 'F')+('P' if answer else 'N')]+=1
   r['common_reference']={'metrics_full':metrics(inf),'metrics_same_ids':metrics(counts),'same_ids':ids,'answers_same_ids':answers,'source':origin,
    'live_mismatch_ids':[i for i,a,b in zip(ids,r['answers'],answers) if a!=b],
    'scope':'Same selected IDs in original relative order; loaded full-150 continuous pass has preceding stimuli and resets differing from live protocol. This is a context comparison, not an isolated save/load effect.'}
 preliminary_modes=[r for r in records if r.get('suite')=='modes' and r not in modes]
 by_model=defaultdict(list)
 for r in cold:
  job=r['job'];key=(job['kind'],job.get('target_id',0));row={'kind':key[0],'target':key[1],'label':('NL' if key[0]=='learner' else 'NT')+(str(key[1]) if key[1] else ' среднее 51 и 61'),
   'repeat':r['repeat'],'status':r['status'],'iterations':r['iterations'],'native_stopped':not r['native_need_to_train'],
   'dendrites':r['dendrites'],'synapses':r['synapses'],'initialized':not r['whole_initialization_audit']['uninitialized'],
   'directory':r['directory'],'training_wall_seconds':r['elapsed_wall_seconds']}
  for cohort in [r['phase'],'all']:
   folder=WORK/'inference/V1C'/cohort/'reference-own'/Path(r['directory']).name
   own,origin=inference_result(folder)
   if own:row['own_answer']=own.get('answers',[None])[0];row['own_peak']=own.get('peaks',[None])[0];row['own_source']=origin;break
  for cohort in [r['phase'],'all']:
   folder=WORK/'inference/V1C'/cohort/'reference'/Path(r['directory']).name
   inf,origin=inference_result(folder)
   if inf and len(inf.get('answers',[]))==150:
    row['inference']=inf;row['metrics']=metrics(inf);row['inference_source']=origin;break
  by_model[key].append(row)
 model_rows=[]
 for (kind,target),rs in sorted(by_model.items()):
  unique={(tuple(r['dendrites']),tuple(r['synapses'])) for r in rs};has=[r for r in rs if 'metrics' in r]
  model_rows.append({'kind':kind,'target':target,'label':rs[0]['label'],'repeats':len(rs),'structural_variants':len(unique),'runs':rs,
   'all_native_stopped':all(r['native_stopped'] for r in rs),'all_initialized':all(r['initialized'] for r in rs),
   'own_checks':sum('own_answer' in r for r in rs),'own_recognized':sum(r.get('own_answer')==1 for r in rs),
   'complete_inferences':len(has),'mean_BAcc':statistics.mean(r['metrics']['BAcc'] for r in has) if has else None,
   'mean_Q':statistics.mean(r['metrics']['Q'] for r in has) if has else None,
   'mean_iterations':statistics.mean(r['iterations'] for r in rs)})
 cohort_performance=[]
 for kind in ['trainer','learner']:
  for target_class in [1,2,3]:
   selected=[m for m in model_rows if m['kind']==kind and m['target']>0 and (m['target']-1)//50+1==target_class]
   measured=[next((r for r in sorted(m['runs'],key=lambda r:r['repeat']) if r.get('metrics')),None) for m in selected];measured=[r for r in measured if r]
   b=[r['metrics']['BAcc'] for r in measured];q=[r['metrics']['Q'] for r in measured]
   cohort_performance.append({'kind':kind,'target_class':target_class,'models_measured':len(measured),'models_planned':50,'median_BAcc':statistics.median(b) if b else None,'min_BAcc':min(b) if b else None,'max_BAcc':max(b) if b else None,'median_Q':statistics.median(q) if q else None,'scope':'One first completed measured repeat per training object; target class groups are separate; each model is tested on all 150 objects'})
 recognition=[]
 for old in science['recognition']:
  label=old['label'];kind='learner' if label.startswith('NL') else 'trainer'
  import re
  target=int(re.search(r'\d+',label).group());new=next((r for r in model_rows if r['kind']==kind and r['target']==target),None)
  raw=next((r for r in archive['recognition'] if r['source_range']==old['range']),None)
  prior=previous_assessment['first_by_job'].get(old['job'])
  prior_native=next((r for r in lines(ROOT/prior['directory']/'results.jsonl') if r.get('answers')==prior['answers']),None) if prior else None
  assert prior is None or prior_native is not None,'Previous physical signals must use the same native observation as its published answers'
  if prior_native:assert len(prior_native['peaks'])==150 and len(prior_native['first_spikes'])==150
  prior_job=previous_jobs.get(old['job'])
  newrun=next((r for r in new['runs'] if 'inference' in r),None) if new else None
  historical_answers=raw['answers'] if raw else None;previous_answers=prior.get('answers') if prior else None;new_answers=newrun['inference']['answers'] if newrun else None
  assert historical_answers is None or len(historical_answers)==150
  recognition.append({'label':label,'kind':kind,'target':target,'historical':old.get('old',{}),'previous':old.get('new',{}),'new':new,
   'source_range':old['range'],'historical_answers':historical_answers,'previous_answers':previous_answers,'new_answers':new_answers,
   'previous_peaks_V':prior_native.get('peaks') if prior_native else None,'previous_first_spikes_seconds':prior_native.get('first_spikes') if prior_native else None,
   'previous_native_source':str(Path(prior['directory'])/'results.jsonl').replace('\\','/') if prior else None,
   'new_peaks_V':newrun['inference'].get('peaks') if newrun else None,'new_first_spikes_seconds':newrun['inference'].get('first_spikes') if newrun else None,
   'previous_structure':{'dendrites':prior_job.get('dendrites'),'synapses':prior_job.get('synapses'),'origin':prior_job.get('origin'),'config':prior_job.get('config')} if prior_job and prior_job.get('dendrites') and prior_job.get('synapses') else None,
   'historical_new_mismatch_ids':[i+1 for i,(a,b) in enumerate(zip(historical_answers,new_answers)) if a!=b] if historical_answers is not None and new_answers is not None else None,
   'previous_new_mismatch_ids':[i+1 for i,(a,b) in enumerate(zip(previous_answers,new_answers)) if a!=b] if previous_answers is not None and new_answers is not None else None})
 causes=[]
 groups=defaultdict(list)
 for r in training:groups[r['variant_id']].append(r)
 def cnt(v,status=None):return sum(status is None or r['status']==status for r in groups[v])
 baseline=sum(r['variant_id']=='V0G' and r['phase']=='causal' and r['status']=='uninitialized_dynamic_structure' for r in training);restored=cnt('R0','completed')
 reversal=sum(r['variant_id']=='V0G' and r['phase']=='causal_reversal' and r['status']=='uninitialized_dynamic_structure' for r in training)
 causes.append({'factor':'Автоматическая инициализация Rdk','status':'Подтверждено экспериментом' if baseline>=18 and restored>=18 else 'Поддерживается ограниченными данными',
  'finding':f'Парный контроль без Init: {baseline} остановок на неинициализированном графе. Возврат исторического Init: {restored} завершённых обучений без изменения PulseLib. Повторное выключение Init: {reversal} повторных отказа.',
  'boundary':'Объясняет сбой динамической инициализации в проверенных случаях. Сам по себе не объясняет все отличия инференса архивных состояний.',
  'source':'Rdk 35f7065ac, 01.01.2026; runs/V0G/causal, runs/R0/causal, runs/V0G/causal_reversal'})
 gates={p.stem:load(p) for p in (WORK/'gates').glob('*.json')}
 causes.append({'factor':'Синаптические параметры и порог','status':'Подтверждено экспериментом' if gates.get('V1C',{}).get('own_recognized')==27 and gates.get('V2',{}).get('own_recognized')==0 else 'Поддерживается ограниченными данными',
  'finding':'Совместное изменение исторических параметров снижает калибровочную амплитуду ниже фиксированного порога 11,5 мВ; отдельные параметры проверяются независимо.',
  'boundary':'Это результат сочетания данного профиля и текущего механизма обучения. Он не доказывает ошибочность исторических запусков с неизвестными полными настройками.',
  'source':'PulseLib 5f3f06d и 0be546f; пилоты V1C/V2; контроль V2 в двух версиях инференса'})
 causes.append({'factor':'Завершение контроллером и алгоритмом','status':'Подтверждено экспериментом',
  'finding':'Нулевые структурные статусы NL наблюдаются за один такт до снятия IsNeedToTrain методом EndOfLearning. В основных новых сериях завершающий такт выполнен самим компонентом.',
  'boundary':'Предварительный V1 сохранён как отдельный контроль. Нулевой статус без завершающего такта не выдаётся за штатное завершение.',
  'source':'training_replay.inc; runs/V1/pilot; runs/V1C/pilot'})
 causes.append({'factor':'Полнота исторического алгоритма','status':'Не установлено',
  'finding':'Архивный цикл 2022 года и наиболее ранние доступные функции решений 2023 года имеют разное происхождение. V3 является частичной реконструкцией.',
  'boundary':'Полная исходная программа конкретного исторического запуска не идентифицирована. Сходство структуры не используется как доказательство её восстановления.',
  'source':'history.json; variants/V3-adaptation.json'})
 factor_rows=[]
 for v in ['FS','FD','FR','FO']:
  for r in groups[v]:
   folder=WORK/'inference'/v/'factor/VB-own'/Path(r['directory']).name;own,origin=inference_result(folder)
   full,full_origin=inference_result(WORK/'inference'/v/'factor/reference'/Path(r['directory']).name)
   factor_rows.append({'variant':v,'kind':r['job']['kind'],'repeat':r['repeat'],'status':r['status'],'iterations':r['iterations'],
    'dendrites':r['dendrites'],'synapses':r['synapses'],'calibration':r.get('initial_soma_potential',r.get('NT_initial_dendrite_potential',r.get('initial_dendrite_potential'))),
    'own_answer':own['answers'][0] if own else None,'own_peak':own['peaks'][0] if own else None,
    'own_zone_mV':own['zone_potential_peaks'][0]*1000 if own and own.get('zone_potential_peaks') else None,
    'full_metrics':metrics(full) if full else None,
    'full_answers':full.get('answers') if full else None,'full_source':str(full_origin) if full_origin else None,'directory':r['directory']})
 summary={'native_processes':len(processes),'process_statuses':dict(Counter(p['status'] for p in processes)),
  'cold_attempts':len(cold),'cold_expected':903,'cold_models':len(model_rows),'cold_expected_models':301,'cold_statuses':dict(Counter(r['status'] for r in cold)),
  'full_inferences_available':sum(r['complete_inferences'] for r in model_rows),'own_checks_available':sum(r['own_checks'] for r in model_rows),
  'own_recognized':sum(r['own_recognized'] for r in model_rows),'confirmed_learning_attempts':sum(r['status']=='completed' and r['native_stopped'] and r['initialized'] and r.get('own_answer')==1 for m in model_rows for r in m['runs']),
  'in_protocol_evaluations':len(evaluations),'mode_observations':len(modes),'gates':gates}
 summary['native_training_protocol_processes']=len(processes)
 summary['cold_process_wall_seconds']=sum(p.get('elapsed_wall_seconds',0) for p in processes if p['variant']=='V1C' and p['phase'] in ['pilot','ten','full'])
 # Real training trace of NL111, iterations 6--10. Time is explicitly aligned
 # to the first maximum, never presented as recovered absolute historical time.
 digitized=load(OLD/'digitized-waves.json');hist=next(r for r in digitized if r['id']=='H111NL')
 trace=[r for r in lines(WORK/'runs/V1C/pilot/learner-111-r1/waveforms.jsonl') if 5<=r.get('iteration',-1)<=9]
 waveform=None
 if trace:
  from bisect import bisect_left
  first=[r for r in trace if r['iteration']==5];anchor=max(first,key=lambda r:r['soma_potential'][0])['time']
  a=[(p['time']-hist['first_peak_time'],p['potential']*1000) for p in hist['points']]
  b=[(p['time']-anchor,p['soma_potential'][0]*1000) for p in trace]
  def interp(points,t):
   xs=[p[0] for p in points];j=bisect_left(xs,t)
   if j==0:return points[0][1] if t>=xs[0] else None
   if j>=len(points):return None
   x0,y0=points[j-1];x1,y1=points[j];return y0+(y1-y0)*(t-x0)/(x1-x0)
  lo=max(a[0][0],b[0][0]);hi=min(a[-1][0],b[-1][0]);times=[lo+i*.002 for i in range(int((hi-lo)/.002)+1)]
  waveform={'source':hist['source'],'source_image':hist['image'],'source_image_sha256':hist['image_sha256'],
   'historical_anchor_seconds':hist['first_peak_time'],'new_anchor_seconds':anchor,'step_seconds':.002,
   'historical_voltage_uncertainty_mV':max(p['potential_uncertainty'] for p in hist['points'])*1000,
   'historical_time_uncertainty_seconds':max(p['time_uncertainty'] for p in hist['points']),
   'rows':[[t,interp(a,t),interp(b,t)] for t in times],
   'new_iteration_maxima_mV':[max(r['soma_potential'][0] for r in trace if r['iteration']==i)*1000 for i in range(5,10)],
   'interpretation':'Сопоставление действительных наблюдений обучения. Выполнен только перенос начала времени к первому максимуму. Амплитуда не нормирована, масштаб времени не растянут. Линейная интерполяция применяется только для общей сетки рисунка.'}
 primary_comparisons=[]
 for source in science['primary_source']['rows']:
  kind='learner' if source['algorithm']=='NL' else 'trainer';model=next((m for m in model_rows if m['kind']==kind and m['target']==source['input_id']),None)
  rs=model['runs'] if model else [];run=next((r for r in sorted(rs,key=lambda r:r['repeat']) if r['status']=='completed' and r['native_stopped'] and r['initialized']),None)
  old_d=source['dendrites'];old_s=source['effective_synapses'];new_d=run['dendrites'] if run else None;new_s=run['synapses'] if run else None
  primary_comparisons.append({'record':source['record'],'id':source['input_id'],'algorithm':source['algorithm'],'old_d':old_d,'old_s':old_s,
   's_provenance':'Дополнены по прямому свидетельству' if source['donors'] else 'Исходные ячейки' if old_s else 'Неизвестны',
   'new_d':new_d,'new_s':new_s,'d_delta':[a-b for a,b in zip(new_d,old_d)] if new_d else None,'s_delta':[a-b for a,b in zip(new_s,old_s)] if new_s and old_s else None,
   'length_range':source['length_range'],'synapse_range':source['synapse_range'],'donors':source['donors'],'new_repeats':len(rs),'new_selected_repeat':run['repeat'] if run else None,'new_status':run['status'] if run else None,'new_inference_BAcc':run.get('metrics',{}).get('BAcc') if run else None,
   'new_directory':run['directory'] if run else None,'comparison_scope':'Известная структура источника и первый штатно завершённый повтор нового обучения тому же ID; ограниченные попытки сохраняются отдельно, старые реакции при отсутствии не подставляются'})
 warm_comparisons=[]
 from training_protocols import warm_job
 warm_definition=warm_job()
 for repeat in [1,2,3]:
  old_rows=[r for r in archive['warm'] if r['repeat']==repeat]
  new_rows=sorted([r for r in training if r['variant_id']=='VP1' and r['phase']=='warm-file-exact' and r['repeat']==repeat and r.get('stage_index',0)>0],key=lambda r:r['stage_index'])
  for index,old in enumerate(old_rows,1):
   new=next((r for r in new_rows if r['stage_index']==index),None);stage=warm_definition['stages'][index-1]
   rounding_delta=max(abs(a-b) for a,b in zip(old['pattern'],stage['pattern']))
   assert all(round(a,4)==b for a,b in zip(old['pattern'],stage['pattern'])),'Archived file stimulus does not match rounded source object'
   before=warm_definition['target_id'] if index==1 else warm_definition['stages'][index-2]['target_id']
   warm_comparisons.append({'repeat':repeat,'transition':index,'from_id':before,'to_id':stage['target_id'],'old':old,'new':new,'stimulus_source':'Archived input_data.txt, four decimal digits','max_table_file_difference_seconds':rounding_delta,
    'd_delta':[a-b for a,b in zip(new['dendrites'],old['dendrites'])] if new else None,'s_delta':[a-b for a,b in zip(new['synapses'],old['synapses'])] if new else None,
    'iteration_delta':new['iterations']-old['iterations'] if new else None})
 controls=load(WORK/'control-analysis.json') if (WORK/'control-analysis.json').exists() else {}
 causes+=controls.get('causes',[])
 from training_waveforms import collect as collect_waveforms
 additional_waveforms=collect_waveforms()
 variants=[load(p) for p in (WORK/'variants').glob('*.json') if 'binary' in load(p)]
 out={'summary':summary,'cohort_performance':cohort_performance,'variants':variants,'source_availability':load(WORK/'source-availability.json') if (WORK/'source-availability.json').exists() else [],'models':model_rows,'recognition':recognition,'history':history,'causes':causes,'factors':factor_rows,'waveform':waveform,'additional_waveforms':additional_waveforms,'controls':controls,'primary_comparisons':primary_comparisons,
  'protocol_evaluations':evaluations,'protocol_training':[{**r,'actual_phase':r['phase'],'phase':'warm' if r['phase']=='warm-file-exact' else r['phase']} for r in training if r['variant_id']=='VP1' and r['phase'] in ['warm-file-exact','schemes']],
  'warm_dataset_initial_controls':[r for r in training if r['variant_id']=='VP1' and r['phase']=='warm'],'warm_comparisons':warm_comparisons,'modes':modes,'preliminary_modes':preliminary_modes,
  'pilot_training':[r for r in training if r['phase'] in ['pilot','factor','causal','causal_reversal']],
  'scientific_reference':{'epochs':science['epochs'],'baselines':science['baselines'],'figures':science['figures'],'primary_source':science['primary_source']}}
 save(WORK/'report-data.json',out);print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':collect()
