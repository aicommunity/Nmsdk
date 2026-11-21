"""Full-resolution soma/input and LT-event views after the production audit.

Produces a technical diagnostic cache, never a Git payload or a new scorer
verdict. Publication figures still require Russian captions and visual review.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path
import sys


def render(audit_path, output, python_source, matplotlib_libs=None):
    sys.path.insert(0,str(Path(python_source).resolve(strict=True)))
    if matplotlib_libs:sys.path.insert(0,str(Path(matplotlib_libs).resolve(strict=True)))
    sys.dont_write_bytecode=True
    from Scripts.StructTrain.TimeLearner.native_evidence import require
    from Scripts.StructTrain.TimeLearner.recognition_metrics import load_diagnostic_evaluation
    from Scripts.StructTrain.TimeLearner.plotting import padded_limits,plotting_runtime,render_soma,render_positive_lobe_views
    from Scripts.StructTrain.TimeLearner.lt_decision_reports import render_lt_decisions
    from Scripts.StructTrain.TimeLearner.runtime import file_record
    audit_path=Path(audit_path).resolve(strict=True)
    audit_raw=audit_path.read_bytes()
    audit=json.loads(audit_raw)
    require(audit['kind']=='timelearner_prepared_diagnostic_independent_audit' and
            audit['complete_source_history_audited'] and audit['all_input_bytes_unchanged'] and
            audit['native_evidence']['frozen_model_verified'], 'prepared_report_requires_complete_audit')
    metrics=audit['native_evidence']['metrics']
    require(metrics['validity']=='valid' and len(metrics['trials'])==8, 'prepared_report_incomplete_metrics')
    native=Path(audit['output'])/'native'
    execution=json.loads((native/'execution.json').read_bytes())
    records={r['path']:r for r in execution['artifacts']}
    require(execution['execution']=='completed' and execution['job_sha256']==audit['resolved_job_sha256'],
            'prepared_report_execution_changed')
    for name in ('evaluation.json',*[f'trial-{i}.json' for i in range(8)]):
        row=file_record(native/name)
        require(records[name]==dict(path=name,bytes=row['size'],sha256=row['sha256']),
                'prepared_report_primary_changed')
    spec,observations=load_diagnostic_evaluation(native/'evaluation.json')
    by_id={o['trial_id']:o for o in observations}
    require(set(by_id)=={r['trial_id'] for r in metrics['trials']} and len(by_id)==8,
            'prepared_report_trial_set_changed')
    runtime=plotting_runtime()
    output=Path(output).absolute()
    require(not output.exists() and '.git' not in output.parts, 'prepared_report_fresh_cache_required')
    output.mkdir(parents=True)
    count=len(observations[0]['samples'][0]['soma'])
    require(0<count<=256 and all(len(s['soma'])==count for o in observations for s in o['samples']),
            'prepared_report_soma_dimension_changed')
    shared=padded_limits([v for o in observations for s in o['samples'] for v in s['soma']])
    plotted=[]
    for trial in metrics['trials']:
        observation=by_id[trial['trial_id']]
        index=trial['presentation_index']
        for channel in range(count):
            folder=output/f'trial-{index:02d}-soma-{channel+1}'
            folder.mkdir()
            maximum=max(range(len(observation['samples'])),key=lambda i:observation['samples'][i]['soma'][channel])
            display={**observation,'diagnostic_peak_indices':([maximum] if 0<maximum<len(observation['samples'])-1 else [])}
            views=render_soma(display,channel,f'Soma channel {channel+1}',shared,folder,
                context_label='Same-Matrix stopped-model Test; actual '+trial['classification'])
            views.extend(render_positive_lobe_views(display,channel,f'Soma channel {channel+1}',folder,
                shared_minimum=min(v for o in observations for s in o['samples'] for v in s['soma']),
                context_label='Same-Matrix stopped-model Test; actual '+trial['classification']))
            plotted.append(dict(trial_id=trial['trial_id'],sample_id=trial['sample_id'],
                classification=trial['classification'],soma_index=channel,folder=folder.name,views=views))
    lt=render_lt_decisions(spec,observations,metrics['effective_threshold'],output,
                          context_label='Same-Matrix stopped-model Test; native LT decision/events')
    require(lt['all_declared_trials_rendered'] and lt['all_observations_complete'],
            'prepared_report_lt_coverage_incomplete')
    report=dict(kind='timelearner_prepared_diagnostic_visual_report',schema_version=1,
        audit_sha256=hashlib.sha256(audit_raw).hexdigest(),source_package_sha256=audit['source_package_sha256'],
        model_revision=metrics['model_revision'],protocol=audit['protocol'],counts=metrics['pooled_counts'],
        threshold=metrics['effective_threshold'],soma_count=count,trial_count=8,soma_views=plotted,lt_views=lt,
        plotting_runtime=runtime,all_patterns_and_somas_rendered=True,native_input_overlay=True,
        full_observation_windows=True,downsampling=False,minimum_native_zoom_tick_pixels=14.208,
        native_spike_events_authoritative=True,visual_acceptance_complete=False,publication_ready=False,
        training_completed=False,independently_heldout_evaluation=False,scientific_verdict=None)
    (output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    def section(title,folder,views):
        images=[]
        for view in views:
            png=next(p for p in view['files'] if p.endswith('.png'))
            images.append('<figure><div class="canvas"><img src="'+html.escape(folder+'/'+png,quote=True)+
                '" width="1920" height="960" loading="lazy"></div><figcaption>'+html.escape(view['view'])+'</figcaption></figure>')
        return '<section><h2>'+html.escape(title)+'</h2>'+images[0]+'<details><summary>Масштабные увеличения без прореживания</summary>'+''.join(images[1:])+'</details></section>'
    sections=[section(row['sample_id']+' — '+row['classification']+f' — Soma {row["soma_index"]+1}',
                      row['folder'],row['views']) for row in plotted]
    sections.extend(section(row['sample_id']+' — LT decision potential',row['folder'],row['views']) for row in lt['trials'])
    text='<!doctype html><html lang="ru"><meta charset="utf-8"><title>TimeLearner: фактические отклики</title><style>body{margin:24px;font:16px system-ui;color:#223}section{border-top:1px solid #ccd;margin-top:24px}.canvas{overflow-x:auto}img{max-width:none;width:1920px;height:960px}figure{margin:16px 0}pre{white-space:pre-wrap}</style><h1>Фактические реакции на восемь паттернов</h1><p>Historical Same-Matrix. Train остановлен; независимая оценка и сходимость не подтверждаются этим отчётом. Показаны реальные входы и события LT; изображения не используются для подсчёта ответов.</p><pre>'+html.escape(json.dumps(dict(counts=report['counts'],threshold=report['threshold'],model_revision=report['model_revision']),ensure_ascii=False,indent=2))+'</pre>'+''.join(sections)+'</html>'
    (output/'index.html').write_text(text,encoding='utf-8')
    require(audit_path.read_bytes()==audit_raw,'prepared_report_audit_changed')
    return report


def main():
    parser=argparse.ArgumentParser()
    for name in ('audit','output','python-source'):parser.add_argument('--'+name,required=True)
    parser.add_argument('--matplotlib-libs')
    args=parser.parse_args()
    result=render(args.audit,args.output,args.python_source,args.matplotlib_libs)
    print(json.dumps({k:result[k] for k in ('kind','counts','soma_count','trial_count','all_patterns_and_somas_rendered','visual_acceptance_complete','scientific_verdict')}))


if __name__=='__main__':main()
