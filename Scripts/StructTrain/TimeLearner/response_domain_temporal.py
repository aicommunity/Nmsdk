"""All-channel native domain diagnostic waveforms; render on designated workers.

The independent packet/primary audit precedes all report output. These figures
describe diagnostic captures, not classification of an eight-pattern matrix.
"""
import argparse
import csv
import hashlib
import html
import io
import json
from pathlib import Path
import re

from .native_evidence import load, number, require
from .response_domain_evidence import audit_response_domain_file
from .plotting import figure_title, padded_limits, plotting_runtime, time_views


def _binding(path):
    require(path.is_file() and not path.is_symlink(), 'domain_report_primary_missing_or_alias')
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def render(corpus, output, source_evidence):
    require(type(source_evidence) is str and re.fullmatch(r'[0-9a-f]{40}', source_evidence) is not None,
            'domain_report_requires_source_commit')
    corpus = Path(corpus).resolve(strict=True); output = Path(output).resolve()
    require(corpus.is_dir() and not output.exists() and not output.is_relative_to(corpus) and
            not corpus.is_relative_to(output), 'domain_report_output_overlaps_or_exists')
    packets = sorted(corpus.rglob('*.domains.json'))
    require(bool(packets), 'domain_report_empty_corpus')
    cases, limits, bindings, identities = [], {}, {}, set()
    # No backend import or output creation before every primary packet passes.
    for path in packets:
        require(not path.is_symlink() and path.resolve(strict=True).is_relative_to(corpus), 'domain_report_packet_alias')
        before = _binding(path)
        audit = audit_response_domain_file(path)
        packet = load(path); trace = path.parent/packet['trace']['path']
        require(trace.resolve(strict=True).is_relative_to(corpus), 'domain_report_trace_outside_corpus')
        trace_binding = _binding(trace); raw = trace.read_bytes()
        require(len(raw)==trace_binding['bytes'] and hashlib.sha256(raw).hexdigest()==trace_binding['sha256'],
                'domain_report_trace_changed_during_read')
        require(trace_binding == {'bytes': packet['trace']['bytes'], 'sha256': packet['trace']['sha256']},
                'domain_report_primary_changed_after_audit')
        require(before == _binding(path), 'domain_report_packet_changed_after_audit')
        observation = packet['native_evidence']['observation']; spec = observation['specification']
        prepared = packet['native_evidence']['prepared']; identity = (spec['run_id'], spec['trial_id'])
        require(identity not in identities, 'domain_report_duplicate_trial'); identities.add(identity)
        rows = list(csv.reader(io.StringIO(raw.decode('utf-8'), newline=''), strict=True))
        values = [[number(float(v)) for v in row] for row in rows[1:]]
        topology = 'Classic' if prepared['routing'] == 'classic_burst' else 'Branch'
        frequency = number(spec['stimulus_profile']['frequency_hz'])
        mappings = packet['capture']['channel_mapping']
        for index, mapping in enumerate(mappings):
            key = (topology, mapping['physical_path'])
            data = [row[index+2] for row in values]+[number(mapping['baseline'])]
            lo, hi = min(data), max(data); previous = limits.get(key, (lo,hi))
            limits[key] = (min(lo,previous[0]), max(hi,previous[1]))
        relative = path.relative_to(corpus).as_posix(); trace_relative = trace.relative_to(corpus).as_posix()
        for filename, binding in ((relative,before),(trace_relative,trace_binding)):
            require(filename not in bindings or bindings[filename] == binding, 'domain_report_binding_collision')
            bindings[filename] = binding
        cases.append({'packet': relative, 'trace': trace_relative, 'topology': topology, 'frequency_hz': frequency,
                      'spec': spec, 'prepared': prepared, 'mapping': mappings, 'events': observation['stimuli'],
                      'values': values, 'audit': audit, 'legacy_assignment_valid': observation['valid']})
    runtime = plotting_runtime()
    import matplotlib.pyplot as plt
    output.mkdir(parents=True, exist_ok=False)
    figures, case_records, selected = [], [], []
    shared = {key: padded_limits(list(value)) for key,value in limits.items()}
    with plt.rc_context({'font.size':12, 'axes.titlesize':12, 'axes.labelsize':12,
                         'xtick.labelsize':11, 'ytick.labelsize':11, 'svg.fonttype':'none',
                         'path.simplify':False, 'agg.path.chunksize':0}):
        for serial, case in enumerate(cases, 1):
            spec = case['spec']; times = [row[0] for row in case['values']]
            stimulus = [row[1] for row in case['values']]
            folder = output/f'case-{serial:04d}-{case["topology"]}'
            folder.mkdir()
            case_record = {key:case[key] for key in ('packet','trace','topology','frequency_hz','audit','legacy_assignment_valid')}
            case_record.update(run_id=spec['run_id'],trial_id=spec['trial_id'],sample_id=spec['sample_id'],
                pattern_hash=spec['pattern_hash'],base_model_revision=case['prepared']['base_model_revision'],
                effective_model_revision=case['prepared']['effective_model_revision'],sample_count=len(times),
                actual_stimuli=case['events'],channels=case['mapping'],figure_indices=[])
            case_records.append(case_record)
            for ch_index, mapping in enumerate(case['mapping']):
                channel = mapping['channel']; physical = mapping['physical_path']
                y_limits = shared[case['topology'],physical]
                values = [row[ch_index+2] for row in case['values']]
                for view, left, right in time_views(spec['begin'], spec['end'], case['frequency_hz']):
                    fig, axis = plt.subplots(figsize=(12,6), dpi=160)
                    try:
                        fig.subplots_adjust(left=.12,right=.86,bottom=.16,top=.67)
                        overlay = axis.twinx()
                        axis.plot(times,values,color='#154c9a',linewidth=1.4,label='Recorded soma potential')
                        axis.axhline(mapping['baseline'],color='#666666',linestyle='--',linewidth=.8,label='Native rest baseline')
                        overlay.step(times,stimulus,where='post',color='#d46200',alpha=.55,linewidth=1.1,
                                     label='Actual shared input (native samples)')
                        amplitude = spec['stimulus_profile']['amplitude']
                        overlay.set_ylim(-.05*amplitude,1.1*amplitude)
                        overlay.set_ylabel('Input [native generator units]',color='#a34d00')
                        overlay.tick_params(axis='y',colors='#a34d00')
                        labelled = False
                        for event in case['events']:
                            if left <= event['time'] <= right:
                                axis.axvline(event['time'],color='#666666',linestyle=':',linewidth=.9,
                                             label='Actual stimulus timestamps' if not labelled else None)
                                labelled = True
                        axis.set_xlim(left,right);axis.set_ylim(*y_limits);axis.grid(alpha=.25)
                        axis.set_xlabel('Native absolute time [s]')
                        axis.set_ylabel('Soma potential [native units; SI unverified]')
                        figure_title(fig, f'{case["topology"]} | {physical} | {case["frequency_hz"]:g} Hz | {view}\n'
                            f'Trial {spec["trial_id"]}\n'
                            'Diagnostic waveform; declared domains do not prove peak origin\n'
                            f'Base {case["prepared"]["base_model_revision"][:12]} | measured {spec["effective_model_revision"][:12]}',
                            font_sizes=(12,))
                        handles,labels=axis.get_legend_handles_labels();more,extra=overlay.get_legend_handles_labels()
                        fig.legend(handles+more,labels+extra,loc='upper center',bbox_to_anchor=(.5,.83),frameon=False,ncol=2)
                        fig.canvas.draw()
                        width,height=fig.canvas.get_width_height(); axes_width=axis.get_window_extent().width
                        pixels_per_tick=axes_width/(case['frequency_hz']*(right-left))
                        require(view=='overview' or pixels_per_tick>=8., 'domain_report_tick_scale_too_small')
                        stem=f'channel-{int(channel):03d}-{view}';files=[]
                        for extension in ('png','svg'):
                            target=folder/(stem+'.'+extension);fig.savefig(target)
                            files.append(target.relative_to(output).as_posix())
                        row={'case_index':serial-1,'packet':case['packet'],'topology':case['topology'],
                             'channel':channel,'physical_path':physical,'frequency_hz':case['frequency_hz'],
                             'view':view,'x_bounds_s':[left,right],'y_bounds_native':list(y_limits),
                             'shared_y_group':[case['topology'],physical],'pixels':[width,height],
                             'axes_width_pixels':axes_width,'minimum_native_tick_pixels_on_zoom':None if view=='overview' else pixels_per_tick,
                             'full_sample_count':len(times),'plotted_sample_count':len(times),'downsampling':False,
                             'matplotlib_path_simplification':False,'actual_input_overlay':True,
                             'actual_event_times':[e['time'] for e in case['events']],
                             'potential_units':'native_units_SI_unverified','files':files}
                        case_record['figure_indices'].append(len(figures));figures.append(row)
                        if view=='overview':selected.append({'case_index':serial-1,'channel':channel,'png':files[0]})
                    finally:plt.close(fig)
    # A changed primary cannot acquire a positive final report manifest.
    for relative, expected in bindings.items():
        require(_binding(corpus/relative)==expected,'domain_report_primary_changed_during_render')
    entries=[]
    for row in figures:
        png,svg=row['files'];caption=f'{row["topology"]} / {row["physical_path"]} / {row["frequency_hz"]:g} Hz / {row["view"]}'
        entries.append('<h2>'+html.escape(caption)+'</h2><p>Case '+str(row['case_index']+1)+
            ' — '+html.escape(row['packet'])+'</p><a href="'+html.escape(svg,quote=True)+'">SVG</a> · '
            '<a href="'+html.escape(png,quote=True)+'">Full-size PNG</a><div class="frame"><img src="'+html.escape(png,quote=True)+'" alt="'+html.escape(caption,quote=True)+'"></div>')
    (output/'index.html').write_text('<!doctype html><html><head><meta charset="utf-8"><title>Native domain diagnostic waveforms</title>'
        '<style>body{font-family:sans-serif;margin:20px}.frame{overflow-x:auto}.frame img{width:1920px;max-width:none;height:auto}</style></head><body>'
        '<h1>Native domain diagnostic waveforms</h1><p>All recorded somas; actual input overlays and stimulus timestamps. '
        'Overview plus 100-native-tick tiles, with no downsampling. Each zoom retains at least eight pixels per tick. '
        'Shared potential Y limits compare corresponding somas within each topology across frequencies. '
        'Open images at full size or scroll horizontally; browser fit-to-window may reduce apparent resolution.</p>'
        '<p>Native potential units, SI unverified. Diagnostic captures only: no proven peak origin, training certificate, '
        'spike-silence claim or eight-pattern classification verdict.</p>'+''.join(entries)+'</body></html>',encoding='utf-8')
    generated={p.relative_to(output).as_posix():_binding(p) for p in sorted(output.rglob('*')) if p.is_file()}
    manifest={'kind':'timelearner_response_domain_temporal_report','schema_version':1,
        'declared_source_evidence':source_evidence,'source_evidence_independently_verified':False,
        'primary_file_bindings':bindings,'cases':case_records,'case_count':len(cases),
        'trial_soma_pairs':sum(len(c['mapping']) for c in cases),'figures':figures,'selected_overviews':selected,
        'figure_files':generated,'plotting_runtime':runtime,
        'y_scale':'shared per (topology, physical soma path) across frequencies',
        'downsampling':False,'time_frame':'absolute_model_time','tick_tile_width':100,
        'diagnostic_only':True,'training_certificate_eligible':False,'causal_origin_verified':False,
        'physical_paths_independently_verified':False,'spike_response':'unknown','scientific_verdict':None}
    with (output/'manifest.json').open('x',encoding='utf-8') as stream:
        json.dump(manifest,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')
    return manifest


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--source-evidence',required=True)
    args=parser.parse_args(argv);result=render(args.corpus,args.output,args.source_evidence)
    print(json.dumps({'cases':result['case_count'],'trial_soma_pairs':result['trial_soma_pairs'],'figures':len(result['figures'])}))


if __name__=='__main__':main()
