"""Run a declared Same-Matrix DATA check after an exact Linux Train audit.

This controller never restarts Train or copies a template learned model.
Native imports, evaluation, threshold proposal and primary audits use the
maintained production modules. Every phase has a separately bounded owner.
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import shutil
import socket
import sys
import time
import traceback

from .native_evidence import load, require
from .runtime import file_record


SOURCE = Path(__file__).resolve().parents[3]
MODULE = 'Scripts.StructTrain.TimeLearner.linux_physical_recognition_sequence'
GIB = 1024**3
BASES = (Path('/home/user/timelearner-refactor'), Path('/media/user/Data/TimeLearnerRefactor'))
PHASES = ('conversion', 'baseline', 'threshold', 'confirmation')
FIELDS = {'kind', 'schema_version', 'job_id', 'worker_host', 'execution_root', 'tool_commit',
          'source_training_request', 'source_audit_controls', 'source_audit_owner',
          'source_audit_output', 'expected_job_sha256', 'protocol_root_commit', 'patterns'}


def write(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def context(request_path):
    from .model_identity import canonical_model_sha256 as sha
    request_path = Path(request_path).resolve(strict=True)
    q = load(request_path)
    require(sys.platform == 'linux' and type(q) is dict and set(q) == FIELDS and
            q['kind'] == 'timelearner_linux_audited_DATA_recognition_sequence' and
            type(q['schema_version']) is int and q['schema_version'] == 1,
            'linux_DATA_sequence_request_schema')
    base = Path(q['execution_root']); name = q['job_id']
    require(base in BASES and base.resolve(strict=True) == base and SOURCE.is_relative_to(base) and
            q['worker_host'] == socket.gethostname() and type(name) is str and 1 <= len(name) <= 75 and
            all(c in 'abcdefghijklmnopqrstuvwxyz0123456789-_' for c in name),
            'linux_DATA_sequence_worker_scope')
    controls = base/'requests'/name
    require(request_path == controls/'request.json' and controls.resolve(strict=True) == controls,
            'linux_DATA_sequence_controls_scope')
    original = Path(q['source_training_request']['path'])
    require(original.is_relative_to(base/'requests') and original.resolve(strict=True) == original and
            file_record(original) == q['source_training_request'], 'linux_DATA_sequence_training_request')
    training = load(original)
    require(training['operation'] == 'train' and training['execution_root'] == str(base) and
            training['sdk_source'] != str(SOURCE), 'linux_DATA_sequence_native_training_scope')
    runtime = Path(training['runtime']['path'])
    require(runtime.resolve(strict=True) == runtime and runtime.is_relative_to(base) and
            file_record(runtime) == training['runtime'], 'linux_DATA_sequence_runtime_binding')
    for key, area in [('source_audit_controls', 'requests'), ('source_audit_output', 'readbacks')]:
        p = Path(q[key])
        require(p.parent == base/area and p.resolve(strict=True) == p,
                'linux_DATA_sequence_audit_path:'+key)
    patterns = q['patterns']
    require(type(patterns) is list and len(patterns) == 8 and
            len({r['sample_id'] for r in patterns}) == len({r['pattern_hash'] for r in patterns}) == 8 and
            sum(r['label'] == 'target' for r in patterns) == 1,
            'linux_DATA_sequence_original_eight_required')
    for row in patterns:
        require(set(row) == {'sample_id', 'label', 'pattern_hash', 'pattern_isi'} and
                row['label'] in ('target', 'foil') and type(row['sample_id']) is str and row['sample_id'] and
                type(row['pattern_isi']) is list and len(row['pattern_isi']) == 4 and
                row['pattern_isi'][0] == .01 and all(type(v) in (int, float) and v > 0 for v in row['pattern_isi']) and
                row['pattern_hash'] == sha(row['pattern_isi']), 'linux_DATA_sequence_pattern_changed')
    return dict(q=q, base=base, controls=controls, output=base/'readbacks'/name,
                request=request_path, request_record=file_record(request_path), training=training,
                runtime=runtime, sdk=Path(training['sdk_source']))


def guard(p):
    require(file_record(p['request']) == p['request_record'] and
            file_record(Path(p['q']['source_training_request']['path'])) == p['q']['source_training_request'] and
            file_record(p['runtime']) == p['training']['runtime'], 'linux_DATA_sequence_bound_input_changed')


def wait_capacity(p, registry, begun, phase):
    while True:
        guard(p)
        require(time.monotonic()-begun < 118000 and not (p['controls']/'cancel.request').exists(),
                'linux_DATA_sequence_capacity_wait_budget_or_cancel')
        available = int(next(v.split()[1] for v in Path('/proc/meminfo').read_text().splitlines()
                             if v.startswith('MemAvailable:')))*1024
        if registry.inspect()['reserved']['slots'] == 0 and available >= 14*GIB and shutil.disk_usage(p['base']).free >= 6*GIB:
            return
        pending = p['controls']/'waiting.pending'
        pending.write_text(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            phase=phase, waiting_for='free_slot_and_declared_memory_disk_capacity',
            available_memory_bytes=available))+'\n')
        os.replace(pending, p['controls']/'waiting.json'); time.sleep(30)


def job_for(p, phase, model):
    from .model_identity import canonical_model_sha256 as sha
    from .physical_threshold_proposal import CRITERION
    name = p['q']['job_id']+'-'+phase
    rows = [dict(row, trial_id=name+'-'+str(i), duration=2., maximum_samples=4005,
                 reset_policy='reset_per_trial', record_threshold_potential=True)
            for i, row in enumerate(p['q']['patterns'])]
    job = dict(kind='timelearner_native_physical_model_evaluation_job', schema_version=1,
        owner_class='NNeuronTimeLearner', implementation_id=model['implementation_id'],
        maximum_model_ticks=32032, run_id=name, coverage_policy='per_trial_windows',
        criterion=CRITERION, trials=rows, source_model_data=model)
    job['sha256'] = sha(job)
    return job


def bind_condition(p, phase, job, model, directory):
    from .condition import ConditionSpec, artifact
    from .physical_threshold_proposal import RULE
    runtime = load(p['runtime'])
    payloads = dict(
        algorithm=dict(implementation_id=model['implementation_id'],
                       native_executable_sha256=runtime['executable']['sha256']),
        model_spec=dict(physical_model_revision=model['model_revision']),
        storage_profiles=dict(physical_model_document_sha256=model['sha256']),
        initial_state=dict(source_training_job_sha256=p['q']['expected_job_sha256']),
        training_plan=dict(new_training=False, original_training_job_sha256=p['q']['expected_job_sha256']),
        input_data=dict(patterns=p['q']['patterns']),
        presentation_protocol=dict(frequency_hz=2000, duration_seconds=2., reset_policy='reset_per_trial'),
        calibration_spec=dict(protocol='historical_same_matrix', rule=RULE, original_threshold=100.,
                              one_candidate=True, actual_confirmation_required=True),
        evaluation_spec=dict(criterion=job['criterion'], coverage_policy=job['coverage_policy'],
                             effective_model_revision=model['model_revision']),
        execution_policy=dict(native_memory_bytes=8*GIB, native_wall_seconds=3600, automatic_retry=False),
        randomness_spec=dict(stochastic_source_declared=False))
    artifacts = {key:artifact(key, value) for key, value in payloads.items()}
    condition = ConditionSpec(controller_version=2, amplitude_goal='captured_per_input',
                             **{key:value['sha256'] for key, value in artifacts.items()})
    condition.resolve({v['sha256']:v for v in artifacts.values()})
    require(ConditionSpec.loads(condition.dumps()) == condition, 'linux_DATA_sequence_condition_roundtrip')
    write(directory/'condition.json', dict(condition=condition.to_object(),
        fingerprint=condition.fingerprint, artifacts=artifacts,
        descriptor_integrity_only=True, scientific_verdict=None))
    return condition.fingerprint


def source_binding(p):
    q = p['q']; audit = Path(q['source_audit_output'])
    terminal = load(audit/'worker-terminal.json')
    require(terminal['execution'] == 'completed' and terminal['validity'] == 'valid' and
            terminal['source_original_unchanged'] is True, 'linux_DATA_sequence_audit_not_accepted')
    proof_path = Path(terminal['full_primary_audit']['path'])
    require(proof_path == audit/'full-primary-audit.json' and
            file_record(proof_path) == terminal['full_primary_audit'], 'linux_DATA_sequence_audit_record')
    proof = load(proof_path); projected = load(audit/'physical-projection.json')
    data = audit/'physical-model-DATA.json'
    native = p['base']/'readbacks'/p['training']['job_id']/'train/native'
    execution = load(native/'execution.json')
    require(execution['job_sha256'] == load(native/'job.json')['sha256'] == q['expected_job_sha256'] and
            execution['training_outcome'] == proof['training_outcome'] == terminal['original_training_outcome'] and
            type(execution['completed_boundary']) is bool and
            execution['completed_boundary'] == proof['completed_boundary'] == terminal['completed_boundary'] and
            execution['model_revision'] == projected['model_revision'] == proof['training_audit']['model_revision'] and
            file_record(data) == projected['output'], 'linux_DATA_sequence_actual_source_mismatch')
    compact_path = Path(terminal['compact']['path'])
    require(file_record(compact_path) == terminal['compact'], 'linux_DATA_sequence_compact_changed')
    compact = load(compact_path)
    require(compact['job_sha256'] == q['expected_job_sha256'], 'linux_DATA_sequence_compact_job_changed')
    filename = execution['package_path']
    require(type(filename) is str and Path(filename).name == filename and '/' not in filename and
            '\\' not in filename and filename in ('train_stopped_state.json', 'train_learned_state.json') and
            file_record(native/filename) == compact['source_package'], 'linux_DATA_sequence_actual_package_changed')
    return dict(kind='timelearner_actual_audited_Train_to_DATA_source_binding', schema_version=1,
        job_sha256=q['expected_job_sha256'], model_revision=execution['model_revision'],
        source_training_outcome=execution['training_outcome'], completed_boundary=execution['completed_boundary'],
        full_primary_audit=terminal['full_primary_audit'], source_DATA=file_record(data),
        source_package=compact['source_package'], original_training_unchanged=True, scientific_verdict=None)


def phase_worker(request_path, phase):
    from .contained_process import inspect
    from .owned_python_job import _source_snapshot
    from .prepared_physical_export import prepare_conversion, prepare_threshold, run as export
    from .physical_model_data_evidence import audit_physical_model_data
    p = context(request_path); q = p['q']; guard(p); _source_snapshot(SOURCE, q['tool_commit'])
    directory = p['output']/phase
    state = inspect(directory/'process/contained')
    require(not state['all_processes_closed'] and state['binding']['initial_main_pid'] == os.getpid(),
            'linux_DATA_sequence_phase_not_bound_main')
    bound = load(p['output']/'actual-source-binding.json')
    names = {v:q['job_id']+'-'+v for v in PHASES}
    outputs = {v:p['base']/'readbacks'/names[v] for v in PHASES}
    if phase in ('conversion', 'threshold'):
        data = Path(bound['source_DATA']['path']) if phase == 'conversion' else outputs['conversion']/'native/model.json'
        if phase == 'conversion':
            require(file_record(data) == bound['source_DATA'], 'linux_DATA_sequence_audited_DATA_changed_before_import')
        plan = dict(kind='timelearner_prepared_physical_'+phase+'_plan' if phase == 'conversion' else
                         'timelearner_prepared_physical_threshold_plan', schema_version=1,
            source_data=file_record(data), runtime_manifest=p['training']['runtime'],
            sdk_source=str(p['sdk']), python_source=str(SOURCE),
            controls=str(p['base']/'requests'/names[phase]),
            inputs=str(p['base']/'readbacks'/(names[phase]+'-inputs')),
            output=str(outputs[phase]), job_id=names[phase])
        if phase == 'conversion':
            plan.update(conversion_spec=dict(schema_version=1, mode='identity', resistance_bounds=[]),
                        reference_amplitudes=[])
        else:
            proposal = load(p['output']/'baseline/threshold-proposal.json')
            require(proposal['status'] == 'candidate', 'linux_DATA_sequence_no_threshold_candidate')
            plan['threshold'] = proposal['threshold']
        write(directory/'plan.json', plan)
        (prepare_conversion if phase == 'conversion' else prepare_threshold)(directory/'plan.json')
        export(Path(plan['controls']))
        result = load(outputs[phase]/'terminal.json')
        require(result['physical_roundtrip_verified'] and result['calibration_confirmed'] is False,
                'linux_DATA_sequence_native_import_incomplete')
    else:
        from .native_pipeline_worker import run_job
        from .native_process_policy import validate_policy
        from .resource_reservations import Reservations
        from .physical_threshold_proposal import propose_physical_same_matrix_threshold
        from .job_source_transport import TRANSPORT
        registry = Reservations.open_existing(p['base']/'resource-reservations.sqlite3')
        native_runtime = load(p['runtime'])
        lease = registry.reserve(names[phase], [dict(path=str(v), access=a) for v, a in
            [(SOURCE, 'read'), (p['sdk'], 'read'), (p['controls'], 'read'), (p['output'], 'write'),
             (Path(native_runtime['executable']['path']).parent, 'read'),
             (outputs['conversion'], 'read'), *([(outputs['threshold'], 'read')] if phase == 'confirmation' else []),
             (outputs[phase], 'write')]], ttl_seconds=4200,
            demands=dict(slots=1, memory_bytes=12*GIB, disk_bytes=2*GIB))
        write(directory/'reservation.json', lease)
        data = outputs['conversion' if phase == 'baseline' else 'threshold']/'native/model.json'
        before = file_record(data); model = load(data); audit_physical_model_data(model, frozen=True)
        job = job_for(p, phase, model); write(directory/'job.json', job)
        fingerprint = bind_condition(p, phase, job, model, directory)
        policy = validate_policy(dict(kind='timelearner_native_process_policy', schema_version=1,
            backend='bound_cgroup', memory_bytes=8*GIB, tasks=64, cooperative_capture=True))
        result = run_job('physical-model-evaluate', directory/'job.json', data, p['runtime'],
                         outputs[phase], 3600, process_policy=policy, job_source_transport=TRANSPORT)
        require(result['execution'] == 'completed' and result['validity'] == 'valid' and
                result['analysis']['frozen_model_verified'] and
                result['analysis']['metrics']['validity'] == 'valid' and
                len(result['analysis']['metrics']['trials']) == 8 and file_record(data) == before,
                'linux_DATA_sequence_complete_frozen_evaluation_required')
        for i in range(8):
            observation = load(outputs[phase]/'native'/('trial-'+str(i)+'.json'))
            require(observation['complete'] and observation['valid'] and not observation['censored'] and
                    len(observation['samples']) == 4001, 'linux_DATA_sequence_incomplete_window')
        if phase == 'baseline':
            proposal = propose_physical_same_matrix_threshold(outputs[phase]/'native', job, model)
            write(directory/'threshold-proposal.json', proposal)
        result = dict(execution='completed', validity='valid', counts=result['analysis']['metrics']['pooled_counts'],
                      model_revision=model['model_revision'], condition_fingerprint=fingerprint,
                      native_execution=file_record(outputs[phase]/'native/execution.json'))
    guard(p); _source_snapshot(SOURCE, q['tool_commit'])
    write(directory/'terminal.json', dict(phase=phase, execution='completed', validity='valid', result=result,
        actual_source_training_outcome=bound['source_training_outcome'], completed_boundary=bound['completed_boundary'],
        training_certificate_transferred=False, calibration_certificate_transferred=False,
        new_Train=False, scientific_verdict=None))


def supervise(request_path):
    from .owned_native_job import _identity, _same_process, _run_owned
    from .owned_python_job import _source_snapshot
    from .contained_process import inspect
    from .resource_reservations import Reservations
    from .runtime import resolved_libraries, runtime_content_identity, digest_json
    p = context(request_path); q = p['q']; root = p['output']; root.mkdir()
    write(p['controls']/'owner.json', _identity()); _source_snapshot(SOURCE, q['tool_commit'])
    registry = Reservations.open_existing(p['base']/'resource-reservations.sqlite3')
    begun = time.monotonic()
    try:
        audit_control = Path(q['source_audit_controls']); audit_output = Path(q['source_audit_output'])
        while True:
            guard(p); require(time.monotonic()-begun < 100000, 'linux_DATA_sequence_audit_wait_budget')
            require(not (p['controls']/'cancel.request').exists(), 'linux_DATA_sequence_cancelled')
            require(load(audit_control/'owner.json') == q['source_audit_owner'], 'linux_DATA_sequence_audit_owner_changed')
            live = _same_process(q['source_audit_owner'])
            require(not (audit_control/'exception.json').exists(), 'linux_DATA_sequence_original_audit_failed_no_retry')
            if not live and (audit_control/'terminal.json').is_file() and registry.inspect()['reserved']['slots'] == 0:
                require(load(audit_control/'terminal.json')['returncode'] == 0 and
                        inspect(audit_output/'process/contained')['all_processes_closed'],
                        'linux_DATA_sequence_audit_closure')
                break
            pending = p['controls']/'waiting.pending'
            pending.write_text(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                audit_owner_live=live, waiting_for='exact_full_primary_audit_DATA_and_free_slot',
                native_recognition_started=False))+'\n')
            os.replace(pending, p['controls']/'waiting.json'); time.sleep(30)
        bound = source_binding(p); write(root/'actual-source-binding.json', bound)
        results = {}
        for phase in PHASES:
            guard(p)
            if phase == 'threshold' and load(root/'baseline/threshold-proposal.json')['status'] != 'candidate':
                write(root/'terminal.json', dict(execution='completed', validity='valid',
                    result='no_representable_same_matrix_threshold_candidate', baseline=results['baseline'],
                    actual_source=bound, new_Train=False, independent_evaluation=False,
                    full_primary_archival_pending=True, all_pattern_temporal_report_pending=True, scientific_verdict=None))
                return
            wait_capacity(p, registry, begun, phase)
            directory = root/phase; directory.mkdir()
            runtime = dict(schema_version=2,
                source_closure=dict(kind='audited_DATA_recognition_sequence_controller', tool_root=q['tool_commit']),
                executable=file_record(Path(sys.executable)), app_ini=p['request_record'],
                compiler=file_record(Path(sys.executable)), resolved_libraries=resolved_libraries(Path(sys.executable)),
                loaded_process_files=None, loader_environment={}, build_flags=dict(role=phase, tool_root=q['tool_commit']))
            runtime['runtime_identity'] = runtime_content_identity(runtime)
            runtime['runtime_fingerprint'] = digest_json(runtime['runtime_identity'])
            write(directory/'runtime.json', runtime)
            child = p['base']/'readbacks'/(q['job_id']+'-'+phase)/'process/contained'
            code = _run_owned(runtime, ['-B', '-m', MODULE, '--worker', str(p['request']), phase], SOURCE,
                directory, directory, [child], registry, q['job_id']+'-'+phase,
                dict(memory_bytes=(1 if phase in ('conversion', 'threshold') else 4)*GIB,
                     tasks=128, maximum_wall_seconds=4000),
                dict(minimum_free_bytes=4*GIB, maximum_increment_bytes=2*GIB),
                [root, p['base']/'readbacks'/(q['job_id']+'-'+phase)], control_guard=lambda:guard(p))
            require(code == 0, 'linux_DATA_sequence_phase_failed_preserved:'+phase)
            results[phase] = load(directory/'terminal.json')
        actual = results['confirmation']['result']; counts = actual['counts']
        write(root/'terminal.json', dict(execution='completed', validity='valid', actual_source=bound,
            baseline=results['baseline']['result'], actual_evaluation=actual,
            threshold_proposal=file_record(root/'baseline/threshold-proposal.json'),
            working_example_criterion_met=counts['TP'] >= 1 and counts['TN'] >= 2,
            protocol='historical_same_matrix', independent_evaluation=False, new_Train=False,
            training_certificate_transferred=False, calibration_certificate_transferred=False,
            full_primary_archival_pending=True, all_pattern_temporal_report_pending=True, scientific_verdict=None))
    except BaseException as error:
        write(p['controls']/'exception.json', dict(reason=str(error), traceback=traceback.format_exc(),
              native_Train_not_restarted=True, scientific_verdict=None))
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--supervise', type=Path)
    group.add_argument('--worker', nargs=2, metavar=('REQUEST', 'PHASE'))
    args = parser.parse_args()
    if args.worker:
        require(args.worker[1] in PHASES, 'linux_DATA_sequence_unknown_phase')
        phase_worker(Path(args.worker[0]), args.worker[1])
    else:
        supervise(args.supervise)


if __name__ == '__main__':
    main()
