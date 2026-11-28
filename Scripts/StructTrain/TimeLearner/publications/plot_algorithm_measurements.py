"""Illustrate measured training probes and search points with Russian labels.

Curves are the recorded native samples, not a fitted physical model. A didactic
crop is explicitly distinguished from an actually incomplete observation.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys


def render(source, output, *, matplotlib_libs=None):
    from ..native_evidence import load, require, number, equal
    from ..probe_reports import _read_probe_data
    source=Path(source).resolve(strict=True);root=source.parent;spec=load(source)
    require(spec.get('kind')=='timelearner_scientific_measurement_figure_sources' and
            type(spec.get('schema_version')) is int and spec['schema_version'] in (1,2),
            'known_measurement_figure_sources_required')
    output=Path(output).resolve();require(not output.exists(),'fresh_measurement_figure_output_required')
    if matplotlib_libs:sys.path.insert(0,str(Path(matplotlib_libs).resolve(strict=True)))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    output.mkdir(parents=True);records=[];identities=set()

    def bound(record):
        rel=Path(record['path']);p=(root/rel).resolve(strict=True)
        require(not rel.is_absolute() and '..' not in rel.parts and p.is_relative_to(root),
                'local_measured_figure_source_required')
        require(p.stat().st_size==record['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==record['sha256'],
                'measured_figure_source_changed')
        return p

    def save(fig,row,details):
        identity=row['id'];require(identity not in identities and all(c in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in identity),
                                  'unique_safe_measurement_figure_id_required');identities.add(identity)
        files=[]
        for suffix in ('png','svg'):
            p=output/(identity+'.'+suffix);fig.savefig(p,dpi=220)
            files.append(dict(name=p.name,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
        plt.close(fig);records.append(dict(id=identity,files=files,source=row,details=details,visually_reviewed=False))

    style={'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':11,'axes.labelsize':10,
           'xtick.labelsize':9,'ytick.labelsize':9,'svg.fonttype':'none'}
    with plt.rc_context(style):
        for row in spec.get('probes',[]):
            packet_path,trace_path=bound(row['packet']),bound(row['trace'])
            packet,audit,observation,probe,frequency,samples,count,quality=_read_probe_data(packet_path,trace_path,allow_incomplete=True)
            channel=row['channel'];require(type(channel) is int and 0<=channel<count,'recorded_probe_channel_required')
            begin=number(probe['begin']);end=number(probe['end'])
            times=[number(s['time'])-begin for s in samples]
            values=[s['soma'][channel] for s in samples]
            # NaN remains a gap. Never connect across a missing native time step.
            x=[];y=[];previous=None
            for time,value in zip(times,values):
                if previous is not None and time-previous>1.5/frequency:x.append(float('nan'));y.append(float('nan'))
                x.append(time);y.append(value);previous=time
            fig,axis=plt.subplots(figsize=(6.35,3.1),layout='constrained')
            stop=row.get('didactic_crop_at')
            if stop is not None:
                require(observation['complete'] is True and 0<stop<end-begin,'explicit_didactic_crop_requires_complete_source')
                visible=[i for i,t in enumerate(x) if t<=stop or not math.isfinite(t)]
                axis.plot([x[i] for i in visible],[y[i] for i in visible],color='#1756a9',lw=1.25)
                axis.axvspan(stop,end-begin,color='#dddddd',alpha=.7)
                axis.text(stop+(end-begin-stop)/2,.82,'Для пояснения\nзапись скрыта',transform=axis.get_xaxis_transform(),ha='center',va='top',fontsize=9)
            else:axis.plot(x,y,color='#1756a9',lw=1.25)
            events=[number(v['time'])-begin for v in observation.get('stimuli',[])]
            for time in events:axis.axvline(time,color='#df7b20',lw=.85,alpha=.8)
            assigned=[]
            for peak in observation.get('peaks',[]):
                if peak.get('validity')=='valid' and any(w.get('input_id')==peak.get('input_id') and w.get('channel')==channel for w in probe['windows']):
                    t=number(peak['time'])-begin;value=number(peak['raw_potential']);assigned.append(dict(time=t,value=value))
                    axis.plot(t,value,'o',mfc='white',mec='#1756a9',ms=6,zorder=5)
            finite=[(t,v) for t,v in zip(times,values) if math.isfinite(v)]
            require(finite,'no_finite_recorded_probe_for_illustration')
            peak_time,peak_value=max(finite,key=lambda pair:pair[1])
            if row.get('mark_whole_maximum'):
                axis.plot(peak_time,peak_value,'x',color='#a51b23',ms=7,mew=1.4)
            view=row.get('view_window',[0,end-begin])
            require(len(view)==2 and 0<=view[0]<view[1]<=end-begin,'valid_recorded_probe_view_required')
            axis.set_xlim(*view);axis.set_xlabel('Время от начала пробы, с');axis.set_ylabel('Потенциал сомы, усл. ед.')
            axis.ticklabel_format(axis='y',style='sci',scilimits=(-3,3),useMathText=True);axis.grid(alpha=.22,lw=.5)
            axis.set_title(row['title'])
            legends=[Line2D([0],[0],color='#1756a9',label='Записанный потенциал'),Line2D([0],[0],color='#df7b20',label='Входной импульс')]
            if assigned:legends.append(Line2D([0],[0],marker='o',mfc='white',mec='#1756a9',ls='',label='Закреплённый пик по исходному измерителю'))
            if row.get('mark_whole_maximum'):legends.append(Line2D([0],[0],marker='x',color='#a51b23',ls='',label='Максимум всей пачки'))
            fig.legend(handles=legends,loc='outside lower center',fontsize=8,ncol=2)
            save(fig,row,dict(audit=audit,quality=quality,source_complete=observation.get('complete'),
                source_valid=observation.get('valid'),source_reasons=observation.get('reasons'),
                recorded_samples=len(samples),didactic_crop_only=stop is not None,assigned_peaks=assigned,
                global_maximum_descriptive_only=dict(time=peak_time,value=peak_value),new_assignment_or_convergence_claimed=False))
        for row in spec.get('searches',[]):
            package=load(bound(row['history']));history=package['summary'];candidates=history['candidates'];configuration=history['configuration']
            input_index=row['input_index']
            require(type(input_index) is int and 0<=input_index<len(configuration['bounds']),
                    'measured_search_input_index_required')
            selected=[(i,c) for i,c in enumerate(candidates) if c['input_index']==row['input_index']]
            require(selected,'recorded_candidate_history_required')
            tolerances=history['tolerances']
            absolute=number(tolerances['amplitude_absolute']);relative=number(tolerances['amplitude_relative'])
            sync=number(tolerances['sync'])
            require(min(absolute,relative,sync)>=0,'negative_measured_search_tolerance')
            references=history['references'];by_id={}
            for ref in references:
                identity=ref['input_id']
                require(type(identity) is str and identity and identity not in by_id,
                        'duplicate_or_invalid_measured_search_reference')
                number(ref['raw_potential']);by_id[identity]=ref
            require(len(by_id)==len(configuration['bounds']),'incomplete_measured_search_references')
            reference=None;reference_audit=None
            proof=row.get('reference_probe')
            require(proof is not None or (spec['schema_version']==1 and relative==0),
                    'measured_search_reference_probe_required')
            if proof is not None:
                # Obtain the physical index from the measured stimulus/window
                # association, as audit_training does. Reference list order and
                # names such as "input0" are not a physical-index contract.
                require(type(proof) is dict and set(proof)=={'packet','trace'},
                        'unknown_measured_search_reference_probe')
                packet_path,trace_path=bound(proof['packet']),bound(proof['trace'])
                packet,reference_audit,observation,probe,_,_,_,_=_read_probe_data(packet_path,trace_path)
                prepared=packet['prepared'];identity=prepared['input_id']
                require(identity in by_id,'measured_search_reference_not_in_history')
                reference=by_id[identity]
                windows=[w for w in probe['windows'] if w['input_id']==identity]
                require(len(windows)==1 and
                        probe['expected_stimulus_ids'].index(windows[0]['stimulus_id'])==input_index,
                        'measured_search_reference_input_mismatch')
                require(probe['trial_id']==reference['trial_id'] and probe['run_id']==reference['run_id'] and
                        prepared['effective_model_revision']==reference['effective_model_revision'] and
                        prepared['base_model_revision']==history['reference_model_revision'] and
                        prepared['model_epoch']==history['reference_model_epoch'],
                        'measured_search_reference_context_mismatch')
                peaks=[p for p in observation['peaks'] if p['input_id']==identity]
                require(len(peaks)==1 and peaks[0]['validity']=='valid' and
                        equal(peaks[0]['raw_potential'],reference['raw_potential']),
                        'measured_search_reference_amplitude_mismatch')
            reference_raw=None if reference is None else number(reference['raw_potential'])
            amp=number(absolute+(0 if reference_raw is None else relative*abs(reference_raw)))
            tolerance_details=dict(amplitude_absolute=absolute,amplitude_relative=relative,
                reference_input_id=None if reference is None else reference['input_id'],
                reference_raw_potential=reference_raw,
                reference_binding='unknown_legacy_absolute_only' if reference is None else 'audited_native_probe',
                reference_audit=reference_audit,effective_amplitude_tolerance=amp)
            fig,axes=plt.subplots(3,1,figsize=(6.35,6.3),layout='constrained')
            index=list(range(1,len(selected)+1));amplitude=[number(c['amplitude_residual']) for _,c in selected]
            low=[number(c['timing_low']) for _,c in selected];high=[number(c['timing_high']) for _,c in selected]
            # Retain actual evaluation order and all changed parameters. These
            # are not silently presented as a single-parameter response curve.
            labels=[]
            for _,c in selected:
                p=c['parameters'];labels.append('L='+str(p['length'])+'\nNₛ='+str(p['synapses'])+'\nRₛ='+format(p['resistance']/1e6,'.3g'))
            if amp>0:axes[0].axhspan(-amp,amp,color='#dcebd9')
            axes[0].axhline(0,color='gray',lw=.7)
            axes[0].plot(index,amplitude,'o-',color='#1756a9',lw=1);axes[0].set_ylabel('Ошибка амплитуды, усл. ед.')
            axes[1].axhspan(-sync,sync,color='#dcebd9');axes[1].axhline(0,color='gray',lw=.7)
            axes[1].plot(index,low,'o-',color='#1756a9',lw=1,label='Нижняя граница')
            axes[1].plot(index,high,'x--',color='#a51b23',lw=.8,label='Верхняя граница');axes[1].set_ylabel('Ошибка времени, с')
            axes[1].set_xticks(index,labels);axes[1].set_xlabel('Последовательность измеренных кандидатов; Rₛ, МОм')
            axes[0].set_xticks(index);axes[0].set_xlabel('Номер измеренного кандидата')
            if amp>0:
                axes[2].axhspan(-amp,amp,color='#dcebd9')
                axes[2].axhline(amp,color='#548447',ls='--',lw=.8);axes[2].axhline(-amp,color='#548447',ls='--',lw=.8)
            axes[2].axhline(0,color='gray',lw=.7)
            axes[2].plot(index[-1],amplitude[-1],'o',color='#1756a9');axes[2].set_xlim(index[-1]-.5,index[-1]+.5)
            zoom_half=number(max(3*amp,1.1*abs(amplitude[-1]),1e-12))
            axes[2].set_ylim(-zoom_half,zoom_half);axes[2].set_xticks([index[-1]])
            axes[2].set_xlabel('Последний измеренный кандидат');axes[2].set_ylabel('Ошибка амплитуды, усл. ед.')
            axes[2].set_title(('Увеличение исходного допуска; ошибка ' if amp>0 else
                              'Нулевой допуск: допустима только ошибка 0; измерено ')+format(amplitude[-1],'.4g'))
            for axis in axes:axis.grid(alpha=.22,lw=.5);axis.ticklabel_format(axis='y',style='sci',scilimits=(-3,3),useMathText=True)
            fig.suptitle(row['title'],fontsize=11)
            save(fig,row,dict(candidate_count=len(selected),amplitude_tolerance=amp,sync_tolerance=sync,
                tolerance=tolerance_details,amplitude_zoom_limits=[-zoom_half,zoom_half],
                zero_tolerance_display_scale_only=amp==0,
                single_factor_curve=False,original_candidate_indices=[i for i,_ in selected],new_training_result_claimed=False))
    result=dict(kind='timelearner_scientific_measurement_figures',schema_version=1,figures=records,
        renderer='Matplotlib',matplotlib_version=matplotlib.__version__,scientific_verdict=None,visually_reviewed=False)
    (output/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sources',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--matplotlib-libs',type=Path)
    a=p.parse_args(argv);r=render(a.sources,a.output,matplotlib_libs=a.matplotlib_libs)
    print(json.dumps(dict(figures=len(r['figures']),visually_reviewed=False)))


if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parents[4]))
    from Scripts.StructTrain.TimeLearner.publications.plot_algorithm_measurements import main as run
    run()
