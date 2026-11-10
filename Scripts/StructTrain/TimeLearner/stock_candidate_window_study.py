"""Measured-reference stock N4 cold7 pilot, with original mathematical tolerances.

Cold characterization supplies window proposals and physical readback only.
New Train captures its own references; no learned model or certificate is seeded.
"""
from copy import deepcopy
from pathlib import Path

from .candidate_window_contract import POLICY_ID
from .candidate_window_package_evidence import audit_candidate_window_package
from .collector_provenance import frozen_digest
from .composite_configuration import METHOD
from .composite_primary import filesystem_primary_resolver
from .contained_process import inspect
from .native_calibration_worker import _signed, _write
from .native_characterization import audit_execution
from .native_evidence import equal, load, number, require
from .native_pipeline_worker import audit_run_manifest, run_job, validate_job
from .native_process_policy import policy_for_reservation
from .model_identity import canonical_model_sha256 as digest
from .process_runner import verify_runtime
from .resource_reservations import Reservations
from .stock_cold_characterization import jobs as characterization_jobs
from .stock_phasea_preflight import audit_stock_profile
from .stock_threshold_study import _condition


def _frame(time, frequency):
    value = number(time);frame = round(value*frequency)
    require(frame >= 0 and equal(value, frame/frequency), 'stock_cold7_reference_not_on_native_grid')
    return frame


def prepare(source, runtime_path, output):
    source = Path(source).resolve(strict=True);output = Path(output)
    require(not output.exists(), 'stock_cold7_preparation_exists')
    runtime = load(Path(runtime_path));verify_runtime(runtime)
    index = load(source/'index.json');expected = characterization_jobs()
    require(index['kind'] == 'timelearner_stock_cold_characterization_result' and
        index['schema_version'] == 1 and index['training_started'] is False and
        {r['name'] for r in index['rows']} == set(expected) and len(index['rows']) == 8,
        'stock_cold7_requires_complete_cold_characterization')
    declarations, origins, identities = {}, {}, {}
    for topology in ('Classic', 'Branch'):
        windows, policies, origin = [], [], []
        for i in range(4):
            name = topology+'-cold-stock-input'+str(i);folder = source/'runs'/name
            job = load(folder/'input/job.json')
            require(job == expected[name], 'stock_cold7_characterization_declaration_changed')
            manifest = audit_run_manifest(folder/'run-manifest.json')
            require(manifest['run_evidence_consistent'], 'stock_cold7_characterization_run_invalid')
            probe = audit_execution(folder/'native')
            require(probe['observation_valid'] and probe['observation_complete'],
                'stock_cold7_characterization_peak_invalid')
            recorded_runtime = load(folder/'process/runtime.json')
            require(recorded_runtime['source_closure'] == runtime['source_closure'] and
                recorded_runtime['executable']['sha256'] == runtime['executable']['sha256'],
                'stock_cold7_characterization_runtime_changed')
            identity = load(folder/'native/initial-state.json')['identity']
            audit_stock_profile(identity, branch=topology == 'Branch')
            require(identity == identities.setdefault(topology, identity),
                'stock_cold7_characterization_initial_graph_changed')
            packet_path = folder/'native/probe_trial_1.json';packet = load(packet_path)
            observation = packet['observation']
            require(len(observation['peaks']) == 1, 'stock_cold7_assigned_peak_count')
            peak = observation['peaks'][0]
            require(peak['input_id'] == 'input'+str(i) and peak['stimulus_id'] == 'pulse'+str(i)
                and peak['validity'] == 'valid', 'stock_cold7_assigned_peak_changed')
            events = [e for e in observation['stimuli'] if e['id'] == peak['stimulus_id']]
            require(len(events) == 1, 'stock_cold7_actual_onset_missing')
            onset = _frame(events[0]['time'], 2000);vertex = _frame(peak['time'], 2000)
            delay = vertex-onset
            require(delay > 0 and onset >= 2 and equal(peak['delay_from_stimulus'], delay/2000),
                'stock_cold7_reference_latency_invalid')
            # Source samples define the initial interval, not a learned target.
            windows.append(dict(begin=(onset-2)/2000, end=(vertex+51)/2000))
            # Total L=1 latency is only an initial linear proposal hypothesis.
            # No derivative/monotonicity or measured-candidate claim follows.
            policies.append(dict(delay_frames_per_segment=delay,
                base_left_guard_frames=0, base_right_guard_frames=0,
                length_guard_frames=0, synapse_count_guard_frames=0,
                resistance_change_guard_frames=5, capacitance_change_guard_frames=0,
                hard_first_frame=1, hard_last_frame=3600, maximum_window_frames=160))
            origin.append(dict(input_index=i, actual_onset_frame=onset, assigned_peak_frame=vertex,
                captured_characterization_amplitude=peak['amplitude'],
                packet=frozen_digest(packet_path, 256*1024**2),
                trace=frozen_digest(packet_path.with_suffix('.csv'), 256*1024**2)))
        name = topology+'-stock-cold7-N1'
        config = dict(kind='timelearner_native_cold_configuration', schema_version=7, base_schema_version=1,
            model=deepcopy(expected[topology+'-cold-stock-input0']['model']),
            stimulus_profile=deepcopy(expected[topology+'-cold-stock-input0']['stimulus_profile']),
            run_id=name, protocol_revision='stock-measured-reference-cold7-pilot-v1', sample_id='phasea-target',
            duration=1.8, maximum_sample_gap=.0005, minimum_amplitude=1e-6,
            maximum_samples=3605, record_spikes=False, peak_selection='isolated_window', windows=windows,
            maximum_reference_probes=8, maximum_invalid_reference_probes=0,
            maximum_model_seconds=7200., maximum_wall_seconds=1800.,
            search=dict(maximum_probes=128, maximum_edits=1280, maximum_candidates_per_input=128,
                maximum_sweeps=4, maximum_invalid_observations=4, resistance_subdivision_depth=8,
                bounds=[dict(minimum_length=1, maximum_length=100 if i < 3 else 1,
                    minimum_synapses=1, maximum_synapses=1,
                    minimum_resistance=1e6 if i < 3 else 86e6, maximum_resistance=86e6) for i in range(4)],
                tolerances=dict(amplitude_absolute=1e-5, amplitude_relative=0., sync=.02)),
            composite_measurement=dict(schema_version=2, method_id=METHOD,
                context_policy=dict(schema_version=1, comparison_radius_ticks=1, maximum_samples=3605,
                    maximum_total_samples=21630, maximum_native_probes=6, time_comparison_tolerance=1e-10,
                    baseline_absolute=1e-12, repeatability_absolute=1e-10, repeatability_relative=0.,
                    influence_absolute=1e-6, influence_relative=0.),
                geometry_policy=dict(schema_version=1, maximum_inputs=4, maximum_samples=3605,
                    maximum_total_samples=21630, repeatability_absolute=1e-10),
                attempt_limits=dict(maximum_groups=512, maximum_native_probes=3072, maximum_total_samples=11074560),
                maximum_group_model_seconds=20., maximum_group_wall_seconds=300.,
                maximum_total_primary_bytes=512*1024**2,
                candidate_window_policy=dict(schema_version=1, policy_id=POLICY_ID,
                    seed_rule='immutable_reference_full_before', coordinate_mode='relative_native_frame_interval',
                    proposals_per_logical_request=1, maximum_feature_terms=4096, inputs=policies)))
        job = _signed(dict(kind='timelearner_native_training_job', schema_version=1,
            owner_class='NNeuronTimeLearner'+('Branch' if topology == 'Branch' else ''),
            implementation_id='stock-measured-reference-cold7-N4-N1-pilot-v1', configuration=config,
            profile_archives=[], optional_modes=dict(sync_capacitance_trim=0, post_train_tuning=False,
                auto_calibrate_threshold=False), calculate_mode=0, structure_build_mode=1,
            maximum_model_ticks=14400000))
        validate_job('preflight', job);validate_job('train', job)
        declarations[name] = job;origins[name] = origin
    output.mkdir(parents=True)
    for directory in ('jobs', 'conditions', 'initial'):(output/directory).mkdir()
    code = dict(pulse_core=runtime['source_closure']['Libraries/Nmsdk-PulseLib']['head'],
        rdk_core=runtime['source_closure']['Rdk']['head'], console_driver=runtime['source_closure']['root']['head'])
    for name, job in declarations.items():
        topology = name.split('-')[0]
        _write(output/'jobs'/(name+'.json'), job)
        _write(output/'initial'/(name+'.json'), identities[topology])
        _write(output/'conditions'/(name+'.json'), _condition(job, identities[topology], code, runtime,
            algorithm_id='stock-measured-reference-cold7-N4-N1-pilot-v1'))
    _write(output/'runtime.json', runtime)
    _write(output/'reference-origin.json', dict(characterization=origins,
        references_recaptured_by_new_train=True, learned_state_imported=False,
        delay_model_is_initial_total_latency_hypothesis=True, scientific_verdict=None))
    result = dict(kind='timelearner_stock_candidate_window_plan', schema_version=1,
        jobs={name:job['sha256'] for name,job in declarations.items()}, scientific_verdict=None)
    _write(output/'index.json', result)
    return result


def run(source, runtime_path, controller, case, output, *, preflight_only=False):
    source = Path(source).resolve(strict=True);output = Path(output).resolve()
    require(not output.exists(), 'stock_cold7_result_exists')
    require(not source.is_relative_to(output) and not output.is_relative_to(source),
        'stock_cold7_output_overlaps_preparation')
    index = load(source/'index.json')
    require(index['kind'] == 'timelearner_stock_candidate_window_plan' and index['schema_version'] == 1
        and case in index['jobs'], 'stock_cold7_unknown_plan_or_case')
    runtime = load(Path(runtime_path));verify_runtime(runtime)
    require(runtime == load(source/'runtime.json'), 'stock_cold7_runtime_changed')
    job_path = source/'jobs'/(case+'.json');job = load(job_path)
    validate_job('train', job)
    require(job['sha256'] == index['jobs'][case], 'stock_cold7_job_changed')
    expected_initial = load(source/'initial'/(case+'.json'))
    code = dict(pulse_core=runtime['source_closure']['Libraries/Nmsdk-PulseLib']['head'],
        rdk_core=runtime['source_closure']['Rdk']['head'], console_driver=runtime['source_closure']['root']['head'])
    condition = load(source/'conditions'/(case+'.json'))
    require(condition == _condition(job, expected_initial, code, runtime,
        algorithm_id='stock-measured-reference-cold7-N4-N1-pilot-v1'), 'stock_cold7_condition_changed')
    before = {p.relative_to(source).as_posix(): frozen_digest(p, 256*1024**2)
        for p in sorted(source.rglob('*.json'))}
    output.mkdir(parents=True)
    _write(output/'condition.json', condition)
    registry = Reservations(output/'leases.sqlite3', managed_units=True,
        capacity=dict(slots=1, memory_bytes=8*1024**3, disk_bytes=4*1024**3, tasks=512))
    lease = registry.reserve('stock-cold7-'+case, [dict(path=str(output/'runs'), access='write')],
        demands=dict(slots=1, memory_bytes=6*1024**3, disk_bytes=2*1024**3, tasks=256),
        controller_directory=str(controller), ttl_seconds=3600)
    policy = policy_for_reservation(registry, lease['token'], memory_bytes=4*1024**3, tasks=64)
    initial = run_job('preflight', job_path, None, runtime_path, output/'runs/preflight', 180., process_policy=policy)
    require(initial['execution'] == 'completed' and initial['validity'] == 'valid', 'stock_cold7_preflight_invalid')
    identity = load(output/'runs/preflight/native/initial-state.json')['identity']
    audit_stock_profile(identity, branch=job['configuration']['model']['branch'])
    require(identity == expected_initial, 'stock_cold7_initial_graph_changed')
    if preflight_only:
        require(inspect(output/'runs/preflight/process/contained')['all_processes_closed'],
            'stock_cold7_preflight_group_live')
        require(before == {p.relative_to(source).as_posix(): frozen_digest(p, 256*1024**2)
            for p in sorted(source.rglob('*.json'))}, 'stock_cold7_preparation_changed')
        registry.release(lease['token'], note='Declared stock cold7 preflight closed; Train not started.')
        record = dict(kind='timelearner_stock_candidate_window_preflight_result', schema_version=1,
            case=case, execution=initial['execution'], validity=initial['validity'],
            initial_model_revision=identity['sha256'], condition_fingerprint=digest(condition['condition']),
            training_started=False, scientific_verdict=None)
        _write(output/'index.json', record)
        return record
    result = run_job('train', job_path, None, runtime_path, output/'runs/train',
        job['configuration']['maximum_wall_seconds'], process_policy=policy)
    require(inspect(output/'runs/train/process/contained')['all_processes_closed'], 'stock_cold7_train_group_live')
    package_audit = None;package_path = None
    if result['validity'] == 'valid':
        audit_run_manifest(output/'runs/train/run-manifest.json')
        root = output/'runs/train/native'
        packages = [p for p in (root/'train_learned_state.json', root/'train_stopped_state.json') if p.is_file()]
        require(len(packages) == 1, 'stock_cold7_actual_terminal_package_required')
        package_path = packages[0]
        summary = load(package_path.with_name(package_path.name.replace('_state.json', '_summary.json')))
        package_audit = audit_candidate_window_package(load(package_path), summary=summary,
            external_resolver=filesystem_primary_resolver(root))
    registry.release(lease['token'], note='Cold Train native groups closed; execution and convergence remain distinct.')
    require(before == {p.relative_to(source).as_posix(): frozen_digest(p, 256*1024**2)
        for p in sorted(source.rglob('*.json'))}, 'stock_cold7_preparation_changed')
    record = dict(kind='timelearner_stock_candidate_window_training_result', schema_version=1,
        case=case, condition_fingerprint=digest(condition['condition']), execution=result['execution'],
        validity=result['validity'], package_audit=package_audit,
        package_path=None if package_path is None else package_path.relative_to(output).as_posix(),
        classification_assessed=False, scientific_verdict=None)
    _write(output/'index.json', record)
    return record
