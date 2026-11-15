"""Render full/omission training probes after replaying the complete package.

Run on an owned analysis worker. Windows are proposals, not measured peaks.
This renderer preserves failed selections and never creates a certificate.
"""
import csv
import argparse
import hashlib
import io
import json
from pathlib import Path

from .composite_package_evidence import audit_composite_package
from .composite_primary import filesystem_primary_resolver
from .native_evidence import load, number, require
from .plotting import figure_title, padded_limits, plotting_runtime


def render(native, output, group_numbers, *, native_window_zooms=False, allow_incomplete_groups=False):
    native = Path(native).resolve(strict=True)
    output = Path(output).resolve()
    require(not output.exists() and not output.is_relative_to(native) and
            not native.is_relative_to(output), 'training_report_output_overlap_or_exists')
    require(type(group_numbers) is list and group_numbers and
            all(type(i) is int and i > 0 for i in group_numbers) and
            len(set(group_numbers)) == len(group_numbers), 'training_report_group_inventory')
    require(type(native_window_zooms) is bool, 'training_report_native_zoom_flag')
    require(type(allow_incomplete_groups) is bool, 'training_report_incomplete_flag')
    runtime = plotting_runtime()
    packages = [native/n for n in ('train_stopped_state.json', 'train_learned_state.json')
                if (native/n).is_file()]
    require(len(packages) == 1, 'training_report_package_missing_or_ambiguous')
    package_path = packages[0]
    summary_path = package_path.with_name(package_path.name.replace('_state.', '_summary.'))
    raw_package, raw_summary = package_path.read_bytes(), summary_path.read_bytes()
    package, summary = load(package_path), load(summary_path)
    resolver = filesystem_primary_resolver(native)
    audit = audit_composite_package(package, summary, external_resolver=resolver)
    records = package['measurement_archive']['records']
    require(max(group_numbers) <= len(records), 'training_report_group_missing')
    prepared = []
    for ordinal in group_numbers:
        record = records[ordinal-1]
        raw_trials = record['raw_trials']
        require(raw_trials and (record['complete_group'] or allow_incomplete_groups),
                'training_report_group_incomplete')
        packets = {p['observation']['specification']['trial_id']: p['observation']
                   for p in record['native_packets'] if p.get('observation') is not None}
        series = []
        for trial in raw_trials:
            ref = trial['primary_ref']; raw = resolver(ref['relative_path'])
            require(len(raw) == ref['bytes'] and hashlib.sha256(raw).hexdigest() == ref['sha256'],
                    'training_report_primary_changed_after_audit')
            rows = list(csv.reader(io.StringIO(raw.decode('utf-8'), newline=''), strict=True))
            values = [[number(float(v)) for v in row] for row in rows[1:]]
            spec = trial['actual_specification']
            observation = packets.get(trial['native_trial_id'])
            require(observation is not None and observation['specification'] == spec and
                    observation['sample_count'] == len(values), 'training_report_trial_packet_binding')
            require(len(values) > 2 and len(spec['baseline']) > 0 and
                    all(len(v) == len(spec['baseline'])+2 for v in values),
                    'training_report_channel_dimensions')
            series.append(dict(reference=ref, values=values, specification=spec,
                               actual_stimuli=trial['actual_stimuli'], complete=observation['complete'],
                               end_reason=observation['end_reason']))
        require(len({len(s['specification']['baseline']) for s in series}) == 1,
                'training_report_control_dimensions')
        prepared.append((ordinal, record, series))
    require(raw_package == package_path.read_bytes() and raw_summary == summary_path.read_bytes(),
            'training_report_package_changed_after_audit')
    import matplotlib.pyplot as plt
    output.mkdir(parents=True, exist_ok=False)
    figures, groups = [], []
    with plt.rc_context({'font.size': 12, 'path.simplify': False, 'svg.fonttype': 'none'}):
        for ordinal, record, series in prepared:
            count = len(series[0]['specification']['baseline'])
            frame = record['method_specification']['candidate_frame']
            frequency = number(series[0]['specification']['stimulus_profile']['frequency_hz'])
            window = [frame[k]/frequency for k in ('first_frame', 'last_frame')]
            duration = number(series[0]['specification']['end'])-number(series[0]['specification']['begin'])
            # Detail includes actual response context and the proposed window;
            # it does not assume the response occurs inside that window.
            event_times = [e['frame_index']/frequency for e in series[0]['actual_stimuli']]
            detail = [max(0., min([window[0], *event_times])-.04),
                      min(duration, max([window[1], *event_times])+.3)]
            groups.append(dict(ordinal=ordinal, group_id=record['group_id'],
                selection=record['selection'], rejection_reason=record['rejection_reason'],
                window_relative_seconds=window, model_revision=record['logical_request']['base_model_revision'],
                primary_references=[s['reference'] for s in series],
                complete_group=record['complete_group'],
                recorded_trials=[dict(reference=s['reference'], complete=s['complete'],
                    end_reason=s['end_reason'], sample_count=len(s['values']),
                    recorded_begin=s['values'][0][0], recorded_end=s['values'][-1][0]) for s in series]))
            for channel in range(count):
                limits = padded_limits([v[channel+2] for s in series for v in s['values']])
                views = [('overview', [0., duration]), ('detail', detail)]
                if native_window_zooms:
                    # Fifty native frames on each side of either boundary.
                    # This is an axis choice, never a new peak assignment.
                    views += [(label, [max(0., boundary-50/frequency),
                                       min(duration, boundary+50/frequency)])
                              for label,boundary in zip(('window-left-native', 'window-right-native'), window)]
                for view, bounds in views:
                    native_zoom = view.endswith('-native')
                    fig, axes = plt.subplots(len(series), 1, figsize=(18, 3*len(series)), sharex=True)
                    for ax, s in zip(list(axes), series):
                        begin = number(s['specification']['begin'])
                        times = [v[0]-begin for v in s['values']]
                        name = Path(s['reference']['relative_path']).stem
                        ax.plot(times, [v[channel+2] for v in s['values']], color='#1755a4', linewidth=1.4,
                                marker='.' if native_zoom else None, markersize=1.8)
                        ax.axvspan(*window, color='#aa3f9d', alpha=.13,
                                   label='proposed assignment window (not a peak)')
                        ax.set_xlim(*bounds); ax.set_ylim(*limits); ax.grid(alpha=.25)
                        ax.set_ylabel('Raw soma potential\nSI units unverified')
                        label = 'complete' if s['complete'] else 'CENSORED: '+s['end_reason']
                        ax.set_title(name+' | '+label+' | same Y scale across all controls', loc='left')
                        if not s['complete']:
                            ax.axvspan(times[-1], number(s['specification']['end'])-begin,
                                       color='#888888', alpha=.18)
                        right = ax.twinx()
                        stimulus = [v[1] for v in s['values']]
                        right.plot(times, stimulus, color='#e47b19', linewidth=.8)
                        right.set_ylim(*padded_limits(stimulus))
                        right.set_ylabel('Actual input\nraw generator units', color='#b96310')
                        # The recorded aggregate signal is shown independently
                        # for every omission control, never a synthetic schedule.
                    axes[-1].set_xlabel('Time since each native probe began [s]')
                    status = (record['selection']['geometry']['validity'] if record['selection']
                              else ('COMPLETE RAW GROUP; assignment unavailable' if record['complete_group']
                                    else 'INCOMPLETE GROUP; assignment unavailable'))
                    figure_title(fig, f'Training group {ordinal} | soma{channel} | {view}\n'
                        f'{record["logical_request"]["input_id"]}: selection={status}; '
                        f'outcome={audit["training_outcome"]}\n'
                        'Full and omission responses; no classification or new peak assignment')
                    fig.subplots_adjust(top=.84, bottom=.05, left=.10, right=.88, hspace=.45)
                    tick_pixels = None
                    if native_zoom:
                        # Measure the actual axes at the exported PNG DPI.
                        tick_pixels = min(ax.get_position().width*fig.get_figwidth()*160
                            for ax in axes)/(bounds[1]-bounds[0])/frequency
                        require(tick_pixels >= 8., 'training_report_native_ticks_not_readable')
                    filenames = []
                    for extension in ('png', 'svg', 'pdf'):
                        filename = f'group-{ordinal:06d}-soma-{channel:03d}-{view}.{extension}'
                        fig.savefig(output/filename, dpi=160); filenames.append(filename)
                    plt.close(fig)
                    figure = dict(group=ordinal, channel=channel, view=view,
                        x_bounds_seconds=bounds, y_bounds=limits, files=filenames)
                    if native_zoom:
                        figure['minimum_native_tick_pixels'] = tick_pixels
                    figures.append(figure)
    manifest = dict(kind='timelearner_composite_training_temporal_report', schema_version=1,
        package_sha256=hashlib.sha256(raw_package).hexdigest(),
        summary_sha256=hashlib.sha256(raw_summary).hexdigest(), package_audit=audit,
        groups=groups, figures=figures, runtime=runtime, downsampling=False,
        time_transform='recorded CSV time minus that native probe specification.begin',
        input_transform='unaltered recorded CSV aggregate stimulus for each control',
        training_certificate_eligible=False, scientific_verdict=None,
        visual_acceptance_complete=False)
    if native_window_zooms:
        manifest.update(schema_version=2, native_window_zoom_policy={
            'axis_selection': 'fifty_native_frames_each_side_of_declared_window_boundary',
            'minimum_tick_pixels': 8, 'sample_markers': True,
            'peak_assignment_changed': False})
    if allow_incomplete_groups:
        manifest.update(schema_version=3, incomplete_group_diagnostics=True,
                        missing_trials_not_synthesized=True)
    (output/'manifest.json').write_text(json.dumps(manifest, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('native', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--groups', nargs='+', type=int, required=True)
    parser.add_argument('--native-window-zooms', action='store_true',
        help='also show both proposed window edges with at least eight pixels per native tick')
    parser.add_argument('--allow-incomplete-groups', action='store_true',
        help='diagnostic only: label censored traces and retain missing trials without filling them')
    args = parser.parse_args(argv)
    result = render(args.native, args.output, args.groups, native_window_zooms=args.native_window_zooms,
                    allow_incomplete_groups=args.allow_incomplete_groups)
    print(json.dumps(dict(groups=len(result['groups']), figures=len(result['figures']),
                          scientific_verdict=None)))


if __name__ == '__main__':
    main()
