"""Independent production evidence audit after a prepared native job closes.

The small executor deliberately does not claim this audit. Run this separately
with sufficient finite memory: every source/model/history check is retained.
Portable evidence consistency is distinct from runtime attestation or convergence.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import traceback


def audit(controls):
    controls = Path(controls).resolve(strict=True)
    spec = json.loads((controls/'specification.json').read_bytes())
    sys.path.insert(0, spec['python_source'])
    sys.dont_write_bytecode = True
    from Scripts.StructTrain.TimeLearner.native_evidence import require
    from Scripts.StructTrain.TimeLearner.runtime import file_record
    from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256 as sha
    from Scripts.StructTrain.TimeLearner.stopped_evidence import load_case
    from Scripts.StructTrain.TimeLearner.native_pipeline_worker import audit_execution

    worker_path = controls/'worker.py'
    require(file_record(worker_path)['sha256'] == spec['worker_sha256'], 'prepared_audit_worker_changed')
    module_spec = importlib.util.spec_from_file_location('prepared_inventory', worker_path)
    worker = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(worker)
    inputs = Path(spec['inputs']).resolve(strict=True)
    require(worker.inventory(inputs, file_record) == spec['input_inventory'], 'prepared_audit_input_changed')
    output = Path(spec['output']).resolve(strict=True)
    terminal = json.loads((output/'terminal.json').read_bytes())
    process = json.loads((output/'process-result.json').read_bytes())
    require(terminal['native_process_completed'] and process['execution'] == 'completed' and
            process['all_processes_closed'] and process['runtime_provenance'] == 'loaded_files_captured',
            'prepared_audit_process_incomplete')
    envelope = json.loads((inputs/'native-job-source.json').read_bytes())
    require(envelope['sha256'] == sha({k:v for k,v in envelope.items() if k != 'sha256'}) and
            envelope['source']['field'] == 'source_stopped' and
            envelope['source']['path'] in spec['input_inventory'], 'prepared_audit_envelope_changed')
    source_case = load_case(inputs/envelope['source']['path'])
    require(source_case[0]['sha256'] == envelope['source']['package_sha256'] == spec['source_package_sha256']
            and source_case[0]['model_revision'] == spec['source_model_revision'], 'prepared_audit_source_changed')
    job = {**envelope['job'], 'source_stopped':source_case[0]}
    require(job['sha256'] == spec['resolved_job_sha256'] == sha({k:v for k,v in job.items() if k != 'sha256'}),
            'prepared_audit_resolved_job_changed')
    result = audit_execution('diagnostic-evaluate', output/'native', job, source_case)
    require(result.get('frozen_model_verified') is True and result.get('diagnostic_only') is True and
            result['metrics']['validity'] == 'valid' and len(result['metrics']['trials']) == 8,
            'prepared_audit_native_evidence_invalid')
    require(worker.inventory(inputs, file_record) == spec['input_inventory'], 'prepared_audit_input_changed_after')
    metrics = result['metrics']
    counts = metrics['pooled_counts']
    return dict(kind='timelearner_prepared_diagnostic_independent_audit', schema_version=1,
        controls=str(controls), output=str(output), source_package_sha256=source_case[0]['sha256'],
        source_model_revision=spec['source_model_revision'], resolved_job_sha256=job['sha256'],
        native_evidence=result, complete_source_history_audited=True, all_input_bytes_unchanged=True,
        report_family_response_requirement_met=counts['TP'] >= 1 and counts['TN'] >= 2,
        protocol='historical_same_matrix' if job['schema_version'] == 2 else 'fixed_threshold_baseline',
        process_result_sha256=file_record(output/'process-result.json')['sha256'],
        training_completed=False, independently_heldout_evaluation=False,
        native_execution_attested_by_this_portable_audit=False, scientific_verdict=None)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--controls', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise ValueError('prepared_audit_fresh_output_required')
    try:
        result = audit(args.controls)
    except BaseException as error:
        result = dict(kind='timelearner_prepared_diagnostic_independent_audit_failure', schema_version=1,
                      reason=str(error), traceback=traceback.format_exc(), scientific_verdict=None)
        with output.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(result, stream, indent=2, allow_nan=False)
            stream.write('\n')
        raise
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps(dict(audited=True, protocol=result['protocol'],
        counts=result['native_evidence']['metrics']['pooled_counts'],
        report_family_response_requirement_met=result['report_family_response_requirement_met'],
        training_completed=False, scientific_verdict=None)))


if __name__ == '__main__':
    main()
