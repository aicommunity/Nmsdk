"""Russian scientific figures from recorded trial samples, without new scoring.

The source manifest binds every observation to an archived primary and its exact
file bytes. Classification and training outcomes remain those of the referenced
experiment; this renderer never manufactures an evaluation verdict.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys


def _digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(specification, output, *, matplotlib_libs=None):
    from ..external_archive import validate_reference
    from ..native_evidence import load, number, require
    if matplotlib_libs is not None:
        sys.path.insert(0, str(Path(matplotlib_libs).resolve(strict=True)))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    specification=Path(specification).resolve(strict=True)
    spec=load(specification);output=Path(output).resolve()
    require(spec.get('kind')=='timelearner_scientific_trial_figure_sources' and
            spec.get('schema_version')==1 and type(spec.get('trials')) is list and
            0<len(spec['trials'])<=256,'known_finite_figure_manifest_required')
    require(not output.exists(),'fresh_scientific_figure_output_required')
    root=specification.parent
    prepared=[];ids=set();limits={}
    for row in spec['trials']:
        identity=row['id'];require(type(identity) is str and identity and
            all(c in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in identity) and
            identity not in ids,'unique_safe_figure_id_required');ids.add(identity)
        validate_reference(row['primary'])
        reference=row['observation'];relative=Path(reference['path'])
        require(not relative.is_absolute() and '..' not in relative.parts,'local_observation_path_required')
        path=(root/relative).resolve(strict=True)
        require(path.is_relative_to(root) and path.is_file() and
                path.stat().st_size==reference['bytes'] and _digest(path)==reference['sha256'],
                'figure_observation_bytes_changed')
        observation=load(path)
        require(observation.get('trial_id')==row['trial_id'] and observation.get('sample_id')==row['sample_id'],
                'figure_observation_identity_mismatch')
        require(observation.get('model_before')==row['model_revision'] and
                observation.get('model_after')==row['model_revision'],'figure_frozen_model_changed')
        require(observation.get('complete') is True and observation.get('valid') is True and
                observation.get('censored') is False,'complete_valid_trial_required_for_recognition_figure')
        samples=observation['samples'];require(type(samples) is list and samples,'recorded_samples_required')
        count=len(samples[0]['soma']);require(0<count<=256,'recorded_soma_dimension_required')
        begin,end,onset=(number(observation[k]) for k in ('begin','end','stimulus_onset'))
        frequency=number(observation['frequency_hz'])
        require(end>begin and begin<=onset<=end and frequency>0,'recorded_figure_window_required')
        require(number(observation['closed_at'])>=end-1e-9,'recognition_figure_window_not_closed')
        previous=None;times=[];potentials=[[] for _ in range(count)]
        for sample in samples:
            time=number(sample['time']);require(previous is None or time>previous,'unordered_figure_samples')
            require(len(sample['soma'])==count,'figure_soma_dimension_changed')
            require(previous is None or time-previous<=1.5/frequency,
                    'incomplete_recorded_grid_for_complete_recognition_figure')
            times.append(time-onset)
            for channel,value in enumerate(sample['soma']):potentials[channel].append(number(value))
            previous=time
        require(number(samples[0]['time'])<=begin+1/frequency+1e-9 and
                number(samples[-1]['time'])>=end-1/frequency-1e-9,'figure_samples_do_not_cover_window')
        stimuli=[number(v)-onset for v in observation['stimulus_times']]
        spikes=[number(v)-onset for v in observation['spike_times']]
        require(len(spikes)==observation['spike_count'],'figure_spike_count_mismatch')
        require(all(begin-onset<=v<=end-onset for v in stimuli+spikes),'figure_event_outside_window')
        expected=row['response']
        require(expected in ('TP','FP','TN','FN') and
            observation['label']==('target' if expected in ('TP','FN') else 'foil'),
            'figure_response_label_mismatch')
        require(expected not in ('TP','FP') or bool(spikes),'declared_response_has_no_recorded_spike')
        require(expected!='TN' or not spikes,'declared_true_negative_has_recorded_spike')
        # A missed target may have spikes outside its declared response window.
        # The production scorer decides this; the figure must retain the events.
        # This is a consistency check on an explicitly selected illustration,
        # not the production target timing criterion or a recalculated score.
        group=row['case_id'];require(type(group) is str and group,'figure_case_required')
        for channel,values in enumerate(potentials):
            finite=[v for v in values if math.isfinite(v)];key=(group,channel)
            low,high=limits.get(key,(min(finite),max(finite)))
            limits[key]=(min(low,min(finite)),max(high,max(finite)))
        prepared.append((row,observation,times,potentials,stimuli,spikes,begin-onset,end-onset))
    output.mkdir(parents=True)
    records=[]
    response_ru={'TP':'Правильное обнаружение','FP':'Ложное срабатывание',
                 'TN':'Правильное отклонение','FN':'Пропуск целевого паттерна'}
    style={'font.family':'DejaVu Sans','font.size':10.5,'axes.titlesize':10.5,
           'axes.labelsize':10,'xtick.labelsize':9,'ytick.labelsize':9,
           'svg.fonttype':'none','savefig.facecolor':'white'}
    with plt.rc_context(style):
        for row,observation,times,potentials,stimuli,spikes,left,right in prepared:
            count=len(potentials)
            fig,axes=plt.subplots(count,2,figsize=(6.35,max(2.7,1.72*count)),
                                 squeeze=False,layout='constrained')
            peak_times=[]
            for values in potentials:
                maximum=max(v for v in values if math.isfinite(v))
                peak_times.append(times[next(i for i,v in enumerate(values) if v==maximum)])
            observed=stimuli+spikes+peak_times
            margin=min(.08,.12*(right-left))
            zoom_left=max(left,min([0.]+observed)-margin*.4)
            zoom_right=min(right,max(observed)+margin)
            if zoom_right-zoom_left<2/frequency:
                zoom_right=min(right,zoom_left+2/frequency)
            for channel,values in enumerate(potentials):
                low,high=limits[(row['case_id'],channel)]
                padding=max((high-low)*.08,1e-8)
                for column,window in enumerate(((left,right),(zoom_left,zoom_right))):
                    axis=axes[channel,column]
                    axis.plot(times,values,color='#1756a9',linewidth=1.25,zorder=3)
                    axis.set_xlim(*window);axis.set_ylim(low-padding,high+padding)
                    axis.grid(alpha=.22,linewidth=.5)
                    axis.ticklabel_format(axis='y',style='sci',scilimits=(-3,3),useMathText=True)
                    axis.set_title('Полное окно' if column==0 else 'Увеличенный фрагмент')
                    if column==0:axis.set_ylabel('Сома '+str(channel+1)+'\nусл. ед.')
                    if channel+1==count:axis.set_xlabel('Время, с')
                    input_axis=axis.twinx();input_axis.set_ylim(0,1.25);input_axis.set_yticks([])
                    input_axis.vlines(stimuli,0,1,color='#df7b20',linewidth=.9,alpha=.8,zorder=2)
                    for time in spikes:
                        axis.axvline(time,color='#a51b23',linestyle='--',linewidth=1,zorder=4)
            fig.suptitle(row['title']+'\n'+response_ru[row['response']],fontsize=11)
            # Explicit prose caption in the DOCX explains the common colour key.
            paths=[]
            for suffix in ('png','svg'):
                path=output/(row['id']+'.'+suffix)
                fig.savefig(path,dpi=220);paths.append(path)
            plt.close(fig)
            records.append(dict(id=row['id'],case_id=row['case_id'],response=row['response'],
                title=row['title'],trial_id=row['trial_id'],sample_id=row['sample_id'],
                source_primary=row['primary'],source_observation=row['observation'],
                model_revision=row['model_revision'],onset=observation['stimulus_onset'],
                relative_stimulus_times=stimuli,relative_spike_times=spikes,
                soma_count=count,limits_scope='all declared illustrated trials of this case',
                data_rescaled=False,files=[dict(name=p.name,bytes=p.stat().st_size,sha256=_digest(p)) for p in paths]))
    result=dict(kind='timelearner_scientific_trial_figures',schema_version=1,
        sources_sha256=_digest(specification),figures=records,renderer='Matplotlib',
        matplotlib_version=matplotlib.__version__,scientific_verdict=None,
        classification_recomputed=False,archive_provenance_reaudited_by_renderer=False,
        visually_reviewed=False)
    (output/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',
                                      encoding='utf-8',newline='\n')
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--matplotlib-libs',type=Path)
    args=parser.parse_args(argv)
    result=render(args.sources,args.output,matplotlib_libs=args.matplotlib_libs)
    print(json.dumps(dict(figures=len(result['figures']),visually_reviewed=False)))


if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parents[4]))
    from Scripts.StructTrain.TimeLearner.publications.plot_algorithm_trials import main as run
    run()
