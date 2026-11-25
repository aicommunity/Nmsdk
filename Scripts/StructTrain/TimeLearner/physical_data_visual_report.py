"""Full-resolution soma/input and LT-event views after the complete DATA production audit.

Produces a technical diagnostic cache, never a Git payload or a new scorer
verdict. Publication figures still require Russian captions and visual review.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path
import sys


def render(manifest_path, output, python_source, matplotlib_libs=None, *, archived_source=False,
           include_native_tiles=True):
    sys.path.insert(0,str(Path(python_source).resolve(strict=True)))
    if matplotlib_libs:sys.path.insert(0,str(Path(matplotlib_libs).resolve(strict=True)))
    sys.dont_write_bytecode=True
    from Scripts.StructTrain.TimeLearner.native_evidence import require
    from Scripts.StructTrain.TimeLearner.recognition_metrics import load_physical_model_data_evaluation
    from Scripts.StructTrain.TimeLearner.plotting import padded_limits,plotting_runtime,render_soma,render_positive_lobe_views
    from Scripts.StructTrain.TimeLearner.lt_decision_reports import render_lt_decisions
    from Scripts.StructTrain.TimeLearner.runtime import file_record
    from Scripts.StructTrain.TimeLearner.native_pipeline_worker import audit_run_manifest
    from Scripts.StructTrain.TimeLearner.contained_process import inspect
    manifest_path=Path(manifest_path).resolve(strict=True)
    manifest_raw=manifest_path.read_bytes();manifest=json.loads(manifest_raw)
    audited=audit_run_manifest(manifest_path)
    require(audited['run_evidence_consistent'] and manifest['operation']=='physical-model-evaluate' and
            manifest['execution']=='completed' and manifest['validity']=='valid',
            'physical_visual_report_requires_complete_production_audit')
    require(type(archived_source) is bool and type(include_native_tiles) is bool,
            'physical_visual_report_source_policy_invalid')
    if not archived_source:
        require(inspect(manifest_path.parent/'process/contained')['all_processes_closed'],
                'physical_visual_report_model_process_not_closed')
    # Portable production audit above still binds every primary byte, the
    # original runtime/process evidence and its complete observation set.
    # A report cache on another host cannot re-observe the original kernel.
    # This option authorizes rendering only; it never authorizes execution or
    # upgrades an archived process claim into a fresh native attestation.
    metrics=manifest['analysis']['metrics'];expected=len(metrics['trials'])
    require(metrics['validity']=='valid' and metrics['data_only'] and expected>=2,
            'physical_visual_report_incomplete_metrics')
    native=manifest_path.parent/'native';execution=json.loads((native/'execution.json').read_bytes())
    records={r['path']:r for r in execution['artifacts']}
    require(execution['execution']=='completed' and execution['job_sha256']==manifest['job_sha256'],
            'physical_visual_report_execution_changed')
    names=['evaluation.json',*[f'trial-{i}.json' for i in range(expected)]]
    before={name:file_record(native/name) for name in records};execution_before=file_record(native/'execution.json')
    require(all(records[name]==dict(path=name,bytes=row['size'],sha256=row['sha256'])
                for name,row in before.items()),'physical_visual_report_primary_changed')
    spec,observations=load_physical_model_data_evaluation(native/'evaluation.json')
    by_id={o['trial_id']:o for o in observations}
    require(set(by_id)=={r['trial_id'] for r in metrics['trials']} and len(by_id)==expected,
            'physical_visual_report_trial_set_changed')
    runtime=plotting_runtime()
    output=Path(output).absolute()
    require(not output.exists() and '.git' not in output.parts, 'physical_visual_report_fresh_cache_required')
    output.mkdir(parents=True)
    count=len(observations[0]['samples'][0]['soma'])
    require(0<count<=256 and all(len(s['soma'])==count for o in observations for s in o['samples']),
            'physical_visual_report_soma_dimension_changed')
    values=[v for o in observations for s in o['samples'] for v in s['soma']]
    shared=padded_limits(values)
    shared_minimum,shared_maximum=min(values),max(values)
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
                include_native_tiles=include_native_tiles,
                context_label='Fixed DATA Test; actual '+trial['classification'])
            views.extend(render_positive_lobe_views(display,channel,f'Soma channel {channel+1}',folder,
                shared_minimum=shared_minimum,shared_maximum=shared_maximum,
                include_native_tiles=include_native_tiles,
                context_label='Fixed DATA Test; actual '+trial['classification']))
            plotted.append(dict(trial_id=trial['trial_id'],sample_id=trial['sample_id'],
                classification=trial['classification'],soma_index=channel,folder=folder.name,views=views))
    lt=render_lt_decisions(spec,observations,metrics['effective_threshold'],output,
                          include_native_tiles=include_native_tiles,
                          context_label='Fixed DATA Test; native LT decision/events')
    require(lt['all_declared_trials_rendered'] and lt['all_observations_complete'],
            'physical_visual_report_lt_coverage_incomplete')
    report=dict(kind='timelearner_physical_data_visual_report',schema_version=1,
        source_manifest_sha256=hashlib.sha256(manifest_raw).hexdigest(),source_model_data_sha256=execution['model_sha256'],
        model_revision=metrics['model_revision'],protocol='frozen_physical_data_evaluation',counts=metrics['pooled_counts'],
        threshold=metrics['effective_threshold'],soma_count=count,trial_count=expected,soma_views=plotted,lt_views=lt,
        plotting_runtime=runtime,all_patterns_and_somas_rendered=True,native_input_overlay=True,
        full_observation_windows=True,downsampling=False,minimum_native_zoom_tick_pixels=14.208,
        native_spike_events_authoritative=True,visual_acceptance_complete=False,publication_ready=False,
        source_process_policy='archived-evidence-only' if archived_source else 'live-host-closure',
        source_kernel_closure_reobserved=not archived_source,native_execution_attested=False,
        time_view_policy='all-native-tiles' if include_native_tiles else 'full-window-and-measured-peak-details',
        training_completed=None,source_training_evidence_checked=False,independently_heldout_evaluation=None,scientific_verdict=None)
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
    text='<!doctype html><html lang="ru"><meta charset="utf-8"><title>TimeLearner: фактические отклики</title><style>body{margin:24px;font:16px system-ui;color:#223}section{border-top:1px solid #ccd;margin-top:24px}.canvas{overflow-x:auto}img{max-width:none;width:1920px;height:960px}figure{margin:16px 0}pre{white-space:pre-wrap}</style><h1>Фактические реакции сохранённой модели</h1><p>Сохранённая DATA-модель и фиксированный порог. Полные наблюдения проверены по production manifest; история обучения и сходимость этим техническим отчётом не подтверждаются. Показаны реальные входы и события LT; изображения не используются для подсчёта ответов.</p><pre>'+html.escape(json.dumps(dict(counts=report['counts'],threshold=report['threshold'],model_revision=report['model_revision']),ensure_ascii=False,indent=2))+'</pre>'+''.join(sections)+'</html>'
    (output/'index.html').write_text(text,encoding='utf-8')
    require(manifest_path.read_bytes()==manifest_raw and {name:file_record(native/name) for name in records}==before and file_record(native/'execution.json')==execution_before,
            'physical_visual_report_source_changed')
    return report


def main():
    parser=argparse.ArgumentParser()
    for name in ('manifest','output','python-source'):parser.add_argument('--'+name,required=True)
    parser.add_argument('--matplotlib-libs')
    parser.add_argument('--archived-source', action='store_true',
                        help='Render audited archived bytes without re-attesting the original host kernel')
    parser.add_argument('--compact-views', action='store_true',
                        help='Full windows and measured peak details; omit exhaustive native-tick tiles')
    args=parser.parse_args()
    result=render(args.manifest,args.output,args.python_source,args.matplotlib_libs,
                  archived_source=args.archived_source, include_native_tiles=not args.compact_views)
    print(json.dumps({k:result[k] for k in ('kind','counts','soma_count','trial_count','all_patterns_and_somas_rendered','visual_acceptance_complete','scientific_verdict')}))


if __name__=='__main__':main()
