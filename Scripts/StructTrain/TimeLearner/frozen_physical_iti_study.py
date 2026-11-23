"""Declared cadence/reset controls of an unchanged eight-pattern DATA model.

Each rotation is a separate native job, beginning with an explicit reset. The
other seven trials either reset or preserve dynamics. Every tick, including a
final two-second quiet tail, must remain observed. This module does not train,
choose a threshold or interpret a zero process exit as scientific success.
"""
from copy import deepcopy

from .condition import ConditionSpec, artifact
from .model_identity import canonical_model_sha256 as sha
from .native_evidence import equal, number, require
from .native_pipeline_worker import validate_job
from .runtime import file_record, runtime_content_identity


PROTOCOL = 'frozen_eight_pattern_cadence_and_reset_v1'


def declare_job(original, run_id, *, rotation, cadence, reset_policy):
    require(type(run_id) is str and bool(run_id) and type(rotation) is int and 0 <= rotation < 8 and
            cadence in ('long', 'short') and reset_policy in ('reset_per_trial', 'preserve_neuron_dynamics'),
            'iti_invalid_condition')
    model = original['source_model_data']
    validate_job('physical-model-evaluate', original, (model,))
    trials = original['trials']
    require(len(trials) == 8 and len({t['sample_id'] for t in trials}) == 8 and
            len({t['pattern_hash'] for t in trials}) == 8 and
            sum(t['label'] == 'target' for t in trials) == 1 and
            sum(t['label'] == 'foil' for t in trials) == 7 and
            all(t['reset_policy'] == 'reset_per_trial' and t['duration'] == 2 and
                t['record_threshold_potential'] is True and
                t['pattern_hash'] == sha(t['pattern_isi']) for t in trials),
            'iti_requires_complete_original_eight_pattern_reset_design')
    target = next(t for t in trials if t['label'] == 'target')
    require(target['pattern_isi'] == model['configuration']['model']['initial_isi'] and
            all(len(t['pattern_isi']) == len(target['pattern_isi']) for t in trials),
            'iti_original_target_or_dimensions_changed')
    frequency = number(model['configuration']['model']['frequency_hz'])
    require(frequency in (2000, 20000), 'iti_unverified_frequency')
    require(all(number(v) > 0 for t in trials for v in t['pattern_isi']), 'iti_nonpositive_interval')
    frequency = int(frequency)
    require(all(equal(v*frequency, round(v*frequency)) for t in trials for v in t['pattern_isi']),
            'iti_requires_native_tick_patterns_and_shorter_cadence')
    # All declared intervals have been checked against the native lattice.
    # Summing their binary floats and applying ceil can add a spurious tick
    # (e.g. .01+.4+.04+.04+.2). Carry out boundary arithmetic as integer ticks.
    last_input_ticks = {t['pattern_hash']:sum(round(v*frequency) for v in t['pattern_isi']) for t in trials}
    short_ticks = max(last_input_ticks.values()) + round(.2*frequency)
    short_duration = short_ticks/frequency
    require(0 < short_duration < 2, 'iti_requires_native_tick_patterns_and_shorter_cadence')
    duration_ticks = 2*frequency if cadence == 'long' else short_ticks
    duration = duration_ticks/frequency
    ordered = trials[rotation:]+trials[:rotation]
    requests = []
    for position, trial in enumerate(ordered):
        # Closing the stream is not an unobserved wait. The final observation
        # includes at least two full seconds after its actual final input.
        # One extra native tick covers the observed generator onset offset.
        ticks = duration_ticks if position != 7 else max(2*frequency,
            last_input_ticks[trial['pattern_hash']]+1+2*frequency)
        requests.append(dict(trial, run_id=run_id, trial_id=f'{run_id}/rotation-{rotation}/position-{position}',
            duration=ticks/frequency, maximum_samples=ticks+5,
            reset_policy='reset_per_trial' if position == 0 else reset_policy))
    job = deepcopy(original)
    job.pop('sha256')
    job.update(run_id=run_id, coverage_policy='continuous_native_stream', trials=requests,
               maximum_model_ticks=sum(t['maximum_samples']-1 for t in requests))
    job['sha256'] = sha(job)
    validate_job('physical-model-evaluate', job, (model,))
    design = dict(protocol_id=PROTOCOL, rotation=rotation, cadence=cadence,
        following_trial_reset_policy=reset_policy, first_trial_reset_policy='reset_per_trial',
        duration_before_final_trial=duration, short_duration_rule='ceil((max_original_last_input+0.2)*frequency)/frequency',
        final_quiet_tail_minimum_seconds=2., final_observation_duration=requests[-1]['duration'],
        frequency_hz=frequency, target_position=next(i for i,t in enumerate(requests) if t['label']=='target'),
        source_pattern_hashes=[t['pattern_hash'] for t in trials],
        actual_onset_intervals_must_be_measured=True, complete_contiguous_observations_required=True,
        training_performed=False, threshold_selected=False, expected_response_counts=None,
        independent_stochastic_repetitions=False)
    return job, design


def condition(job, design, runtime, *, threshold):
    """Scientific identity excludes attempt IDs, paths and unrelated cases."""
    from pathlib import Path
    model = job['source_model_data']
    trials = [{k:v for k,v in t.items() if k not in ('run_id','trial_id')} for t in job['trials']]
    payloads = dict(
        algorithm=dict(protocol_id=PROTOCOL, implementation_id=job['implementation_id'],
            protocol_source_sha256=file_record(Path(__file__))['sha256'],
            native_runtime_content=runtime_content_identity(runtime)),
        model_spec=model['configuration']['model'],
        storage_profiles=dict(model_revision=model['model_revision'], model_data_sha256=model['sha256']),
        initial_state=dict(dynamic_checkpoint=False, first_trial_reset_policy='reset_per_trial'),
        training_plan=dict(performed=False), input_data=dict(trials=trials),
        presentation_protocol=design,
        calibration_spec=dict(performed=False, fixed_threshold=number(threshold)),
        evaluation_spec=dict(criterion=job['criterion'],coverage_policy=job['coverage_policy']),
        execution_policy=dict(maximum_model_ticks=job['maximum_model_ticks']),
        randomness_spec=dict(random_factors=[],independent_stochastic_repetitions=False))
    artifacts = {role:artifact(role,payload) for role,payload in payloads.items()}
    spec = ConditionSpec(controller_version=2, amplitude_goal='captured_per_input',
                        **{role:item['sha256'] for role,item in artifacts.items()})
    require(ConditionSpec.loads(spec.dumps()) == spec, 'iti_condition_roundtrip')
    return dict(condition=spec.to_object(),condition_fingerprint=spec.fingerprint,
        artifacts={item['sha256']:item for item in artifacts.values()},
        descriptor_integrity_only=True,scientific_verdict=None)


def run_case(declaration, runtime_path, output, *, run_id, rotation, cadence,
             reset_policy, maximum_wall_seconds, process_policy):
    """Use the ordinary native pipeline; resource admission belongs to its owner."""
    from .frozen_physical_trial_study import run_declared_case
    return run_declared_case(declaration, runtime_path, output, run_id=run_id,
        study=dict(rotation=rotation, cadence=cadence, reset_policy=reset_policy),
        declare_job=declare_job, bind_condition=condition, expected_trials=8,
        protocol_id=PROTOCOL, result_kind='timelearner_frozen_cadence_reset_result',
        maximum_wall_seconds=maximum_wall_seconds, process_policy=process_policy)
