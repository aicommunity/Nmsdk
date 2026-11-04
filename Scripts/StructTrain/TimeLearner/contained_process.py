"""User-systemd cgroup ownership surviving loss of the calling controller.

This backend owns a single local execution and all its forked descendants.
Execution/closure are separate: neither means converged training. No existing
process-runner schema or live experiment is changed by importing this module.
"""
from pathlib import Path, PurePosixPath
import json
import math
import os
import re
import subprocess
import sys
import time
import uuid

from .native_evidence import load, require
from .process_runner import verify_runtime, _start_identity, _write
from .runtime import digest_json


_HELPER = '''import json,os,time,sys
from pathlib import Path
p=Path(sys.argv[1]);request=json.loads((p/'request.json').read_text())
ready={'pid':os.getpid(),'start_ticks':Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19]}
temporary=p/'ready.pending';temporary.write_text(json.dumps(ready));temporary.rename(p/'ready.json')
while not (p/'start.ack').exists():time.sleep(.01)
env=dict(os.environ)
for key in ('LD_LIBRARY_PATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM'):env.pop(key,None)
env.update(request['environment'])
os.execve(request['executable'],[request['executable'],*request['arguments']],env)
'''
_PROPERTIES = ('LoadState', 'ActiveState', 'SubState', 'InvocationID', 'ControlGroup', 'MainPID',
               'Result', 'ExecMainCode', 'ExecMainStatus', 'Description', 'KillMode', 'Restart',
               'MemoryMax', 'TasksMax', 'Type', 'RemainAfterExit')


def _signed(value):
    return {**value, 'sha256': digest_json(value)}


def _read(path):
    value = load(path)
    require(type(value) is dict and value.get('sha256') == digest_json({k: v for k, v in value.items() if k != 'sha256'}),
            'contained_record_changed')
    return value


def _show(unit):
    result = subprocess.run(['systemctl', '--user', 'show', unit, '--property='+','.join(_PROPERTIES)],
                            capture_output=True, text=True, timeout=15)
    values = dict(line.split('=', 1) for line in result.stdout.splitlines() if '=' in line)
    require(values.get('LoadState') == 'not-found' or result.returncode == 0, 'contained_manager_unavailable')
    return values


def _request(directory):
    directory = Path(directory).resolve(strict=True)
    request = _read(directory/'request.json')
    require(set(request) == {'kind', 'schema_version', 'attempt_id', 'unit', 'boot_id', 'uid', 'controller',
            'executable', 'arguments', 'working_directory', 'runtime_fingerprint', 'memory_bytes', 'tasks',
            'maximum_wall_seconds', 'environment', 'sha256'} and
            request.get('kind') == 'timelearner_contained_request' and type(request.get('schema_version')) is int and request['schema_version'] == 1 and
            request['unit'] == 'timelearner-'+str(uuid.UUID(request['attempt_id']))+'.service', 'contained_request_schema')
    require(request['boot_id'] == Path('/proc/sys/kernel/random/boot_id').read_text().strip() and
            request['uid'] == os.getuid(), 'contained_worker_epoch_changed')
    return directory, request


def _group_path(value):
    path = PurePosixPath(value)
    require(value and path.is_absolute() and '..' not in path.parts and value != '/', 'contained_cgroup_path')
    return Path('/sys/fs/cgroup')/path.relative_to('/')


def _populated(group):
    try:
        fields = dict(line.split() for line in (group/'cgroup.events').read_text().splitlines())
    except FileNotFoundError:
        return False
    require(fields.get('populated') in ('0', '1'), 'contained_cgroup_events_invalid')
    return fields['populated'] == '1'


def adopt(directory):
    """Bind the launch intent after a controller crash; never invent completion."""
    directory, request = _request(directory)
    if (directory/'owned-unit.json').exists():
        binding = _read(directory/'owned-unit.json')
        require(binding['request_sha256'] == request['sha256'], 'contained_binding_changed')
        return binding
    owner = request['controller']
    try:
        live = _start_identity(owner['pid']) == owner['start_ticks']
    except (FileNotFoundError, ProcessLookupError):
        live = False
    require(not live or owner['pid'] == os.getpid(), 'contained_launch_controller_still_live')
    state = _show(request['unit'])
    require(state.get('Description') == 'TimeLearner contained attempt '+request['attempt_id'] and
            re.fullmatch('[0-9a-f]{32}', state.get('InvocationID', '')) is not None, 'contained_launch_not_bound')
    group = state.get('ControlGroup', '')
    require(_group_path(group).name == request['unit'], 'contained_cgroup_identity_changed')
    ready = load(directory/'ready.json')
    require(type(ready['pid']) is int and state['MainPID'] == str(ready['pid']) and
            _start_identity(ready['pid']) == ready['start_ticks'], 'contained_helper_identity_changed')
    require(Path('/proc', str(ready['pid']), 'cgroup').read_text().strip() == '0::'+group,
            'contained_helper_group_changed')
    binding = _signed({'kind': 'timelearner_contained_binding', 'schema_version': 1,
        'request_sha256': request['sha256'], 'unit': request['unit'], 'invocation_id': state['InvocationID'],
        'control_group': group, 'initial_main_pid': ready['pid'], 'initial_start_ticks': ready['start_ticks']})
    _write(directory/'owned-unit.json', binding)
    return binding


def start(manifest, arguments, working_directory, output, *, memory_bytes, tasks, maximum_wall_seconds,
          environment=None):
    require(sys.platform == 'linux', 'contained_linux_required')
    require(type(memory_bytes) is int and 0 < memory_bytes <= 2**63-1 and
            type(tasks) is int and 0 < tasks <= 2**31-1 and
            type(maximum_wall_seconds) in (int, float) and math.isfinite(maximum_wall_seconds) and
            1 <= maximum_wall_seconds <= 86400, 'contained_limits_invalid')
    require(type(arguments) is list and all(type(a) is str and '\0' not in a for a in arguments), 'contained_arguments_invalid')
    environment = {} if environment is None else environment
    require(type(environment) is dict and all(type(k) is str and type(v) is str and '\0' not in v and
            (k == 'ASAN_OPTIONS' or re.fullmatch('TIMELEARNER_[A-Z0-9_]+', k)) for k, v in environment.items()),
            'contained_environment_invalid')
    executable = verify_runtime(manifest)
    cwd = Path(working_directory).resolve(strict=True);require(cwd.is_dir(), 'contained_cwd_invalid')
    output = Path(output).resolve();output.mkdir(parents=True, exist_ok=False)
    attempt = str(uuid.uuid4());unit = 'timelearner-'+attempt+'.service'
    loader = manifest['loader_environment']
    require(type(loader) is dict and set(loader) <= {'LD_LIBRARY_PATH', 'QT_PLUGIN_PATH', 'QT_QPA_PLATFORM'} and
            all(type(v) is str and '\0' not in v for v in loader.values()), 'contained_loader_environment_invalid')
    request = _signed({'kind': 'timelearner_contained_request', 'schema_version': 1,
        'attempt_id': attempt, 'unit': unit, 'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
        'uid': os.getuid(), 'controller': {'pid': os.getpid(), 'start_ticks': _start_identity(os.getpid())},
        'executable': str(executable), 'arguments': arguments, 'working_directory': str(cwd),
        'runtime_fingerprint': manifest['runtime_fingerprint'], 'memory_bytes': memory_bytes, 'tasks': tasks,
        'maximum_wall_seconds': maximum_wall_seconds,
        'environment': {**loader, **environment}})
    _write(output/'request.json', request);_write(output/'runtime.json', manifest)
    (output/'launcher.py').write_text(_HELPER, encoding='utf-8')
    command = ['systemd-run', '--user', '--quiet', '--unit='+unit,
        '--property=Description=TimeLearner contained attempt '+attempt, '--property=Type=exec',
        '--property=RemainAfterExit=yes', '--property=KillMode=control-group', '--property=Restart=no',
        '--property=TimeoutStopSec=1s', '--property=MemorySwapMax=0', '--property=MemoryMax='+str(memory_bytes),
        '--property=TasksMax='+str(tasks), '--property=RuntimeMaxSec='+str(maximum_wall_seconds)+'s',
        '--property=UnsetEnvironment=LD_PRELOAD LD_AUDIT PYTHONPATH PYTHONHOME',
        '--property=WorkingDirectory='+str(cwd), '--property=StandardOutput=file:'+str(output/'stdout.log'),
        '--property=StandardError=file:'+str(output/'stderr.log'), sys.executable, str(output/'launcher.py'), str(output)]
    launched = subprocess.run(command, capture_output=True, text=True, timeout=15)
    _write(output/'launch-result.json', {'returncode': launched.returncode, 'stdout': launched.stdout, 'stderr': launched.stderr})
    require(launched.returncode == 0, 'contained_launch_failed_recovery_required')
    deadline = time.monotonic()+10
    while not (output/'ready.json').exists() and time.monotonic() < deadline:
        time.sleep(.01)
    binding = adopt(output)
    state = inspect(output)
    require(state['memory_max'] == memory_bytes and state['tasks_max'] == tasks, 'contained_limits_not_applied')
    group = _group_path(binding['control_group'])
    require((group/'memory.max').read_text().strip() == str(memory_bytes) and
            (group/'pids.max').read_text().strip() == str(tasks) and
            (group/'memory.swap.max').read_text().strip() == '0', 'contained_kernel_limits_not_applied')
    verify_runtime(manifest)
    (output/'start.ack').write_text('binding committed\n')
    return binding


def inspect(directory):
    directory, request = _request(directory)
    binding = adopt(directory)
    require(binding.get('kind') == 'timelearner_contained_binding' and type(binding.get('schema_version')) is int and
            binding['schema_version'] == 1 and binding['unit'] == request['unit'] and
            _group_path(binding['control_group']).name == request['unit'] and
            re.fullmatch('[0-9a-f]{32}', binding['invocation_id']) is not None, 'contained_binding_changed')
    group = _group_path(binding['control_group']);state = _show(binding['unit'])
    if state.get('LoadState') == 'not-found':
        require(not group.exists(), 'contained_manager_lost_populated_group')
        return {'execution': 'unknown', 'all_processes_closed': True, 'reason': 'bound_unit_and_group_absent',
                'scientific_verdict': None, 'binding': binding, 'state': state}
    invocation = state.get('InvocationID', '')
    require(invocation in ('', binding['invocation_id']), 'contained_invocation_changed')
    active = state.get('ActiveState')
    if invocation:
        require(state.get('ControlGroup', '') in ('', binding['control_group']) and
                state.get('KillMode') == 'control-group' and state.get('Restart') == 'no', 'contained_policy_changed')
    populated = _populated(group)
    closed = not populated and active in ('inactive', 'failed') or (
        not populated and active == 'active' and state.get('SubState') == 'exited')
    execution = 'running' if populated else 'unknown'
    # Closed membership alone never manufactures a successful native result.
    return {'execution': execution, 'all_processes_closed': closed, 'reason': 'kernel_cgroup_observed',
        'binding': binding, 'state': state, 'memory_max': int(state['MemoryMax']), 'tasks_max': int(state['TasksMax']),
        'scientific_verdict': None}


def stop(directory):
    """Stop this recorded invocation only, then prove its whole group is empty."""
    directory, request = _request(directory);before = inspect(directory)
    if before['all_processes_closed'] and (before['state'].get('LoadState') == 'not-found' or
                                         not before['state'].get('InvocationID')):
        return before
    require(before['state'].get('InvocationID') == before['binding']['invocation_id'], 'contained_invocation_changed')
    result = subprocess.run(['systemctl', '--user', 'stop', request['unit']], capture_output=True, text=True, timeout=15)
    require(result.returncode == 0, 'contained_stop_failed')
    after = inspect(directory);require(after['all_processes_closed'], 'contained_processes_still_present')
    return after
