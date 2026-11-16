"""Fixed-model full-window/reset comparisons through the ordinary native runner.

Longer windows also change the observed quiet tail and onset spacing. This is
not an isolated ITI intervention, a new training, or an independent-data test.
"""
import math
import os
from pathlib import Path

from .condition import CONDITION_ROLES, ConditionSpec, artifact
from .contained_process import inspect
from .frozen_diagnostic_order import compare_samples
from .native_calibration_worker import _signed, _write
from .native_evidence import load, number, parse_json_bytes, require
from .native_pipeline_worker import audit_run_manifest, run_job
from .native_process_policy import policy_for_reservation
from .model_identity import canonical_model_sha256 as sha
from .process_runner import verify_runtime
from .recognition_metrics import load_diagnostic_evaluation
from .resource_reservations import Reservations
from .runtime import file_record


def variant_trials(patterns, identifier, duration, reset_policy):
    require(type(patterns) is list and len(patterns) > 1 and
            len({p['sample_id'] for p in patterns}) == len(patterns) and
            sum(p['label'] == 'target' for p in patterns) == 1 and
            all(p['label'] in ('target', 'foil') and
                p['reset_policy'] == 'reset_per_trial' and
                p['record_threshold_potential'] is True for p in patterns),
            'frozen_protocol_requires_complete_recorded_reset_matrix')
    duration = number(duration)
    require(0 < duration <= 30 and
            all(duration >= number(p['duration']) for p in patterns) and
            reset_policy in ('reset_per_trial', 'preserve_neuron_dynamics') and
            type(identifier) is str and bool(identifier),
            'frozen_protocol_cannot_shorten_windows_or_change_reset_contract')
    return [{**p, 'run_id': identifier, 'trial_id': f'{identifier}/position-{i}',
             'duration': duration, 'maximum_samples': math.ceil(duration*2000)+5,
             'reset_policy': reset_policy} for i, p in enumerate(patterns)]


def condition_for(package, job, runtime, wall, memory):
    projected = [{k: t[k] for k in ('sample_id', 'label', 'pattern_hash',
                 'pattern_isi', 'duration', 'reset_policy')} for t in job['trials']]
    payloads = {
        'algorithm': {'experiment': 'frozen-full-window-reset-v1',
            'implementation_id': package['implementation_id'],
            'pulse': runtime['source_closure']['Libraries/Nmsdk-PulseLib']['head'],
            'rdk': runtime['source_closure']['Rdk']['head']},
        'model_spec': package['configuration']['model'],
        'storage_profiles': {'definitions_sha256': sha(package['neuron']['class_definitions'])},
        'initial_state': {'model_revision': package['model_revision'],
                          'initialization': 'fresh-native-import'},
        'training_plan': {'training_performed': False,
                          'source_training_outcome': package['training_outcome']},
        'input_data': {'patterns': [{k: p[k] for k in ('sample_id', 'label',
                                      'pattern_hash', 'pattern_isi')} for p in projected]},
        'presentation_protocol': {'ordered_trials': projected, 'frequency_hz': 2000,
            'spacing': 'full-trial-window-plus-native-boundary-step'},
        'calibration_spec': {'threshold': job['diagnostic_threshold'],
            'adaptation': False, 'selection': 'prior-same-matrix'},
        'evaluation_spec': {'criterion': job['criterion'], 'independent_patterns': False,
            'quiet_tail_and_observation_window_change_together': True},
        'execution_policy': {'maximum_model_ticks': job['maximum_model_ticks'],
            'maximum_wall_seconds': wall, 'native_memory_bytes': memory, 'native_tasks': 128},
        'randomness_spec': {'deterministic_saved_model': True, 'independent_trainings': 0},
    }
    artifacts = {role: artifact(role, payloads[role]) for role in CONDITION_ROLES}
    spec = ConditionSpec(controller_version=package['controller_version'],
        amplitude_goal='captured_per_input',
        **{role: row['sha256'] for role, row in artifacts.items()})
    spec.resolve({row['sha256']: row for row in artifacts.values()})
    return {'condition': spec.to_object(), 'artifacts': artifacts}


def run(source_manifest, controls):
    controls = Path(controls).resolve(strict=True)
    declaration = load(controls/'declaration.json')
    require(set(declaration) == {'controller', 'output', 'source_manifest_sha256',
        'leaf_memory_bytes', 'leaf_wall_seconds', 'extended_duration'},
        'frozen_protocol_declaration_fields')
    source_manifest = Path(source_manifest).resolve(strict=True)
    source_before = file_record(source_manifest)
    require(source_before['sha256'] == declaration['source_manifest_sha256'],
        'frozen_protocol_source_manifest_changed')
    require(audit_run_manifest(source_manifest)['run_evidence_consistent'],
        'frozen_protocol_source_audit_failed')
    manifest = load(source_manifest);root = source_manifest.parent
    require(manifest['operation'] == 'diagnostic-evaluate' and
        manifest['execution'] == 'completed' and manifest['validity'] == 'valid',
        'frozen_protocol_requires_closed_valid_diagnostic')
    prior = manifest['analysis']['metrics']
    require(prior['diagnostic_only'] and not prior['training_completed'] and
        prior['diagnostic_threshold_experiment'] and not prior['calibration_performed'],
        'frozen_protocol_source_role_changed')
    original = parse_json_bytes((root/'input/job.json').read_bytes())
    package = original['source_stopped'];patterns = original['trials']
    require(package['certificate'] is None and package['controller_version'] == 2 and
        package['configuration']['model']['frequency_hz'] == 2000 and
        original['conversion_spec'] == dict(schema_version=1, mode='identity', resistance_bounds=[]) and
        original['diagnostic_threshold'] == prior['effective_threshold'],
        'frozen_protocol_source_model_or_threshold_changed')
    duration = number(patterns[0]['duration'])
    require(all(number(p['duration']) == duration for p in patterns) and
        number(declaration['extended_duration']) > duration, 'frozen_protocol_duration_design')
    designs = [('baseline', duration, 'reset_per_trial'),
        ('long-reset', declaration['extended_duration'], 'reset_per_trial'),
        ('continuous', duration, 'preserve_neuron_dynamics'),
        ('long-continuous', declaration['extended_duration'], 'preserve_neuron_dynamics')]
    planned = [(name, variant_trials(patterns, 'frozen-protocol/'+name, d, p))
               for name, d, p in designs]
    runtime_path = controls/'runtime.json';runtime = load(runtime_path);verify_runtime(runtime)
    live = inspect(declaration['controller'])
    require(live['execution'] == 'running' and live['binding']['initial_main_pid'] == os.getpid(),
        'frozen_protocol_requires_bound_main_controller')
    memory = declaration['leaf_memory_bytes'];wall = declaration['leaf_wall_seconds']
    require(type(memory) is int and 1024**3 <= memory <= 8*1024**3 and
        type(wall) is int and 60 <= wall <= 14400, 'frozen_protocol_native_limits')
    output = Path(declaration['output']).resolve()
    require(output.is_relative_to(Path(os.environ['TMPDIR']).resolve(strict=True)) and
        not output.exists(), 'frozen_protocol_requires_new_owned_output')
    old_spec, old_observations = load_diagnostic_evaluation(root/'native/evaluation.json')
    require(old_spec['model_revision'] == prior['model_revision'] and
        len(old_observations) == len(patterns), 'frozen_protocol_baseline_observations')
    old_by_sample = {o['sample_id']: o for o in old_observations}
    source = root/'input/source/train_stopped_state.json';package_before = file_record(source)
    output.mkdir();(output/'jobs').mkdir()
    demands = dict(slots=1, memory_bytes=live['memory_max']+memory,
                   tasks=live['tasks_max']+128, disk_bytes=8*1024**3)
    registry = Reservations(output/'leases.sqlite3', managed_units=True, capacity=demands)
    lease = registry.reserve('frozen-window-reset-study',
        [dict(path=str(output/'runs'), access='write')], ttl_seconds=4*wall+600,
        demands=demands, controller_directory=declaration['controller'])
    results = [];baseline_difference = 0.
    try:
        policy = policy_for_reservation(registry, lease['token'], memory_bytes=memory, tasks=128)
        for name, trials in planned:
            job = {k: v for k, v in original.items() if k != 'sha256'}
            job.update(run_id='frozen-protocol/'+name, trials=trials,
                maximum_model_ticks=sum(math.ceil(t['duration']*2000)+4 for t in trials))
            job = _signed(job);path = output/'jobs'/(name+'.json');_write(path, job)
            condition = condition_for(package, job, runtime, wall, memory)
            _write(output/'jobs'/(name+'-condition.json'), condition)
            folder = output/'runs'/name
            result = run_job('diagnostic-evaluate', path, source, runtime_path, folder,
                             wall, process_policy=policy)
            require(result['execution'] == 'completed' and result['validity'] == 'valid',
                'frozen_protocol_native_run_incomplete')
            metrics = result['analysis']['metrics']
            require(metrics['model_revision'] == prior['model_revision'] and
                metrics['effective_threshold'] == prior['effective_threshold'] and
                metrics['diagnostic_only'] and not metrics['training_completed'] and
                not metrics['calibration_performed'], 'frozen_protocol_frozen_model_changed')
            _, observations = load_diagnostic_evaluation(folder/'native/evaluation.json')
            require(len(observations) == len(trials), 'frozen_protocol_missing_trials')
            for expected, observed in zip(trials, observations):
                require(all(observed[k] == expected[k] for k in ('trial_id', 'sample_id',
                    'pattern_hash', 'pattern_isi', 'reset_policy')) and observed['complete'] and
                    not observed['censored'] and observed['valid'] and
                    abs(observed['end']-observed['begin']-expected['duration']) <= 1.1/2000,
                    'frozen_protocol_effective_trial_changed')
                if name == 'baseline':
                    baseline_difference = max(baseline_difference, compare_samples(
                        old_by_sample[observed['sample_id']]['samples'], observed['samples'], 0.))
            if name == 'baseline':
                require(metrics['pooled_counts'] == prior['pooled_counts'],
                    'frozen_protocol_baseline_classification_changed')
            results.append(dict(name=name, metrics=metrics, condition=condition['condition'],
                onset_intervals=[b['stimulus_onset']-a['stimulus_onset']
                                 for a, b in zip(observations, observations[1:])],
                last_input_to_next_onset=[b['stimulus_onset']-a['stimulus_times'][-1]
                                 for a, b in zip(observations, observations[1:])]))
            _write(output/f'progress-{len(results)}.json', dict(completed_conditions=len(results),
                completed_trials=sum(len(r['metrics']['trials']) for r in results)))
    finally:
        registry.release(lease['token'], note='Fixed model/threshold; no scientific PASS asserted.')
    require(file_record(source_manifest) == source_before and file_record(source) == package_before,
        'frozen_protocol_original_source_changed')
    result = dict(kind='frozen_diagnostic_full_window_reset_study', schema_version=1,
        source_manifest=source_before, model_revision=prior['model_revision'],
        threshold=prior['effective_threshold'], actual_results=results, expected_trials=4*len(patterns),
        baseline_maximum_sample_absolute_difference=baseline_difference,
        training_completed=False, independent_evaluation=False, independent_trainings=0,
        isolated_iti_intervention=False, scientific_verdict=None)
    _write(output/'result.json', result);return result
