"""A predeclared new-foil ISI grid on fixed DATA, with a repeated target control.

This is deterministic foil sensitivity under reset-per-trial. Exact-pattern
labels and every excluded calibration pattern are declared before execution.
No training, threshold selection, new positive class, or convergence is inferred.
"""
import argparse
from copy import deepcopy
from itertools import product
import math
import os
from pathlib import Path

from .condition import ConditionSpec, artifact
from .frozen_physical_source import frozen_physical_source
from .model_identity import canonical_model_sha256 as sha
from .native_calibration_worker import _write
from .native_evidence import equal, load, number, require
from .native_pipeline_worker import run_job, validate_job
from .runtime import file_record, runtime_content_identity
from .trial_response_comparison import compare_trial_responses

PROTOCOL = 'frozen_new_foil_isi_grid_half_steps_v1'


def declare_trials(source_job, run_id):
    """Multiply the three non-onset ISIs by (1/2, 1, 3/2), on native ticks."""
    require(type(run_id) is str and bool(run_id), 'foil_grid_run_identity')
    originals = source_job['trials']; model = source_job['source_model_data']
    targets = [t for t in originals if t['label'] == 'target']
    require(len(originals) == 8 and len(targets) == 1 and
            all(t['label'] in ('target','foil') and t['pattern_hash'] == sha(t['pattern_isi'])
                for t in originals), 'foil_grid_source_matrix_invalid')
    target = targets[0]; pattern = target['pattern_isi']
    require(pattern == model['configuration']['model']['initial_isi'] and len(pattern) == 4,
            'foil_grid_requires_original_four_pulse_target')
    frequency = number(model['configuration']['model']['frequency_hz'])
    require(frequency > 0 and all(number(t) > 0 for t in pattern), 'foil_grid_invalid_native_clock_or_isi')
    ticks = [round(number(t)*frequency) for t in pattern]
    require(all(equal(t*frequency,n) for t,n in zip(pattern,ticks)) and
            all(n > 0 and n % 2 == 0 for n in ticks[1:]), 'foil_grid_requires_exact_half_tick_intervals')
    require(target['reset_policy'] == 'reset_per_trial' and target['record_threshold_potential'] is True,
            'foil_grid_requires_full_recorded_reset_trials')
    excluded = {t['pattern_hash'] for t in originals}
    trials, skipped, scale_rows = [], [], []
    for numerators in product((1,2,3),repeat=3):
        control = numerators == (2,2,2)
        values = list(pattern) if control else [pattern[0]]+[
            (n*k//2)/frequency for n,k in zip(ticks[1:],numerators)]
        fingerprint = sha(values)
        require(sum(values) < number(target['duration']), 'foil_grid_stimulus_outside_observation')
        if not control and fingerprint in excluded:
            skipped.append(dict(numerators=list(numerators),pattern_hash=fingerprint));continue
        sample = target['sample_id'] if control else 'unseen-isi-grid-v1-'+'-'.join(map(str,numerators))
        trial = dict(target,run_id=run_id,trial_id=run_id+'/grid-'+'-'.join(map(str,numerators)),
                     sample_id=sample,label='target' if control else 'foil',pattern_isi=values,
                     pattern_hash=fingerprint)
        trials.append(trial);scale_rows.append(dict(sample_id=sample,numerators=list(numerators),denominator=2))
    require(sum(t['label']=='target' for t in trials) == 1 and len(trials) >= 2 and
            len({t['pattern_hash'] for t in trials}) == len(trials), 'foil_grid_missing_or_duplicate_conditions')
    return trials,dict(protocol_id=PROTOCOL,scale_numerators=[1,2,3],scale_denominator=2,
        varied_isi_indices=[1,2,3],fixed_onset_isi=pattern[0],excluded_calibration_hashes=sorted(excluded),
        skipped_previously_used_conditions=skipped,scale_rows=scale_rows,
        target_position=next(i for i,t in enumerate(trials) if t['label']=='target'),
        new_foil_trials=len(trials)-1,target_control_trials=1,
        label_rule='exact_original_target_hash_is_target; all_new_grid_hashes_are_foil',
        interpretation='new_foil_sensitivity; no_new_positive_class_or_stochastic_replicates')


def declare_job(original, run_id, *, holdout_protocol=None):
    job=deepcopy(original);job.pop('sha256');job['run_id']=run_id
    if holdout_protocol is None:
        job['trials'],design=declare_trials(original,run_id)
    else:
        from .frozen_duration_holdout import declare_trials as heldout_trials
        job['trials'],design=heldout_trials(original,run_id,holdout_protocol)
    frequency=original['source_model_data']['configuration']['model']['frequency_hz']
    job['maximum_model_ticks']=sum(math.ceil(t['duration']*frequency)+4 for t in job['trials'])
    job['sha256']=sha(job)
    validate_job('physical-model-evaluate',job,(original['source_model_data'],))
    return job,design


def condition(job, design, runtime, declaration, *, _trial_index=None):
    """Use the production serializer; paths and attempt IDs do not enter it."""
    model = job['source_model_data']; config = model['configuration']
    from .frozen_duration_holdout import PROTOCOL as HOLDOUT_PROTOCOL
    heldout = design['protocol_id'] == HOLDOUT_PROTOCOL
    require(design['protocol_id'] in (PROTOCOL, HOLDOUT_PROTOCOL), 'foil_condition_protocol')
    require(_trial_index is None or heldout and type(_trial_index) is int and
            0 <= _trial_index < len(job['trials']), 'foil_condition_trial_scope')
    selected = job['trials'] if _trial_index is None else [job['trials'][_trial_index]]
    trials = [{k:v for k,v in t.items() if k not in ('run_id','trial_id')} for t in selected]
    presentation = dict(design=design, reset_policy='reset_per_trial')
    ticks = job['maximum_model_ticks']
    if _trial_index is not None:
        # A reset-per-trial case is identified by its own input/window, frozen
        # model and runtime. Other holdout members or their sampling provenance
        # belong to the matrix, not to this case's scientific identity.
        presentation = dict(reset_policy='reset_per_trial', protocol_id=HOLDOUT_PROTOCOL,
            matched_total_interval_ticks=design['matched_total_interval_ticks'],
            label_rule=design['label_rule'], time_frame='relative_to_trial_onset')
        ticks = math.ceil(selected[0]['duration']*config['model']['frequency_hz'])+4
    payloads=dict(
        algorithm=dict(protocol_id=design['protocol_id'],implementation_id=job['implementation_id'],
                       native_runtime_content=runtime_content_identity(runtime)),
        model_spec=config['model'],
        storage_profiles=dict(effective_graph_sha256=model['model_revision'],
                              neuron_class=config['model']['neuron_class']),
        initial_state=dict(frozen_recognition_graph=model['model_revision'],dynamic_checkpoint=False),
        training_plan=dict(performed=False),input_data=dict(trials=trials),
        presentation_protocol=presentation,
        calibration_spec=dict(performed=False,fixed_threshold=declaration['threshold'],
                              selected_on_previous_eight_pattern_matrix=True),
        evaluation_spec=dict(criterion=job['criterion'],coverage_policy=job['coverage_policy'],
                             new_positive_class_assessed=False),
        execution_policy=dict(maximum_model_ticks=ticks,
            native_memory_bytes=declaration['native_memory_bytes'],
            native_wall_seconds=declaration['maximum_native_wall_seconds']),
        randomness_spec=dict(random_factors=[],independent_stochastic_repetitions=False))
    artifacts={role:artifact(role,payload) for role,payload in payloads.items()}
    spec=ConditionSpec(controller_version=2,amplitude_goal='captured_per_input',
                       **{role:item['sha256'] for role,item in artifacts.items()})
    require(ConditionSpec.loads(spec.dumps()) == spec, 'foil_grid_condition_roundtrip')
    result = dict(condition=spec.to_object(),condition_fingerprint=spec.fingerprint,
                  artifacts={item['sha256']:item for item in artifacts.values()},
                  descriptor_integrity_only=True,scientific_verdict=None)
    if heldout and _trial_index is None:
        result['condition_scope'] = 'matrix'
        result['case_conditions'] = {t['sample_id']:condition(job,design,runtime,declaration,_trial_index=i)
                                     for i,t in enumerate(job['trials'])}
    return result


def run(controls):
    from .contained_process import inspect
    controls=Path(controls).resolve(strict=True);declaration_record=file_record(controls/'declaration.json')
    d=load(controls/'declaration.json')
    fields={'kind','schema_version','base','actor','name','inputs','output','source_original','source_export',
            'sdk_source','source_manifest','source_manifest_sha256','source_comparison','source_comparison_sha256',
            'model_revision','threshold','worker_root','worker_sha256','protocol_id','run_id','reset_policy',
            'native_memory_bytes','maximum_native_wall_seconds','maximum_outer_wall_seconds','outer_memory_bytes',
            'minimum_free_bytes','maximum_output_bytes','prepared_job_sha256','prepared_design_sha256',
            'condition_fingerprint'}
    from .frozen_duration_holdout import PROTOCOL as HOLDOUT_PROTOCOL
    version = d.get('schema_version') if type(d) is dict else None
    require(type(version) is int and version in (1,2), 'foil_study_declaration_schema')
    expected = fields if version == 1 else fields | {'protocol_document'}
    require(type(d) is dict and set(d)==expected and
            d['kind']=='timelearner_frozen_new_foil_declaration' and
            d['protocol_id']==(PROTOCOL if version==1 else HOLDOUT_PROTOCOL) and d['reset_policy']=='reset_per_trial' and
            d['native_memory_bytes']==2*1024**3 and d['maximum_native_wall_seconds']==7200,
            'foil_study_declaration_scope')
    require(version == 1 or type(d['protocol_document']) is dict, 'foil_study_holdout_protocol_required')
    require(file_record(Path(__file__))['sha256']==d['worker_sha256'], 'foil_study_worker_changed')
    owner=inspect(controls/'outer-process/contained')
    require(owner['execution']=='running' and owner['binding']['initial_main_pid']==os.getpid(),
            'foil_study_requires_owned_controller')
    runtime=load(controls/'runtime.json');runtime_before=file_record(controls/'runtime.json')
    base=Path(d['base']).resolve(strict=True);output=Path(d['output']).absolute()
    require(base in {Path('/home/user/timelearner-refactor'),Path('/media/user/Data/TimeLearnerRefactor')} and
            controls.is_relative_to(base/'requests') and output.is_relative_to(base/'readbacks') and
            not output.exists(),'foil_study_fresh_output_required');output.mkdir()
    with frozen_physical_source(d) as source:
        job,design=declare_job(source['job'],d['run_id'],holdout_protocol=d.get('protocol_document'))
        require(design['protocol_id']==d['protocol_id'] and
                job['sha256']==d['prepared_job_sha256'] and sha(design)==d['prepared_design_sha256'],
                'foil_study_predeclared_matrix_changed')
        _write(output/'job.json',job)
        _write(output/'design.json',dict(kind='timelearner_frozen_new_foil_design',schema_version=1,
            **design,source_files=source['records'],model_revision=d['model_revision'],threshold=d['threshold'],
            training_performed=False,threshold_selected=False,new_foils_excluded_from_previous_matrix=True,
            continuous_stream_verified=False,inter_pattern_interval_varied=False,scientific_verdict=None))
        binding=condition(job,design,runtime,d)
        require(binding['condition_fingerprint']==d['condition_fingerprint'],
                'foil_study_predeclared_condition_changed')
        _write(output/'condition.json',binding)
        result=run_job('physical-model-evaluate',output/'job.json',source['model_path'],controls/'runtime.json',
            output/'run',d['maximum_native_wall_seconds'],process_policy=dict(
                kind='timelearner_native_process_policy',schema_version=1,backend='bound_cgroup',
                memory_bytes=d['native_memory_bytes'],tasks=128,cooperative_capture=True))
        require(result['execution']=='completed' and result['validity']=='valid','foil_study_native_run_incomplete')
        metrics=result['analysis']['metrics']
        require(metrics['data_only'] and metrics['validity']=='valid' and
                metrics['model_revision']==d['model_revision'] and metrics['effective_threshold']==d['threshold'] and
                len(metrics['trials'])==len(job['trials']),'foil_study_frozen_model_or_coverage_changed')
        from .recognition_metrics import load_physical_model_data_evaluation
        _,observations=load_physical_model_data_evaluation(output/'run/native/evaluation.json')
        observed=next(o for o in observations if o['label']=='target')
        expected=next(o for o in source['observations'] if o['label']=='target')
        comparison=compare_trial_responses(expected,observed,source['model'],physical_data=True)
        terminal=dict(kind='timelearner_frozen_new_foil_result',schema_version=1,execution='completed',validity='valid',
            protocol_id=d['protocol_id'],model_revision=d['model_revision'],threshold=d['threshold'],
            new_foil_trials=design['new_foil_trials'],target_position=design['target_position'],
            counts=metrics['pooled_counts'],trials=metrics['trials'],target_control_comparison=comparison,
            target_control_preserved=comparison['response_preserved'],
            interpretation_control='passed' if comparison['response_preserved'] else 'changed_target_response',
            new_foils_excluded_from_previous_matrix=True,training_completed=False,
            threshold_selected_on_previous_matrix=True,new_positive_class_assessed=False,
            independent_stochastic_repetitions=False,continuous_stream_verified=False,
            inter_pattern_interval_varied=False,scientific_verdict=None)
        if version == 2:
            terminal.pop('training_completed')
            terminal.update(kind='timelearner_frozen_duration_holdout_result', training_performed=False,
                source_training_completed=None, protocol_sha256=design['protocol_sha256'],
                independence_scope=design['independence_scope'])
    require(file_record(controls/'runtime.json')==runtime_before,'foil_study_runtime_changed')
    require(file_record(controls/'declaration.json')==declaration_record,'foil_study_declaration_changed')
    _write(output/'terminal.json',terminal)


def main():
    p=argparse.ArgumentParser();p.add_argument('--controls',required=True);run(p.parse_args().controls)


if __name__=='__main__':main()
