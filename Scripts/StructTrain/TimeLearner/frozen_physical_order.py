"""All target positions for an audited physical DATA model, without retuning.

The complete eight-trial source run is the measured rotation-zero control.
The native production pipeline evaluates the other seven rotations. This is
reset-per-trial order robustness on the same matrix, never held-out accuracy,
continuous-stream/ITI robustness, or evidence of training convergence.
"""
import argparse
from collections import Counter
import json
import math
import os
from pathlib import Path
import sys


def _write(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def run(controls):
    controls = Path(controls).resolve(strict=True)
    declaration = json.loads((controls/'declaration.json').read_bytes())
    sys.path.insert(0, declaration['actor'])
    sys.dont_write_bytecode = True
    from Scripts.StructTrain.TimeLearner.native_evidence import require
    from Scripts.StructTrain.TimeLearner.runtime import file_record
    from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256 as sha
    from Scripts.StructTrain.TimeLearner.native_pipeline_worker import audit_run_manifest, run_job, validate_job
    from Scripts.StructTrain.TimeLearner.recognition_metrics import load_physical_model_data_evaluation
    from Scripts.StructTrain.TimeLearner.frozen_diagnostic_order import rotated_trials
    from Scripts.StructTrain.TimeLearner.trial_response_comparison import trial_response_comparison
    from Scripts.StructTrain.TimeLearner.contained_process import inspect

    require(declaration['kind'] == 'timelearner_frozen_physical_order_declaration' and
            declaration['schema_version'] == 1 and declaration['reset_policy'] == 'reset_per_trial' and
            declaration['baseline_sample_absolute_tolerance'] == 1e-12,
            'physical_order_declaration_scope')
    require(file_record(Path(__file__))['sha256'] == declaration['worker_sha256'],
            'physical_order_worker_changed')
    controller = inspect(controls/'outer-process/contained')
    require(controller['execution'] == 'running' and
            controller['binding']['initial_main_pid'] == os.getpid(),
            'physical_order_requires_owned_controller')
    source = Path(declaration['source_manifest']).resolve(strict=True)
    before = file_record(source)
    require(before['sha256'] == declaration['source_manifest_sha256'], 'physical_order_source_changed')
    audited = audit_run_manifest(source)
    baseline = json.loads(source.read_bytes())
    require(audited['run_evidence_consistent'] and baseline['operation'] == 'physical-model-evaluate' and
            baseline['execution'] == 'completed' and baseline['validity'] == 'valid',
            'physical_order_requires_complete_audited_DATA_run')
    comparison_path = Path(declaration['source_comparison']).resolve(strict=True)
    comparison_before = file_record(comparison_path)
    comparison_result = json.loads(comparison_path.read_bytes())
    require(comparison_before['sha256'] == declaration['source_comparison_sha256'] and
            comparison_result['all_eight_waveforms_and_events_preserved'],
            'physical_order_source_roundtrip_not_confirmed')
    job_path = source.parent/'input/job.json'
    source_job_before = file_record(job_path)
    original = json.loads(job_path.read_bytes())
    require(original['kind'] == 'timelearner_native_physical_model_evaluation_job' and
            original['coverage_policy'] == 'per_trial_windows', 'physical_order_source_job_scope')
    model_path = source.parent/'input/source/model.json'
    # The canonical source filename is recorded by the production manifest;
    # discover it from the job model hash, rather than using a template graph.
    if not model_path.exists():
        candidates = list((source.parent/'input/source').glob('*.json'))
        require(len(candidates) == 1, 'physical_order_source_model_ambiguous')
        model_path = candidates[0]
    model_before = file_record(model_path)
    model = json.loads(model_path.read_bytes())
    require(model == original['source_model_data'] and
            model['model_revision'] == declaration['model_revision'], 'physical_order_model_changed')
    metrics = baseline['analysis']['metrics']
    require(metrics['data_only'] and metrics['validity'] == 'valid' and
            metrics['model_revision'] == model['model_revision'] and
            metrics['effective_threshold'] == declaration['threshold'] and
            comparison_result['model_revision'] == model['model_revision'] and
            comparison_result['source_model_data_sha256'] == model['sha256'] and
            comparison_result['counts'] == metrics['pooled_counts'], 'physical_order_source_metrics_changed')
    patterns = original['trials']
    require(len(patterns) == 8 and len(metrics['trials']) == 8 and
            declaration['rotations'] == list(range(1, 8)), 'physical_order_requires_all_eight_positions')
    control_spec, control_observations = load_physical_model_data_evaluation(source.parent/'native/evaluation.json')
    require(control_spec['model_revision'] == model['model_revision'] and len(control_observations) == 8,
            'physical_order_control_observations_changed')
    by_sample = {o['sample_id']: o for o in control_observations}
    require(len(by_sample) == 8, 'physical_order_control_samples_not_unique')
    job = {k: v for k, v in original.items() if k != 'sha256'}
    job['run_id'] = declaration['run_id']
    job['trials'] = rotated_trials(patterns, job['run_id'], declaration['rotations'])
    frequency = model['configuration']['model']['frequency_hz']
    job['maximum_model_ticks'] = sum(math.ceil(t['duration']*frequency)+4 for t in job['trials'])
    job['sha256'] = sha(job)
    validate_job('physical-model-evaluate', job, (model,))
    require(3600 <= declaration['maximum_native_wall_seconds'] <= 28800 and
            declaration['native_memory_bytes'] == 2*1024**3, 'physical_order_finite_native_budget')
    output = Path(declaration['output']).absolute()
    require(not output.exists(), 'physical_order_fresh_output_required')
    output.mkdir()
    _write(output/'job.json', job)
    _write(output/'design.json', dict(kind='timelearner_frozen_physical_order_design', schema_version=1,
        source_manifest=before, source_job=source_job_before, source_model=model_before,
        source_comparison=comparison_before, model_revision=model['model_revision'],
        source_model_data_sha256=model['sha256'], threshold=declaration['threshold'],
        rotations=[0]+declaration['rotations'], source_control_trials=8, new_trials=56,
        reset_policy='reset_per_trial', training_performed=False, threshold_selected=False,
        independently_heldout_evaluation=False, continuous_stream_verified=False,
        inter_pattern_interval_varied=False, scientific_verdict=None))
    policy=dict(kind='timelearner_native_process_policy',schema_version=1,backend='bound_cgroup',
        memory_bytes=declaration['native_memory_bytes'],tasks=128,cooperative_capture=True)
    result = run_job('physical-model-evaluate', output/'job.json', model_path,
                     controls/'runtime.json', output/'run', declaration['maximum_native_wall_seconds'],
                     process_policy=policy)
    require(result['execution'] == 'completed' and result['validity'] == 'valid',
            'physical_order_native_run_incomplete')
    study = result['analysis']['metrics']
    require(study['data_only'] and study['model_revision'] == metrics['model_revision'] and
            study['effective_threshold'] == metrics['effective_threshold'] and len(study['trials']) == 56,
            'physical_order_frozen_model_threshold_or_coverage_changed')
    _, observations = load_physical_model_data_evaluation(output/'run/native/evaluation.json')
    observed_by_id = {o['trial_id']: o for o in observations}
    require(len(observed_by_id) == 56, 'physical_order_observation_set_changed')
    rows=[]
    baseline_metrics = {t['sample_id']: t for t in metrics['trials']}
    with trial_response_comparison(model, physical_data=True) as compare:
        for measured in study['trials']:
            observation = observed_by_id[measured['trial_id']]
            expected = by_sample[observation['sample_id']]
            response_comparison = compare(expected, observation)
            rows.append(dict(trial_id=measured['trial_id'],sample_id=measured['sample_id'],
                rotation=declaration['rotations'][measured['presentation_index']//8],
                target_position=next(i for i,t in enumerate(job['trials'][measured['presentation_index']//8*8:][:8])
                                     if t['label']=='target'),
                position=measured['presentation_index']%8,classification=measured['classification'],
                source_classification=baseline_metrics[measured['sample_id']]['classification'],
                classification_preserved=measured['classification']==baseline_metrics[measured['sample_id']]['classification'],
                waveforms_equal_within_declared_tolerance=response_comparison['waveforms_equal_within_declared_tolerance'],
                maximum_absolute_sample_difference=response_comparison['maximum_absolute_sample_difference'],
                waveform_difference_reason=next(iter(response_comparison['difference_reasons']), None),
                stimulus_and_spike_events_equal=response_comparison['stimulus_and_spike_events_equal'],
                response_comparison=response_comparison))
    positions={next(i for i,t in enumerate(patterns) if t['label']=='target')}
    positions.update(row['target_position'] for row in rows if row['classification'] in ('TP','FN'))
    require(positions == set(range(8)), 'physical_order_target_positions_incomplete')
    by_rotation=[dict(rotation=r,counts=dict(Counter(row['classification'] for row in rows if row['rotation']==r)))
                 for r in declaration['rotations']]
    require(file_record(source)==before and file_record(job_path)==source_job_before and
            file_record(model_path)==model_before and file_record(comparison_path)==comparison_before,
            'physical_order_source_mutated')
    _write(output/'terminal.json', dict(kind='timelearner_frozen_physical_order_result',schema_version=1,
        execution='completed',validity='valid',model_revision=model['model_revision'],
        threshold=metrics['effective_threshold'],source_control_counts=metrics['pooled_counts'],
        new_study_counts=study['pooled_counts'],by_rotation=by_rotation,rows=rows,
        all_eight_target_positions_observed=True,source_control_trials=8,new_study_trials=56,
        classifications_preserved=all(r['classification_preserved'] for r in rows),
        waveforms_and_events_preserved=all(r['waveforms_equal_within_declared_tolerance'] and
                                         r['stimulus_and_spike_events_equal'] for r in rows),
        training_completed=False,independently_heldout_evaluation=False,
        continuous_stream_verified=False,inter_pattern_interval_varied=False,scientific_verdict=None))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--controls',required=True)
    args=parser.parse_args()
    run(args.controls)


if __name__=='__main__':
    main()
