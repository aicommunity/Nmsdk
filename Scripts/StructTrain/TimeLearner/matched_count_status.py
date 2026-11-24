"""Read the actual launch/supervisor contract of Linux matched-count runs.

linux_count_training uses _run_owned directly. Its controller directory is
not an owned_native_job request directory; requiring controller/request.json
there confuses two protocols and prevents the next independent Train.
"""
import json
from pathlib import Path

from Scripts.StructTrain.TimeLearner.contained_process import inspect
from Scripts.StructTrain.TimeLearner.native_evidence import require
from Scripts.StructTrain.TimeLearner.owned_native_job import _same_process
from Scripts.StructTrain.TimeLearner.runtime import file_record

BASES = (Path('/home/user/timelearner-refactor'), Path('/media/user/Data/TimeLearnerRefactor'))


def inspect_training(request_path):
    request_path = Path(request_path).absolute()
    require(request_path.resolve(strict=True) == request_path, 'count_status_noncanonical_request')
    before = file_record(request_path)
    spec = json.loads(request_path.read_bytes())
    require(spec.get('kind') == 'timelearner_linux_matched_count_training' and
            type(spec.get('schema_version')) is int and spec['schema_version'] in (1, 2),
            'count_status_unknown_request')
    base = Path(spec['execution_root']);name = spec['job_id']
    require(base in BASES and type(name) is str and 1 <= len(name) <= 100 and
            all(c in 'abcdefghijklmnopqrstuvwxyz0123456789-_' for c in name) and
            request_path == base/'requests'/name/'request.json' and spec['operation'] in ('preflight', 'train'),
            'count_status_request_scope')
    controller, output = base/'readbacks'/(name+'-controller'), base/'readbacks'/name
    require(controller.resolve(strict=True) == controller, 'count_status_controller_alias')
    launch = json.loads((controller/'launch-context.json').read_bytes())
    require(launch['request_sha256'] == before['sha256'] and launch['tool_commit'] == spec['tool_commit'] and
            launch['operation'] == spec['operation'], 'count_status_launch_binding')
    owner_path = controller/'supervisor-identity.json'
    owner = json.loads(owner_path.read_bytes()) if owner_path.exists() else None
    supervisor_live = _same_process(owner) if owner is not None else None
    paths = [controller/'process/contained', output/'preflight/process/contained',
             output/'factor-preflight/process/contained']
    if spec['operation'] == 'train':paths.append(output/'train/process/contained')
    groups = {str(p):inspect(p) for p in paths if (p/'owned-unit.json').is_file()}
    result_path = controller/'supervisor-result.json'
    result = json.loads(result_path.read_bytes()) if result_path.exists() else None
    outer = groups.get(str(paths[0]))
    if result is not None and outer is not None:
        require(result['outer_binding'] == outer['binding'], 'count_status_outer_binding')
        expected_children = set(map(str, paths[1:]))
        for child in result['children_closed']:
            require(child['directory'] in expected_children and child['directory'] in groups and
                    child['binding'] == groups[child['directory']]['binding'], 'count_status_child_binding')
    terminal_path = output/'terminal.json'
    terminal = json.loads(terminal_path.read_bytes()) if terminal_path.exists() else None
    closed = (owner is not None and supervisor_live is False and result is not None and
              result['outer_closed'] is True and outer is not None and outer['all_processes_closed'] is True and
              all(g['all_processes_closed'] for g in groups.values()) and
              all(child['closure']['all_processes_closed'] for child in result['children_closed']))
    # A successful Train must have actually entered all its declared phases.
    if terminal is not None and terminal.get('execution') == 'completed':
        require(len(groups) == len(paths) and terminal['job_sha256'] == launch['job_sha256'],
                'count_status_completed_phase_missing')
    require(file_record(request_path) == before, 'count_status_request_changed')
    return dict(kind='timelearner_matched_count_execution_status', schema_version=1,
        request=before, job_id=name, controller=str(controller), output=str(output),
        supervisor_live=supervisor_live, groups=groups, supervisor_result=result,
        terminal=terminal, all_processes_closed=bool(closed), execution_status_only=True,
        full_primary_audit_inferred=False, training_certificate_verified=False, scientific_verdict=None)
