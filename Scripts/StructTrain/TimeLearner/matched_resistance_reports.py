"""Readable soma/input overlays for actual matched-clock diagnostic controls."""
import hashlib
import html
from pathlib import Path

from .matched_resistance_analysis import analyze, _trace
from .native_calibration_worker import _write
from .native_evidence import load, require
from .plotting import padded_limits, plotting_runtime


def render(directory, output):
    directory, output = Path(directory).resolve(strict=True), Path(output).resolve()
    require(not output.exists() and not output.is_relative_to(directory) and not directory.is_relative_to(output),
            'matched_report_requires_separate_new_cache')
    analysis = analyze(directory)
    require(analysis['all_conditions_matched'], 'matched_report_conditions_not_matched')
    environment = plotting_runtime()
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows = load(directory/'index.json')['rows'];output.mkdir(parents=True);views = [];links = []
    _write(output/'analysis.json', analysis)
    for branch in (False, True):
        topology = 'Branch' if branch else 'Classic'
        sources = {r['variant']: directory/'runs'/r['name']/'native' for r in rows if r['branch'] is branch}
        data = {k: _trace(v) for k, v in sources.items()}
        control, spec, samples = data['matched-control'];changed = data['resistance'][2]
        relative = [s['time']-spec['begin'] for s in samples];n = len(samples)
        intervals = [('full', 0, n)]+[('samples-'+str(first)+'-'+str(min(first+900, n-1)), first, min(first+901, n))
                                      for first in range(0, n-1, 800)]
        for channel in range(len(spec['baseline'])):
            folder = output/topology/('soma-'+str(channel+1));folder.mkdir(parents=True)
            limits = padded_limits([s['soma'][channel] for _, _, trace in data.values() for s in trace])
            for label, first, last in intervals:
                x = relative[first:last];delta = [b['soma'][channel]-a['soma'][channel] for a, b in zip(samples[first:last], changed[first:last])]
                with plt.rc_context({'font.size': 11, 'svg.fonttype': 'none'}):
                    fig, axes = plt.subplots(3, 1, figsize=(14, 8), dpi=160, sharex=True,
                                             gridspec_kw={'height_ratios': [4, 2, 1]})
                    for variant, color, style, legend in [('baseline', '#777777', '--', 'Source replay (absolute begin 0 s)'),
                            ('matched-control', '#0063a6', '-', 'Matched control, Rs unchanged'),
                            ('resistance', '#c44b00', '-', 'Changed bank Rs')]:
                        _, series_spec, trace = data[variant]
                        times = [s['time']-series_spec['begin'] for s in trace[first:last]]
                        axes[0].plot(times, [s['soma'][channel] for s in trace[first:last]], color=color,
                                     linestyle=style, linewidth=1.3, label=legend,
                                     marker='.' if label != 'full' else None, markersize=2)
                    axes[0].set_ylim(limits);axes[0].set_ylabel('Soma SumPotential\n[model units; SI unverified]');axes[0].legend(loc='best')
                    axes[1].plot(x, delta, color='#603a8c', linewidth=1.2, marker='.' if label != 'full' else None, markersize=2)
                    axes[1].set_ylabel('Changed - control\n[model units]');axes[1].set_ylim(padded_limits(delta))
                    if all(v == 0 for v in delta):axes[1].text(.02, .85, 'All recorded differences = 0', transform=axes[1].transAxes)
                    axes[2].step(x, [s['stimulus'] for s in samples[first:last]], where='post', color='#a34d00', label='Actual matched input')
                    for event in control['observation']['stimuli']:
                        time = event['time']-spec['begin']
                        if x[0] <= time <= x[-1]:
                            axes[0].axvline(time, color='#a34d00', alpha=.3, linewidth=.8)
                    axes[2].set_ylabel('Input\n[native units]')
                    axes[2].set_xlabel('Time relative to recorded trial begin [s]; matched absolute begin '+str(spec['begin'])+' s')
                    for axis in axes:axis.grid(alpha=.25);axis.set_xlim(x[0], x[-1])
                    fig.suptitle(topology+' soma '+str(channel+1)+' | diagnostic stopped model, target pattern only | '+label+
                                 '\nNo training certificate or classification verdict; actual samples, no resampling')
                    fig.tight_layout(rect=(0, 0, 1, .94))
                    for extension in ('png', 'svg'):fig.savefig(folder/(label+'.'+extension))
                    record = {'topology': topology, 'channel': channel, 'view': label, 'first_frame': first,
                        'last_frame_inclusive': last-1, 'sample_count': last-first, 'time_begin_relative': x[0], 'time_end_relative': x[-1],
                        'matched_absolute_begin': spec['begin'], 'soma_y_limits': list(axes[0].get_ylim()),
                        'difference_y_limits': list(axes[1].get_ylim()), 'png': (folder/(label+'.png')).relative_to(output).as_posix(),
                        'raw_samples_not_resampled': True, 'local_view_has_sample_markers': label != 'full'}
                    views.append(record);plt.close(fig)
                links.append('<li>'+html.escape(topology+' soma '+str(channel+1)+' '+label)+'<br><img src="'+record['png']+'"></li>')
    manifest = {'kind': 'matched_resistance_diagnostic_report', 'schema_version': 1, 'plotting_environment': environment,
                'views': views, 'single_target_pattern_only': True, 'expected_full_pattern_matrix_test': False,
                'all_soma_channels_plotted': True, 'analysis': analysis, 'scientific_classification_verdict': None}
    _write(output/'manifest.json', manifest)
    (output/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Matched Rs diagnostics</title>'
        '<style>body{font:18px sans-serif;margin:2em}img{width:100%;max-width:2240px}</style>'
        '<h1>Stopped stock models: matched-clock Rs controls</h1><p>One target training pattern only. '
        'All soma channels and actual input samples are shown. Full views share per-soma Y limits; local views contain '
        'at most 901 actual samples and explicit sample markers. The difference axis has its own recorded numeric scale. '
        'Input times and samples of matched control and changed-Rs probes are identical. Source replay is context at another '
        'absolute clock, not the causal control. SI potential units and spiking response are unverified. '
        'This is not completed training or classification.</p><ul>'+''.join(links)+'</ul>', encoding='utf-8')
    sums = {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in output.rglob('*') if p.is_file()}
    _write(output/'SHA256SUMS.json', sums)
    return {'views': len(views), 'soma_channels': 5, 'full_pattern_matrix_test': False, 'scientific_classification_verdict': None}
