"""Bounded Rs diagnostics on one immutable stopped model, without retraining.

The caller is the existing owned Python controller. Native processes and their
leases use the production runner; a probe failure stops the declared study.
"""
import os
from pathlib import Path

from .contained_process import inspect
from .matched_resistance_analysis import _trace, compare_probe_inputs
from .native_calibration_worker import _write
from .native_characterization import prepare_burst_readback_job
from .native_evidence import load, number, require
from .native_pipeline_worker import audit_run_manifest, run_job
from .native_process_policy import policy_for_reservation
from .process_runner import verify_runtime
from .resource_reservations import Reservations
from .runtime import file_record
from .stopped_evidence import load_case


def run(source_path, controls):
    """Run a finite, predeclared list; native live domain checks remain required."""
    source_path = Path(source_path).resolve(strict=True)
    controls = Path(controls).resolve(strict=True)
    declaration = load(controls/'declaration.json')
    require(set(declaration) == {'kind', 'schema_version', 'source_revision',
        'source_geometry', 'input_index', 'resistances', 'runtime', 'controller',
        'output', 'maximum_wall_seconds'}, 'burst_study_declaration_fields')
    require(declaration['kind'] == 'native_burst_resistance_study' and
        type(declaration['schema_version']) is int and declaration['schema_version'] == 1,
        'burst_study_declaration_version')
    index = declaration['input_index'];values = declaration['resistances']
    require(type(index) is int and index >= 0 and type(values) is list and
        2 <= len(values) <= 8 and all(number(v) > 0 for v in values) and
        len(set(values)) == len(values), 'burst_study_finite_resistance_grid')
    wall = declaration['maximum_wall_seconds']
    require(type(wall) is int and 1 <= wall <= 1800, 'burst_study_probe_wall_budget')
    runtime_path = controls/'runtime.json';runtime = load(runtime_path)
    require(runtime == declaration['runtime'], 'burst_study_runtime_changed')
    verify_runtime(runtime)
    output = Path(declaration['output']).resolve()
    require(output.is_relative_to(Path(os.environ['TMPDIR']).resolve(strict=True)) and
        not output.exists(), 'burst_study_owned_new_output')
    controller = Path(declaration['controller']).resolve(strict=True)
    live = inspect(controller)
    require(live['execution'] == 'running' and
        live['binding']['initial_main_pid'] == os.getpid(), 'burst_study_owned_controller')
    case = load_case(source_path);package = case[0]
    require(package['schema_version'] == 7 and package['certificate'] is None and
        package['model_revision'] == declaration['source_revision'] and
        package['configuration']['model']['normalization'] == 'N1',
        'burst_study_actual_stopped_n1_source')
    parameters = package['trained_inputs']
    require(index < len(parameters) and
        [p['length'] for p in parameters] == declaration['source_geometry'] and
        number(parameters[index]['resistance']) == values[0],
        'burst_study_geometry_or_control_changed')
    branch = package['configuration']['model']['branch']
    owners = [i for i, p in enumerate(parameters) if
        (not branch and i == index) or (branch and p['length'] == parameters[index]['length'])]
    require(all(number(parameters[i]['resistance']) == values[0] for i in owners),
        'burst_study_shared_bank_source_mismatch')
    source_files = [source_path, source_path.with_name(
        source_path.name.removesuffix('_stopped_state.json')+'_stopped_summary.json')]
    before = [file_record(p) for p in source_files]
    output.mkdir(parents=True)
    memory = live['memory_max'];leaf_memory = 3*1024**3
    registry = Reservations(output/'leases.sqlite3', managed_units=True,
        capacity=dict(slots=1, memory_bytes=memory+2*leaf_memory,
                      disk_bytes=8*1024**3, tasks=512))
    lease = registry.reserve('fixed-geometry-native-burst-resistance-study',
        [dict(path=str(output/'runs'), access='write')], ttl_seconds=14400,
        demands=dict(slots=1, memory_bytes=memory+leaf_memory,
                     disk_bytes=6*1024**3, tasks=256), controller_directory=str(controller))
    policy = policy_for_reservation(registry, lease['token'], memory_bytes=leaf_memory, tasks=64)
    rows = [];folders = {}
    try:
        variants = [('replay', None), ('matched', values[0])]+[
            ('resistance-'+str(i), v) for i, v in enumerate(values[1:], 1)]
        for name, resistance in variants:
            changes = [] if resistance is None else [dict(input_index=i, resistance=resistance)
                                                      for i in owners]
            job = prepare_burst_readback_job(case, index, 'fixed-geometry/'+name,
                resistance_intervention=changes, maximum_wall_seconds=wall,
                channel_diagnostics=True)
            job_path = output/(name+'-job.json');_write(job_path, job)
            folder = output/'runs'/name;folder.parent.mkdir(exist_ok=True)
            registry.heartbeat(lease['token'], ttl_seconds=14400)
            result = run_job('probe', job_path, source_path, runtime_path, folder,
                             wall+120., process_policy=policy)
            require((result['execution'], result['validity']) == ('completed', 'valid'),
                    'burst_study_probe_failed:'+name)
            require(inspect(folder/'process/contained')['all_processes_closed'] and
                audit_run_manifest(folder/'run-manifest.json')['run_evidence_consistent'],
                'burst_study_native_evidence_invalid:'+name)
            native = folder/'native';folders[name] = native
            packet, spec, samples = _trace(native)
            effective = load(native/'initial-state.json')
            require([p['length'] for p in effective['parameters']] == declaration['source_geometry'],
                    'burst_study_geometry_changed:'+name)
            requested = values[0] if resistance is None else resistance
            require(all(number(effective['parameters'][i]['resistance']) == requested for i in owners),
                    'burst_study_resistance_not_applied:'+name)
            rows.append(dict(name=name, resistance=requested,
                model_revision=effective['identity']['sha256'],
                observation_complete=packet['observation']['complete'],
                sample_count=len(samples), global_diagnostic_maxima=[
                    dict(channel=c, potential=max(s['soma'][c] for s in samples))
                    for c in range(len(spec['baseline']))],
                global_maxima_are_not_assigned_impulse_measurements=True))
            _write(output/(name+'-readback.json'), rows[-1])
        control, control_spec, a = _trace(folders['matched'])
        require((folders['replay']/'probe_trial_1.csv').read_bytes() ==
                (folders['matched']/'baseline_trial_1.csv').read_bytes(),
                'burst_study_replay_baseline_differs')
        require(rows[0]['model_revision'] == rows[1]['model_revision'] == package['model_revision'],
                'burst_study_source_model_changed')
        comparisons = []
        for row in rows[2:]:
            name = row['name'];changed, changed_spec, b = _trace(folders[name])
            conditions = compare_probe_inputs(control, control_spec, a, changed, changed_spec, b)
            require(all(conditions.values()) and
                (folders['matched']/'baseline_trial_1.csv').read_bytes() ==
                (folders[name]/'baseline_trial_1.csv').read_bytes(),
                'burst_study_clock_or_input_confound:'+name)
            require(row['model_revision'] != package['model_revision'],
                    'burst_study_changed_resistance_has_same_model:'+name)
            comparisons.append(dict(name=name, conditions=conditions,
                maximum_absolute_potential_difference=[
                    max(abs(y['soma'][c]-x['soma'][c]) for x, y in zip(a, b))
                    for c in range(len(control_spec['baseline']))]))
        require(before == [file_record(p) for p in source_files], 'burst_study_source_files_changed')
        result = dict(kind='native_burst_resistance_study_result', schema_version=1,
            source_revision=package['model_revision'], source_geometry=declaration['source_geometry'],
            input_index=index, physical_bank_owners=owners, rows=rows, comparisons=comparisons,
            source_files=before, runtime_fingerprint=runtime['runtime_fingerprint'],
            declared_grid_completed=True, training_executed=False, assigned_peak_measured=False,
            single_training_pattern_only=True, classification_verdict=None)
        _write(output/'result.json', result)
        return result
    finally:
        registry.release(lease['token'], note='Managed study groups closed; no training or classification verdict.')
        _write(output/'leases-final.json', registry.inspect())


def render(directory, output):
    """Plot all recorded soma channels, full views and <=901-sample details."""
    from .plotting import padded_limits, plotting_runtime
    directory = Path(directory).resolve(strict=True);output = Path(output).resolve()
    require(not output.exists() and not output.is_relative_to(directory) and
        not directory.is_relative_to(output), 'burst_study_separate_plot_cache')
    result = load(directory/'result.json')
    require(result['kind'] == 'native_burst_resistance_study_result' and
        result['declared_grid_completed'] and result['classification_verdict'] is None,
        'burst_study_report_requires_completed_diagnostic')
    environment = plotting_runtime()
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows = [r for r in result['rows'] if r['name'] != 'replay'];traces = {}
    for row in rows:
        folder = directory/'runs'/row['name']
        require(audit_run_manifest(folder/'run-manifest.json')['run_evidence_consistent'],
                'burst_study_plot_requires_audited_run')
        traces[row['name']] = _trace(folder/'native')
    packet, spec, samples = traces['matched'];n = len(samples)
    for row in rows[1:]:
        other, other_spec, b = traces[row['name']]
        require(all(compare_probe_inputs(packet, spec, samples, other, other_spec, b).values()),
                'burst_study_plot_clock_or_input_confound')
    output.mkdir(parents=True);views = []
    intervals = [('full', 0, n)]+[('frames-'+str(first)+'-'+str(min(first+900, n-1)),
        first, min(first+901, n)) for first in range(0, n-1, 800)]
    for channel in range(len(spec['baseline'])):
        folder = output/('soma-'+str(channel+1));folder.mkdir()
        limits = padded_limits([s['soma'][channel] for _, _, trace in traces.values() for s in trace])
        for label, first, last in intervals:
            x = [s['time']-spec['begin'] for s in samples[first:last]]
            with plt.rc_context({'font.size': 12}):
                fig, axes = plt.subplots(2, 1, figsize=(16, 7), dpi=200, sharex=True,
                                         gridspec_kw={'height_ratios': [5, 1]})
                for row in rows:
                    trace = traces[row['name']][2]
                    axes[0].plot(x, [s['soma'][channel] for s in trace[first:last]],
                        linewidth=1.3, marker='.' if label != 'full' else None, markersize=2,
                        label='Rs='+format(row['resistance'], '.9g')+' ohm | '+row['name'])
                axes[0].set_ylim(limits);axes[0].set_ylabel('Soma SumPotential\n[model units; SI unverified]')
                axes[0].legend(loc='best')
                axes[1].step(x, [s['stimulus'] for s in samples[first:last]], where='post', color='#a34d00')
                for event in packet['observation']['stimuli']:
                    t = event['time']-spec['begin']
                    if x[0] <= t <= x[-1]:axes[0].axvline(t, color='#a34d00', alpha=.3, linewidth=.8)
                axes[1].set_ylabel('Actual input');axes[1].set_xlabel('Time from recorded trial begin [s]')
                for axis in axes:axis.grid(alpha=.25);axis.set_xlim(x[0], x[-1])
                fig.suptitle('Fixed geometry '+str(result['source_geometry'])+' | soma '+str(channel+1)+' | '+label+
                    '\nOne full training pattern; matched clocks; no assigned-peak or classification verdict')
                fig.tight_layout(rect=(0, 0, 1, .92));path=folder/(label+'.png');fig.savefig(path);plt.close(fig)
            views.append(dict(path=path.relative_to(output).as_posix(), file=file_record(path),
                channel=channel, first_frame=first, last_frame_inclusive=last-1,
                samples=last-first, raw_samples_not_resampled=True, y_limits=list(limits)))
    manifest = dict(kind='native_burst_resistance_study_plots', schema_version=1,
        result=file_record(directory/'result.json'), plotting_environment=environment,
        views=views, all_soma_channels_plotted=True, single_training_pattern_only=True,
        classification_verdict=None)
    _write(output/'manifest.json', manifest)
    return manifest
