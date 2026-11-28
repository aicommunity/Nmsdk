"""Declared third-pulse and foil studies after an actual frozen Windows repeat.

This controller contains no generated executable worker, model tuning or Train.
Every phase uses prepared_physical_study and its original model/source audit.
"""
import argparse
import ctypes
import os
from pathlib import Path, PureWindowsPath
import shutil
import sys
import time
import traceback

from .native_evidence import load, require
from .runtime import file_record

BASE = Path('C:/Projects/TimeLearnerWorker')
SOURCE = Path(__file__).resolve().parents[3]
PHASES = ('third_pulse', 'new_foils')
FIELDS = {'kind', 'schema_version', 'job_id', 'python_root', 'source_repeat_request',
          'source_repeat_owner', 'preparation_gate', 'preparation_source_inventory',
          'native_wall_seconds', 'native_memory_bytes', 'maximum_wait_seconds', 'maximum_whole_seconds'}


def validate_request(q):
    require(type(q) is dict and set(q) == FIELDS and
            q['kind'] == 'timelearner_windows_frozen_physical_followups' and
            type(q['schema_version']) is int and q['schema_version'] == 1,
            'windows_frozen_followups_request_schema')
    require(type(q['job_id']) is str and 1 <= len(q['job_id']) <= 60 and
            all(c in 'abcdefghijklmnopqrstuvwxyz0123456789-_' for c in q['job_id']) and
            type(q['python_root']) is str and len(q['python_root']) == 40 and
            all(c in '0123456789abcdef' for c in q['python_root']), 'windows_frozen_followups_identity')
    for key in ('source_repeat_request', 'preparation_gate', 'preparation_source_inventory'):
        r = q[key]
        require(type(r) is dict and set(r) == {'path', 'sha256', 'size'} and
                type(r['path']) is str and PureWindowsPath(r['path']).is_absolute() and
                '..' not in PureWindowsPath(r['path']).parts and
                type(r['size']) is int and r['size'] > 0 and type(r['sha256']) is str and
                len(r['sha256']) == 64 and all(c in '0123456789abcdef' for c in r['sha256']),
                'windows_frozen_followups_bound_record:'+key)
    owner = q['source_repeat_owner']
    require(type(owner) is dict and set(owner) == {'pid', 'executable', 'creation_filetime'} and
            type(owner['pid']) is int and owner['pid'] > 0 and
            type(owner['creation_filetime']) is str and owner['creation_filetime'].isdigit() and
            int(owner['creation_filetime']) > 0 and type(owner['executable']) is str and
            PureWindowsPath(owner['executable']).is_absolute(), 'windows_frozen_followups_owner_identity')
    require(type(q['native_memory_bytes']) is int and 4*1024**3 <= q['native_memory_bytes'] <= 16*1024**3 and
            type(q['native_wall_seconds']) is dict and set(q['native_wall_seconds']) == set(PHASES) and
            all(type(v) is int and 3600 <= v <= 36000 for v in q['native_wall_seconds'].values()),
            'windows_frozen_followups_native_limits')
    require(type(q['maximum_wait_seconds']) is int and 0 < q['maximum_wait_seconds'] <= 60000 and
            type(q['maximum_whole_seconds']) is int and
            q['maximum_wait_seconds']+sum(q['native_wall_seconds'].values())+3600 <=
            q['maximum_whole_seconds'] <= 172800, 'windows_frozen_followups_controller_limits')
    return q


def supervise(request):
    from .owned_python_job import _source_snapshot
    from .prepared_physical_study import _source, prepare, run
    from .windows_stopped_recognition_study import _kernel, live, state, write

    request = Path(request).resolve(strict=True)
    q = validate_request(load(request))
    controls = request.parent
    require(os.name == 'nt' and BASE.resolve(strict=True) == BASE and SOURCE.is_relative_to(BASE) and
            controls == BASE/'controls'/q['job_id'], 'windows_frozen_followups_worker_paths')
    _source_snapshot(SOURCE, q['python_root'])
    bound = {str(request): file_record(request)}
    for key in ('source_repeat_request', 'preparation_gate', 'preparation_source_inventory'):
        p = Path(q[key]['path'])
        require(p.is_relative_to(BASE) and p.resolve(strict=True) == p and file_record(p) == q[key],
                'windows_frozen_followups_input_changed:'+key)
        bound[str(p)] = q[key]
    gate = load(Path(q['preparation_gate']['path']))
    projection = load(Path(q['preparation_source_inventory']['path']))
    require(gate['assertion_status'] == 'passed' and gate['actual_tests'] == 24 and gate['skipped'] == 0 and
            gate['original_and_shared_conditions_identical'] and gate['root_commit'] == projection['commit'] and
            gate['objects']['projection.json']['sha256'] == q['preparation_source_inventory']['sha256'],
            'windows_frozen_followups_preparation_gate_required')
    for name in ('frozen_physical_condition.py', 'frozen_third_pulse_study.py', 'prepared_physical_study.py'):
        relative = 'Scripts/StructTrain/TimeLearner/'+name
        record = file_record(SOURCE/relative)
        require(record['sha256'] == projection['inventory'][relative]['sha256'],
                'windows_frozen_followups_protocol_changed_since_gate')
    api, kernel = _kernel()
    write(controls/'owner.json', dict(pid=os.getpid(), **api.identity(kernel.GetCurrentProcess())))
    begun = time.monotonic()

    def guard():
        require(time.monotonic()-begun < q['maximum_whole_seconds'] and
                not (controls/'cancel.request').exists(), 'windows_frozen_followups_budget_or_cancel')
        require(all(file_record(Path(p)) == r for p,r in bound.items()),
                'windows_frozen_followups_bound_input_changed')

    def capacity():
        started = time.monotonic()
        while True:
            guard()
            memory = api.Memory(); memory.length = ctypes.sizeof(memory)
            api.check(api.memory_status(ctypes.byref(memory)))
            if memory.available_physical >= q['native_memory_bytes']+2*1024**3 and shutil.disk_usage(BASE).free >= 3*1024**3:
                return
            require(time.monotonic()-started < q['maximum_wait_seconds'], 'windows_frozen_followups_capacity_budget')
            state(controls/'waiting.json', dict(phase='capacity', available_physical_bytes=memory.available_physical))
            time.sleep(30)

    try:
        predecessor = Path(q['source_repeat_request']['path']).parent
        started = time.monotonic()
        while True:
            guard()
            require(load(predecessor/'owner.json') == q['source_repeat_owner'], 'windows_frozen_followups_predecessor_changed')
            require(not (predecessor/'exception.json').exists(), 'windows_frozen_followups_repeat_failed')
            alive = live(api, kernel, q['source_repeat_owner'])
            if not alive and (predecessor/'terminal.json').is_file():
                break
            require(time.monotonic()-started < q['maximum_wait_seconds'], 'windows_frozen_followups_repeat_wait_budget')
            state(controls/'waiting.json', dict(phase='actual_repeat', owner_live=alive,
                                              exact_owner=q['source_repeat_owner']))
            time.sleep(30)
        prior = load(predecessor/'terminal.json')
        require(prior['execution'] == 'completed' and prior['validity'] == 'valid' and
                prior['all_eight_actual_responses_compared'] and prior['frozen_study_adapter_admitted'],
                'windows_frozen_followups_verified_repeat_required')
        if prior['source_no_threshold_candidate']:
            write(controls/'terminal.json', dict(execution='completed', validity='valid',
                no_threshold_candidate=True, new_native_classification_not_run=True, scientific_verdict=None))
            return
        repeat = load(Path(q['source_repeat_request']['path']))
        source_controls = BASE/'controls'/repeat['run_id']
        source = _source(source_controls)
        source_revision, threshold = source['model']['model_revision'], source['metrics']['effective_threshold']
        results = {}
        for phase in PHASES:
            guard(); capacity()
            name = q['job_id']+'-'+phase.replace('_', '-')
            destination = BASE/'controls'/name
            require(not destination.exists(), 'windows_frozen_followups_fresh_phase_required')
            destination.mkdir()
            declaration = dict(kind='timelearner_physical_study_preparation', schema_version=2,
                source_controls=str(source_controls), destination=str(destination),
                inputs=str(BASE/'jobs'/(name+'-inputs')), output=str(BASE/'jobs'/name),
                run_id=name, study=dict(protocol=phase), python_source=str(SOURCE), python_root=q['python_root'],
                execution_limits=dict(memory_bytes=q['native_memory_bytes'], maximum_wall_seconds=q['native_wall_seconds'][phase]))
            write(controls/(phase+'-declaration.json'), declaration)
            prepared = prepare(declaration); write(controls/(phase+'-prepared.json'), prepared)
            run(destination)
            result = load(BASE/'jobs'/name/'terminal.json')
            require(result['execution'] == 'completed' and result['validity'] == 'valid' and
                    result['model_revision'] == source_revision and result['threshold'] == threshold and
                    result['frozen_model_verified'] and result['complete_native_observations'] and
                    result['source_protocol_repeated_control_checked'] and
                    len(result['repeated_control_comparisons']) == 1,
                    'windows_frozen_followups_phase_not_verified')
            results[phase] = result
            write(controls/(phase+'-completed.json'), result)
        guard(); _source_snapshot(SOURCE, q['python_root'])
        write(controls/'terminal.json', dict(kind='timelearner_windows_frozen_physical_followups_result',
            schema_version=1, execution='completed', validity='valid', phases=results,
            model_revision=source_revision, threshold=threshold, training_performed=False,
            threshold_selected=False, full_primary_archive_pending=True, all_pattern_figures_pending=True,
            scientific_verdict=None))
    except BaseException as error:
        write(controls/'exception.json', dict(reason=str(error), traceback=traceback.format_exc(),
            no_automatic_native_retry=True, scientific_verdict=None))
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--supervise', type=Path, required=True)
    supervise(parser.parse_args().supervise)
