"""Full Phase A diagnostics of recorded stopped models, without retraining.

Called only by the finite native DATA controller. Materialize declared embedded
primary first; the ordinary pipeline must then validate actual external files.
"""
import argparse
import html
import json
from pathlib import Path, PurePosixPath
import re

from .native_evidence import load, load_json, parse_json_bytes, require


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


def audit_matrix(directory, controller, runtime_manifest):
    """Portable DATA joins; saved closure alone never proves successful work."""
    from .native_data_checks import validate_request
    from .native_pipeline_worker import audit_run_manifest
    from .phasea_matrix import extract, trial_design
    from .recognition_metrics import load_diagnostic_evaluation
    from .collector_provenance import _frozen, frozen_digest

    directory, controller = Path(directory).resolve(strict=True), Path(controller).resolve(strict=True)
    request = validate_request(load(controller/'request.json'))
    require(request['schema_version'] == 2, 'recorded_matrix_requires_diagnostic_request')
    runtime_raw, runtime_record = _frozen(Path(runtime_manifest).resolve(strict=True), 16*1024**2)
    require(runtime_record['sha256'] == request['runtime_manifest']['sha256'],
            'recorded_matrix_pinned_runtime_changed')
    runtime = parse_json_bytes(runtime_raw)
    terminal = load(directory/'terminal.json')
    require(terminal['operation_passed'] is True and terminal['heartbeat_errors'] == [],
            'recorded_matrix_operation_not_completed')
    result = load(controller/'supervisor-result.json')
    require(result['outer_closed'] and result['reason'] is None and result['record_errors'] == [],
            'recorded_matrix_controller_not_closed')
    outer = load(controller/'outer-closure.json')
    require(outer['all_processes_closed'] and outer['binding'] == result['outer_binding'],
            'recorded_matrix_outer_binding')
    outcome = load(controller/'original-outcome.json')['kernel_before_stop']['state']
    require(outcome['ExecMainStatus'] == '0' and outcome['Result'] == 'success',
            'recorded_matrix_original_worker_failed')
    leases = load_json(controller/'reservation-final.json')
    require(type(leases) is list and len(leases) == 1 and leases[0]['state'] == 'released',
            'recorded_matrix_lease_not_released')
    for stem in ('source', 'tool'):
        require((directory/(stem+'-before.json')).read_bytes() ==
                (directory/(stem+'-after.json')).read_bytes(), 'recorded_matrix_source_changed')
    original = PurePosixPath(request['execution_root'])/'readbacks'/request['job_id']
    children = result['children_closed']
    expected = {str(original/r['name']/'process/contained') for r in request['cases']}
    require(len(children) == len(expected) and {r['directory'] for r in children} == expected,
            'recorded_matrix_foreign_or_missing_children')
    by_directory = {r['directory']: r for r in children}
    staged = directory/'native-inputs'
    for record in request['inputs']:
        path = staged/record['name']
        actual = frozen_digest(path, 64*1024**2)
        require(actual['bytes'] == record['bytes'] and actual['sha256'] == record['sha256'],
                'recorded_matrix_staged_input_changed')
    matrix = extract((staged/request['matrix']['parameters_name']).read_bytes(),
                     (staged/request['matrix']['observations_name']).read_bytes(), request['matrix']['revision'])
    rows = []
    for row in request['cases']:
        root = directory/row['name']
        child = by_directory[str(original/row['name']/'process/contained')]
        binding = load(root/'process/contained/owned-unit.json')
        require(child['binding'] == binding and child['closure']['binding'] == binding and
                child['closure']['all_processes_closed'], 'recorded_matrix_foreign_child_binding')
        audit = audit_run_manifest(root/'run-manifest.json')
        manifest = load(root/'run-manifest.json')
        require(manifest['operation'] == 'diagnostic-evaluate' and manifest['execution'] == 'completed'
                and manifest['validity'] == 'valid', 'recorded_matrix_invalid_case')
        require(manifest['runtime_fingerprint'] == runtime['runtime_fingerprint'] and
                manifest['source_closure'] == runtime['source_closure'],
                'recorded_matrix_case_runtime_substitution')
        source = root/'input/source/train_stopped_state.json'
        actual = frozen_digest(source, 256*1024**2)
        require(actual['bytes'] == row['source_raw_bytes'] and actual['sha256'] == row['source_raw_sha256'],
                'recorded_matrix_source_substitution')
        job = load(root/'input/job.json');package = job['source_stopped'];model = package['configuration']['model']
        run_id = row['name']+'/stopped-phasea-diagnostic'
        require(job['trials'] == trial_design(matrix, model['initial_isi'], run_id, duration=2., rotations=1),
                'recorded_matrix_wrong_pattern_design')
        spec, observations = load_diagnostic_evaluation(root/'native/evaluation.json')
        require(len(observations) == len(spec['trials']) == 8 and
                all(o['complete'] for o in observations), 'recorded_matrix_incomplete_observations')
        metrics = manifest['analysis']['metrics']
        require(metrics['diagnostic_only'] is True and metrics['training_completed'] is False and
                metrics['training_certificate_present'] is False and metrics['evaluation_verdict'] is None,
                'recorded_matrix_false_training_or_scientific_verdict')
        rows.append(dict(name=row['name'], source_model_revision=package['model_revision'],
            training_outcome=package['training_outcome'], topology='Branch' if model['branch'] else 'Classic',
            source_threshold=package['neuron']['metadata']['calibration']['threshold'],
            trial_count=len(observations), metrics=metrics, run_audit=audit))
    return dict(kind='timelearner_recorded_n4_matrix_analysis', schema_version=1,
        original_job_id=request['job_id'], models=rows, trials=8*len(rows), diagnostic_only=True,
        training_completed=False, native_execution_attested=False, scientific_verdict=None)


def report_matrix(directory, controller, runtime_manifest, output):
    """Reuse the production renderer for every trial/soma; never change models."""
    from .live_pipeline_reports import render_pipeline_run
    directory, controller = Path(directory).resolve(strict=True), Path(controller).resolve(strict=True)
    output = Path(output).resolve()
    require(not output.exists() and all(not output.is_relative_to(p) and not p.is_relative_to(output)
            for p in (directory, controller)), 'recorded_matrix_report_overlaps_primary')
    analysis = audit_matrix(directory, controller, runtime_manifest)
    output.mkdir(parents=True)
    reports = []
    for row in analysis['models']:
        value = render_pipeline_run(directory/row['name']/'run-manifest.json', output/row['name'])
        reports.append(dict(name=row['name'], report=value))
    manifest = dict(analysis=analysis, reports=reports, visual_acceptance_complete=False,
                    scientific_verdict=None)
    (output/'manifest.json').write_text(json.dumps(manifest, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    links = ''.join('<li><a href="'+html.escape(r['name'])+'/index.html">'+html.escape(r['name'])+'</a></li>'
                    for r in reports)
    (output/'index.html').write_text('<!doctype html><meta charset="utf-8"><h1>Recorded N4 diagnostic responses</h1>'
        '<p>Stopped models; inherited fixed thresholds. All eight patterns per model, actual input overlays. '
        'No training convergence, threshold selection or independent scientific verdict.</p><ul>'+links+'</ul>', encoding='utf-8')
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('audit', 'report'))
    parser.add_argument('directory', type=Path);parser.add_argument('controller', type=Path)
    parser.add_argument('runtime_manifest', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    if args.action == 'audit':result = audit_matrix(args.directory, args.controller, args.runtime_manifest)
    else:
        require(args.output is not None, 'recorded_matrix_report_output_required')
        result = report_matrix(args.directory, args.controller, args.runtime_manifest, args.output)
    print(json.dumps(result, allow_nan=False));return 0


if __name__ == '__main__':
    raise SystemExit(main())
