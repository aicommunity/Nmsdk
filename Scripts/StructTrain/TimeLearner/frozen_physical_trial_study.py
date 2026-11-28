"""Execute declared frozen DATA trials through the shared native pipeline.

The protocol supplies its declaration and condition serializer. Complete sample
windows, frozen model/threshold, exact trial coverage and final quiet tail are
validated here for both cadence and two-pattern predecessor controls.
"""
from .native_evidence import after, equal, number, require
from .runtime import file_record


def run_declared_case(declaration, runtime_path, output, *, run_id, study,
                      declare_job, bind_condition, expected_trials, protocol_id,
                      result_kind, maximum_wall_seconds, process_policy,
                      job_source_transport=None):
    from pathlib import Path
    from .frozen_physical_source import frozen_physical_source
    from .native_calibration_worker import _write
    from .native_evidence import load
    from .native_pipeline_worker import run_job
    from .recognition_metrics import load_physical_model_data_evaluation
    output = Path(output).resolve()
    require(not output.exists(), 'frozen_study_fresh_output_required')
    source_root = Path(declaration['source_manifest']).resolve(strict=True).parent
    require(not output.is_relative_to(source_root) and not source_root.is_relative_to(output),
            'frozen_study_output_overlaps_original_source')
    runtime_path = Path(runtime_path).resolve(strict=True)
    runtime_before = file_record(runtime_path)
    runtime = load(runtime_path)
    with frozen_physical_source(declaration) as source:
        job, design = declare_job(source['job'], run_id, **study)
        require(len(job['trials']) == expected_trials and
                design['protocol_id'] == protocol_id, 'frozen_study_declared_design_changed')
        binding = bind_condition(job,design,runtime,threshold=declaration['threshold'])
        output.mkdir()
        _write(output/'job.json',job)
        _write(output/'design.json',design)
        _write(output/'condition.json',binding)
        run = run_job('physical-model-evaluate',output/'job.json',source['model_path'],
            runtime_path,output/'run',maximum_wall_seconds,process_policy=process_policy,
            job_source_transport=job_source_transport)
        require(run['execution'] == 'completed' and run['validity'] == 'valid', 'frozen_study_native_run_incomplete')
        metrics = run['analysis']['metrics']
        require(run['analysis']['frozen_model_verified'] and
                metrics['validity'] == 'valid' and metrics['data_only'] and
                metrics['model_revision'] == declaration['model_revision'] and
                metrics['effective_threshold'] == declaration['threshold'] and
                len(metrics['trials']) == expected_trials, 'frozen_study_frozen_model_or_complete_design_changed')
        _, observations = load_physical_model_data_evaluation(output/'run/native/evaluation.json')
        by_id = {o['trial_id']:o for o in observations}
        ordered = [by_id[t['trial_id']] for t in job['trials']]
        require(len(ordered) == len(by_id) == expected_trials, 'frozen_study_observation_set_changed')
        last = ordered[-1]
        quiet = number(last['end'])-number(last['stimulus_times'][-1])
        require(quiet > 2 or equal(quiet,2), 'frozen_study_final_quiet_tail_incomplete')
        rows = []
        for index, observation in enumerate(ordered):
            # The scorer has already checked every complete sample window,
            # event count and the absence of gaps between consecutive windows.
            rows.append(dict(trial_id=observation['trial_id'],sample_id=observation['sample_id'],
                reset_policy=observation['reset_policy'],stimulus_times=observation['stimulus_times'],
                spike_times=observation['spike_times'],
                events_before_current_first_input=[t for t in observation['spike_times']
                    if after(observation['stimulus_times'][0],t)],
                first_input_interval_from_previous=None if index == 0 else
                    observation['stimulus_times'][0]-ordered[index-1]['stimulus_times'][0]))
        terminal = dict(kind=result_kind,schema_version=1,
            execution='completed',validity='valid',protocol_id=protocol_id,
            model_revision=declaration['model_revision'],threshold=declaration['threshold'],design=design,
            condition_fingerprint=binding['condition_fingerprint'],counts=metrics['pooled_counts'],
            trials=metrics['trials'],actual_timing_and_events=rows,final_quiet_tail_seconds=quiet,
            frozen_model_verified=run['analysis']['frozen_model_verified'],
            complete_contiguous_observations_verified=True,threshold_selected=False,
            training_performed=False,source_training_certificate_inferred=False,
            carryover_events_not_causally_assigned_to_a_single_pattern=True,
            scientific_verdict=None)
    require(file_record(runtime_path) == runtime_before, 'frozen_study_runtime_changed')
    _write(output/'terminal.json',terminal)
    return terminal
