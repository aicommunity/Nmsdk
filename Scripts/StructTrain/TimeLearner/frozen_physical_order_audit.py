"""Versioned post-analysis of a closed DATA order study; no native rerun.

Original manifests, observations and the original terminal receipt stay intact.
The production native audit/scorer establish execution and classification;
trial_response_comparison establishes stimulus-relative response differences.
"""
import argparse
from collections import Counter
import json
from pathlib import Path

from .contained_process import inspect
from .frozen_diagnostic_order import rotated_trials
from .native_evidence import load, require
from .native_pipeline_worker import audit_run_manifest
from .recognition_metrics import load_physical_model_data_evaluation
from .runtime import file_record
from .trial_response_comparison import trial_response_comparison


def audit_closed_order(controls, output):
    controls = Path(controls).resolve(strict=True)
    output = Path(output).absolute()
    require(not output.exists(), 'order_reanalysis_fresh_output_required')
    declaration_path = controls/'declaration.json'
    declaration = load(declaration_path)
    require(declaration['kind'] == 'timelearner_frozen_physical_order_declaration' and
            declaration['schema_version'] == 1 and declaration['reset_policy'] == 'reset_per_trial' and
            declaration['rotations'] == list(range(1, 8)) and
            declaration['baseline_sample_absolute_tolerance'] == 1e-12,
            'order_reanalysis_declaration_scope')
    root = Path(declaration['output']).resolve(strict=True)
    source_path = Path(declaration['source_manifest']).resolve(strict=True)
    comparison_path = Path(declaration['source_comparison']).resolve(strict=True)
    study_path = root/'run/run-manifest.json'
    paths = [declaration_path, source_path, comparison_path, study_path, root/'terminal.json',
             root/'job.json', source_path.parent/'input/job.json', controls/'outer-result.json',
             root/'run/process/result.json']
    # Full manifests bind all their primary files. Also retain independent
    # before/after hashes of every response being compared, not just a CSV.
    paths += sorted((source_path.parent/'native').glob('trial-*.json'))
    paths += sorted((root/'run/native').glob('trial-*.json'))
    records = {str(p): file_record(p) for p in paths}
    require(records[str(source_path)]['sha256'] == declaration['source_manifest_sha256'] and
            records[str(comparison_path)]['sha256'] == declaration['source_comparison_sha256'],
            'order_reanalysis_source_binding_changed')
    for process in (controls/'outer-process/contained', root/'run/process/contained'):
        require(inspect(process)['all_processes_closed'], 'order_reanalysis_process_still_live_or_unknown')
    for process_result in (controls/'outer-result.json', root/'run/process/result.json'):
        process = load(process_result)
        require(process['execution'] == 'completed' and process['all_processes_closed'] and
                process['runtime_provenance'] == 'loaded_files_captured',
                'order_reanalysis_execution_not_confirmed')
    for manifest_path in (source_path, study_path):
        audited = audit_run_manifest(manifest_path)
        manifest = load(manifest_path)
        require(audited['run_evidence_consistent'] and manifest['operation'] == 'physical-model-evaluate' and
                manifest['execution'] == 'completed' and manifest['validity'] == 'valid',
                'order_reanalysis_production_audit_failed')
    baseline = load(source_path); study = load(study_path)
    source_job = load(source_path.parent/'input/job.json'); job = load(root/'job.json')
    model = source_job['source_model_data']
    old_terminal = load(root/'terminal.json'); source_roundtrip = load(comparison_path)
    require(old_terminal['execution'] == 'completed' and old_terminal['validity'] == 'valid' and
            source_roundtrip['all_eight_waveforms_and_events_preserved'] and
            source_roundtrip['source_model_data_sha256'] == model['sha256'],
            'order_reanalysis_requires_audited_source_roundtrip')
    metrics = baseline['analysis']['metrics']; measured = study['analysis']['metrics']
    for item in (metrics, measured):
        require(item['validity'] == 'valid' and item['data_only'] and
                item['model_revision'] == model['model_revision'] == declaration['model_revision'] and
                item['effective_threshold'] == declaration['threshold'],
                'order_reanalysis_frozen_condition_changed')
    require(len(source_job['trials']) == len(metrics['trials']) == 8 and
            len(job['trials']) == len(measured['trials']) == 56 and
            job['trials'] == rotated_trials(source_job['trials'], job['run_id'], declaration['rotations']) and
            job['source_model_data'] == model and job['criterion'] == source_job['criterion'] and
            job['coverage_policy'] == source_job['coverage_policy'],
            'order_reanalysis_trial_protocol_changed')
    _, source_observations = load_physical_model_data_evaluation(source_path.parent/'native/evaluation.json')
    _, study_observations = load_physical_model_data_evaluation(root/'run/native/evaluation.json')
    by_sample = {o['sample_id']: o for o in source_observations}
    by_trial = {o['trial_id']: o for o in study_observations}
    require(len(by_sample) == 8 and len(by_trial) == 56, 'order_reanalysis_observation_set_changed')
    classifications = {t['sample_id']: t['classification'] for t in metrics['trials']}
    rows = []
    with trial_response_comparison(model, physical_data=True) as compare:
        for item in measured['trials']:
            observation = by_trial[item['trial_id']]
            expected = by_sample[observation['sample_id']]
            response = compare(expected, observation)
            index = item['presentation_index']
            rotation = declaration['rotations'][index//8]
            block = job['trials'][index//8*8:][:8]
            rows.append(dict(trial_id=item['trial_id'], sample_id=item['sample_id'],
                rotation=rotation, position=index%8,
                target_position=next(i for i,t in enumerate(block) if t['label']=='target'),
                classification=item['classification'], source_classification=classifications[item['sample_id']],
                classification_preserved=item['classification'] == classifications[item['sample_id']],
                response_comparison=response))
    positions = {next(i for i,t in enumerate(source_job['trials']) if t['label']=='target')}
    positions.update(r['target_position'] for r in rows if r['classification'] in ('TP', 'FN'))
    require(positions == set(range(8)) and {str(p): file_record(p) for p in paths} == records,
            'order_reanalysis_incomplete_positions_or_input_mutation')
    result = dict(kind='timelearner_closed_physical_order_reanalysis', schema_version=1,
        comparator_version=1, time_basis='actual_stimulus_onset', absolute_tolerance=1e-12,
        execution='completed', validity='valid', native_rerun_performed=False,
        source_control_trials=8, new_study_trials=56, rows=rows,
        source_control_counts=metrics['pooled_counts'], new_study_counts=measured['pooled_counts'],
        by_rotation=[dict(rotation=r, counts=dict(Counter(t['classification'] for t in rows if t['rotation']==r)))
                     for r in declaration['rotations']],
        model_revision=model['model_revision'], source_model_data_sha256=model['sha256'],
        threshold=declaration['threshold'], all_eight_target_positions_observed=True,
        classifications_preserved=all(r['classification_preserved'] for r in rows),
        waveforms_and_events_preserved=all(r['response_comparison']['response_preserved'] for r in rows),
        original_terminal=records[str(root/'terminal.json')],
        original_absolute_clock_comparison_result=old_terminal['waveforms_and_events_preserved'],
        input_records=list(records.values()), all_input_bytes_unchanged=True,
        training_completed=False, independently_heldout_evaluation=False,
        continuous_stream_verified=False, inter_pattern_interval_varied=False, scientific_verdict=None)
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--controls', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    args = p.parse_args()
    audit_closed_order(args.controls, args.output)


if __name__ == '__main__':
    main()
