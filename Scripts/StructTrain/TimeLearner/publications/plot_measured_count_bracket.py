"""Draw measured integer-count neighbours from an already audited cold Train.

Every plotted byte is bound through the full audit's execution record. This
does not rerun the model, rescore recognition or claim physical infeasibility.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

from ..native_evidence import equal, number, require
from ..plotting import plotting_runtime
from ..runtime import file_record


def read_bracket(native, audit_path, input_index, length, counts):
    native=Path(native).resolve(strict=True);audit_path=Path(audit_path).resolve(strict=True)
    require(type(input_index) is int and input_index>=0 and type(length) is int and length>0 and
        2<=len(counts)<=8 and all(type(n) is int and n>0 for n in counts) and
        counts==sorted(set(counts)), 'count_bracket_selection')
    records={}

    def read(path, expected=None):
        path=Path(path).resolve(strict=True);raw=path.read_bytes();record=file_record(path)
        require(record['size']==len(raw) and record['sha256']==hashlib.sha256(raw).hexdigest(),
                'count_bracket_file_changed_during_read')
        if expected is not None:
            require(record['size']==expected['bytes'] and record['sha256']==expected['sha256'],
                    'count_bracket_audited_bytes_changed')
        records[str(path)]=record
        return raw

    proof=json.loads(read(audit_path))
    require(proof['kind']=='timelearner_closed_matched_count_training_audit' and
        proof['source_package_full_decodes']==1 and proof['original_outcome_unchanged'] is True and
        proof['full_primary_audit']['training_outcome']=='budget_exhausted' and
        proof['full_primary_audit']['completed_boundary'] is False,
        'count_bracket_requires_completed_full_stopped_audit')
    source=proof['execution_file']
    execution=json.loads(read(native/'execution.json',dict(bytes=source['size'],sha256=source['sha256'])))
    require(execution['execution']=='completed' and execution['job_sha256']==proof['consumed_job_sha256'],
            'count_bracket_execution_changed')
    artifacts=execution['artifacts'];by_name={r['path']:r for r in artifacts}
    require(len(by_name)==len(artifacts), 'count_bracket_duplicate_primary')

    def primary(name):
        relative=Path(name)
        require(not relative.is_absolute() and '..' not in relative.parts and name in by_name,
                'count_bracket_primary_path')
        path=native/relative
        require(path.resolve(strict=True).is_relative_to(native) and not path.is_symlink(),
                'count_bracket_primary_alias')
        return read(path,by_name[name])

    job_record=proof['consumed_job_file']
    job=json.loads(read(native/'job.json',dict(bytes=job_record['size'],sha256=job_record['sha256'])))
    require(job['sha256']==execution['job_sha256'] and
        job['configuration']['model']['normalization']=='N0' and
        job['configuration']['model']['branch'] is False,
        'count_bracket_requires_ordinary_count_normalization')
    summary=json.loads(primary('train_stopped_summary.json'));history=summary['historical_summary']
    require(summary['actual_model_revision']==execution['model_revision'] and
        summary['outcome']=='budget_exhausted' and summary['certificate'] is None,
        'count_bracket_summary_changed')
    references=[r for r in history['references'] if r['input_id']=='input'+str(input_index)]
    require(len(references)==1, 'count_bracket_reference_identity')
    reference=number(references[0]['raw_potential']);tolerance=history['tolerances']
    epsilon=number(tolerance['amplitude_absolute'])+number(tolerance['amplitude_relative'])*abs(reference)
    require(epsilon>0, 'count_bracket_positive_amplitude_tolerance_required')
    rows=[];background=None;actual_stimuli=None
    for ns in counts:
        candidates=[c for c in history['candidates'] if c['input_index']==input_index and
            c['parameters']['length']==length and c['parameters']['synapses']==ns]
        require(bool(candidates), 'count_bracket_unmeasured_count')
        candidate=candidates[0];parameters=[dict(p) for p in candidate['full_parameters']]
        require(parameters[input_index]==candidate['parameters'], 'count_bracket_candidate_parameters')
        parameters[input_index]['synapses']=0
        require(background is None or background==parameters, 'count_bracket_changed_background')
        background=parameters
        # The filename is only a lookup hint; identity and effective revision
        # must match. No positional row is accepted as the requested group.
        serial=int(candidate['measurement_group_id'].rsplit('/',1)[1])
        group_path='composite-measurements/group-%06d.json'%serial
        group=json.loads(primary(group_path))
        require(group['group_id']==candidate['measurement_group_id'] and group['complete_group'] is True and
            group['consumed'] is True and group['method_specification']['method_id']==
            'declared-window-basin-necessity-v1' and group['method_specification']['assigned_input']==input_index and
            group['logical_request']['base_model_revision']==candidate['model_revision'] and
            group['measurement']['semantic_proof_id']==candidate['semantic_proof_id'] and
            group['selection']['geometry']['validity']=='valid', 'count_bracket_group_identity_or_validity')
        full=[r for r in group['raw_trials'] if
            r['primary_ref']['relative_path'].endswith('/full-before.csv')]
        require(len(full)==1, 'count_bracket_full_burst_identity')
        trial=full[0];spec=trial['actual_specification'];selected=group['measurement']['actual_peak']
        raw=primary(trial['primary_ref']['relative_path'])
        require(len(raw)==trial['primary_ref']['bytes'] and hashlib.sha256(raw).hexdigest()==
            trial['primary_ref']['sha256'], 'count_bracket_trial_bytes_changed')
        reader=csv.DictReader(io.StringIO(raw.decode('utf-8')))
        require(reader.fieldnames==['time','stimulus',*(f'soma{i}' for i in range(len(spec['baseline'])))],
                'count_bracket_trace_columns')
        samples=[{k:number(float(v)) for k,v in row.items()} for row in reader]
        require(len(samples)==group['native_packets'][0]['observation']['sample_count'] and
            equal(samples[0]['time'],spec['begin']) and equal(samples[-1]['time'],spec['end']) and
            all(equal(b['time']-a['time'],spec['maximum_sample_gap']) for a,b in zip(samples,samples[1:])),
            'count_bracket_incomplete_trace')
        require(spec['effective_model_revision']==candidate['model_revision'] and
            spec['expected_stimulus_ids']==[r['id'] for r in trial['actual_stimuli']],
            'count_bracket_trial_model_or_stimuli')
        for event in trial['actual_stimuli']:
            require(equal(samples[event['frame_index']]['time'],event['time']) and
                samples[event['frame_index']]['stimulus']>0 and
                (event['frame_index']==0 or samples[event['frame_index']-1]['stimulus']<=0),
                'count_bracket_actual_input_edge')
        times=[s['time']-spec['begin'] for s in samples]
        stimuli=[r['time']-spec['begin'] for r in trial['actual_stimuli']]
        require(actual_stimuli is None or len(stimuli)==len(actual_stimuli) and
            all(equal(a,b) for a,b in zip(actual_stimuli,stimuli)), 'count_bracket_different_input_times')
        actual_stimuli=stimuli
        channel=group['method_specification']['channel'];values=[s['soma'+str(channel)] for s in samples]
        index=selected['first_sample']
        require(0<=index<len(values) and equal(samples[index]['time'],selected['time']) and
            equal(values[index],selected['raw_potential']) and
            equal(selected['raw_potential']-reference,candidate['amplitude_residual']),
            'count_bracket_selected_peak_changed')
        maximum=max(range(len(values)),key=values.__getitem__)
        rows.append(dict(synapses=ns,candidate=candidate,group_file=group_path,
            trace_file=trial['primary_ref']['relative_path'],samples=len(samples),
            selected_time=times[index],selected_potential=values[index],
            global_time=times[maximum],global_potential=values[maximum],
            global_is_selected=maximum==index,amplitude_tolerance_units=candidate['amplitude_residual']/epsilon,
            time=times,potential=values,stimulus=[s['stimulus'] for s in samples]))
    return dict(rows=rows,records=records,reference=reference,amplitude_tolerance=epsilon,
        sync_tolerance=number(tolerance['sync']),actual_stimuli=actual_stimuli,
        input_index=input_index,length=length,full_audit_file=str(audit_path),
        actual_final_model_revision=summary['actual_model_revision'],
        mathematical_scope='measured integer neighbours at one geometry; no global infeasibility or convergence',
        classification_performed=False,new_native_execution=False)


def render(native,audit,output,input_index,length,counts):
    data=read_bracket(native,audit,input_index,length,counts);environment=plotting_runtime()
    import matplotlib.pyplot as plt
    output=Path(output);require(not output.exists(),'count_bracket_fresh_output_required');output.mkdir(parents=True)
    colors=['#c66b08','#1b62a8','#328148','#964592','#676767','#008b90','#b22537','#6e5798']
    with plt.rc_context({'font.family':'DejaVu Sans','font.size':13,'svg.fonttype':'none'}):
        fig=plt.figure(figsize=(17,13),dpi=160);grid=fig.add_gridspec(3,2,height_ratios=[1.3,1.3,1])
        full=fig.add_subplot(grid[0,:]);detail=fig.add_subplot(grid[1,:])
        amplitude=fig.add_subplot(grid[2,0]);timing=fig.add_subplot(grid[2,1])
        fig.subplots_adjust(left=.10,right=.90,top=.88,bottom=.13,hspace=.52,wspace=.30)
        fig.suptitle('Нормализация числом синапсов: измеренные соседние варианты\n'
            f'Обычный нейрон, M={len(data["actual_stimuli"])}; путь {input_index+1}, L={length}',fontsize=19,y=.97)
        for row,color in zip(data['rows'],colors):
            for axis in (full,detail):
                axis.plot(row['time'],row['potential'],color=color,lw=1.6,label=f'Nₛ={row["synapses"]}')
                axis.plot(row['selected_time'],row['selected_potential'],'o',color=color,ms=7)
            full.plot(row['global_time'],row['global_potential'],'x',color=color,ms=8,mew=2)
        first=data['rows'][0];overlay=full.twinx()
        overlay.step(first['time'],first['stimulus'],where='post',color='#d57a18',alpha=.65,lw=1)
        overlay.set_ylabel('Фактический вход',color='#a55100');overlay.set_ylim(-.02,1.15)
        for axis in (full,detail):
            axis.axhspan(data['reference']-data['amplitude_tolerance'],data['reference']+data['amplitude_tolerance'],
                color='#555555',alpha=.25)
            axis.axhline(data['reference'],color='#555555',ls='--',lw=1)
            axis.set_ylabel('Потенциал сомы\n(условные единицы модели)')
            axis.set_xlabel('Время от начала пробы, с');axis.grid(alpha=.25)
        full.set_xlim(first['time'][0],first['time'][-1]);full.set_title('Полное окно: ○ — закреплённая вершина; × — максимум всей пачки',loc='left')
        full.legend(loc='upper right',ncol=len(counts));lo=min(r['selected_time'] for r in data['rows'])-.04
        hi=max(r['selected_time'] for r in data['rows'])+.04;detail.set_xlim(lo,hi)
        visible=[v for r in data['rows'] for t,v in zip(r['time'],r['potential']) if lo<=t<=hi]+[data['reference']]
        spread=max(visible)-min(visible);detail.set_ylim(min(visible)-spread*.08,max(visible)+spread*.10)
        detail.set_title('Увеличение закреплённой вершины; пунктир — собственная исходная амплитуда',loc='left')
        xs=[r['synapses'] for r in data['rows']]
        amplitude.axhspan(-1,1,color='#328148',alpha=.17);amplitude.axhline(0,color='#777777',lw=.8)
        amplitude.plot(xs,[r['amplitude_tolerance_units'] for r in data['rows']],'o-',color='#1b62a8')
        amplitude.set_title('Ошибка амплитуды / исходный допуск',loc='left');amplitude.set_ylabel('Доли допуска');amplitude.set_xlabel('Число синапсов Nₛ')
        timing.axhspan(-data['sync_tolerance']*1000,data['sync_tolerance']*1000,color='#328148',alpha=.17)
        lows=[r['candidate']['timing_low']*1000 for r in data['rows']]
        highs=[r['candidate']['timing_high']*1000 for r in data['rows']]
        centers=[(a+b)/2 for a,b in zip(lows,highs)]
        timing.errorbar(xs,centers,yerr=[[c-a for c,a in zip(centers,lows)],
            [b-c for b,c in zip(highs,centers)]],fmt='o-',color='#1b62a8',capsize=4)
        timing.set_title('Измеренная временная ошибка',loc='left');timing.set_ylabel('Миллисекунды');timing.set_xlabel('Число синапсов Nₛ')
        for axis in (amplitude,timing):axis.set_xticks(xs);axis.grid(alpha=.25)
        passed=sum(abs(r['amplitude_tolerance_units'])<=1 for r in data['rows'])
        fig.text(.10,.055,f'Зелёная область — исходный допуск. Амплитудный допуск выполнен для {passed} из {len(counts)} вариантов.\n'
            'Показаны измерения обучения одной геометрии, не результат распознавания и не доказательство недостижимости.',fontsize=12)
        for ext in ('png','svg'):fig.savefig(output/('measured-count-bracket.'+ext),facecolor='white')
        plt.close(fig)
    require(all(file_record(Path(p))==record for p,record in data['records'].items()),
            'count_bracket_primary_changed_during_render')
    result={k:v for k,v in data.items() if k!='rows'}
    result.update(kind='timelearner_measured_count_bracket_figure',schema_version=1,plotting_runtime=environment,
        rows=[{k:v for k,v in r.items()if k not in ('time','potential','stimulus')}for r in data['rows']],
        files=[file_record(output/('measured-count-bracket.'+ext))for ext in ('png','svg')],
        downsampling=False,actual_input_overlay=True,visual_review_complete=False,scientific_verdict=None)
    (output/'figure-data.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--native',required=True)
    parser.add_argument('--audit',required=True);parser.add_argument('--output',required=True)
    parser.add_argument('--input-index',type=int,required=True);parser.add_argument('--length',type=int,required=True)
    parser.add_argument('--counts',nargs='+',type=int,required=True);args=parser.parse_args()
    render(args.native,args.audit,args.output,args.input_index,args.length,args.counts)


if __name__=='__main__':main()
