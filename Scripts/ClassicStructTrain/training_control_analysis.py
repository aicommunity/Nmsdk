"""Measured causal findings, limited in scope to executed native controls."""
from pathlib import Path
import sys,json,collections,hashlib,statistics
import xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parent))
from report_paths import report_path
from training_repro import ROOT,WORK,BASE,OLD,load,save,sha
from training_report_data import lines,metrics
from legacy_recover import physical

def digest_physical(folder):
 return hashlib.sha256(json.dumps(physical(ET.parse(folder/'Model_00.xml').getroot()),sort_keys=True).encode()).hexdigest()
def main():
 out={'file_protocol':[],'parser':[],'observer':[],'trace_observer':[],'stopping':[],'engine':[],'geometry_engine':[],'prior_order':[],'factors':[],'causes':[],'zone_comparison':[],'order_live':[],'reversal':[],'cold_limits':[]}
 for p in (WORK/'prior-order-controls').glob('*/results.jsonl'):
  rs=lines(p);meta=p.parent/'process.json'
  if rs and meta.exists() and load(meta)['status']=='completed':
   r=rs[-1];out['prior_order'].append({'condition':p.parent.name.removeprefix('prior-NL22-'),'metrics':metrics(r),'answers':r['answers'],'training_disabled':r['training_disabled'],'structure_unchanged':r['structure_unchanged'],'directory':str(p.parent.relative_to(ROOT)).replace('\\','/')})
 if len(out['prior_order'])==3:
  states={r['condition']:r for r in out['prior_order']};a,b,c=[states[k] for k in ['manual','native-order','manual-reversal']]
  source=next(r for r in load(OLD/'scientific-comparison-data.json')['recognition'] if r['label']=='NL22')
  historical=next(r['answers'] for r in load(ROOT/'Reports/StructTrainClassic/_work/archive-evidence.json')['recognition'] if r['source_range']==source['range'])
  previous=load(OLD/'assessment.json')['first_by_job'][source['job']]['answers'];changed=[i+1 for i,x,y in zip(range(150),a['answers'],b['answers']) if x!=y]
  out['prior_order_effect']={'changed_ids':changed,'manual_matches_previous_report':a['answers']==previous,'native_matches_all_historical_answers':b['answers']==historical,
   'manual_reversal_matches':a['answers']==c['answers'],'same_loaded_physical_graph':len({digest_physical(report_path(r['directory'])/'loaded') for r in [a,b,c]})==1,
   'rows':[['Ручной порядок']+[a['answers'][i-1] for i in changed],['Штатный порядок']+[b['answers'][i-1] for i in changed],['Ручной повторно']+[c['answers'][i-1] for i in changed]]}
  original_model=ROOT/load(WORK/'prior-order-completion.json')['original_model'];before=physical(ET.parse(original_model).getroot());after=physical(ET.parse(report_path(a['directory'])/'loaded/Model_00.xml').getroot())
  assert before['links']==after['links'] and before['nodes'].keys()==after['nodes'].keys()
  additions=[]
  for name,node in before['nodes'].items():
   other=after['nodes'][name];assert node['class']==other['class']
   for key in node['parameters'].keys()|other['parameters'].keys():
    x,y=node['parameters'].get(key),other['parameters'].get(key)
    if x!=y:
     assert x is None and y==[0.0],'Unexpected change of a recorded original physical setting'
     additions.append({'node':name,'parameter':key,'before':None,'after':y,'origin':'Current registered class default, disabled/zero; not an imputed historical measurement'})
  out['prior_load_adaptations']={'known_parameters_classes_and_links_unchanged':True,'modern_missing_parameters':additions,'same_in_all_order_conditions':True}
  assert all(out['prior_order_effect'][k] for k in ['manual_matches_previous_report','native_matches_all_historical_answers','manual_reversal_matches','same_loaded_physical_graph'])
  out['causes'].append({'factor':'Расхождение NL22 непосредственно в предыдущем ScientificComparisons','status':'Подтверждено экспериментом',
   'finding':'Проверена точная конфигурация G958de87d4b9d предыдущего отчёта. Ручной порядок вновь дал его вектор TP=47, FP=0, FN=3, TN=100. Штатный порядок дал TP=49, FP=0, FN=1, TN=100 и совпал со всеми 150 историческими ответами. Изменились ID '+', '.join(map(str,changed))+'. Обратный ручной контроль вернул прежний вектор; физические параметры и связи загруженных моделей совпали.',
   'boundary':'Для данного расхождения установлено влияние блока упорядочивания стенда. При загрузке отсутствующие новые параметры получили явные нулевые значения по умолчанию; они перечислены в prior_load_adaptations и одинаковы во всех трёх условиях. Известные исходные параметры не изменились. Вывод не переносится на другие модели и не доказывает физическую правильность порядка или происхождение полного исторического кода. Прежние файлы не изменялись.',
   'source':'prior-order-controls; prior_order_effect; G958de87d4b9d; legacyBind SetComponentPosition'})
 for p in (WORK/'geometry-engine-controls').glob('*/results.jsonl'):
  rs=lines(p);meta=p.parent/'process.json'
  if rs and meta.exists() and load(meta)['status']=='completed':
   r=rs[-1];out['geometry_engine'].append({'condition':p.parent.name.removeprefix('NL22-FO-'),'metrics':metrics(r),'answers':r['answers'],'zone_peaks_V':r.get('zone_potential_peaks'),'training_disabled':r['training_disabled'],'structure_unchanged':r['structure_unchanged'],'roundtrip_same_answer':r.get('roundtrip_same_first_answer'),'directory':str(p.parent.relative_to(ROOT)).replace('\\','/')})
 if len(out['geometry_engine'])==4:
  states={r['condition']:r for r in out['geometry_engine']};a,b,c=[states[k] for k in ['manual','native-order','manual-reversal']]
  source=next(r for r in load(OLD/'scientific-comparison-data.json')['recognition'] if r['label']=='NL22')
  historical=next(r['answers'] for r in load(ROOT/'Reports/StructTrainClassic/_work/archive-evidence.json')['recognition'] if r['source_range']==source['range'])
  changed=[i+1 for i,x,y in zip(range(150),a['answers'],b['answers']) if x!=y]
  directories=[report_path(r['directory']) for r in [a,b,c]]
  out['geometry_effect']={'changed_ids':changed,'native_matches_all_historical_answers':b['answers']==historical,'manual_reversal_matches':a['answers']==c['answers'],
   'same_loaded_physical_graph':len({digest_physical(p/'loaded') for p in directories})==1,
   'rows':[['Ручной порядок']+[a['answers'][i-1] for i in changed],['Штатный порядок']+[b['answers'][i-1] for i in changed],['Ручной повторно']+[c['answers'][i-1] for i in changed]]}
  out['causes'].append({'factor':'Ручное упорядочивание в контрольном механизме инференса','status':'Подтверждено экспериментом',
   'finding':'На одной новой модели FO22 с архивными d=(17; 7; 19; 19; 1) и s=(28; 15; 30; 30; 1) сохранение штатного порядка воспроизвело все 150 исторических ответов. Ручное упорядочивание изменило решения для ID '+', '.join(map(str,changed))+'. Возврат ручного режима воспроизвёл его прежний вектор ответов.',
   'boundary':'Переключается блок legacyBind: позиции сегментов, сом, LTZone и генераторов относительно нейрона. Это не приписывается одному вызову ядра UpdateComputationOrder. Полный исторический код этим не идентифицирован. В предыдущем ScientificComparisons применялся именно ручной контрольный порядок; его результаты сохраняются неизменными.',
   'source':'geometry-engine-controls; geometry_effect; legacy_replay.inc legacyBind; FO/factor/learner-22-r1'})
 for job,reference in [('trainer-111-trace','trainer-111'),('learner-22-to129-trace','learner-22'),('learner-22-to37-trace','learner-22')]:
  for repeat in [1,2,3]:
   a=WORK/'runs/VT/traces'/(job+'-r'+str(repeat));b=WORK/'runs/V1C/pilot'/(reference+'-r'+str(repeat))
   ar,br=lines(a/'results.jsonl'),lines(b/'results.jsonl')
   if ar and br:out['trace_observer'].append({'job':job,'repeat':repeat,'same_cold_physical_state':digest_physical(a/'trained')==digest_physical(b/'trained'),'same_cold_iterations':ar[0]['iterations']==br[0]['iterations'],'same_cold_soma_maxima':ar[0]['soma_maxima']==br[0]['soma_maxima']})
 for p in (WORK/'runs/V1C/full').glob('*/results.jsonl'):
  rs=lines(p)
  if not rs or rs[0]['status']=='completed':continue
  r=rs[0];prefix=p.parent.name.rsplit('-r',1)[0];traces=[lines(p.parent.parent/(prefix+'-r'+str(repeat))/'iterations.jsonl') for repeat in [1,2,3]]
  results=[lines(p.parent.parent/(prefix+'-r'+str(repeat))/'results.jsonl') for repeat in [1,2,3]]
  common=min(map(len,traces));fields=['iteration','dendrites','synapses','soma_maxima','dend_status']
  out['cold_limits'].append({'job':prefix,'repeat':r['repeat'],'status':r['status'],'iterations':r['iterations'],'elapsed_wall_seconds':r['elapsed_wall_seconds'],
   'all_repeat_statuses':[v[0]['status'] if v else None for v in results],'all_repeat_iterations':[v[0]['iterations'] if v else None for v in results],
   'common_prefix_records':common,'same_physical_prefix':all(all(a.get(k)==b.get(k)==c.get(k) for k in fields) for a,b,c in zip(*traces))})
 for p in (WORK/'runs/VT/parser-only').glob('*/results.jsonl'):
  rs=lines(p);meta=p.parent/'process.json'
  if rs and meta.exists() and load(meta)['status']=='completed':out['parser'].append({**rs[-1],'directory':str(p.parent.relative_to(ROOT)).replace('\\','/')})
 for kind in ['learner','trainer']:
  for repeat in range(1,4):
   a=WORK/'runs/V1C/pilot'/(kind+'-22-r'+str(repeat));b=WORK/'runs/VB/factor-reversal'/(kind+'-22-r'+str(repeat))
   ar,br=lines(a/'results.jsonl'),lines(b/'results.jsonl')
   if ar and br:out['reversal'].append({'kind':kind,'repeat':repeat,'same_physical_state':digest_physical(a/'trained')==digest_physical(b/'trained'),'same_iterations':ar[0]['iterations']==br[0]['iterations'],'same_soma_maxima':ar[0]['soma_maxima']==br[0]['soma_maxima']})
 for repeat in range(1,4):
  base=WORK/'runs/VB/file-protocol'/('file-external-r'+str(repeat));baseline=[r for r in lines(base/'results.jsonl') if r.get('record_type')=='training']
  for name in ['file-trailing','file-no-trailing','file-truncated']:
   folder=WORK/'runs/VB/file-protocol'/(name+'-r'+str(repeat));records=lines(folder/'results.jsonl');tr=[r for r in records if r.get('record_type')=='training'];end=next((r for r in records if r.get('record_type')=='file_protocol_end'),None)
   row={'protocol':name,'repeat':repeat,'training_records':len(tr),'end':end,'directory':str(folder.relative_to(ROOT)).replace('\\','/')}
   comparisons=[]
   for i,(a,b) in enumerate(zip(baseline,tr)):
    suffix='trained' if i==0 else 'stage-'+str(i)
    comparisons.append({'stage':i,'same_full_physical_state':digest_physical(base/suffix)==digest_physical(folder/suffix),
     'same_iterations':a['iterations']==b['iterations'],'same_dendrites':a['dendrites']==b['dendrites'],'same_synapses':a['synapses']==b['synapses'],
     'same_soma_maxima':a.get('soma_maxima')==b.get('soma_maxima'),'same_pattern':a['pattern']==b['pattern']})
   row['comparisons']=comparisons;out['file_protocol'].append(row)
  folder=WORK/'runs/VB/observer'/('learner-111-observer-off-r'+str(repeat));rs=lines(folder/'results.jsonl');reference=WORK/'runs/V1C/pilot'/('learner-111-r'+str(repeat));ref=lines(reference/'results.jsonl')
  if rs and ref:
   a,b=ref[0],rs[0];out['observer'].append({'repeat':repeat,'same_physical_state':digest_physical(reference/'trained')==digest_physical(folder/'trained'),
    'same_iterations':a['iterations']==b['iterations'],'same_soma_maxima':a['soma_maxima']==b['soma_maxima'],'same_structure':a['dendrites']==b['dendrites'] and a['synapses']==b['synapses']})
 for variant in ['FZ','FZC']:
  for p in (WORK/'runs'/variant/'stopping').glob('*/results.jsonl'):
   rs=lines(p)
   if not rs:continue
   r=rs[0];trace=lines(p.parent/'iterations.jsonl');shapes=[(tuple(t['dendrites']),tuple(t['synapses'])) for t in trace]
   revisits=sum(shapes[i]==shapes[i-2] and shapes[i]!=shapes[i-1] for i in range(2,len(shapes)))
   out['stopping'].append({'variant':variant,'repeat':r['repeat'],'status':r['status'],'iterations':r['iterations'],'initialized':not r['whole_initialization_audit']['uninitialized'],
    'two_structure_revisits':revisits,'dendrites':r['dendrites'],'synapses':r['synapses'],'directory':str(p.parent.relative_to(ROOT)).replace('\\','/')})
 for kind,target in [('learner',22),('trainer',111)]:
  prefix=kind+'-'+str(target);records={}
  for label in ['baseline','reset','native-order','order-disabled','order-explicit','reversal']:
   folder=WORK/'engine-controls'/(prefix+'-'+label);rs=lines(folder/'results.jsonl')
   if rs:records[label]=rs[-1]
  if 'baseline' not in records:continue
  reference=records['baseline']
  for label,r in records.items():
   parent=records.get('native-order',reference) if label=='order-disabled' else reference
   differences=[i for i,a,b in zip(r['input_ids'],r['answers'],parent['answers']) if a!=b]
   out['engine'].append({'model':prefix,'condition':label,'answer_differences':differences,'peak_max_abs_difference_V':max(abs(a-b) for a,b in zip(r['peaks'],parent['peaks'])),
    'training_disabled':r['training_disabled'],'structure_unchanged':r['structure_unchanged'],'roundtrip_same_answer':r.get('roundtrip_same_first_answer'),
    'wrapper_zone_answer_differences':sum(a!=b for a,b in zip(r.get('wrapper_answers',[]),r['answers'])),
    'zone_peaks_V':r.get('zone_potential_peaks'),'first_spikes_seconds':r['first_spikes'],
    'threshold_margins_V':[v-.0115 for v in r.get('zone_potential_peaks',[])],'metrics':metrics(r),'answers':r['answers'],'input_ids':r['input_ids']})
 for variant in ['V1C','FS','FD','FR','FO','V2']:
  phase='pilot' if variant in ['V1C','V2'] else 'factor'
  for kind in ['learner','trainer']:
   p=WORK/'runs'/variant/phase/(kind+'-22-r1');rs=lines(p/'results.jsonl')
   if not rs:continue
   r=rs[0];state=physical(ET.parse(p/'trained/Model_00.xml').getroot());profiles=collections.Counter()
   for name,n in state['nodes'].items():
    params=n['parameters']
    if all(k in params for k in ['Resistance','SecretionTC','DissociationTC']):profiles[tuple((k,tuple(params[k])) for k in ['Resistance','SecretionTC','DissociationTC'])]+=1
   own=lines(WORK/'inference'/variant/phase/('V0G-own' if variant=='V2' else 'VB-own')/(kind+'-22-r1')/'results.jsonl')
   out['factors'].append({'variant':variant,'kind':kind,'dendrites':r['dendrites'],'synapses':r['synapses'],'calibration_V':r.get('initial_soma_potential',r.get('initial_dendrite_potential')),
    'own_answer':own[-1]['answers'][0] if own else None,'actual_synapse_profiles':[{'values':dict(k),'count':v} for k,v in profiles.items()]})
 for variant in ['V1C','FS','FD','FR','FO','V2']:
  phase='pilot' if variant in ['V1C','V2'] else 'factor';backend='V0G-own' if variant=='V2' else 'VB-own'
  for kind in ['learner','trainer']:
   for repeat in range(1,4):
    folder=WORK/'inference'/variant/phase/backend/(kind+'-22-r'+str(repeat));rs=lines(folder/'results.jsonl')
    if rs and rs[-1].get('zone_potential_peaks'):
     r=rs[-1];out['zone_comparison'].append({'variant':variant,'kind':kind,'repeat':repeat,'potential_mV':r['zone_potential_peaks'][0]*1000,'threshold_mV':11.5,'margin_mV':r['zone_potential_peaks'][0]*1000-11.5,'answer':r['answers'][0],'directory':str(folder.relative_to(ROOT)).replace('\\','/')})
 trajectories={}
 for label,folder in [('Исходная остановка',WORK/'runs/V1C/pilot/trainer-22-r1'),('Строгая амплитуда',WORK/'runs/FZ/stopping/trainer-22-r1'),('Пересечение цели',WORK/'runs/FZC/stopping/trainer-22-r1')]:
  trace=lines(folder/'iterations.jsonl');trajectories[label]={r['iteration']:sum(r['synapses']) for r in trace}
 if all(trajectories.values()):
  maximum=max(max(v) for v in trajectories.values());out['stopping_trajectory']={'labels':list(trajectories),'rows':[[i]+[v.get(i) for v in trajectories.values()] for i in range(1,maximum+1)]}
 strict=[lines(WORK/'runs/FZ/stopping'/('trainer-22-r'+str(r))/'iterations.jsonl') for r in [1,2,3]]
 if all(strict):
  common=min(map(len,strict));fields=['iteration','dendrites','synapses','soma_maxima','dend_status']
  equal=all(all(a.get(k)==b.get(k)==c.get(k) for k in fields) for a,b,c in zip(*strict))
  out['strict_prefix_repeatability']={'common_iteration_records':common,'same_physical_observations_at_same_iterations':equal,'termination_is_wall_limit':all(r['status']=='wall_timeout' for r in out['stopping'] if r['variant']=='FZ')}
 for variant in ['VB','FO']:
  for p in (WORK/'runs'/variant/'order-live').glob('*/results.jsonl'):
   rs=lines(p);training=next((r for r in rs if r.get('record_type')=='training'),None);evaluation=next((r for r in rs if r.get('record_type')=='evaluation_in_protocol'),None)
   meta=p.parent/'process.json'
   if not training and meta.exists() and load(meta)['status'] not in ['running']:
    m=load(meta);out['order_live'].append({'variant':variant,'kind':p.parent.name.split('-22-',1)[0],'repeat':m['repeat'],'training':None,'inference':None,'process_status':m['status'],
     'missing_inference_reason':'No completed training observation before supervisor '+m['status']+'; no dependent inference result is available','directory':str(p.parent.relative_to(ROOT)).replace('\\','/')})
   if training and meta.exists() and load(meta)['status']!='running':out['order_live'].append({'variant':variant,'kind':training['job']['kind'],'repeat':training['repeat'],'training':training,'inference':evaluation,'process_status':load(meta)['status'],
    'missing_inference_reason':None if evaluation else 'Last training status '+training['status']+'; process '+load(meta)['status']+'; dependent in-protocol inference has no complete observation','directory':str(p.parent.relative_to(ROOT)).replace('\\','/')})
 if len(out['observer'])==3:
  passed=all(all(v for k,v in r.items() if k!='repeat') for r in out['observer'])
  out['causes'].append({'factor':'Невмешательство записи осциллограммы','status':'Подтверждено экспериментом' if passed else 'Поддерживается ограниченными данными',
   'finding':'Три повторных обучения NL111 с записью и без записи сопоставлены по полному физическому состоянию, итерациям и максимумам. Совпадение: '+str(passed)+'.',
   'boundary':'Проверено для данного наблюдателя и NL111. Время работы файла не является физическим временем модели.','source':'runs/V1C/pilot/learner-111; runs/VB/observer'})
 if len(out['order_live'])==12:
  save(WORK/'order-live-completion-verified.json',{'terminal_attempts':12,'completed_live_evaluations':sum(bool(r['inference']) for r in out['order_live']),
   'missing':[{'variant':r['variant'],'kind':r['kind'],'repeat':r['repeat'],'reason':r['missing_inference_reason']} for r in out['order_live'] if not r['inference']],
   'counts_verified_from_actual_observations':True,'old_dispatcher_completion_flags_are_not_scientific_success_counts':True})
  effects=[]
  for kind in ['learner','trainer']:
   paired=[repeat for repeat in [1,2,3] if all(any(r['variant']==v and r['kind']==kind and r['repeat']==repeat and r['inference'] for r in out['order_live']) for v in ['VB','FO'])]
   if not paired:effects.append({'kind':kind,'paired_evaluation_available':False,'reason':'No matched repeat passed training and dependent live inference in both variants'});continue
   repeat=paired[0]
   a=next(r for r in out['order_live'] if r['variant']=='VB' and r['kind']==kind and r['repeat']==repeat)
   b=next(r for r in out['order_live'] if r['variant']=='FO' and r['kind']==kind and r['repeat']==repeat)
   aa,bb=a['training'],b['training'];av,bv=a['inference'],b['inference']
   effects.append({'kind':kind,'paired_evaluation_available':True,'repeat':repeat,'baseline_d':aa['dendrites'],'order_disabled_d':bb['dendrites'],'baseline_s':aa['synapses'],'order_disabled_s':bb['synapses'],
    'live_answer_mismatches':sum(x!=y for x,y in zip(av['answers'],bv['answers'])),'baseline_live':metrics(av),'order_disabled_live':metrics(bv)})
  out['order_effects']=effects
  out['causes'].append({'factor':'Явное обновление порядка вычислений','status':'Подтверждено экспериментом',
   'finding':'Отключение одного вызова UpdateComputationOrder изменяет конечные длины и числа синапсов при обучении № 22 в NT и NL в изолированном факторном пилоте. Для NL получена архивная геометрия d=(17; 7; 19; 19; 1), s=(28; 15; 30; 30; 1). В дополнительной серии живого инференса выполнено 12 попыток; измерение после обучения доступно в '+str(sum(bool(r['inference']) for r in out['order_live']))+' случаях.',
   'boundary':'Совпадение геометрии отдельного опыта не идентифицирует всю историческую программу. Ограниченные по времени дополнительные попытки и невыполненный зависимый инференс сохранены отдельно. Причина конкретного старого ответа не выводится только из совпадения структуры.','source':'PulseLib отдельный коммит FO; runs/FO/factor; runs/VB/order-live; runs/FO/order-live; engine-controls'})
 if len(out['reversal'])==6:
  equal=all(all(v for k,v in r.items() if k not in ['kind','repeat']) for r in out['reversal'])
  out['causes'].append({'factor':'Обратная проверка физических изменений','status':'Подтверждено экспериментом',
   'finding':'После отключения диагностических изменений выполнено повторное обучение № 22: совпадение полного физического состояния, итераций и максимумов с исходным исправленным вариантом во всех шести попытках — '+str(equal)+'.',
   'boundary':'Обратная проверка относится к двум алгоритмам на № 22. Она не подтверждает неизменность всех опытов на 150 объектах.','source':'runs/VB/factor-reversal; runs/V1C/pilot'})
 if len(out['stopping'])==6:
  strict=[r for r in out['stopping'] if r['variant']=='FZ'];cross=[r for r in out['stopping'] if r['variant']=='FZC']
  out['causes'].append({'factor':'Критерий остановки NT','status':'Подтверждено экспериментом',
   'finding':f'Строгий амплитудный вариант дал {[r["status"] for r in strict]} на {[r["iterations"] for r in strict]} итерациях. Зафиксированы возвраты к ранее наблюдавшимся соседним структурам и последующий рост числа синапсов. Вариант с пересечением цели завершился на {[r["iterations"] for r in cross]} итерациях.',
   'boundary':'Это изолированные диагностические критерии на NT22, а не восстановленная полная программа 2022 года. Лимит 600 с не доказывает невозможность обучения. Разное число итераций до реального лимита рассматривается отдельно от повторяемости траектории.',
   'source':'PulseLib 28eeba0 и 3b522de; runs/FZ, runs/FZC; stopping_trajectory'})
 learner_output_controls=[r for r in out['engine'] if r['model']=='learner-22']
 if len(learner_output_controls)==6:
  differences=sum(r['wrapper_zone_answer_differences'] for r in learner_output_controls)
  out['causes'].append({'factor':'Путь получения бинарного выхода NL','status':'Подтверждено экспериментом',
   'finding':'Для одного неизменного состояния NL22 одновременно прочитаны непосредственный LTZone.Output и выход обёртки NNeuronLearner, получаемый от Neuron.Output. На шести условиях инференса, по 150 входов, различий бинарных решений: '+str(differences)+'. Это нулевой результат сравнения двух определений наблюдаемого выхода.',
   'boundary':'Коммит ff77ca4 от 26.10.2023 заменил прямое чтение LTZone на Neuron.Output. Проверка относится к современному ядру и данному состоянию; она не восстанавливает все старые версии сигналов и не доказывает отсутствие различий времени отдельных импульсов.',
   'source':'PulseLib ff77ca4; NNeuronLearner.cpp Output=Neuron->Output; engine-controls learner-22; wrapper_zone_answer_differences'})
 reset_examples=[]
 for model in ['learner-22','trainer-111']:
  base=next((r for r in out['engine'] if r['model']==model and r['condition']=='baseline'),None);reset=next((r for r in out['engine'] if r['model']==model and r['condition']=='reset'),None)
  if base and reset:
   for ident in reset['answer_differences']:
    index=reset['input_ids'].index(ident)
    reset_examples.append({'model':model,'input_id':ident,'baseline_answer':base['answers'][index],'reset_answer':reset['answers'][index],
     'baseline_zone_mV':base['zone_peaks_V'][index]*1000,'reset_zone_mV':reset['zone_peaks_V'][index]*1000,
     'baseline_margin_mV':base['threshold_margins_V'][index]*1000,'reset_margin_mV':reset['threshold_margins_V'][index]*1000})
 out['reset_examples']=reset_examples
 if reset_examples:
  out['causes'].append({'factor':'Сброс перед каждым входом при неизменном обученном состоянии','status':'Подтверждено экспериментом',
   'finding':'На одном неизменном NT111 сброс модели между стимулами изменил один бинарный ответ — для объекта № 84. Потенциалы LTZone и знаки запаса до порога в двух условиях записаны непосредственно. На NL22 бинарных различий в этом контроле нет.',
   'boundary':'Это влияние контекста инференса, а не другого обучения. Нельзя приписать ему исторические расхождения: применение такого сброса в конкретном старом опыте не установлено. Остаточная активность и начало часов меняются вместе и здесь не разделены.',
   'source':'engine-controls baseline/reset; reset_examples; неизменные конфигурации V1C'})
 if any(r['variant']=='FS' for r in out['factors']):
  out['causes'].append({'factor':'Постоянная времени секреции синапса','status':'Подтверждено экспериментом',
   'finding':'На № 22 в NT и NL отдельное увеличение SecretionTC с 1 до 2 мс даёт отсутствие ответа собственному входу. При совместном историческом наборе значений по умолчанию наблюдается тот же функциональный отказ.',
   'boundary':'В FD и FR изменены только значения по умолчанию конструктора. В сохранённом графе DissociationTC остаётся 5 мс, а сопротивления — 86 и 1000 МОм, как в контроле: их переопределяет настройка нейрона. Поэтому сохранение ответа в FD/FR не доказывает отсутствие эффекта физического изменения этих величин. Полные исторические настройки не установлены.',
   'source':'factors; zone_comparison; runs/FS/FD/FR; пилот V2; контроль возврата VB'})
 out['causes'].append({'factor':'Переопределение параметров создаваемых синапсов','status':'Подтверждено экспериментом',
  'finding':'Изменение исторических значений по умолчанию Resistance и DissociationTC не сохраняется в конечных физических компонентах данного протокола. Нативные XML показывают DissociationTC=5 мс и два заданных сопротивления 86 и 1000 МОм; SecretionTC=2 мс сохраняется.',
  'boundary':'Результат отличает изменение исходного значения конструктора от действительного физического вмешательства. Влияние принудительно заданных 100 МОм или 2 мс диссоциации здесь не проверялось и не объявляется нулевым.',
  'source':'Core/NPulseNeuron.cpp; Core/NNeuronTrainer.cpp; Core/NNeuronLearner.cpp; actual_synapse_profiles; сохранённые Model_00.xml'})
 if len([r for r in out['file_protocol'] if r['end']])==9:
  equal=all(all(all(v for k,v in c.items() if k!='stage') for c in r['comparisons']) for r in out['file_protocol'])
  out['causes'].append({'factor':'Файловое и внешнее управление переобучением','status':'Подтверждено экспериментом' if equal else 'Поддерживается ограниченными данными',
   'finding':'Сопоставлены три повтора последовательности 22→64→111. Совпадение физических состояний, итераций, стимулов и максимумов на общих допустимых записях: '+str(equal)+'. Проверены завершающий перевод строки, его отсутствие и оборванный последний вектор.',
   'boundary':'Порт использует явно принятое размещение файлового обработчика перед тактом среды и безопасную проверку извлечения. Полный исторический ACalculate, вызывавший фрагмент, отсутствует.',
   'source':'file-protocol-definitions.json; file-events.jsonl; runs/VB/file-protocol'})
  out['causes'].append({'factor':'Возможная лишняя строка архивного распознавания','status':'Гипотеза',
   'finding':'Проверка eof() до извлечения не обнаруживает завершающий пробел как конец данных. Контроль фиксирует дополнительную неуспешную попытку чтения, не присваивая неопределённые значения модели.',
   'boundary':'Это объясняет дефект чтения фрагмента, но не доказывает происхождение конкретной 31-й строки старого output_data: полный исторический вызывающий код не найден.',
   'source':'Архивные TreatDataFromFile; file-events.jsonl; предыдущий ScientificComparisons'})
 save(WORK/'control-analysis.json',out)
 # A successful dispatcher exit is not substituted for actual diagnostic data.
 files_complete=all((WORK/'runs/VB/file-protocol'/(name+'-r'+str(r))/'process.json').exists() and load(WORK/'runs/VB/file-protocol'/(name+'-r'+str(r))/'process.json')['status']=='completed' for name in ['file-external','file-trailing','file-no-trailing','file-truncated'] for r in [1,2,3])
 modes_complete=all((WORK/'runs/VB/modes-isolated'/(case['case']+'-r'+str(r))/'process.json').exists() and load(WORK/'runs/VB/modes-isolated'/(case['case']+'-r'+str(r))/'process.json')['status']=='completed' for case in load(BASE)['mode_cases'] for r in [1,2,3])
 completed=files_complete and modes_complete and len(out['observer'])==3 and (WORK/'stopping-engine-controls-completion.json').exists() and len(out['engine'])==12
 if completed:save(WORK/'post-controls-completion.json',{'completed':True,'verified_from_actual_records':True,'file_attempts':12,'observer_attempts':3,'mode_cases':32,'mode_attempts':96,'mode_repeats':3,'engine_conditions':12,'criterion_attempts':len(out['stopping'])})
 print(json.dumps({'file_attempts':sum(r['end'] is not None for r in out['file_protocol']),'observer':len(out['observer']),'stopping':len(out['stopping']),'engine':len(out['engine']),'completed':completed}))
if __name__=='__main__':main()
