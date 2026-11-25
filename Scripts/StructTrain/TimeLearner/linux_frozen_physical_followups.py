"""Repeat and probe an actual completed Linux DATA recognition sequence.

Each native phase uses the production runner, whole-group ownership and exact
observations. A failed predecessor is retained without retry or substitution.
No training or threshold selection takes place in this continuation.
"""
import argparse
from copy import deepcopy
import datetime
import json
import os
from pathlib import Path
import socket
import sys
import time
import traceback

from .native_evidence import load, require
from .runtime import file_record
from .linux_physical_recognition_sequence import BASES, GIB, write

SOURCE = Path(__file__).resolve().parents[3]
MODULE = 'Scripts.StructTrain.TimeLearner.linux_frozen_physical_followups'
PHASES = ('repeat', 'third-pulse', 'new-foils')
FIELDS = {'kind', 'schema_version', 'job_id', 'worker_host', 'execution_root', 'tool_commit',
          'source_recognition_request', 'source_recognition_owner', 'native_wall_seconds', 'validation_request'}


def validate_request(q):
    from .owned_native_job import _validate_identity
    require(type(q) is dict and set(q) == FIELDS and
            q['kind'] == 'timelearner_linux_frozen_physical_followups' and
            type(q['schema_version']) is int and q['schema_version'] == 1,
            'linux_frozen_followups_request_schema')
    require(type(q['job_id']) is str and 1 <= len(q['job_id']) <= 60 and
            all(c in 'abcdefghijklmnopqrstuvwxyz0123456789-_' for c in q['job_id']) and
            type(q['tool_commit']) is str and len(q['tool_commit']) == 40 and
            all(c in '0123456789abcdef' for c in q['tool_commit']), 'linux_frozen_followups_identity')
    require(type(q['native_wall_seconds']) is dict and set(q['native_wall_seconds']) == set(PHASES) and
            all(type(v) is int and 0 < v <= 36000 for v in q['native_wall_seconds'].values()),
            'linux_frozen_followups_wall_budgets')
    _validate_identity(q['source_recognition_owner'])
    for key in ('source_recognition_request', 'validation_request'):
        r = q[key]
        require(type(r) is dict and set(r) == {'path', 'sha256', 'size'} and
                type(r['path']) is str and Path(r['path']).is_absolute() and
                type(r['size']) is int and r['size'] > 0 and type(r['sha256']) is str and
                len(r['sha256']) == 64 and all(c in '0123456789abcdef' for c in r['sha256']),
                'linux_frozen_followups_source_request_record:'+key)
    return q


def context(request):
    from .linux_physical_recognition_sequence import context as recognition_context
    request = Path(request).resolve(strict=True); q = validate_request(load(request))
    base = Path(q['execution_root'])
    require(sys.platform == 'linux' and base in BASES and base.resolve(strict=True) == base and
            SOURCE.is_relative_to(base) and q['worker_host'] == socket.gethostname(),
            'linux_frozen_followups_worker_scope')
    controls = base/'requests'/q['job_id']; output = base/'readbacks'/q['job_id']
    require(request == controls/'request.json' and controls.resolve(strict=True) == controls,
            'linux_frozen_followups_controls_scope')
    source_path = Path(q['source_recognition_request']['path'])
    require(source_path.is_relative_to(base/'requests') and source_path.resolve(strict=True) == source_path and
            file_record(source_path) == q['source_recognition_request'], 'linux_frozen_followups_source_changed')
    source = recognition_context(source_path)
    require(source['base'] == base and source['controls'] != controls and source['output'] != output,
            'linux_frozen_followups_source_overlap')
    from .owned_python_job import validate_request as validation_request
    validation_path = Path(q['validation_request']['path'])
    require(validation_path == controls/'scope-gate/request.json' and
            validation_path.resolve(strict=True) == validation_path and
            file_record(validation_path) == q['validation_request'], 'linux_frozen_followups_validation_binding')
    gate = validation_request(load(validation_path)); operation = gate['operation']
    require(gate['tool_commit'] == q['tool_commit'] and gate['execution_root'] == str(base) and
            gate['worker_host'] == q['worker_host'] and gate['job_id'] == q['job_id']+'-scope-gate' and
            operation['kind'] == 'python-validation' and operation['source'] ==
            dict(path=str(SOURCE), commit=q['tool_commit']) and
            set(operation['fixtures']) == {'TIMELEARNER_LINUX_DATA_SEQUENCE_FIXTURE'},
            'linux_frozen_followups_validation_scope')
    suite_path = Path(operation['suite']['path'])
    require(suite_path == controls/'scope-gate/suite.json' and
            file_record(suite_path)['sha256'] == operation['suite']['sha256'],
            'linux_frozen_followups_validation_suite_binding')
    suite = load(suite_path)
    require(suite['modules'] == ['Scripts.StructTrain.TimeLearner.tests.test_actual_linux_DATA_recognition_job',
            'Scripts.StructTrain.TimeLearner.tests.test_actual_linux_frozen_followup_jobs'],
            'linux_frozen_followups_required_validation_modules')
    return dict(q=q, base=base, controls=controls, output=output, request=request, gate=gate,
                request_record=file_record(request), source=source)


def guard(p):
    require(file_record(p['request']) == p['request_record'] and
            file_record(p['source']['request']) == p['q']['source_recognition_request'] and
            file_record(Path(p['q']['validation_request']['path'])) == p['q']['validation_request'] and
            not (p['controls']/'cancel.request').exists(),
            'linux_frozen_followups_bound_request_changed')
    from .linux_physical_recognition_sequence import guard as source_guard
    source_guard(p['source'])


def confirmed_source(p):
    from .contained_process import inspect
    from .owned_native_job import _same_process
    from .native_pipeline_worker import audit_run_manifest, validate_job
    s = p['source']; expected_owner = p['q']['source_recognition_owner']
    require(load(s['controls']/'owner.json') == expected_owner and not _same_process(expected_owner) and
            not (s['controls']/'exception.json').exists(), 'linux_frozen_followups_source_owner_not_closed')
    terminal = load(s['output']/'terminal.json')
    require(terminal['execution'] == 'completed' and terminal['validity'] == 'valid' and
            terminal['new_Train'] is False, 'linux_frozen_followups_source_sequence_incomplete')
    no_candidate = terminal.get('result') == 'no_representable_same_matrix_threshold_candidate'
    for phase in (('conversion', 'baseline') if no_candidate else ('conversion', 'baseline', 'threshold', 'confirmation')):
        d = s['output']/phase
        require(load(d/'terminal.json')['validity'] == 'valid' and
                inspect(d/'process/contained')['all_processes_closed'] and
                inspect(s['base']/'readbacks'/(s['q']['job_id']+'-'+phase)/'process/contained')['all_processes_closed'],
                'linux_frozen_followups_source_group_not_closed:'+phase)
    if no_candidate:
        return dict(no_candidate=True, terminal=terminal)
    require(terminal['protocol'] == 'historical_same_matrix' and terminal['independent_evaluation'] is False,
            'linux_frozen_followups_source_calibration_protocol')
    run = s['base']/'readbacks'/(s['q']['job_id']+'-confirmation')
    manifest = run/'run-manifest.json'
    require(audit_run_manifest(manifest)['run_evidence_consistent'], 'linux_frozen_followups_source_manifest')
    result = load(manifest); job = load(run/'input/job.json')
    model_path = run/result['source_package_path']; model = load(model_path)
    validate_job('physical-model-evaluate', job, (model,))
    metrics = result['analysis']['metrics']
    require(result['operation'] == 'physical-model-evaluate' and result['execution'] == 'completed' and
            result['validity'] == 'valid' and result['analysis']['frozen_model_verified'] and
            result['runtime_fingerprint'] == load(s['runtime'])['runtime_fingerprint'] and
            job['source_model_data'] == model and len(job['trials']) == len(metrics['trials']) == 8 and
            metrics['validity'] == 'valid' and metrics['data_only'] and
            len({t['sample_id'] for t in job['trials']}) == 8 and
            sum(t['label'] == 'target' for t in job['trials']) == 1 and
            all(t['reset_policy'] == 'reset_per_trial' and t['record_threshold_potential'] is True for t in job['trials']) and
            metrics['pooled_counts'] == terminal['actual_evaluation']['counts'] and
            metrics['model_revision'] == model['model_revision'] == terminal['actual_evaluation']['model_revision'] and
            metrics['effective_threshold'] == model['threshold'], 'linux_frozen_followups_source_frozen_eight')
    paths = [s['controls']/'owner.json', s['output']/'terminal.json', s['output']/'actual-source-binding.json',
             manifest, run/'input/job.json', model_path, *[run/'native'/f'trial-{i}.json' for i in range(8)]]
    return dict(no_candidate=False, terminal=terminal, run=run, job=job, model=model, model_path=model_path,
                metrics=metrics, records={str(f):file_record(f) for f in paths})


def declared_job(original, run_id, phase):
    from .model_identity import canonical_model_sha256 as sha
    from .native_pipeline_worker import validate_job
    if phase == 'third-pulse':
        from .frozen_third_pulse_study import declare_job
        return declare_job(original, run_id)
    if phase == 'new-foils':
        from .frozen_physical_foil_study import declare_job
        return declare_job(original, run_id)
    require(phase == 'repeat', 'linux_frozen_followups_unknown_phase')
    job = deepcopy(original); job.pop('sha256'); job['run_id'] = run_id
    job['trials'] = [dict(t, run_id=run_id, trial_id=run_id+'/trial-'+str(i)) for i,t in enumerate(job['trials'])]
    job['sha256'] = sha(job)
    validate_job('physical-model-evaluate', job, (original['source_model_data'],))
    return job, dict(protocol_id='fresh_frozen_eight_response_repeat_v1', reset_policy='reset_per_trial',
        compared_trials=8, absolute_tolerance=1e-12, training_performed=False, calibration_performed=False)


def condition(job, design, runtime, wall_seconds, *, index=None):
    from .condition import ConditionSpec, artifact
    from .runtime import runtime_content_identity
    import math
    selected = job['trials'] if index is None else [job['trials'][index]]
    model = job['source_model_data']; frequency = model['configuration']['model']['frequency_hz']
    trials = [{k:v for k,v in t.items() if k not in ('run_id', 'trial_id')} for t in selected]
    presentation = design if index is None else dict(protocol_id=design['protocol_id'],
        reset_policy='reset_per_trial', time_frame='relative_to_actual_first_input')
    payloads = dict(algorithm=dict(operation='physical-model-evaluate', implementation_id=job['implementation_id'],
        native_runtime_content=runtime_content_identity(runtime)), model_spec=model['configuration']['model'],
        storage_profiles=dict(effective_graph_sha256=model['model_revision']),
        initial_state=dict(frozen_recognition_graph=model['model_revision'], dynamic_checkpoint=False),
        training_plan=dict(performed=False), input_data=dict(trials=trials), presentation_protocol=presentation,
        calibration_spec=dict(performed=False, fixed_threshold=model['threshold'],
                              selected_on_previous_eight_pattern_matrix=True),
        evaluation_spec=dict(criterion=job['criterion'], coverage_policy=job['coverage_policy'],
                             new_positive_class_assessed=False),
        execution_policy=dict(maximum_model_ticks=sum(math.ceil(t['duration']*frequency)+4 for t in selected),
                              native_memory_bytes=8*GIB, native_wall_seconds=wall_seconds),
        randomness_spec=dict(random_factors=[], independent_stochastic_repetitions=False))
    artifacts = {k:artifact(k,v) for k,v in payloads.items()}
    spec = ConditionSpec(controller_version=2, amplitude_goal='captured_per_input',
                         **{k:v['sha256'] for k,v in artifacts.items()})
    require(ConditionSpec.loads(spec.dumps()) == spec, 'linux_frozen_followups_condition_roundtrip')
    spec.resolve({v['sha256']:v for v in artifacts.values()})
    result = dict(condition=spec.to_object(), condition_fingerprint=spec.fingerprint,
                  artifacts={v['sha256']:v for v in artifacts.values()},
                  descriptor_integrity_only=True, scientific_verdict=None)
    if index is None:
        result.update(condition_scope='matrix', case_conditions={t['sample_id']:condition(
            job, design, runtime, wall_seconds, index=i) for i,t in enumerate(job['trials'])})
    return result


def phase_worker(request, phase):
    from .contained_process import inspect
    from .owned_python_job import _source_snapshot
    from .resource_reservations import Reservations
    from .native_process_policy import validate_policy
    from .native_pipeline_worker import run_job, audit_run_manifest
    from .job_source_transport import TRANSPORT
    from .trial_response_comparison import trial_response_comparison
    from .trial_response_timing import summarize_trial_timing
    p = context(request); q = p['q']; guard(p); _source_snapshot(SOURCE, q['tool_commit'])
    directory = p['output']/phase; output = p['base']/'readbacks'/(q['job_id']+'-'+phase)
    state = inspect(directory/'process/contained')
    require(not state['all_processes_closed'] and state['binding']['initial_main_pid'] == os.getpid(),
            'linux_frozen_followups_worker_not_bound_main')
    source = confirmed_source(p); require(not source['no_candidate'], 'linux_frozen_followups_no_threshold_candidate')
    if phase != 'repeat':
        repeat = load(p['output']/'repeat/terminal.json')
        require(repeat['execution'] == 'completed' and repeat['validity'] == 'valid' and
                repeat['all_eight_waveforms_and_events_preserved'] and
                repeat['model_revision'] == source['model']['model_revision'], 'linux_frozen_followups_repeat_not_verified')
    runtime = load(p['source']['runtime']); wall = q['native_wall_seconds'][phase]
    registry = Reservations.open_existing(p['base']/'resource-reservations.sqlite3')
    lease = registry.reserve(q['job_id']+'-'+phase,
        [dict(path=str(v), access=a) for v,a in [(SOURCE,'read'),(p['source']['sdk'],'read'),
         (p['controls'],'read'),(p['output'],'write'),(output,'write'),(source['run'],'read'),
         (Path(runtime['executable']['path']).parent,'read')]], ttl_seconds=wall+600,
        demands=dict(slots=1, memory_bytes=12*GIB, disk_bytes=2*GIB))
    write(directory/'reservation.json', lease)
    job, design = declared_job(source['job'], q['job_id']+'-'+phase, phase)
    binding = condition(job, design, runtime, wall)
    write(directory/'job.json', job); write(directory/'design.json', design); write(directory/'condition.json', binding)
    write(directory/'source-records.json', source['records'])
    policy = validate_policy(dict(kind='timelearner_native_process_policy', schema_version=1,
        backend='bound_cgroup', memory_bytes=8*GIB, tasks=64, cooperative_capture=True))
    result = run_job('physical-model-evaluate', directory/'job.json', source['model_path'],
        p['source']['runtime'], output, wall, process_policy=policy, job_source_transport=TRANSPORT)
    require(result['execution'] == 'completed' and result['validity'] == 'valid' and
            result['analysis']['frozen_model_verified'] and
            audit_run_manifest(output/'run-manifest.json')['run_evidence_consistent'],
            'linux_frozen_followups_complete_native_evaluation_required')
    metrics = result['analysis']['metrics']; expected_count = len(job['trials'])
    require(metrics['validity'] == 'valid' and metrics['data_only'] and len(metrics['trials']) == expected_count and
            metrics['model_revision'] == source['model']['model_revision'] and
            metrics['effective_threshold'] == source['model']['threshold'], 'linux_frozen_followups_metrics_changed')
    observations = [load(output/'native'/f'trial-{i}.json') for i in range(expected_count)]
    require(all(o['complete'] and o['valid'] and not o['censored'] and len(o['samples']) == 4001
                for o in observations), 'linux_frozen_followups_incomplete_observation_window')
    prior = {t['sample_id']:load(source['run']/'native'/f'trial-{i}.json') for i,t in enumerate(source['job']['trials'])}
    comparisons = []
    with trial_response_comparison(source['model'], physical_data=True) as compare:
        for row in observations:
            if row['sample_id'] in prior:
                comparisons.append(compare(prior[row['sample_id']], row))
    require(len(comparisons) == (8 if phase == 'repeat' else 1) and
            all(r['response_preserved'] for r in comparisons), 'linux_frozen_followups_actual_control_changed')
    write(directory/'response-comparisons.json', comparisons)
    write(directory/'timing.json', summarize_trial_timing(job, observations, metrics))
    require(all(file_record(Path(f)) == r for f,r in source['records'].items()),
            'linux_frozen_followups_original_source_bytes_changed')
    guard(p); _source_snapshot(SOURCE, q['tool_commit'])
    write(directory/'terminal.json', dict(kind='timelearner_linux_frozen_physical_followup', schema_version=1,
        phase=phase, execution='completed', validity='valid', counts=metrics['pooled_counts'],
        complete_observations=expected_count, model_revision=source['model']['model_revision'],
        source_model_data_sha256=source['model']['sha256'], threshold=source['model']['threshold'],
        condition_fingerprint=binding['condition_fingerprint'], frozen_model_verified=True,
        compared_source_controls=len(comparisons), all_eight_waveforms_and_events_preserved=phase == 'repeat',
        source_training_outcome=source['terminal']['actual_source']['source_training_outcome'],
        source_completed_boundary=source['terminal']['actual_source']['completed_boundary'],
        training_performed=False, threshold_selected=False, independent_positive_class=False,
        training_certificate_transferred=False, scientific_verdict=None))


def supervise(request):
    from .owned_native_job import _identity, _same_process, _run_owned
    from .owned_python_job import _source_snapshot
    from .resource_reservations import Reservations
    from .runtime import resolved_libraries, runtime_content_identity, digest_json
    from .linux_physical_recognition_sequence import wait_capacity
    p = context(request); q = p['q']; root = p['output']; root.mkdir()
    write(p['controls']/'owner.json', _identity()); _source_snapshot(SOURCE, q['tool_commit'])
    registry = Reservations.open_existing(p['base']/'resource-reservations.sqlite3'); begun = time.monotonic()
    try:
        while True:
            guard(p)
            require(time.monotonic()-begun < 118000 and not (p['controls']/'cancel.request').exists(),
                    'linux_frozen_followups_predecessor_wait_budget_or_cancel')
            require(load(p['source']['controls']/'owner.json') == q['source_recognition_owner'] and
                    not (p['source']['controls']/'exception.json').exists(), 'linux_frozen_followups_predecessor_failed')
            live = _same_process(q['source_recognition_owner'])
            if not live and (p['source']['output']/'terminal.json').is_file():
                break
            pending = p['controls']/'waiting.pending'
            pending.write_text(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                predecessor_live=live, exact_owner=q['source_recognition_owner'],
                waiting_for='actual_complete_original_eight_and_threshold_confirmation', native_started=False))+'\n')
            os.replace(pending, p['controls']/'waiting.json'); time.sleep(30)
        source = confirmed_source(p)
        if source['no_candidate']:
            write(root/'terminal.json', dict(execution='completed', validity='valid',
                source_no_threshold_candidate=True, native_followups_not_run=True,
                original_negative_result_retained=True, training_performed=False, threshold_selected=False,
                scientific_verdict=None))
            return
        write(root/'actual-source.json', dict(model_revision=source['model']['model_revision'],
            threshold=source['model']['threshold'], records=source['records'],
            actual_training=source['terminal']['actual_source'], scientific_verdict=None))
        del source
        # Numerical work keeps priority. The contained preparation checks wait
        # for the exact predecessor and run before any new native calculation.
        from .owned_python_job import run as run_validation
        from .contained_process import inspect
        wait_capacity(p, registry, begun, 'scope-gate', check_guard=guard)
        require(run_validation(Path(q['validation_request']['path'])) == 0,
                'linux_frozen_followups_scope_gate_failed_no_native_start')
        gate_output = p['base']/'readbacks'/p['gate']['job_id']
        checked = load(gate_output/'worker/validation/result.json')
        require(checked['assertion_status'] == 'passed' and
                checked['executed_tests'] == len(checked['expected_test_ids']) and
                not checked['failures'] and not checked['errors'] and not checked['skipped'] and
                inspect(gate_output/'process/contained')['all_processes_closed'],
                'linux_frozen_followups_complete_scope_gate_required')
        write(root/'scope-gate-accepted.json', dict(result=file_record(gate_output/'worker/validation/result.json'),
            executed_tests=checked['executed_tests'], skipped=0, all_processes_closed=True,
            metadata_only=True, native_response_preservation_not_yet_proven=True))
        results = {}
        for phase in PHASES:
            wait_capacity(p, registry, begun, phase, check_guard=guard)
            directory = root/phase; directory.mkdir()
            runtime = dict(schema_version=2, source_closure=dict(kind='frozen_physical_followups_controller', tool_root=q['tool_commit']),
                executable=file_record(Path(sys.executable)), app_ini=p['request_record'], compiler=file_record(Path(sys.executable)),
                resolved_libraries=resolved_libraries(Path(sys.executable)), loaded_process_files=None,
                loader_environment={}, build_flags=dict(role=phase, tool_root=q['tool_commit']))
            runtime['runtime_identity'] = runtime_content_identity(runtime)
            runtime['runtime_fingerprint'] = digest_json(runtime['runtime_identity']); write(directory/'runtime.json', runtime)
            child = p['base']/'readbacks'/(q['job_id']+'-'+phase)/'process/contained'
            code = _run_owned(runtime, ['-B','-m',MODULE,'--worker',str(p['request']),phase], SOURCE,
                directory, directory, [child], registry, q['job_id']+'-'+phase,
                dict(memory_bytes=4*GIB, tasks=128, maximum_wall_seconds=q['native_wall_seconds'][phase]+400),
                dict(minimum_free_bytes=4*GIB, maximum_increment_bytes=2*GIB), [root, child.parents[1]],
                control_guard=lambda:guard(p))
            require(code == 0, 'linux_frozen_followups_phase_failed_preserved:'+phase)
            results[phase] = load(directory/'terminal.json')
        guard(p); _source_snapshot(SOURCE, q['tool_commit'])
        write(root/'terminal.json', dict(execution='completed', validity='valid', phases=results,
            training_performed=False, threshold_selected=False, independent_positive_class=False,
            full_primary_archival_pending=True, all_pattern_temporal_report_pending=True, scientific_verdict=None))
    except BaseException as error:
        write(p['controls']/'exception.json', dict(reason=str(error), traceback=traceback.format_exc(),
            automatic_native_retry=False, new_Train=False, scientific_verdict=None))
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__); group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--supervise', type=Path); group.add_argument('--worker', nargs=2)
    args = parser.parse_args()
    if args.worker:
        require(args.worker[1] in PHASES, 'linux_frozen_followups_unknown_phase')
        phase_worker(Path(args.worker[0]), args.worker[1])
    else:
        supervise(args.supervise)


if __name__ == '__main__':
    main()
