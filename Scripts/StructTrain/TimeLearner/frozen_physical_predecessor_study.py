"""Two-pattern controls of predecessor identity on one frozen DATA model.

Each case starts from a reset, presents one original foil, then the original
target. The target either resets or preserves dynamics. Timing is identical
across predecessor identities, and the complete final quiet tail is observed.
"""
from copy import deepcopy
from pathlib import Path

from .condition import ConditionSpec, artifact
from .frozen_physical_iti_study import declare_job as declare_cadence
from .model_identity import canonical_model_sha256 as sha
from .native_evidence import number, require
from .native_pipeline_worker import validate_job
from .runtime import file_record, runtime_content_identity


PROTOCOL = 'frozen_predecessor_identity_and_reset_v1'


def declare_job(original, run_id, *, predecessor, cadence, reset_policy):
    # Reuse the actual eight-pattern source validation and integer tick policy.
    # Its eight-trial request is not executed or interpreted as this study.
    _, base = declare_cadence(original, run_id, rotation=0, cadence=cadence,
                             reset_policy=reset_policy)
    require(type(predecessor) is str and bool(predecessor), 'predecessor_id_required')
    foils = [t for t in original['trials'] if t['sample_id'] == predecessor and t['label'] == 'foil']
    require(len(foils) == 1, 'predecessor_must_be_one_original_foil')
    target = next(t for t in original['trials'] if t['label'] == 'target')
    frequency = base['frequency_hz']
    last_target_tick = sum(round(v*frequency) for v in target['pattern_isi'])
    final_ticks = max(2*frequency, last_target_tick+1+2*frequency)
    trials = []
    for position, source in enumerate((foils[0], target)):
        ticks = round(base['duration_before_final_trial']*frequency) if position == 0 else final_ticks
        trials.append(dict(source, run_id=run_id, trial_id=run_id+'/position-'+str(position),
            duration=ticks/frequency, maximum_samples=ticks+5,
            reset_policy='reset_per_trial' if position == 0 else reset_policy))
    job = deepcopy(original)
    job.pop('sha256')
    job.update(run_id=run_id, trials=trials, coverage_policy='continuous_native_stream',
               maximum_model_ticks=sum(t['maximum_samples']-1 for t in trials))
    job['sha256'] = sha(job)
    validate_job('physical-model-evaluate', job, (job['source_model_data'],))
    design = dict(protocol_id=PROTOCOL, predecessor=predecessor,
        target_sample_id=target['sample_id'], target_position=1, pattern_count=2,
        pulses_per_pattern=len(target['pattern_isi']), cadence=cadence,
        duration_before_final_trial=base['duration_before_final_trial'],
        final_observation_duration=final_ticks/frequency,
        frequency_hz=frequency, first_trial_reset_policy='reset_per_trial',
        target_reset_policy=reset_policy, final_quiet_tail_minimum_seconds=2.,
        source_pattern_hashes=[t['pattern_hash'] for t in trials],
        source_validation_scope='complete_original_eight_pattern_design',
        actual_onset_intervals_must_be_measured=True,
        complete_contiguous_observations_required=True,
        training_performed=False, threshold_selected=False,
        original_patterns_reused=True, independently_heldout_patterns=False,
        independent_stochastic_repetitions=False, expected_response_counts=None)
    return job, design


def condition(job, design, runtime, *, threshold):
    """Use the shared production serializer, without paths or attempt IDs."""
    model = job['source_model_data']
    trials = [{k:v for k,v in t.items() if k not in ('run_id', 'trial_id')} for t in job['trials']]
    payloads = dict(
        algorithm=dict(protocol_id=PROTOCOL, implementation_id=job['implementation_id'],
            protocol_source_sha256=file_record(Path(__file__))['sha256'],
            reused_cadence_source_sha256=file_record(Path(__file__).with_name('frozen_physical_iti_study.py'))['sha256'],
            native_runtime_content=runtime_content_identity(runtime)),
        model_spec=model['configuration']['model'],
        storage_profiles=dict(model_revision=model['model_revision'], model_data_sha256=model['sha256']),
        initial_state=dict(dynamic_checkpoint=False, first_trial_reset_policy='reset_per_trial'),
        training_plan=dict(performed=False), input_data=dict(trials=trials),
        presentation_protocol=design,
        calibration_spec=dict(performed=False, fixed_threshold=number(threshold)),
        evaluation_spec=dict(criterion=job['criterion'], coverage_policy=job['coverage_policy']),
        execution_policy=dict(maximum_model_ticks=job['maximum_model_ticks']),
        randomness_spec=dict(random_factors=[], independent_stochastic_repetitions=False))
    artifacts = {role:artifact(role,payload) for role,payload in payloads.items()}
    spec = ConditionSpec(controller_version=2, amplitude_goal='captured_per_input',
                        **{role:item['sha256'] for role,item in artifacts.items()})
    require(ConditionSpec.loads(spec.dumps()) == spec, 'predecessor_condition_roundtrip')
    return dict(condition=spec.to_object(), condition_fingerprint=spec.fingerprint,
        artifacts={item['sha256']:item for item in artifacts.values()},
        descriptor_integrity_only=True, scientific_verdict=None)


def run_case(declaration, runtime_path, output, *, run_id, predecessor, cadence,
             reset_policy, maximum_wall_seconds, process_policy):
    """Execute both actual patterns with the ordinary native runtime and scorer."""
    from .frozen_physical_trial_study import run_declared_case
    return run_declared_case(declaration, runtime_path, output, run_id=run_id,
        study=dict(predecessor=predecessor, cadence=cadence, reset_policy=reset_policy),
        declare_job=declare_job, bind_condition=condition, expected_trials=2,
        protocol_id=PROTOCOL, result_kind='timelearner_frozen_predecessor_reset_result',
        maximum_wall_seconds=maximum_wall_seconds, process_policy=process_policy)
