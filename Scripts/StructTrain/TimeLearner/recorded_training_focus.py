"""Display an explicit native-frame slice; never change peak selection."""
import argparse
import hashlib
from pathlib import Path

from .composite_package_evidence import audit_composite_package
from .composite_primary import filesystem_primary_resolver
from .native_calibration_worker import _write
from .native_evidence import load, require
from .plotting import figure_title, padded_limits, plotting_runtime
from .stimulus_subset_evidence import parse_console_subset_observation


def render(native, output, groups, *, channel, first_frame, last_frame):
    environment = plotting_runtime()
    native = Path(native).resolve(strict=True);output = Path(output).resolve()
    require(not output.exists() and not output.is_relative_to(native) and
            not native.is_relative_to(output), 'training_focus_output_overlap')
    require(type(groups) is list and 1 <= len(groups) <= 16 and
            all(type(g) is int and g > 0 for g in groups) and len(set(groups)) == len(groups),
            'training_focus_groups')
    require(type(channel) is int and channel >= 0 and type(first_frame) is int and
            type(last_frame) is int and 0 <= first_frame < last_frame,
            'training_focus_frames_or_channel')
    state_path = native/'train_stopped_state.json'
    summary_path = native/'train_stopped_summary.json'
    before = [p.read_bytes() for p in (state_path, summary_path)]
    state, summary = load(state_path), load(summary_path)
    resolver = filesystem_primary_resolver(native)
    audit_composite_package(state, summary, external_resolver=resolver)
    records = state['measurement_archive']['records']
    require(max(groups) <= len(records), 'training_focus_group_missing')
    prepared = []
    for ordinal in groups:
        record = records[ordinal-1]
        require(record['complete_group'], 'training_focus_requires_complete_group')
        trials = [t for t in record['raw_trials'] if
                  Path(t['primary_ref']['relative_path']).name == 'full-before.csv']
        require(len(trials) == 1, 'training_focus_full_before_missing')
        trial = trials[0];ref = trial['primary_ref'];raw = resolver(ref['relative_path'])
        require(len(raw) == ref['bytes'] and hashlib.sha256(raw).hexdigest() == ref['sha256'],
                'training_focus_primary_changed')
        packets = [p for p in record['native_packets'] if p.get('observation') and
                   p['observation']['specification']['trial_id'] == trial['native_trial_id']]
        require(len(packets) == 1, 'training_focus_packet_binding')
        observation, spec, samples, _ = parse_console_subset_observation(packets[0],
            raw, state['configuration']['model']['initial_isi'],
            expected_trial_id=trial['native_trial_id'])
        require(channel < len(spec['baseline']) and last_frame < len(samples),
                'training_focus_slice_out_of_bounds')
        prepared.append(dict(ordinal=ordinal, record=record, ref=ref, spec=spec,
                             observation=observation, samples=samples,
                             selected=samples[first_frame:last_frame+1]))
    require(before == [p.read_bytes() for p in (state_path, summary_path)],
            'training_focus_source_changed')
    limits = padded_limits([s['soma'][channel] for item in prepared for s in item['selected']])
    stimulus_limits = padded_limits([s['stimulus'] for item in prepared for s in item['samples']])
    import matplotlib.pyplot as plt
    output.mkdir();rows = []
    with plt.rc_context({'font.size': 12, 'path.simplify': False, 'svg.fonttype': 'none'}):
        fig, axes = plt.subplots(len(prepared), 1, figsize=(14, 4*len(prepared)),
                                 dpi=200, sharey=True, squeeze=False)
        for axis, item in zip(axes[:, 0], prepared):
            spec = item['spec'];samples = item['selected']
            times = [s['time']-spec['begin'] for s in samples]
            axis.plot(times, [s['soma'][channel] for s in samples], '-o',
                      color='#1755a4', markersize=4, linewidth=1.2)
            axis.set_xlim(times[0], times[-1]);axis.set_ylim(*limits)
            axis.ticklabel_format(axis='y', style='plain', useOffset=False)
            axis.set_ylabel('Raw soma potential\nlocal Y scale; SI unverified')
            axis.set_xlabel('Time from recorded native trial begin [s]')
            axis.grid(alpha=.25)
            axis.set_title('Group '+str(item['ordinal'])+' | recorded selection='+
                           item['record']['selection']['geometry']['validity'], loc='left')
            right = axis.twinx()
            right.step(times, [s['stimulus'] for s in samples], where='post', color='#e47b19')
            right.set_ylim(*stimulus_limits);right.set_ylabel('Actual input', color='#b96310')
            rows.append(dict(group=item['ordinal'], model_revision=item['record']['logical_request']['base_model_revision'],
                primary_reference=item['ref'], first_frame=first_frame, last_frame=last_frame,
                samples=len(samples), x_bounds=[times[0], times[-1]],
                original_selection=item['record']['selection']['geometry']['validity']))
        figure_title(fig, 'Recorded full-before response: native frames '+str(first_frame)+'..'+str(last_frame)+
            '\nShared local Y scale; every native sample shown; no new assignment or training verdict')
        fig.subplots_adjust(top=.82, bottom=.08, left=.13, right=.88, hspace=.55)
        pixels = min(a.get_position().width*fig.get_figwidth()*200 for a in axes[:, 0])/(last_frame-first_frame)
        require(pixels >= 8., 'training_focus_native_samples_not_readable')
        files = []
        for extension in ('png', 'svg', 'pdf'):
            name = 'native-frame-focus.'+extension;fig.savefig(output/name);files.append(name)
        plt.close(fig)
    result = dict(kind='recorded_training_native_frame_focus', schema_version=1,
        source_package_sha256=hashlib.sha256(before[0]).hexdigest(),
        source_summary_sha256=hashlib.sha256(before[1]).hexdigest(), rows=rows, channel=channel,
        y_limits=list(limits), minimum_native_tick_pixels=pixels, files=files,
        plotting_environment=environment, downsampling=False, scientific_verdict=None,
        assignment_changed=False, display_only=True)
    _write(output/'manifest.json', result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('native', type=Path);parser.add_argument('output', type=Path)
    parser.add_argument('--groups', type=int, nargs='+', required=True)
    parser.add_argument('--channel', type=int, required=True)
    parser.add_argument('--first-frame', type=int, required=True)
    parser.add_argument('--last-frame', type=int, required=True)
    args = parser.parse_args(argv)
    render(args.native, args.output, args.groups, channel=args.channel,
           first_frame=args.first_frame, last_frame=args.last_frame)


if __name__ == '__main__':
    main()
