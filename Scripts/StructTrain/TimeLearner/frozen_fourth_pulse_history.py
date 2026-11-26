"""Vary only the fourth impulse after a common five-pattern history.

Every case begins from a reset and uses the same three leading target impulses.
The reference is the original r3 short-cadence sequence. Changed probes are
labelled foils; the original target is then presented as the final control.
There is no training, target replacement in the model, or threshold selection.
"""
from copy import deepcopy
from pathlib import Path

from .condition import ConditionSpec, artifact
from .model_identity import canonical_model_sha256 as sha
from .native_evidence import number, require
from .native_pipeline_worker import validate_job
from .runtime import file_record, runtime_content_identity


PROTOCOL = 'frozen_common_history_first_three_varied_fourth_v1'
FOURTH_TICKS = (560, 640, 720, 800, 880, 960, 1040, 1120)


def declare_job(original, run_id, *, fourth_from_first_ticks, reset_policy):
    from .frozen_physical_iti_study import declare_job as cadence_job
    require(type(fourth_from_first_ticks) is int and
            fourth_from_first_ticks in FOURTH_TICKS, 'fourth_history_unverified_fourth_time')
    job, base = cadence_job(original, run_id, rotation=3, cadence='short',
                            reset_policy=reset_policy)
    target = next(t for t in original['trials'] if t['label'] == 'target')
    require(base['frequency_hz'] == 2000 and base['target_position'] == 5 and
            target['pattern_isi'] == [.01, .08, .16, .24],
            'fourth_history_requires_original_M4_2000_target_and_position')
    reference = fourth_from_first_ticks == 960
    if not reference:
        probe = job['trials'][5]
        pattern = [.01, .08, .16, (fourth_from_first_ticks-480)/2000]
        sample = 'fourth-history-tick-'+str(fourth_from_first_ticks)
        require(sample not in {t['sample_id'] for t in original['trials']},
                'fourth_history_sample_identity_collision')
        probe.update(sample_id=sample, label='foil', pattern_isi=pattern,
                     pattern_hash=sha(pattern))
        # This positive control is strictly after the compared probe. Preserve
        # its boundary/reset settings and retain trial 6 from the reference.
        final = job['trials'][7]
        job['trials'][7] = dict(deepcopy(target),
            **{k:final[k] for k in ('run_id', 'trial_id', 'duration',
                                  'maximum_samples', 'reset_policy')})
    job.pop('sha256')
    job['sha256'] = sha(job)
    validate_job('physical-model-evaluate', job, (job['source_model_data'],))
    require(len({t['sample_id'] for t in job['trials']}) == 8 and
            len({t['pattern_hash'] for t in job['trials']}) == 8,
            'fourth_history_duplicate_sample_or_pattern')
    design = dict(protocol_id=PROTOCOL, frequency_hz=2000, pulse_count=4,
        rotation=3, cadence='short', following_trial_reset_policy=reset_policy,
        first_trial_reset_policy='reset_per_trial', reference_fourth_from_first_ticks=960,
        fourth_from_first_ticks=fourth_from_first_ticks,
        fixed_leading_impulse_ticks=[0, 160, 480],
        initial_input_delay_ticks=20, probe_position=5,
        common_prefix_positions=[0, 1, 2, 3, 4], unchanged_following_position=6,
        reference_case=reference, target_position=5 if reference else 7,
        final_trial_role='original_foil' if reference else 'original_target_positive_control',
        later_positive_control_not_part_of_preprobe_history=True,
        duration_before_final_trial=base['duration_before_final_trial'],
        final_observation_duration=base['final_observation_duration'],
        final_quiet_tail_minimum_seconds=2.,
        source_pattern_hashes=base['source_pattern_hashes'],
        actual_leading_inputs_and_prior_full_waveforms_must_match=True,
        compare_probe_until_first_differing_fourth_input=True,
        prefix_absolute_comparison_tolerance=1e-12,
        actual_onset_intervals_must_be_measured=True,
        complete_contiguous_observations_required=True,
        label_rule='exact_original_target_is_target; changed_fourth_probe_is_foil',
        selection_scope='directed_followup_of_observed_early_output_not_independent_holdout',
        training_performed=False, threshold_selected=False,
        expected_response_counts=None, independent_stochastic_repetitions=False)
    return job, design


def condition(job, design, runtime, *, threshold):
    """Bind the entire history; a preserve probe has no isolated case identity."""
    model = job['source_model_data']
    trials = [{k:v for k,v in t.items() if k not in ('run_id', 'trial_id')}
              for t in job['trials']]
    payloads = dict(
        algorithm=dict(protocol_id=PROTOCOL, implementation_id=job['implementation_id'],
            protocol_source_sha256=file_record(Path(__file__))['sha256'],
            cadence_source_sha256=file_record(Path(__file__).with_name('frozen_physical_iti_study.py'))['sha256'],
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
    require(ConditionSpec.loads(spec.dumps()) == spec, 'fourth_history_condition_roundtrip')
    spec.resolve({item['sha256']:item for item in artifacts.values()})
    return dict(condition=spec.to_object(), condition_fingerprint=spec.fingerprint,
        artifacts={item['sha256']:item for item in artifacts.values()},
        descriptor_integrity_only=True, scientific_verdict=None)


def run_case(declaration, runtime_path, output, *, run_id, fourth_from_first_ticks,
             reset_policy, maximum_wall_seconds, process_policy):
    from .frozen_physical_trial_study import run_declared_case
    from .job_source_transport import TRANSPORT
    return run_declared_case(declaration, runtime_path, output, run_id=run_id,
        study=dict(fourth_from_first_ticks=fourth_from_first_ticks, reset_policy=reset_policy),
        declare_job=declare_job, bind_condition=condition, expected_trials=8,
        protocol_id=PROTOCOL, result_kind='timelearner_frozen_fourth_history_result',
        maximum_wall_seconds=maximum_wall_seconds, process_policy=process_policy,
        job_source_transport=TRANSPORT)
