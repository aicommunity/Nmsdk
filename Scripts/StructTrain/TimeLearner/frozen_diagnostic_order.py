"""Frozen stopped-model order probes with a measured same-order control.

No training, threshold selection, or held-out scientific claim is performed.
Both phases use the ordinary owned diagnostic-evaluate production path.
"""
from collections import Counter
import math
import os
from pathlib import Path

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


def rotated_trials(patterns, run_id, rotations):
    """Preserve each stimulus/window/reset declaration; change order and IDs."""
    size = len(patterns)
    require(size >= 2 and len({t['sample_id'] for t in patterns}) == size and
            sum(t['label'] == 'target' for t in patterns) == 1 and
            all(t['label'] in ('target', 'foil') for t in patterns),
            'frozen_order_unique_labeled_matrix_required')
    require(type(rotations) is list and bool(rotations) and
            all(type(r) is int and 0 <= r < size for r in rotations) and
            len(set(rotations)) == len(rotations), 'frozen_order_invalid_rotations')
    require(all(t['reset_policy'] == 'reset_per_trial' and
                t['record_threshold_potential'] is True for t in patterns),
            'frozen_order_requires_recorded_reset_per_trial')
    return [{**t, 'run_id': run_id,
             'trial_id': f'{run_id}/rotation-{rotation}/position-{position}'}
            for rotation in rotations
            for position, t in enumerate(patterns[rotation:]+patterns[:rotation])]


def compare_samples(expected, observed, tolerance):
    """Finite absolute comparison of the full recorded baseline, no decimation."""
    tolerance = number(tolerance)
    require(0 <= tolerance <= 1e-10, 'frozen_order_baseline_tolerance_invalid')
    require(type(expected) is list and type(observed) is list and
            len(expected) == len(observed), 'frozen_order_baseline_sample_count_changed')
    maximum = 0.
    pending = [(expected, observed)]
    while pending:
        left, right = pending.pop()
        if type(left) in (int, float) and type(right) in (int, float):
            delta = abs(number(left)-number(right))
            require(delta <= tolerance, 'frozen_order_baseline_waveform_changed')
            maximum = max(maximum, delta)
        elif type(left) is dict:
            require(type(right) is dict and left.keys() == right.keys(),
                    'frozen_order_baseline_sample_fields_changed')
            pending.extend((left[k], right[k]) for k in left)
        elif type(left) is list:
            require(type(right) is list and len(left) == len(right),
                    'frozen_order_baseline_sample_shape_changed')
            pending.extend(zip(left, right))
        else:
            require(type(left) is type(right) and left == right,
                    'frozen_order_baseline_sample_value_changed')
    return maximum


def run(source_manifest, controls):
    source_manifest = Path(source_manifest).resolve(strict=True)
    controls = Path(controls).resolve(strict=True)
    declaration = load(controls/'declaration.json')
    require(set(declaration) == {'controller', 'output', 'baseline_wall_seconds',
            'study_wall_seconds', 'leaf_memory_bytes', 'baseline_sample_absolute_tolerance',
            'rotations', 'expected_source_manifest_sha256'}, 'frozen_order_control_fields')
    source_manifest_before = file_record(source_manifest)
    require(source_manifest_before['sha256'] == declaration['expected_source_manifest_sha256'],
            'frozen_order_source_manifest_changed')
    output = Path(declaration['output']).resolve()
    require(output.is_relative_to(Path(os.environ['TMPDIR']).resolve(strict=True)) and
            not output.exists(), 'frozen_order_new_owned_output_required')
    live = inspect(Path(declaration['controller']).resolve(strict=True))
    require(live['execution'] == 'running' and
            live['binding']['initial_main_pid'] == os.getpid(),
            'frozen_order_owned_controller_required')
    memory = declaration['leaf_memory_bytes']
    require(type(memory) is int and 1024**3 <= memory <= 8*1024**3 and
            all(type(declaration[k]) is int and 1 <= declaration[k] <= 28800
                for k in ('baseline_wall_seconds', 'study_wall_seconds')),
            'frozen_order_declared_native_limits')
    tolerance = number(declaration['baseline_sample_absolute_tolerance'])
    require(0 <= tolerance <= 1e-10, 'frozen_order_baseline_tolerance_invalid')
    runtime_path = controls/'runtime.json';runtime = load(runtime_path)
    verify_runtime(runtime)
    audit = audit_run_manifest(source_manifest)
    manifest = load(source_manifest);root = source_manifest.parent
    require(manifest['operation'] == 'diagnostic-evaluate' and
            manifest['execution'] == 'completed' and manifest['validity'] == 'valid' and
            audit['run_evidence_consistent'], 'frozen_order_requires_audited_diagnostic')
    original_metrics = manifest['analysis']['metrics']
    require(original_metrics['diagnostic_only'] and
            not original_metrics['training_completed'] and
            original_metrics['diagnostic_threshold_experiment'] and
            not original_metrics['calibration_performed'],
            'frozen_order_requires_fixed_diagnostic_threshold')
    source = root/'input/source/train_stopped_state.json'
    records = {r['path']: r for r in manifest['artifacts']}
    source_before = file_record(source)
    job_raw, job_record = _frozen(root/'input/job.json', 384*1024**2)
    require(source_before['size'] == records['input/source/train_stopped_state.json']['bytes'] and
            source_before['sha256'] == records['input/source/train_stopped_state.json']['sha256'] and
            all(job_record[k] == records['input/job.json'][k] for k in ('bytes', 'sha256')),
            'frozen_order_primary_binding_changed')
    original_job = parse_json_bytes(job_raw);del job_raw
    require(original_job['schema_version'] == 2 and original_job['conversion_spec'] ==
            dict(schema_version=1, mode='identity', resistance_bounds=[]) and
            original_job['diagnostic_threshold'] == original_metrics['effective_threshold'] and
            original_job['coverage_policy'] == 'per_trial_windows' and
            original_job['criterion'] == dict(id='post_anchor_target_whole_window_foil_v1',
                anchor='onset', begin_offset=0., end_offset=None,
                reject_target_outside_window=True), 'frozen_order_source_protocol_changed')
    patterns = original_job['trials'];size = len(patterns)
    require(declaration['rotations'] == list(range(1, size)),
            'frozen_order_all_other_target_positions_required')
    # Validate the entire planned design before the first native process.
    rotated_trials(patterns, 'frozen-order/baseline', [0])
    rotated_trials(patterns, 'frozen-order/study', declaration['rotations'])
    old_spec, old_observations = load_diagnostic_evaluation(root/'native/evaluation.json')
    require(old_spec['model_revision'] == original_metrics['model_revision'] and
            len(old_observations) == size, 'frozen_order_source_observations_changed')
    old_by_sample = {o['sample_id']: o for o in old_observations}
    output.mkdir();(output/'jobs').mkdir()
    _write(output/'design.json', dict(source_manifest=source_manifest_before,
        source_model_revision=original_metrics['model_revision'],
        threshold=original_metrics['effective_threshold'], rotations=[0]+declaration['rotations'],
        expected_trials=size*size, baseline_sample_absolute_tolerance=tolerance,
        reset_policy='reset_per_trial', training_completed=False, independent_evaluation=False))
    leaf_tasks = 128;controller_tasks = live['tasks_max']
    registry = Reservations(output/'leases.sqlite3', managed_units=True,
        capacity=dict(slots=1, memory_bytes=live['memory_max']+2*memory,
                      disk_bytes=8*1024**3, tasks=controller_tasks+2*leaf_tasks))
    lease = registry.reserve('frozen-stopped-order-study',
        [dict(path=str(output/'runs'), access='write')], ttl_seconds=43200,
        demands=dict(slots=1, memory_bytes=live['memory_max']+memory,
                     disk_bytes=8*1024**3, tasks=controller_tasks+leaf_tasks),
        controller_directory=declaration['controller'])
    results = [];baseline_maximum_difference = 0.
    try:
        policy = policy_for_reservation(registry, lease['token'], memory_bytes=memory, tasks=leaf_tasks)
        for name, rotations, wall in [('baseline', [0], declaration['baseline_wall_seconds']),
                ('study', declaration['rotations'], declaration['study_wall_seconds'])]:
            job = {k: v for k, v in original_job.items() if k != 'sha256'}
            job['run_id'] = 'frozen-order/'+name
            job['trials'] = rotated_trials(patterns, job['run_id'], rotations)
            frequency = original_job['source_stopped']['configuration']['model']['frequency_hz']
            job['maximum_model_ticks'] = sum(math.ceil(t['duration']*frequency)+4 for t in job['trials'])
            job_path = output/'jobs'/(name+'.json');_write(job_path, _signed(job))
            folder = output/'runs'/name;folder.parent.mkdir(exist_ok=True)
            registry.heartbeat(lease['token'], ttl_seconds=43200)
            result = run_job('diagnostic-evaluate', job_path, source, runtime_path, folder,
                             wall, process_policy=policy)
            require((result['execution'], result['validity']) == ('completed', 'valid') and
                    inspect(folder/'process/contained')['all_processes_closed'],
                    'frozen_order_execution_incomplete:'+name)
            metrics = result['analysis']['metrics']
            require(metrics['diagnostic_only'] and not metrics['training_completed'] and
                    metrics['evaluation_verdict'] is None and
                    metrics['model_revision'] == original_metrics['model_revision'] and
                    metrics['effective_threshold'] == original_metrics['effective_threshold'] and
                    metrics['diagnostic_threshold_experiment'] and
                    not metrics['calibration_performed'] and
                    len(metrics['trials']) == size*len(rotations),
                    'frozen_order_model_threshold_or_scope_changed')
            if name == 'baseline':
                _, observations = load_diagnostic_evaluation(folder/'native/evaluation.json')
                require(len(observations) == len(old_by_sample) == size and
                        metrics['pooled_counts'] == original_metrics['pooled_counts'],
                        'frozen_order_baseline_responses_changed')
                for observed in observations:
                    prior = old_by_sample[observed['sample_id']]
                    require(observed['model_before'] == prior['model_before'],
                            'frozen_order_baseline_model_changed')
                    baseline_maximum_difference = max(baseline_maximum_difference,
                        compare_samples(prior['samples'], observed['samples'], tolerance))
            per_rotation = []
            by_trial = {t['trial_id']: t for t in metrics['trials']}
            for rotation in rotations:
                expected = [t for t in job['trials'] if f'/rotation-{rotation}/' in t['trial_id']]
                rows = [by_trial[t['trial_id']] for t in expected]
                counts = Counter(t['classification'] for t in rows)
                require(len(rows) == size and sum(counts.values()) == size and
                        set(counts) <= {'TP', 'FP', 'FN', 'TN'},
                        'frozen_order_incomplete_rotation')
                per_rotation.append(dict(rotation=rotation,
                    target_position=next(i for i, t in enumerate(expected) if t['label'] == 'target'),
                    counts={k: counts[k] for k in ('TP', 'FP', 'FN', 'TN')}, trials=rows))
            results.append(dict(name=name, run_manifest=str(folder/'run-manifest.json'),
                metrics=metrics, rotations=per_rotation))
            _write(output/(name+'-accepted.json'), results[-1])
        require(source_before == file_record(source) and
                source_manifest_before == file_record(source_manifest), 'frozen_order_source_changed')
        verify_runtime(runtime)
        final = dict(kind='frozen_stopped_order_native_result', schema_version=1,
            source=source_before, source_manifest=source_manifest_before,
            model_revision=original_metrics['model_revision'],
            threshold=original_metrics['effective_threshold'],
            runtime_fingerprint=runtime['runtime_fingerprint'], actual_results=results,
            baseline_maximum_sample_absolute_difference=baseline_maximum_difference,
            baseline_sample_absolute_tolerance=tolerance, expected_trials=size*size,
            deterministic_order_probes=True, independent_trainings=0,
            training_completed=False, independent_evaluation=False, scientific_verdict=None)
        _write(output/'result.json', final)
        return final
    finally:
        registry.release(lease['token'], note='Frozen order native groups closed; no retraining or retuning.')
