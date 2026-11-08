"""Readable server-side figures for the native shared-vertex rejection control."""
import argparse
import hashlib
import json
from pathlib import Path

from .assigned_vertex_evidence import read_shared_vertex
from .native_evidence import require
from .plotting import padded_limits, plotting_runtime


def render_control(primary, output):
    primary = Path(primary).resolve(strict=True);output = Path(output).absolute()
    require(not output.exists() and not output.is_relative_to(primary.parent) and
            not primary.parent.is_relative_to(output), 'shared_vertex_plot_output_overlaps_primary')
    audit, packet, execution, rows = read_shared_vertex(primary)
    runtime = plotting_runtime()
    import matplotlib.pyplot as plt
    values = [[float(v) for v in row] for row in rows[1:]]
    times = [r[0] for r in values];stimulus = [r[1] for r in values]
    events = [e['time'] for e in audit['actual_stimuli']]
    dt = packet['observation']['maximum_sample_gap']
    input_left = max(times[0], events[0]-5*dt)
    input_right = min(times[-1], events[-1]+max(5*dt, execution['stimulus_profile']['pulse_length_s']*2))
    input_indices = [i for i, t in enumerate(times) if input_left <= t <= input_right]
    response_end = min(times[-1], max(events[-1], audit['plateau_end'])+.15)
    output.mkdir(parents=True, exist_ok=False)
    figures = []
    style = {'font.size':12, 'axes.titlesize':12, 'axes.labelsize':12,
             'xtick.labelsize':12, 'ytick.labelsize':12, 'legend.fontsize':12}
    with plt.rc_context(style):
        for channel in range(audit['channel_count']):
            soma = [r[channel+2] for r in values]
            for view in ('full', 'response'):
                indices = list(range(len(times))) if view == 'full' else [i for i, t in enumerate(times) if t <= response_end]
                require(len(indices) >= 3 and len(input_indices) >= 3, 'shared_vertex_plot_empty_interval')
                fig, axes = plt.subplots(2, 1, figsize=(14, 8), dpi=160,
                                         gridspec_kw={'height_ratios':[3,1]})
                try:
                    top, detail = axes
                    top.plot([times[i] for i in indices], [soma[i] for i in indices],
                             color='#1f5aaa', linewidth=1.6, label='Recorded soma '+str(channel))
                    top.set_xlim(times[indices[0]], times[indices[-1]])
                    top.set_ylim(*padded_limits([soma[i] for i in indices]))
                    top.set_ylabel('Raw potential [native units; SI unverified]')
                    top.set_xlabel('Native absolute time [s]')
                    top.grid(alpha=.25)
                    overlay = top.twinx()
                    overlay.step([times[i] for i in indices], [stimulus[i] for i in indices], where='post',
                                 color='#e17b28', linewidth=1, alpha=.7, label='Actual input')
                    overlay.set_ylim(-.05*max(stimulus), 1.2*max(stimulus))
                    overlay.set_ylabel('Actual input [generator units]', color='#a85813')
                    if channel == audit['shared_channel']:
                        top.axvline(audit['shared_peak_time'], color='#b6282c', linestyle='--',
                                    label='One vertex shared by both windows')
                        for w in packet['observation']['windows']:
                            top.axvspan(w['begin'], w['end'], color='#b6282c', alpha=.035)
                    handles, labels = top.get_legend_handles_labels()
                    h, l = overlay.get_legend_handles_labels()
                    top.legend(handles+h, labels+l, loc='upper right')
                    # The narrow source pulses remain individually visible even in a long response.
                    detail.step([(times[i]-events[0])*1000 for i in input_indices],
                                [stimulus[i] for i in input_indices], where='post', color='#e17b28')
                    for event in audit['actual_stimuli']:
                        x = (event['time']-events[0])*1000
                        detail.axvline(x, color='#a85813', linestyle=':', alpha=.7)
                        detail.annotate(event['id'], (x, max(stimulus)*.8), xytext=(4,2), textcoords='offset points')
                    detail.set_xlabel('Actual source detail: time from first recorded pulse [ms]')
                    detail.set_ylabel('Input');detail.grid(alpha=.25)
                    fig.suptitle('Classic native merged-burst control | soma '+str(channel)+' | '+view+' window\n'
                                 'Certificate rejected: shared measured vertex | spike response unknown', fontsize=12)
                    fig.tight_layout(rect=(0,0,1,.91))
                    name='soma'+str(channel)+'-'+view+'.png';path=output/name
                    fig.savefig(path)
                    figures.append({'path':name, 'bytes':path.stat().st_size,
                                    'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                                    'channel':channel,'view':view,'width':2240,'height':1280,
                                    'font_size_points':12,'samples':len(indices),
                                    'first_time':times[indices[0]],'last_time':times[indices[-1]]})
                finally:plt.close(fig)
    result={'kind':'native_shared_vertex_temporal_report','schema_version':1,'audit':audit,
            'plotting_runtime':runtime,'figures':figures,'all_recorded_channels_rendered':True,
            'input_detail_in_each_figure':True,'scientific_verdict':None,'whole_plan_complete':False}
    (output/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    links='\n'.join('<h2>'+f['path']+'</h2><img style="max-width:100%;height:auto" src="'+f['path']+'">' for f in figures)
    (output/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Shared vertex control</title>'
        '<h1>Native shared-vertex control</h1><p>Diagnostic rejection; classification not evaluated; spike response unknown.</p>'+links)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('primary',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();result=render_control(args.primary,args.output)
    print(json.dumps({'figures':len(result['figures']),'scientific_verdict':None}))


if __name__ == '__main__':main()
