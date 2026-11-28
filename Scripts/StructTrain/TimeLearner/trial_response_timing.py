"""Separate actual event timing from the already declared response criterion.

This does not rescore, calibrate, authenticate execution or infer a permitted
response latency. Callers first audit observations/source or bind them to a
completed audit. A spike after the last input is not by itself a timing PASS.
"""
import copy
import html

from .native_evidence import after, equal, number, require
from .recognition_metrics import _counts


def summarize_trial_timing(spec, observations, metrics):
    require(type(spec) is dict and type(metrics) is dict and
        metrics.get('validity')=='valid' and not metrics.get('invalid_trial_ids') and
        metrics['run_id']==spec['run_id'] and metrics['model_revision']==spec['model_revision'] and
        metrics['criterion']==spec['criterion'], 'timing_requires_complete_matching_metrics')
    declared=spec['trials'];rows=metrics['trials']
    require(type(declared) is list and type(observations) is list and type(rows) is list and declared,
        'timing_trial_arrays_required')
    def unique(values):
        result={}
        for value in values:
            require(type(value) is dict and type(value.get('trial_id')) is str and
                value['trial_id'] and value['trial_id'] not in result,'timing_duplicate_or_missing_trial_id')
            result[value['trial_id']]=value
        return result
    design,actual,scored=unique(declared),unique(observations),unique(rows)
    require(set(design)==set(actual)==set(scored),'timing_incomplete_or_foreign_trial_set')
    require(_counts(rows)==metrics['pooled_counts'],'timing_declared_counts_changed')
    require({t['presentation_index']for t in declared}==set(range(len(declared))),
        'timing_invalid_presentation_positions')
    result=[]
    for wanted in sorted(declared,key=lambda t:t['presentation_index']):
        o=actual[wanted['trial_id']];row=scored[wanted['trial_id']]
        require(type(o.get('schema_version')) is int and o['schema_version'] in (1,2) and
            o['complete'] is True and o['valid'] is True and o['censored'] is False and o['armed'] is True,
            'timing_requires_valid_complete_observation')
        require(o['run_id']==spec['run_id'] and o['model_before']==o['model_after']==spec['model_revision'] and
            all(o[k]==wanted[k] for k in ('sample_id','label','pattern_hash','reset_policy')) and
            all(row[k]==wanted[k]for k in ('sample_id','label','reset_policy','presentation_index')),
            'timing_trial_identity_or_model_changed')
        require(wanted['label'] in ('target','foil') and row['classification'] in ('TP','FN','FP','TN'),
            'timing_unknown_label_or_classification')
        stimuli=[number(t)for t in o['stimulus_times']];spikes=[number(t)for t in o['spike_times']]
        require(stimuli and all(after(b,a)for a,b in zip(stimuli,stimuli[1:])) and
            all(after(b,a)for a,b in zip(spikes,spikes[1:])) and
            type(o['spike_count']) is int and o['spike_count']==len(spikes)==row['spike_count'] and
            all(not after(o['begin'],t) and not after(t,o['end'])for t in stimuli+spikes),
            'timing_event_count_order_or_window_mismatch')
        require(equal(o['stimulus_onset'],stimuli[0]),'timing_actual_onset_mismatch')
        partition=sorted(number(t)for key in ('window_spikes','early_spikes','late_spikes')for t in row[key])
        require(len(partition)==len(spikes) and all(equal(a,b)for a,b in zip(partition,spikes)),
            'timing_scored_spike_partition_changed')
        before=[t for t in spikes if after(stimuli[-1],t)]
        after_last=[t for t in spikes if not after(stimuli[-1],t)]
        result.append(dict(trial_id=wanted['trial_id'],sample_id=wanted['sample_id'],label=wanted['label'],
            presentation_index=wanted['presentation_index'],reset_policy=wanted['reset_policy'],
            declared_classification=row['classification'],first_actual_input=stimuli[0],last_actual_input=stimuli[-1],
            native_spike_times=list(spikes),spike_times_from_last_input=[t-stimuli[-1]for t in spikes],
            spikes_before_last_input=before,spikes_at_or_after_last_input=after_last,
            before_last_input_count=len(before),at_or_after_last_input_count=len(after_last),timing_verdict=None))
    target=[r for r in result if r['label']=='target']
    return dict(kind='timelearner_actual_trial_event_timing',schema_version=1,
        source_run_id=spec['run_id'],source_model_revision=spec['model_revision'],
        declared_criterion=copy.deepcopy(spec['criterion']),declared_counts=copy.deepcopy(metrics['pooled_counts']),
        source_classifications_unchanged=True,full_declared_trial_set=True,trials=result,
        target_trials_with_before_last_output=[r['trial_id']for r in target if r['before_last_input_count']],
        target_trials_with_at_or_after_last_output=[r['trial_id']for r in target if r['at_or_after_last_input_count']],
        target_trials_without_output=[r['trial_id']for r in target if not r['native_spike_times']],
        timing_scope='actual_events_relative_to_last_recorded_input; necessary condition only, no inferred latency limit',
        native_execution_attested=False,new_response_criterion=False,scientific_verdict=None)


def timing_html(summary):
    require(summary['kind']=='timelearner_actual_trial_event_timing' and summary['schema_version']==1,
        'unknown_timing_summary')
    rows=[]
    for r in summary['trials']:
        delays='; '.join(format(number(t)*1000,'.6g').replace('.',',') for t in r['spike_times_from_last_input']) or '—'
        label='цель' if r['label']=='target' else 'отвлекающий'
        cells=[r['sample_id'],label,r['declared_classification'],str(r['before_last_input_count']),
               str(r['at_or_after_last_input_count']),delays]
        rows.append('<tr>'+''.join('<td>'+html.escape(v)+'</td>'for v in cells)+'</tr>')
    headings=['Паттерн','Метка','Исходная оценка','Выходов до последнего входа',
              'Выходов с последнего входа','Время выхода от последнего входа, мс']
    return ('<section><h2>Порядок входов и фактическое время ответа</h2>'
        '<p>Классификация соответствует исходному критерию. Отрицательное время означает '
        'выход до завершения паттерна. Выход после последнего входа сам по себе не подтверждает '
        'допустимую задержку или правильную форму ответа; новый временной допуск не вводится.</p>'
        '<div style="overflow-x:auto"><table border="1" cellpadding="6"><thead><tr>'+
        ''.join('<th>'+html.escape(v)+'</th>'for v in headings)+'</tr></thead><tbody>'+''.join(rows)+
        '</tbody></table></div></section>')
