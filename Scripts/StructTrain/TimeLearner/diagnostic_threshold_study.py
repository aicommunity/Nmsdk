"""Same-matrix stopped-model threshold experiment; no training certificate.

The baseline is replayed on the candidate SDK before applying the threshold.
Nonspiking maxima only propose it; actual spikes supply the reported counts.
"""
import os
from pathlib import Path, PurePosixPath

from .collector_provenance import _frozen
from .contained_process import inspect
from .native_calibration_worker import _signed, _write
from .native_evidence import load, number, parse_json_bytes, require
from .native_pipeline_worker import audit_run_manifest, run_job
from .native_process_policy import policy_for_reservation
from .process_runner import verify_runtime
from .recognition_metrics import load_diagnostic_evaluation
from .resource_reservations import Reservations
from .runtime import file_record


def propose(source_manifest):
    source_manifest = Path(source_manifest).resolve(strict=True)
    before = file_record(source_manifest)
    audit = audit_run_manifest(source_manifest)
    manifest = load(source_manifest);root = source_manifest.parent
    require(manifest['operation'] == 'diagnostic-evaluate' and
        manifest['execution'] == 'completed' and manifest['validity'] == 'valid' and
        audit['run_evidence_consistent'], 'threshold_study_requires_audited_diagnostic')
    metrics = manifest['analysis']['metrics']
    require(metrics['diagnostic_only'] and not metrics['training_completed'] and
        metrics['effective_threshold'] == 100. and not metrics.get('diagnostic_threshold_experiment', False),
        'threshold_study_requires_original_nonspiking_baseline')
    records = {r['path']: r for r in manifest['artifacts']}

    def bound(relative, maximum):
        path = PurePosixPath(relative)
        require(not path.is_absolute() and '..' not in path.parts and relative in records,
                'threshold_study_source_path')
        raw, record = _frozen(root/relative, maximum)
        require(all(record[k] == records[relative][k] for k in ('bytes', 'sha256')),
                'threshold_study_primary_changed')
        return parse_json_bytes(raw)

    spec = bound('native/evaluation.json', 16*1024**2)
    require(len(spec['trials']) == 8, 'threshold_study_requires_full_phasea_eight')
    require(spec['criterion'] == dict(id='post_anchor_target_whole_window_foil_v1', anchor='onset',
        begin_offset=0., end_offset=None, reject_target_outside_window=True),
        'threshold_study_requires_whole_pattern_onset_criterion')
    rows = []
    for trial in spec['trials']:
        observation = bound('native/'+trial['observation'], 16*1024**2)
        require(observation['schema_version'] == 2 and observation['complete'] and
            observation['valid'] and observation['spike_count'] == 0 and
            observation['reset_policy'] == 'reset_per_trial' and
            all(observation[k] == trial[k] for k in ('trial_id', 'sample_id', 'label', 'pattern_hash')),
            'threshold_study_requires_complete_nonspiking_lt_recording')
        samples = observation['samples'];values = [number(s['lt_potential']) for s in samples]
        maximum = max(values);frame = values.index(maximum)
        rows.append(dict(trial_id=trial['trial_id'], sample_id=trial['sample_id'], label=trial['label'],
            pattern_hash=trial['pattern_hash'], lt_maximum=maximum, first_maximum_frame=frame,
            maximum_time=samples[frame]['time'], samples=len(samples),
            threshold_potential_source=observation['threshold_potential_source']))
    targets = [r['lt_maximum'] for r in rows if r['label'] == 'target']
    foils = [r['lt_maximum'] for r in rows if r['label'] == 'foil']
    require(len(targets) == 1 and len(foils) == 7, 'threshold_study_phasea_labels')
    upper = min(targets);below = [v for v in foils if v < upper]
    require(below, 'threshold_study_no_target_preserving_midgap')
    lower = max(below);threshold = lower+(upper-lower)/2
    require(lower < threshold < upper, 'threshold_study_midgap_unresolvable')
    require(before == file_record(source_manifest), 'threshold_study_manifest_changed')
    return dict(kind='stopped_model_same_matrix_threshold_proposal', schema_version=1,
        rule='midpoint_of_target_maximum_and_highest_strictly_lower_foil_maximum',
        source_manifest=before, source_model_revision=spec['model_revision'],
        source_training_outcome=spec['training_outcome'], rows=rows, threshold=threshold,
        lower_peak=lower, upper_peak=upper, full_matrix_peak_margin=upper-max(foils),
        nonspiking_proxy=dict(TP=1, FN=0, FP=sum(v >= threshold for v in foils),
            TN=sum(v < threshold for v in foils)),
        protocol='historical_same_matrix', calibrated=False, classification_assessed=False,
        training_completed=False, scientific_verdict=None)


def run(source_manifest, controls):
    controls = Path(controls).resolve(strict=True);declaration = load(controls/'declaration.json')
    require(set(declaration) == {'controller', 'output', 'maximum_wall_seconds', 'leaf_memory_bytes'},
            'threshold_study_control_fields')
    output = Path(declaration['output']).resolve()
    require(output.is_relative_to(Path(os.environ['TMPDIR']).resolve(strict=True)) and not output.exists(),
            'threshold_study_new_owned_output_required')
    live = inspect(Path(declaration['controller']).resolve(strict=True))
    require(live['execution'] == 'running' and live['binding']['initial_main_pid'] == os.getpid(),
            'threshold_study_owned_controller_required')
    wall = declaration['maximum_wall_seconds'];memory = declaration['leaf_memory_bytes']
    require(type(wall) is int and 1 <= wall <= 1800 and type(memory) is int and
            1024**3 <= memory <= 8*1024**3, 'threshold_study_declared_native_limits')
    runtime_path = controls/'runtime.json';runtime = load(runtime_path);verify_runtime(runtime)
    proposal = propose(source_manifest);root = Path(source_manifest).resolve(strict=True).parent
    source = root/'input/source/train_stopped_state.json'
    source_before = file_record(source)
    manifest = load(Path(source_manifest))
    records = {r['path']: r for r in manifest['artifacts']}
    job_raw, job_record = _frozen(root/'input/job.json', 384*1024**2)
    require(source_before['size'] == records['input/source/train_stopped_state.json']['bytes'] and
            source_before['sha256'] == records['input/source/train_stopped_state.json']['sha256'] and
            all(job_record[k] == records['input/job.json'][k] for k in ('bytes', 'sha256')),
            'threshold_study_source_binding_changed')
    original_job = parse_json_bytes(job_raw)
    del job_raw
    require(original_job['schema_version'] == 1 and original_job['conversion_spec'] ==
        dict(schema_version=1, mode='identity', resistance_bounds=[]), 'threshold_study_identity_source_required')
    output.mkdir();(output/'jobs').mkdir();_write(output/'proposal.json', proposal)
    registry = Reservations(output/'leases.sqlite3', managed_units=True,
        capacity=dict(slots=1, memory_bytes=live['memory_max']+2*memory, disk_bytes=8*1024**3, tasks=512))
    lease = registry.reserve('same-matrix-stopped-threshold-study',
        [dict(path=str(output/'runs'), access='write')], ttl_seconds=14400,
        demands=dict(slots=1, memory_bytes=live['memory_max']+memory, disk_bytes=8*1024**3, tasks=256),
        controller_directory=declaration['controller'])
    policy = policy_for_reservation(registry, lease['token'], memory_bytes=memory, tasks=128)
    results = []
    try:
        for name in ('baseline100', 'candidate'):
            job = {k: v for k, v in original_job.items() if k != 'sha256'}
            job['run_id'] = 'same-matrix-stopped-threshold/'+name
            job['trials'] = [{**t, 'run_id': job['run_id']} for t in original_job['trials']]
            if name == 'candidate':
                job.update(schema_version=2, diagnostic_threshold=proposal['threshold'])
            job = _signed(job);job_path = output/'jobs'/(name+'.json');_write(job_path, job)
            folder = output/'runs'/name;folder.parent.mkdir(exist_ok=True)
            registry.heartbeat(lease['token'], ttl_seconds=14400)
            result = run_job('diagnostic-evaluate', job_path, source, runtime_path, folder,
                             wall, process_policy=policy)
            require((result['execution'], result['validity']) == ('completed', 'valid'),
                    'threshold_study_execution_incomplete:'+name)
            require(inspect(folder/'process/contained')['all_processes_closed'], 'threshold_study_child_not_closed')
            metrics = result['analysis']['metrics']
            require(metrics['diagnostic_only'] and not metrics['training_completed'] and
                metrics['evaluation_verdict'] is None, 'threshold_study_false_training_claim')
            if name == 'baseline100':
                require(metrics['model_revision'] == proposal['source_model_revision'],
                        'threshold_study_baseline_model_changed')
                _, old = load_diagnostic_evaluation(root/'native/evaluation.json')
                _, new = load_diagnostic_evaluation(folder/'native/evaluation.json')
                old_by_id = {o['trial_id']: o for o in old}
                require(len(new) == len(old_by_id) == 8 and all(
                    o['samples'] == old_by_id[o['trial_id']]['samples'] and
                    o['model_before'] == old_by_id[o['trial_id']]['model_before'] for o in new),
                    'threshold_study_new_sdk_baseline_waveform_differs')
            else:
                require(metrics['effective_threshold'] == proposal['threshold'] and
                    metrics['diagnostic_threshold_experiment'] and not metrics['calibration_performed'],
                    'threshold_study_factor_or_role_changed')
            results.append(dict(name=name, run_manifest=str(folder/'run-manifest.json'), metrics=metrics))
        require(source_before == file_record(source), 'threshold_study_source_changed')
        result = dict(kind='same_matrix_stopped_threshold_native_result', schema_version=1,
            proposal=proposal, actual_results=results, baseline_waveforms_equal=True,
            runtime_fingerprint=runtime['runtime_fingerprint'], source=source_before,
            training_completed=False, calibrated=False, independent_evaluation=False, scientific_verdict=None)
        _write(output/'result.json', result)
        return result
    finally:
        registry.release(lease['token'])
