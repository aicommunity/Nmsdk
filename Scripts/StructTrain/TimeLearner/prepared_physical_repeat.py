"""Repeat an actual frozen DATA evaluation without a diagnostic-state overlay.

The source and the repeat remain ordinary physical evaluations. Their separate
comparison proves response preservation and never manufactures a legacy replay,
training certificate or independent calibration result.
"""
import argparse
from copy import deepcopy
import json
import os
from pathlib import Path

from .native_evidence import load, require
from .runtime import file_record


BASE = Path('C:/Projects/TimeLearnerWorker')


def _write(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def _closed_evaluation(controls):
    """Read the real source graph, complete observations and process receipts."""
    from .job_source_transport import verify_envelope
    from .model_identity import canonical_model_sha256 as sha
    from .native_pipeline_worker import audit_execution, validate_job
    from .prepared_physical_evaluation import _inventory
    from .windows_stopped_recognition_study import _kernel, live

    controls = Path(controls).resolve(strict=True)
    require(os.name == 'nt' and controls.parent == BASE/'controls', 'physical_repeat_source_scope')
    spec = load(controls/'specification.json')
    require(spec['kind'] == 'timelearner_prepared_physical_evaluation' and
            spec['schema_version'] == 1, 'physical_repeat_source_kind')
    inputs, output = Path(spec['inputs']), Path(spec['output'])
    require(inputs.parent == output.parent == BASE/'jobs' and
            inputs.resolve(strict=True) == inputs and output.resolve(strict=True) == output,
            'physical_repeat_source_paths')
    require(_inventory(inputs) == spec['input_inventory'], 'physical_repeat_source_inputs_changed')
    model_path = inputs/'model.json'
    model = load(model_path)
    envelope = load(inputs/'native-job-source.json')
    job = dict(envelope['job'], source_model_data=model)
    require(job['sha256'] == spec['resolved_job_sha256'] ==
            sha({k:v for k,v in job.items() if k != 'sha256'}), 'physical_repeat_source_job_changed')
    verify_envelope(envelope, job, model_path, inputs)
    validate_job('physical-model-evaluate', job, (model,))
    process, terminal = load(output/'process-result.json'), load(output/'terminal.json')
    require(process['execution'] == 'completed' and process['all_processes_closed'] and
            process['runtime_provenance'] == 'loaded_files_captured' and
            terminal['kind'] == 'timelearner_initial_windows_physical_evaluation' and
            terminal['execution'] == 'completed' and terminal['validity'] == 'valid',
            'physical_repeat_source_execution_not_closed')
    api, kernel = _kernel()
    owners = list((output/'process').rglob('owned-process.json'))
    require(owners and all(not live(api, kernel, load(p)) for p in owners),
            'physical_repeat_source_process_live')
    audited = audit_execution('physical-model-evaluate', output/'native', job, (model,))
    metrics = audited['metrics']
    require(audited['frozen_model_verified'] and metrics['validity'] == 'valid' and
            metrics['data_only'] and len(job['trials']) == len(metrics['trials']) == 8 and
            len({t['sample_id'] for t in job['trials']}) == 8 and
            sum(t['label'] == 'target' for t in job['trials']) == 1 and
            terminal['complete_observations'] == 8 and terminal['counts'] == metrics['pooled_counts'] and
            terminal['model_revision'] == metrics['model_revision'] == model['model_revision'] and
            terminal['threshold'] == metrics['effective_threshold'], 'physical_repeat_source_audit_changed')
    paths = [controls/'specification.json', controls/'runtime.json', inputs/'native-job-source.json',
             model_path, output/'process-result.json', output/'terminal.json', output/'native/execution.json',
             *[output/'native'/f'trial-{i}.json' for i in range(8)]]
    return dict(spec=spec, model=model, model_path=model_path, job=job, metrics=metrics,
                output=output, runtime=load(controls/'runtime.json'),
                records={str(p):file_record(p) for p in paths})


def prepare(declaration):
    """Only attempt/trial identifiers may change; the original graph is copied."""
    from . import prepared_physical_evaluation as evaluation
    from .owned_python_job import _source_snapshot

    fields = {'kind', 'schema_version', 'source_controls', 'run_id', 'python_source', 'python_root'}
    require(type(declaration) is dict and set(declaration) == fields and
            declaration['kind'] == 'timelearner_physical_repeat_preparation' and
            type(declaration['schema_version']) is int and declaration['schema_version'] == 1,
            'physical_repeat_preparation_schema')
    actor = Path(declaration['python_source']).resolve(strict=True)
    require(Path(__file__).resolve(strict=True) == actor/'Scripts/StructTrain/TimeLearner/prepared_physical_repeat.py',
            'physical_repeat_actor_mismatch')
    _source_snapshot(actor, declaration['python_root'])
    source = _closed_evaluation(declaration['source_controls'])
    job = deepcopy(source['job'])
    job.pop('sha256'); job.pop('source_model_data')
    job['run_id'] = declaration['run_id']
    job['trials'] = [dict(t, run_id=job['run_id'], trial_id=job['run_id']+'/trial-'+str(i))
                     for i,t in enumerate(job['trials'])]
    plan = dict(kind='timelearner_prepared_physical_evaluation_plan', schema_version=1,
                job_id=job['run_id'], source_data=file_record(source['model_path']),
                runtime_manifest=file_record(Path(declaration['source_controls'])/'runtime.json'),
                sdk_source=source['spec']['sdk_source'], worker_origin=dict(root_commit=declaration['python_root'],
                path='Scripts/StructTrain/TimeLearner/prepared_physical_evaluation.py',
                sha256=file_record(Path(evaluation.__file__))['sha256']), job=job)
    # Let the production preparer validate all scopes before creating controls.
    name = job['run_id']
    require(type(name) is str and 1 <= len(name) <= 100 and
            all(c in 'abcdefghijklmnopqrstuvwxyz0123456789-_' for c in name), 'physical_repeat_run_id')
    plan_path = BASE/'controls'/(name+'-repeat-plan.json')
    require(not plan_path.exists(), 'physical_repeat_plan_exists')
    _write(plan_path, plan)
    controls = evaluation.prepare(plan_path)
    _write(controls/'repeat-binding.json', dict(kind='timelearner_physical_repeat_binding', schema_version=1,
        source_controls=str(Path(declaration['source_controls']).resolve(strict=True)),
        source_records=source['records'], model_revision=source['model']['model_revision'],
        threshold=source['metrics']['effective_threshold'], source_counts=source['metrics']['pooled_counts'],
        preparation=declaration, absolute_tolerance=1e-12, training_certificate_transferred=False,
        calibration_confirmed=False, scientific_verdict=None))
    return controls


def _binding(controls):
    controls = Path(controls).resolve(strict=True)
    binding = load(controls/'repeat-binding.json')
    require(set(binding) == {'kind', 'schema_version', 'source_controls', 'source_records',
            'model_revision', 'threshold', 'source_counts', 'preparation', 'absolute_tolerance',
            'training_certificate_transferred', 'calibration_confirmed', 'scientific_verdict'} and
            binding['kind'] == 'timelearner_physical_repeat_binding' and binding['schema_version'] == 1 and
            binding['absolute_tolerance'] == 1e-12, 'physical_repeat_binding_schema')
    require(all(file_record(Path(p)) == r for p,r in binding['source_records'].items()),
            'physical_repeat_original_bytes_changed')
    return binding


def verify(controls):
    """Recompute every response comparison; saved booleans alone grant nothing."""
    from .trial_response_comparison import trial_response_comparison

    controls = Path(controls).resolve(strict=True)
    binding = _binding(controls)
    source = _closed_evaluation(binding['source_controls'])
    observed = _closed_evaluation(controls)
    require(source['records'] == binding['source_records'] and source['model'] == observed['model'] and
            binding['model_revision'] == source['model']['model_revision'] and
            binding['source_counts'] == source['metrics']['pooled_counts'] and
            binding['training_certificate_transferred'] is False and binding['calibration_confirmed'] is False and
            source['metrics']['effective_threshold'] == observed['metrics']['effective_threshold'] ==
            binding['threshold'], 'physical_repeat_model_or_threshold_changed')
    normalized = lambda j: {k:([{f:v for f,v in t.items() if f not in ('run_id','trial_id')} for t in x]
                             if k == 'trials' else x) for k,x in j.items() if k not in ('sha256','run_id')}
    require(normalized(source['job']) == normalized(observed['job']), 'physical_repeat_protocol_changed')
    expected = {}
    for i in range(8):
        row = load(source['output']/'native'/f'trial-{i}.json')
        require(row['sample_id'] not in expected, 'physical_repeat_duplicate_source_sample')
        expected[row['sample_id']] = row
    rows = []
    with trial_response_comparison(source['model'], physical_data=True) as compare:
        for i in range(8):
            actual = load(observed['output']/'native'/f'trial-{i}.json')
            rows.append(compare(expected[actual['sample_id']], actual))
    result = dict(kind='timelearner_actual_windows_physical_repeat', schema_version=1,
        execution='completed', validity='valid', model_revision=source['model']['model_revision'],
        source_model_data_sha256=source['model']['sha256'], threshold=binding['threshold'],
        counts=observed['metrics']['pooled_counts'], compared_trials=8, comparisons=rows,
        all_eight_waveforms_and_events_preserved=all(r['response_preserved'] for r in rows),
        training_certificate_transferred=False, calibration_confirmed=False, scientific_verdict=None)
    require(result['all_eight_waveforms_and_events_preserved'], 'physical_repeat_response_changed')
    require(all(file_record(Path(p)) == r for context in (source, observed)
                for p,r in context['records'].items()),
            'physical_repeat_original_bytes_changed')
    return result, observed


def source_for_study(controls):
    """Accept a verified modern repeat without relabelling its source as legacy."""
    result, observed = verify(controls)
    terminal = observed['output']/'repeat-terminal.json'
    require(load(terminal) == result, 'physical_repeat_saved_comparison_changed')
    observed['records'].update({str(p):file_record(p) for p in
                               (Path(controls)/'repeat-binding.json', terminal)})
    return observed


def run(controls):
    from . import prepared_physical_evaluation as evaluation
    controls = Path(controls).resolve(strict=True)
    _binding(controls)
    before = file_record(controls/'repeat-binding.json')
    evaluation.run(controls)
    result, observed = verify(controls)
    require(file_record(controls/'repeat-binding.json') == before, 'physical_repeat_binding_changed_during_run')
    _write(observed['output']/'repeat-terminal.json', result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare', type=Path)
    mode.add_argument('--run', type=Path)
    mode.add_argument('--verify', type=Path)
    args = parser.parse_args(argv)
    if args.prepare:
        print(prepare(load(args.prepare)))
    else:
        print(json.dumps((verify(args.verify)[0] if args.verify else run(args.run)), allow_nan=False))


if __name__ == '__main__':
    main()
