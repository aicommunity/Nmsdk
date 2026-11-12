"""Full Phase A diagnostics of recorded stopped models, without retraining.

Called only by the finite native DATA controller. Materialize declared embedded
primary first; the ordinary pipeline must then validate actual external files.
"""
from pathlib import Path
import re

from .native_evidence import load, parse_json_bytes, require


SHA = re.compile('[0-9a-f]{64}')
COMMIT = re.compile('[0-9a-f]{40}')
CASE_FIELDS = {'name', 'source_name', 'summary_name', 'source_raw_bytes', 'source_raw_sha256'}


def validate_declaration(request):
    require(request['operation'] == 'diagnostic-evaluate', 'native_data_diagnostic_operation')
    matrix = request['matrix']
    require(type(matrix) is dict and set(matrix) == {'parameters_name', 'observations_name', 'revision'}
            and type(matrix['revision']) is str and COMMIT.fullmatch(matrix['revision']),
            'native_data_diagnostic_matrix')
    names = {r['name'] for r in request['inputs']}
    used = [matrix['parameters_name'], matrix['observations_name']]
    require(all(type(n) is str and n in names for n in used), 'native_data_diagnostic_matrix_input')
    cases = request['cases']
    require(type(cases) is list and 1 <= len(cases) <= 2 and all(type(r) is dict and
            set(r) == CASE_FIELDS for r in cases), 'native_data_diagnostic_cases')
    for row in cases:
        require(type(row['source_raw_bytes']) is int and 0 < row['source_raw_bytes'] <= 256*1024**2
                and type(row['source_raw_sha256']) is str and SHA.fullmatch(row['source_raw_sha256']),
                'native_data_diagnostic_raw_binding')
        used += [row['source_name'], row['summary_name']]
    require(all(type(n) is str and n in names for n in used) and len(used) == len(set(used))
            and set(used) == names, 'native_data_diagnostic_input_roles')


def run_case(request, row, runtime_path, output):
    from .candidate_window_package_evidence import audit_candidate_window_recovery_package
    from .composite_primary import capture_primary_blobs, write_primary_snapshot, filesystem_primary_resolver
    from .native_pipeline_worker import run_job
    from .phasea_matrix import extract
    from .qt_json import read_qcompress_bytes
    from .stock_stopped_evaluation import job_for
    from .n1_protocol_robustness import _write

    output = Path(output);staged = output/'native-inputs';matrix_spec = request['matrix']
    matrix = extract((staged/matrix_spec['parameters_name']).read_bytes(),
                     (staged/matrix_spec['observations_name']).read_bytes(), matrix_spec['revision'])
    raw = read_qcompress_bytes(staged/row['source_name'], expected_bytes=row['source_raw_bytes'],
                              expected_sha256=row['source_raw_sha256'])
    package = parse_json_bytes(raw);summary_raw = (staged/row['summary_name']).read_bytes()
    summary = parse_json_bytes(summary_raw)
    require(type(package) is dict and package.get('schema_version') == 7 and
            package.get('kind') == 'timelearner_stopped_state' and package.get('certificate') is None,
            'recorded_diagnostic_requires_actual_stopped7')
    source_audit = audit_candidate_window_recovery_package(package, summary)
    require(len(package['configuration']['model']['inputs']) == 4,
            'recorded_diagnostic_requires_n4')
    source = output/(row['name']+'-source')
    archive = package['measurement_archive']
    references = [trial['primary_ref'] for group in archive['records'] for trial in group['raw_trials']]
    primary = capture_primary_blobs(archive['primary_blobs'], references, archive['maximum_total_primary_bytes'])
    write_primary_snapshot(primary, source)
    del primary
    state_path = source/'train_stopped_state.json'
    with state_path.open('xb') as stream:stream.write(raw)
    with (source/'train_stopped_summary.json').open('xb') as stream:stream.write(summary_raw)
    del raw, summary_raw
    # Embedded bytes have now become declared external source files. Future
    # audits must check those files, never silently replace a damaged mirror.
    audit_candidate_window_recovery_package(package, summary,
        external_resolver=filesystem_primary_resolver(source))
    model = package['configuration']['model']
    descriptor = dict(name=row['name'], model_revision=package['model_revision'],
        topology='Branch' if model['branch'] else 'Classic', initial_threshold=model['initial_threshold'])
    job = job_for(descriptor, package, matrix)
    require(len(job['trials']) == 8 and all(t['reset_policy'] == 'reset_per_trial' for t in job['trials']),
            'recorded_diagnostic_complete_matrix_required')
    job_path = output/(row['name']+'-diagnostic-job.json');_write(job_path, job)
    _write(output/(row['name']+'-matrix.json'), matrix)
    _write(output/(row['name']+'-source-audit.json'), source_audit)
    policy = dict(kind='timelearner_native_process_policy', schema_version=1, backend='bound_cgroup',
        memory_bytes=request['limits']['leaf_memory_bytes'], tasks=request['limits']['leaf_tasks'],
        cooperative_capture=True)
    result = run_job('diagnostic-evaluate', job_path, state_path, runtime_path, output/row['name'],
                     request['limits']['leaf_wall_seconds'], process_policy=policy)
    require(result['execution'] == 'completed' and result['validity'] == 'valid',
            'recorded_diagnostic_execution_incomplete')
    metrics = result['analysis']['metrics']
    require(metrics['diagnostic_only'] is True and metrics['training_completed'] is False and
            metrics['training_certificate_present'] is False and metrics['evaluation_verdict'] is None,
            'recorded_diagnostic_false_training_verdict')
    return result
