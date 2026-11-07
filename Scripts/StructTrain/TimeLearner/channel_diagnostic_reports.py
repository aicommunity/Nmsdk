"""Joint native soma/channel/feedback/LT plots with actual input overlays.

Channel deltas use the first recorded values, never an assumed zero rest state.
Every ordinate is a recorded value or an explicitly labelled subtraction.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import html
import json
import re

from .domain_evidence import _property
from .native_characterization import audit_execution, is_single_pulse
from .native_evidence import load, measured_wave_plateaus, number, require
from .plotting import figure_title, padded_limits, plotting_runtime, time_views
from .primary_reuse import _git_archive, _stream


def chart(directory, soma):
    directory = Path(directory)
    accepted = audit_execution(directory)
    require(accepted['execution'] == 'completed' and accepted['observation_complete'],
            'channel_plot_requires_closed_native_probe')
    job, execution = load(directory/'job.json'), load(directory/'execution.json')
    require(job['schema_version'] in (3, 4, 5) and job['channel_diagnostics'] is True and
            not job['resistance_intervention'] and execution['terminal_phase'] == 'main_probe',
            'channel_plot_requires_unmodified_main_diagnostic_probe')
    n = 1 if job['model']['branch'] else len(job['model']['inputs'])
    require(type(soma) is int and 0 <= soma < n, 'channel_plot_soma_out_of_range')
    data = load(directory/'probe_diagnostics_1.json')
    packet = load(directory/'probe_trial_1.json');spec = packet['observation']['specification']
    with (directory/'probe_trial_1.csv').open(encoding='utf-8', newline='') as stream:
        primary = list(csv.DictReader(stream))
    columns = {d['path']: i for i, d in enumerate(data['descriptors'])}
    def series(path):
        return [number(row['values'][columns[path]]) for row in data['samples']]
    path = '$.Soma'+str(soma+1)
    exc, inh = series(path+'.ExcChannel.Output'), series(path+'.InhChannel.Output')
    identity = load(directory/'initial-state.json')['identity']
    zone = next(n for n in identity['model']['nodes'] if n['path'] == '$.LTZone')
    threshold = number(_property(zone, 'Threshold'))
    panels = [
        {'label': 'Recorded soma SumPotential', 'series': [('SumPotential', series(path+'.SumPotential'))]},
        {'label': 'Channel output changes from first recorded sample',
         'series': [('Exc output minus initial '+format(exc[0], '.8g'), [v-exc[0] for v in exc]),
                    ('Inh output minus initial '+format(inh[0], '.8g'), [v-inh[0] for v in inh])]},
        {'label': 'Recorded membrane Feedback and LT Output',
         'series': [('Feedback', series(path+'.Feedback')), ('LT Output', series('$.LTZone.Output'))]},
        {'label': 'Recorded LT decision potential',
         'series': [('LT Potential', series('$.LTZone.Potential'))]},
    ]
    for i, panel in enumerate(panels):
        values = [v for _, signal in panel['series'] for v in signal]
        if i == 3:values.append(threshold)
        panel['shared_limits'] = padded_limits(values)
    signal=panels[0]['series'][0][1]
    peak_indices=[first for first,_ in measured_wave_plateaus(
        [v-number(spec['baseline'][soma]) for v in signal], number(spec['minimum_amplitude']))]
    return {'soma_path': path, 'trial_id': data['trial_id'], 'model_revision': data['base_model_revision'],
            'observed_model_revision':spec['effective_model_revision'],
            'begin': spec['begin'], 'end': spec['end'], 'frequency_hz': job['model']['frequency_hz'],
            'times': [number(row['time']) for row in data['samples']],
            'stimulus': [number(float(row['stimulus'])) for row in primary],
            'panels': panels, 'threshold': threshold,
            'lt_spike_times': [number(t) for row in data['samples'] for t in row['new_lt_spike_times']],
            'raw_initial_channel_values': {'Exc': exc[0], 'Inh': inh[0]},
            'diagnostic_peak_indices': peak_indices,
            'peak_observation_valid': packet['observation']['valid'],
            'observation_context': {
                'complete': packet['observation']['complete'],
                'packet_valid': packet['observation']['valid'],
                'packet_reasons': packet['observation']['reasons'],
                'window_input_ids': [w['input_id'] for w in spec['windows']],
                'window_channels': sorted({w['channel'] for w in spec['windows']}),
                'plotted_channel_has_window': any(w['channel'] == soma for w in spec['windows'])},
            **({'diagnostic_purpose':'single_pulse_characterization'} if is_single_pulse(job) else {}),
            **({'storage_profile_intervention':job['profile_intervention']} if job['schema_version']==5 else {}),
            'primary': {name: hashlib.sha256((directory/name).read_bytes()).hexdigest() for name in
                        ('probe_trial_1.json', 'probe_trial_1.csv', 'probe_diagnostics_1.json', 'initial-state.json')}}


def observation_caption(data):
    """Packet validity does not independently classify an additional soma."""
    context = data.get('observation_context')
    require(type(context) is dict and
            all(type(context.get(k)) is bool for k in ('complete','packet_valid','plotted_channel_has_window')) and
            type(context.get('window_input_ids')) is list and bool(context['window_input_ids']) and
            all(type(v) is str and bool(v) for v in context['window_input_ids']),
            'channel_plot_observation_scope_missing')
    return ('Recorded waveform complete='+str(context['complete'])+
            ' | packet observation valid='+str(context['packet_valid'])+'\n'+
            'Packet window input(s): '+', '.join(context['window_input_ids'])+
            ' | plotted channel has window='+str(context['plotted_channel_has_window']))


def render_figure(data, name, left, right, output, local=False):
    import matplotlib.pyplot as plt
    times = data['times'];panels = data['panels']
    fig, axes = plt.subplots(4, 1, figsize=(12, 12), dpi=160, sharex=True)
    fig.subplots_adjust(left=.12, right=.86, bottom=.06, top=.79, hspace=.43)
    handles=[];labels=[];colors=['#154c9a', '#b45f06', '#228b22', '#7d3c98'];limits=[]
    visible=[i for i,t in enumerate(times) if left <= t <= right]
    bracket=range(max(0,visible[0]-1), min(len(times),visible[-1]+2))
    for i, (ax, panel) in enumerate(zip(axes, panels)):
        for j, (label, values) in enumerate(panel['series']):
            line, = ax.plot(times, values, color=colors[(i+j)%len(colors)], linewidth=1.3, label=label)
            handles.append(line);labels.append(label)
            if local:
                ax.plot([times[k] for k in visible], [values[k] for k in visible], linestyle='none',
                        marker='o',markersize=3,markerfacecolor='none',color=line.get_color())
        panel_limits=(padded_limits([values[k] for _,values in panel['series'] for k in bracket])
                      if local else panel['shared_limits'])
        limits.append(panel_limits)
        ax.set_ylim(*panel_limits);ax.set_xlim(left, right)
        ax.set_ylabel('Native units\nSI unverified', fontsize=12)
        extra=('; threshold outside local Y' if i==3 and not panel_limits[0] <= data['threshold'] <= panel_limits[1] else '')
        ax.set_title(panel['label']+extra, fontsize=12, loc='left');ax.grid(alpha=.25)
        ax.tick_params(axis='both', labelsize=12)
        ax.xaxis.get_offset_text().set_fontsize(12)
        ax.yaxis.get_offset_text().set_fontsize(12)
        for spike in data['lt_spike_times']:
            if left <= spike <= right:ax.axvline(spike, color='#8c2c91', linestyle=':', alpha=.65)
        if i == 3:
            level = ax.axhline(data['threshold'], color='#477a32', linestyle='--', linewidth=1.)
            handles.append(level);labels.append('Actual LT threshold '+format(data['threshold'], '.8g'))
    overlay=axes[0].twinx()
    line, = overlay.step(times, data['stimulus'], where='post', color='#d46200', alpha=.7, linewidth=1.1)
    overlay.set_ylabel('Actual input\ngenerator units', fontsize=12, color='#a34d00')
    overlay.tick_params(axis='both', labelsize=12)
    overlay.xaxis.get_offset_text().set_fontsize(12)
    overlay.yaxis.get_offset_text().set_fontsize(12)
    handles.append(line);labels.append('Actual native input; dotted lines: actual LT events')
    axes[-1].set_xlabel('Native absolute time [s]', fontsize=12)
    figure_title(fig, ('Closed native single-pulse characterization' if data.get('diagnostic_purpose') else 'Closed native burst characterization')+'\n'+
                 observation_caption(data)+'\n'+
                 data['trial_id']+'\n'+data['soma_path']+' | '+name+
                 (' | local Y per panel' if local else ' | shared Y per panel')+
                 ' | base '+data['model_revision'][:12]+' | observed '+data['observed_model_revision'][:12], font_sizes=(12,))
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(.5,.885), ncol=2, fontsize=12, frameon=False)
    fig.canvas.draw()
    from matplotlib.text import Text
    text_sizes=[artist.get_fontsize() for artist in fig.findobj(Text) if artist.get_visible() and artist.get_text()]
    require(text_sizes and min(text_sizes)>=12, 'channel_plot_font_below_readable_minimum')
    paths=[]
    for extension in ('png', 'svg', 'pdf'):
        path=output/(name+'.'+extension);fig.savefig(path);paths.append(path.name)
    plt.close(fig)
    return {'view': name, 'begin': left, 'end': right, 'files': paths,
            'png_width': 1920, 'png_height': 1920, 'downsampling': False,
            'minimum_visible_text_fontsize_pt': min(text_sizes),
            'minimum_native_tick_pixels': None if name == 'overview' else 1420.8/(data['frequency_hz']*(right-left)),
            'y_scale': 'local_per_panel' if local else 'shared_per_panel', 'panel_y_limits': limits,
            'shared_panel_y_limits': [p['shared_limits'] for p in panels], 'sample_markers':local,
            'threshold_outside_local_Y': local and not limits[3][0] <= data['threshold'] <= limits[3][1]}


def render(directory, output, source_evidence, repository):
    directory, output = Path(directory).resolve(strict=True), Path(output).resolve()
    require(type(source_evidence) is dict and set(source_evidence) == {'commit', 'archive_path', 'native_member_prefix'} and
            type(source_evidence['commit']) is str and re.fullmatch('[0-9a-f]{40}', source_evidence['commit']) and
            all(type(source_evidence[k]) is str and source_evidence[k] and
                not Path(source_evidence[k]).is_absolute() and '\\' not in source_evidence[k] and
                ':' not in source_evidence[k] and '..' not in Path(source_evidence[k]).parts
                for k in ('archive_path', 'native_member_prefix')), 'channel_plot_requires_immutable_source_reference')
    require(not output.exists() and not output.is_relative_to(directory) and
            not directory.is_relative_to(output), 'channel_plot_output_exists_or_overlaps_primary')
    archive=_git_archive(repository,source_evidence)
    member_prefix=source_evidence['native_member_prefix'].rstrip('/')+'/'
    expected={member_prefix+p.relative_to(directory).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
              for p in directory.rglob('*') if p.is_file()}
    require(expected and not any(p.is_symlink() for p in directory.rglob('*')),
            'channel_plot_primary_symlink_or_empty')
    seen=set()
    for name,raw in _stream(archive):
        if name.startswith(member_prefix):
            require(name in expected and hashlib.sha256(raw).hexdigest()==expected[name],
                    'channel_plot_git_primary_mismatch')
            seen.add(name)
    require(seen==set(expected),'channel_plot_git_primary_missing')
    job = load(directory/'job.json');n = 1 if job['model']['branch'] else len(job['model']['inputs'])
    charts = [chart(directory, i) for i in range(n)]
    runtime = plotting_runtime();output.mkdir(parents=True)
    reports=[]
    for i, data in enumerate(charts):
        folder=output/('soma-'+str(i+1).zfill(3));folder.mkdir()
        views=[render_figure(data, name, left, right, folder)
               for name,left,right in time_views(data['begin'],data['end'],data['frequency_hz'])]
        for index in data['diagnostic_peak_indices']:
            first,last=max(0,index-10),min(len(data['times'])-1,index+10)
            views.append(render_figure(data,'measured-peak-'+str(index).zfill(5)+'-detail',
                                       data['times'][first],data['times'][last],folder,local=True))
        reports.append({'soma_path':data['soma_path'], 'folder':folder.name, 'views':views,
                        'base_model_revision':data['model_revision'],'observed_model_revision':data['observed_model_revision'],
                        'raw_initial_channel_values':data['raw_initial_channel_values'],
                        'lt_spike_times':data['lt_spike_times'], 'threshold':data['threshold'],
                        'observation_context':data['observation_context'],
                        'primary_sha256':data['primary']})
    manifest={'kind':'native_channel_joint_temporal_report','schema_version':2,
              'source_evidence':source_evidence,'runtime':runtime,'reports':reports,
              'source_archive_sha256':hashlib.sha256(archive).hexdigest(),'native_files_verified_in_Git':len(expected),
              'sample_phase':'native_after_children','channel_delta_reference':'first actual recorded sample',
              'visual_acceptance_complete':False,
              'causal_intervention_performed':job['schema_version']==5 and not job['profile_intervention']['baseline_reconstruction'],
              **({'storage_profile_intervention':job['profile_intervention'],'causal_claim_requires_paired_control':True} if job['schema_version']==5 else {}),
              'scientific_verdict':None}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    sections=[]
    for report in reports:
        sections.append('<h2>'+html.escape(report['soma_path'])+'</h2>')
        for view in report['views']:
            file=report['folder']+'/'+view['files'][0]
            sections.append('<p>'+html.escape(view['view']+' | '+view['y_scale'])+'</p><a href="'+file+'"><img style="width:100%;max-width:1920px" src="'+file+'"></a>')
    (output/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Native channel diagnostics</title>'+
        '<h1>Actual soma, channels, feedback and LT events</h1><p>Native units; SI unverified. Channel deltas subtract '
        'the first recorded value, not an assumed zero rest. Overview/zoom Y scales are shared per panel; '
        'measured-peak details have explicitly labelled local Y scales. Packet observation validity applies to '
        'its declared input windows; an additional plotted soma has no separate peak verdict from that flag. '
        'Waveform completeness and plotted-channel window membership are shown separately. '
        'No training or causal verdict.</p>'+
        ''.join(sections),encoding='utf-8')
    sums={p.relative_to(output).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
          for p in output.rglob('*') if p.is_file()}
    (output/'SHA256SUMS.json').write_text(json.dumps(sums,indent=2)+'\n',encoding='utf-8')
    return {'soma_count':n,'views':sum(len(r['views']) for r in reports),'files':len(sums),'scientific_verdict':None}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('native',type=Path);parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--source-reference',required=True,type=Path)
    parser.add_argument('--repository',required=True,type=Path)
    args=parser.parse_args()
    print(json.dumps(render(args.native,args.output,load(args.source_reference),args.repository),indent=2))


if __name__ == '__main__':
    main()
