"""Russian scientific figures from recorded trial samples, without new scoring.

The source manifest binds every observation to an archived primary and its exact
file bytes. Classification and training outcomes remain those of the referenced
experiment; this renderer never manufactures an evaluation verdict.
"""
import argparse
import hashlib
import html
import json
import math
from pathlib import Path
import sys
import textwrap


def _digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _checked_heading(figure, lines, height):
    """Keep the complete scientific title inside the exported image."""
    title = figure.suptitle('\n'.join(lines), fontsize=11, y=1-.04/height)
    figure.canvas.draw()
    extent = title.get_window_extent(figure.canvas.get_renderer())
    bounds = figure.bbox
    if extent.x0 < bounds.x0 or extent.x1 > bounds.x1 or extent.y0 < bounds.y0 or extent.y1 > bounds.y1:
        raise ValueError('Scientific figure heading exceeds the image bounds')


def physical_trial_title(observation):
    """Name the actual trial boundary, including the first reset of a stream."""
    from ..native_evidence import number, require
    labels={'target':'Целевой паттерн','foil':'Отвлекающий паттерн'}
    policies={'reset_per_trial':'сброс динамики',
              'preserve_neuron_dynamics':'сохранение динамики'}
    label=observation['label'];policy=observation['reset_policy']
    require(label in labels and policy in policies,'known_measured_figure_condition_required')
    intervals=observation['pattern_isi']
    require(type(intervals) is list and bool(intervals),'measured_figure_pattern_required')
    values='; '.join(format(number(v)*1000,'.8g') for v in intervals[1:])
    return labels[label]+' · '+policies[policy]+' · '+(values+' мс' if values else 'один импульс')


def _index(output, records):
    response_ru={'TP':'Правильное обнаружение','FP':'Ложное срабатывание',
                 'TN':'Правильное отклонение','FN':'Пропуск целевого паттерна'}
    sections=[]
    for i,row in enumerate(records,1):
        positive=next(p['name'] for p in row['positive_full_view']['files'] if p['name'].endswith('.png'))
        complete=next(p['name'] for p in row['files'] if p['name'].endswith('.png'))
        stimuli='; '.join(format(v,'.8g') for v in row['relative_stimulus_times'])
        spikes=row['relative_spike_times']
        events=('Выходные импульсы зарегистрированы в моменты '+
                '; '.join(format(v,'.8g') for v in spikes)+' с и отмечены красным пунктиром.'
                if spikes else 'Выходные импульсы в полном окне не зарегистрированы.')
        pattern='целевой' if row['response'] in ('TP','FN') else 'отвлекающий'
        description=('На рисунке '+str(i)+' приведены записанные потенциалы '+str(row['soma_count'])+
            ' участков сомы при предъявлении '+('целевого' if pattern=='целевой' else 'отвлекающего')+
            ' паттерна '+row['sample_id']+'. Каждая панель соответствует отдельной соме; '+
            'синяя кривая показывает её потенциал, оранжевые линии — фактические входные импульсы '+
            'в моменты '+stimuli+' с от первого зарегистрированного входа. '+events+' '+
            'Полное окно сохраняет поздние отклики; шкала положительного потенциала одинакова '+
            'для одной и той же сомы во всех показанных паттернах этого примера.')
        caption='Рисунок '+str(i)+' — '+response_ru[row['response']]+' паттерна '+row['sample_id']
        sections.append('<section><h2>'+html.escape(row['title'])+'</h2><p>'+html.escape(description)+
            '</p><figure><img src="'+positive+
            '" alt="Полное окно потенциала сом с входными импульсами"><figcaption>'+html.escape(caption)+
            '</figcaption></figure>'
            '<details><summary>Полная перезарядка и временное увеличение</summary><img src="'+complete+
            '" alt="Полный диапазон потенциала и временное увеличение"></details>'
            '<p class="identity">Модель: '+html.escape(row['model_revision'])+'</p></section>')
    text='''<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Фактические реакции: временные графики</title><style>
body{max-width:1100px;margin:24px auto;padding:0 16px;font:17px/1.5 system-ui;color:#18222e}
h1{font-size:1.7em}h2{font-size:1.2em}section{border-top:1px solid #ccd;margin-top:32px;padding-top:12px}
figure{margin:12px 0}img{width:100%;height:auto}figcaption,.identity{font-size:.9em}.identity{overflow-wrap:anywhere;color:#52606d}
summary{cursor:pointer;padding:8px 0}a{color:#1558a2}@media print{details{display:block}section{break-inside:avoid}}
</style><h1>Временные графики фактических реакций</h1>
<p>Показаны сохранённые отсчёты без прореживания. Начало отсчёта времени — первый зарегистрированный входной импульс каждой пробы.
Масштаб потенциала одинаков для иллюстраций одного примера. Отдельный вид полного положительного отклика сохраняет поздние вершины;
полный диапазон с перезарядкой доступен ниже каждого рисунка.</p>
<p>Подписи ответов взяты из исходной декларации иллюстраций. Этот просмотр не пересчитывает классификацию и не подтверждает сходимость обучения.
<a href="manifest.json">Источники, версии модели и контрольные суммы</a>.</p>'''+''.join(sections)+'</html>'
    path=output/'index.html';path.write_text(text,encoding='utf-8',newline='\n')
    return dict(name=path.name,bytes=path.stat().st_size,sha256=_digest(path))


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
    prepared=[];ids=set();limits={};response_limits={}
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
        if 'reset_policy' in row:
            require(row['reset_policy']==observation.get('reset_policy'),
                    'figure_declared_reset_policy_mismatch')
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
            baseline=values[0]
            response_low,response_high=response_limits.get(key,(baseline,max(finite)))
            response_limits[key]=(min(response_low,baseline),max(response_high,max(finite)))
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
            heading = [part for line in row['title'].splitlines()
                       for part in textwrap.wrap(line, width=66, break_on_hyphens=False)]
            heading.append(response_ru[row['response']])
            extra_header = .2 * max(0, len(heading)-2)
            height=max(3.,1.7*count+.6) + extra_header
            fig,axes=plt.subplots(count,2,figsize=(6.35,height),squeeze=False)
            # Explicit margins are stable with twinned stimulus axes. Automatic
            # title positioning may otherwise overlap another row's ticks or
            # the two-line overall title after a short-window zoom.
            fig.subplots_adjust(left=.13,right=.98,bottom=.52/height,
                                top=1-(.67+extra_header)/height,hspace=.72,wspace=.31)
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
                    axis.set_xlim(*window)
                    if column==0:axis.set_ylim(low-padding,high+padding)
                    else:
                        response_low,response_high=response_limits[(row['case_id'],channel)]
                        response_span=max(response_high-response_low,abs(response_low)*.01,1e-8)
                        axis.set_ylim(response_low-.05*response_span,response_high+.08*response_span)
                    axis.grid(alpha=.22,linewidth=.5)
                    axis.ticklabel_format(axis='y',style='sci',scilimits=(-3,3),useMathText=True)
                    axis.set_title('Полное окно' if column==0 else 'Масштаб отклика',y=1.,pad=5)
                    if column==0:axis.set_ylabel('Сома '+str(channel+1)+'\nусл. ед.')
                    if channel+1==count:axis.set_xlabel('Время от первого импульса, с')
                    input_axis=axis.twinx();input_axis.set_ylim(0,1.25);input_axis.set_yticks([])
                    input_axis.vlines(stimuli,0,1,color='#df7b20',linewidth=.9,alpha=.8,zorder=2)
                    for time in spikes:
                        axis.axvline(time,color='#a51b23',linestyle='--',linewidth=1,zorder=4)
            _checked_heading(fig, heading, height)
            # Explicit prose caption in the DOCX explains the common colour key.
            paths=[]
            for suffix in ('png','svg'):
                path=output/(row['id']+'.'+suffix)
                fig.savefig(path,dpi=220);paths.append(path)
            plt.close(fig)

            # A zoom around events and maxima can end before a later, lower
            # positive lobe. Keep the full-time positive-scale view as well.
            full,full_axes=plt.subplots(count,1,figsize=(6.35,height),squeeze=False)
            full.subplots_adjust(left=.13,right=.98,bottom=.52/height,
                                 top=1-(.67+extra_header)/height,hspace=.72)
            for channel,values in enumerate(potentials):
                axis=full_axes[channel,0];low,high=response_limits[(row['case_id'],channel)]
                span=max(high-low,abs(low)*.01,1e-8)
                axis.plot(times,values,color='#1756a9',linewidth=1.25,zorder=3)
                axis.set_xlim(left,right);axis.set_ylim(low-.05*span,high+.08*span)
                axis.grid(alpha=.22,linewidth=.5)
                axis.ticklabel_format(axis='y',style='sci',scilimits=(-3,3),useMathText=True)
                axis.set_ylabel('Сома '+str(channel+1)+'\nусл. ед.')
                if channel==0:axis.set_title('Положительный отклик — полное окно',y=1.,pad=5)
                if channel+1==count:axis.set_xlabel('Время от первого импульса, с')
                input_axis=axis.twinx();input_axis.set_ylim(0,1.25);input_axis.set_yticks([])
                input_axis.vlines(stimuli,0,1,color='#df7b20',linewidth=.9,alpha=.8,zorder=2)
                for time in spikes:axis.axvline(time,color='#a51b23',linestyle='--',linewidth=1,zorder=4)
            _checked_heading(full, heading, height)
            full_paths=[]
            for suffix in ('png','svg'):
                path=output/(row['id']+'-positive-full.'+suffix)
                full.savefig(path,dpi=220);full_paths.append(path)
            plt.close(full)
            records.append(dict(id=row['id'],case_id=row['case_id'],response=row['response'],
                title=row['title'],trial_id=row['trial_id'],sample_id=row['sample_id'],
                actual_reset_policy=observation.get('reset_policy'),
                complete_heading_within_image=True, heading_lines=heading,
                source_primary=row['primary'],source_observation=row['observation'],
                model_revision=row['model_revision'],onset=observation['stimulus_onset'],
                relative_stimulus_times=stimuli,relative_spike_times=spikes,
                soma_count=count,limits_scope='all declared illustrated trials of this case',
                response_limits_scope='right panels: above recorded initial level; shared within case and channel; full recharge remains in left panels',
                positive_full_view=dict(full_observation_window=True,late_positive_lobes_retained=True,
                    negative_recharge_shown_in_primary_full_window=True,
                    amplitude_limits_shared_with_other_trials_of_case=True,
                    files=[dict(name=p.name,bytes=p.stat().st_size,sha256=_digest(p)) for p in full_paths]),
                data_rescaled=False,files=[dict(name=p.name,bytes=p.stat().st_size,sha256=_digest(p)) for p in paths]))
    result=dict(kind='timelearner_scientific_trial_figures',schema_version=1,
        sources_sha256=_digest(specification),figures=records,renderer='Matplotlib',
        matplotlib_version=matplotlib.__version__,scientific_verdict=None,
        classification_recomputed=False,archive_provenance_reaudited_by_renderer=False,
        visually_reviewed=False)
    result['html_viewer']=_index(output,records)
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
