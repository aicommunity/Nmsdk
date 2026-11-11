"""Freeze one complete, closed owned Python validation gate without rerunning it.

Only the existing owned_python_job/python-validation layout is admitted.
Collection success and the original gate outcome are separate. Extra files are
opaque metadata, including SQLite/kernel-case observations; their inclusion
does not attest nested kernel closure. Git staging/publication remains owned
by publisher.stage_artifact_set/verify_artifact_set/publish_closure.
"""
from dataclasses import dataclass
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import threading
import uuid

from . import collector_provenance as provenance
from . import contained_process, owned_python_job, portable_primary, publisher, resource_reservations, runtime
from .native_evidence import EvidenceError, require

ROOT = Path(__file__).resolve().parents[3]
SHA = re.compile(r'[0-9a-f]{64}')
COMMIT = re.compile(r'[0-9a-f]{40}')
ROLE = re.compile(r'[A-Za-z][A-Za-z0-9_.-]*')
REQUIRED_JOB_FILES = (
    'request.json', 'launch-context.json', 'preflight.json', 'supervisor.log',
    'controller-result.json', 'closure-and-reservation.json', 'lease-recovery.json',
    'process/runtime.json', 'process/contained/request.json', 'process/contained/runtime.json',
    'process/contained/owned-unit.json', 'process/contained/stdout.log', 'process/contained/stderr.log',
    'worker/reservation.json', 'worker/tool-source-before.json', 'worker/tool-source-after.json',
    'worker/validation-source-before.json', 'worker/validation-source-after.json',
    'worker/fixtures-before.json', 'worker/fixtures-after.json', 'worker/validation-process.json',
    'worker/terminal.json', 'worker/validation/suite.json', 'worker/validation/result.json',
    'worker/validation/unittest.log')
LEASE_IDENTITY = ('token', 'job_id', 'owner', 'resources', 'state', 'created', 'deadline', 'updated', 'release_note')
OBSERVATIONS = ('heartbeat_expired', 'owner_status', 'inspection_required')
CONTROL_MAX = 1024**2
FINALIZATION_RESERVE = 4*1024**2


def _keys(value, names, reason):
    require(type(value) is dict and set(value) == set(names), reason)


def _text(value, reason):
    require(type(value) is str and value and '\0' not in value, reason)


def _path(value):
    _text(value, 'closed_collection_path')
    require(Path(value).is_absolute() and '..' not in Path(value).parts, 'closed_collection_path')
    return Path(value)


def _count(value, maximum):
    require(type(value) is int and 0 < value <= maximum, 'closed_collection_budget')


def _binding(value):
    _keys(value, ('path', 'commit'), 'closed_collection_repository_binding')
    _path(value['path'])
    require(type(value['commit']) is str and COMMIT.fullmatch(value['commit']), 'closed_collection_commit')


def validate_projection_patterns(expected, actual):
    """Order is explicit data: JSON key sorting cannot define sparse policy."""
    require(type(expected) is list and expected and all(type(v) is str and v and
        not any(c in v for c in ('\0', '\n', '\r')) for v in expected) and
        len(expected) == len(set(expected)), 'closed_collection_projection_declaration')
    require(type(actual) is list and actual == expected, 'closed_collection_projection_changed')
    return list(expected)


def _expected(expected):
    _keys(expected, ('suite_id', 'package_fingerprint', 'test_ids', 'failures', 'errors', 'skipped',
        'diagnostic_fragments', 'gate_outcome', 'controller_execution', 'controller_returncode', 'worker_operation_passed'),
        'closed_collection_expected_schema')
    _text(expected['suite_id'], 'closed_collection_suite_id')
    require(type(expected['package_fingerprint']) is str and SHA.fullmatch(expected['package_fingerprint']), 'closed_collection_digest')
    ids = expected['test_ids']
    require(type(ids) is list and ids and all(type(n) is str and n for n in ids) and len(ids) == len(set(ids)), 'closed_collection_test_ids')
    for key in ('failures', 'errors'):
        require(type(expected[key]) is list and all(type(n) is str and n in ids for n in expected[key]) and
            len(expected[key]) == len(set(expected[key])), 'closed_collection_failure_ids')
    require(type(expected['skipped']) is list, 'closed_collection_skipped')
    for row in expected['skipped']:
        _keys(row, ('test_id', 'reason'), 'closed_collection_skipped')
        require(type(row['test_id']) is str and row['test_id'] in ids and type(row['reason']) is str, 'closed_collection_skipped')
    nonpass = expected['failures']+expected['errors']+[r['test_id'] for r in expected['skipped']]
    require(len(nonpass) == len(set(nonpass)), 'closed_collection_overlapping_outcomes')
    diagnostics = expected['diagnostic_fragments']
    require(type(diagnostics) is dict and set(diagnostics) == set(expected['failures']+expected['errors']) and
        all(type(rows) is list and rows and all(type(s) is str and s.strip() and len(s) <= 4096 for s in rows)
            for rows in diagnostics.values()), 'closed_collection_failure_diagnostics')
    failed = bool(nonpass)
    require(expected['gate_outcome'] == ('failed' if failed else 'passed') and
        expected['controller_execution'] == ('process_error' if failed else 'completed') and
        type(expected['controller_returncode']) is int and expected['controller_returncode'] == (1 if failed else 0) and
        type(expected['worker_operation_passed']) is bool and expected['worker_operation_passed'] == (not failed),
        'closed_collection_outcome_not_consistent')


def validate_manifest(value):
    _keys(value, ('kind', 'schema_version', 'collection_id', 'worker_host', 'execution_root',
        'collector_tool', 'job', 'expected', 'files', 'git', 'projections', 'fixture_reference_roles',
        'extra_metadata_note', 'limits'), 'closed_collection_manifest_schema')
    require(value['kind'] == 'timelearner_closed_python_validation_collection' and
        type(value['schema_version']) is int and value['schema_version'] == 1, 'closed_collection_manifest_schema')
    require(type(value['collection_id']) is str and ROLE.fullmatch(value['collection_id']), 'closed_collection_id')
    _text(value['worker_host'], 'closed_collection_host');_path(value['execution_root'])
    _binding(value['collector_tool'])
    job = value['job']
    _keys(job, ('path', 'id', 'original_tool', 'source', 'plan', 'binding', 'lease_token',
        'request_sha256', 'suite_sha256'), 'closed_collection_job_schema')
    _path(job['path']);require(type(job['id']) is str and ROLE.fullmatch(job['id']), 'closed_collection_job_id')
    require(Path(job['path']) == Path(value['execution_root'])/'readbacks'/job['id'], 'closed_collection_job_path')
    for key in ('original_tool', 'source', 'plan'):_binding(job[key])
    _keys(job['binding'], ('kind', 'schema_version', 'request_sha256', 'unit', 'invocation_id',
        'control_group', 'initial_main_pid', 'initial_start_ticks', 'sha256'), 'closed_collection_owned_binding_required')
    binding = job['binding']
    require(binding['kind'] == 'timelearner_contained_binding' and type(binding['schema_version']) is int and
        binding['schema_version'] == 1, 'closed_collection_owned_binding_required')
    provenance._signed((json.dumps(binding, allow_nan=False)).encode())
    require(type(binding['initial_main_pid']) is int and binding['initial_main_pid'] > 0 and
        type(binding['initial_start_ticks']) is str and binding['initial_start_ticks'].isdigit(), 'closed_collection_owned_binding_required')
    _text(job['lease_token'], 'closed_collection_lease_token')
    for key in ('request_sha256', 'suite_sha256'):
        require(type(job[key]) is str and SHA.fullmatch(job[key]), 'closed_collection_digest')
    _expected(value['expected'])
    _keys(value['limits'], ('maximum_capture_bytes', 'maximum_git_bytes', 'minimum_free_bytes',
        'maximum_output_bytes'), 'closed_collection_limits')
    for key, maximum in (('maximum_capture_bytes', 64*1024**2), ('maximum_git_bytes', 128*1024**2),
        ('minimum_free_bytes', 2**53-1), ('maximum_output_bytes', 256*1024**2)):_count(value['limits'][key], maximum)
    require(type(value['files']) is list and type(value['git']) is list and value['git'], 'closed_collection_roles')
    require(type(value['extra_metadata_note']) is str, 'closed_collection_extra_metadata_note')
    files = []
    for row in value['files']:
        _keys(row, ('role', 'root', 'relative_path', 'expected_bytes', 'expected_sha256', 'maximum_bytes',
            'staged_name', 'archive_path', 'purpose'), 'closed_collection_file_role')
        require(row['purpose'] in ('code_or_plan', 'observer_metadata', 'opaque_extra'), 'closed_collection_file_purpose')
        require(type(row['role']) is str and ROLE.fullmatch(row['role']), 'closed_collection_file_role')
        _path(row['root'])
        require(row['role'] != 'collection-manifest' and not row['role'].startswith('original.'), 'closed_collection_reserved_file_role')
        if row['purpose'] == 'opaque_extra':require(value['extra_metadata_note'].strip(), 'closed_collection_opaque_reason_required')
        portable_primary._name(row['archive_path'])
        require(not row['archive_path'].startswith(('original-job/', 'collector-provenance/', 'observer/')),
            'closed_collection_reserved_archive_path')
        files.append(provenance.RequiredFileRole(**{k:(Path(v) if k == 'root' else v) for k,v in row.items()
            if k not in ('archive_path', 'purpose')}))
    if files:provenance._requirements(files, provenance._file_role, value['limits']['maximum_capture_bytes'])
    require(len({r['archive_path'] for r in value['files']}) == len(value['files']), 'closed_collection_duplicate_archive')
    for row in value['git']:
        _keys(row, ('role', 'repository', 'repository_head', 'commit', 'path', 'git_blob', 'expected_bytes',
            'expected_sha256', 'maximum_bytes'), 'closed_collection_Git_role_schema')
        _path(row['repository'])
    git = [provenance.GitInputRole(**{k:(Path(v) if k == 'repository' else v) for k,v in row.items()}) for row in value['git']]
    provenance._requirements(git, provenance._git_role, value['limits']['maximum_git_bytes'])
    require(type(value['fixture_reference_roles']) is list and len(value['fixture_reference_roles']) == len(set(value['fixture_reference_roles'])) and
        all(type(r) is str and r in {v.role for v in git} for r in value['fixture_reference_roles']), 'closed_collection_fixture_reference_roles')
    require(type(value['projections']) is list, 'closed_collection_projections')
    for row in value['projections']:
        _keys(row, ('repository', 'commit', 'patterns'), 'closed_collection_projection_schema')
        _path(row['repository']);require(type(row['commit']) is str and COMMIT.fullmatch(row['commit']), 'closed_collection_commit')
        validate_projection_patterns(row['patterns'], row['patterns'])
    return value


def compare_released_lease(original, observed):
    """Immutable identity excludes only explicitly observation-derived fields."""
    require(type(original) is dict and type(observed) is dict and
        all(k in original and k in observed for k in LEASE_IDENTITY+OBSERVATIONS), 'closed_collection_lease_schema')
    require(original['state'] == observed['state'] == 'released', 'closed_collection_lease_not_released')
    require({k:original[k] for k in LEASE_IDENTITY} == {k:observed[k] for k in LEASE_IDENTITY}, 'closed_collection_lease_changed')
    for row in (original, observed):
        require(type(row['heartbeat_expired']) is bool and type(row['inspection_required']) is bool and
            type(row['owner_status']) is str, 'closed_collection_lease_observation')
    # Unknown persisted fields cannot silently become another observation exemption.
    require({k:v for k,v in original.items() if k not in OBSERVATIONS} ==
        {k:v for k,v in observed.items() if k not in OBSERVATIONS}, 'closed_collection_lease_changed')


def validate_python_outcome(expected, suite, result, log, controller, terminal):
    """Pure metadata validation; this function performs/attests no kernel query."""
    _expected(expected)
    _keys(suite, ('kind', 'schema_version', 'suite_id', 'package_fingerprint', 'modules', 'expected_test_ids', 'fixtures'),
        'closed_collection_suite_schema')
    require(suite['kind'] == 'timelearner_python_validation_suite' and type(suite['schema_version']) is int and
        suite['schema_version'] == 1, 'closed_collection_suite_schema')
    required = ('kind', 'schema_version', 'suite_id', 'package_fingerprint', 'execution', 'assertion_status',
        'expected_test_ids', 'executed_tests', 'failures', 'errors', 'skipped', 'fixtures', 'scientific_verdict')
    _keys(result, required, 'closed_collection_result_schema')
    require(result['kind'] == 'timelearner_python_validation_result' and type(result['schema_version']) is int and
        result['schema_version'] == 1 and result['execution'] == 'completed' and result['scientific_verdict'] is None,
        'closed_collection_result_schema')
    require(suite['expected_test_ids'] == result['expected_test_ids'] == expected['test_ids'] and
        suite['suite_id'] == result['suite_id'] == expected['suite_id'] and
        suite['package_fingerprint'] == result['package_fingerprint'] == expected['package_fingerprint'], 'closed_collection_suite_changed')
    require(type(result['executed_tests']) is int and result['executed_tests'] == len(expected['test_ids']), 'closed_collection_partial_inventory')
    for key in ('failures', 'errors', 'skipped'):require(result[key] == expected[key], 'closed_collection_unexpected_'+key)
    require(result['assertion_status'] == expected['gate_outcome'], 'closed_collection_gate_outcome_changed')
    try:lines = log.decode('utf-8').splitlines()
    except UnicodeDecodeError as error:raise EvidenceError('closed_collection_log_UTF8') from error
    observed = {}
    for line in lines:
        match = re.fullmatch(r'(\S+) \(([^()\n]+)\) \.\.\. (ok|FAIL|ERROR|skipped(?: .*)?)', line)
        if not match:continue
        short, identifier, status = match.groups()
        require(identifier not in observed and short == identifier.rsplit('.', 1)[-1], 'closed_collection_log_duplicate_or_alias')
        observed[identifier] = 'skipped' if status.startswith('skipped') else status
    wanted = {name:'ok' for name in expected['test_ids']}
    for key,status in (('failures', 'FAIL'), ('errors', 'ERROR')):
        for name in expected[key]:wanted[name] = status
    for row in expected['skipped']:wanted[row['test_id']] = 'skipped'
    require(observed == wanted, 'closed_collection_log_inventory_or_outcome')
    runs = [(index, re.fullmatch(r'Ran (\d+) tests? in [0-9]+(?:\.[0-9]+)?s', line))
        for index,line in enumerate(lines) if line.startswith('Ran ')]
    require(len(runs) == 1 and runs[0][1] is not None and int(runs[0][1].group(1)) == len(wanted),
        'closed_collection_log_run_count_or_truncation')
    count_parts = [label+'='+str(len(expected[key])) for key,label in
        (('failures', 'failures'), ('errors', 'errors'), ('skipped', 'skipped')) if expected[key]]
    footer = ('FAILED' if expected['failures'] or expected['errors'] else 'OK')
    if count_parts:footer += ' ('+', '.join(count_parts)+')'
    tail = [line for line in lines[runs[0][0]+1:] if line.strip()]
    require(tail == [footer], 'closed_collection_log_footer_or_truncation')
    headings = []
    for index,line in enumerate(lines[:runs[0][0]]):
        match = re.fullmatch(r'(FAIL|ERROR): (\S+) \(([^()\n]+)\)', line)
        if match:
            status,short,identifier = match.groups()
            require(short == identifier.rsplit('.', 1)[-1], 'closed_collection_log_detail_alias')
            headings.append((index,identifier,status))
    require(len(headings) == len(expected['failures'])+len(expected['errors']) and
        {(identifier,status) for _,identifier,status in headings} ==
        {(name,'FAIL') for name in expected['failures']}|{(name,'ERROR') for name in expected['errors']},
        'closed_collection_log_failure_details_missing')
    for offset,(index,identifier,_) in enumerate(headings):
        end = headings[offset+1][0] if offset+1 < len(headings) else runs[0][0]
        detail = '\n'.join(lines[index+1:end])
        require('Traceback (most recent call last):' in detail and
            all(fragment in detail for fragment in expected['diagnostic_fragments'][identifier]),
            'closed_collection_log_failure_diagnostic_missing')
    require(controller.get('kind') == 'timelearner_process_result' and type(controller.get('schema_version')) is int and controller.get('schema_version') == 2 and
        type(controller.get('returncode')) is int and
        controller.get('execution') == expected['controller_execution'] and controller.get('returncode') == expected['controller_returncode'] and
        controller.get('runtime_provenance') == 'loaded_files_captured' and controller.get('all_processes_closed') is True,
        'closed_collection_controller_outcome')
    require(terminal.get('operation') == 'python-validation' and
        terminal.get('operation_passed') is expected['worker_operation_passed'] and terminal.get('heartbeat_errors') == [] and
        terminal.get('scientific_verdict') is None, 'closed_collection_worker_outcome')
    return {'gate_outcome':expected['gate_outcome'], 'tests':len(wanted), 'passed':sum(s == 'ok' for s in wanted.values()),
        'failures':list(result['failures']), 'errors':list(result['errors']), 'skipped':list(result['skipped']),
        'actual_log_ids':list(observed), 'kernel_closure_attested':False, 'scientific_verdict':None}


def _load(path, maximum=16*1024**2):
    return provenance._json(provenance._frozen(path, maximum)[0])


def validate_saved_joins(suite, saved_suite, result, controller, validation_process,
                         observation, fixture_snapshot, fixture_bindings):
    """Join retained metadata; no supplied file is itself a fresh kernel proof."""
    require(saved_suite == suite, 'closed_collection_copied_suite_changed')
    require(controller.get('runtime_fingerprint') == observation['runtime_fingerprint'], 'closed_collection_controller_runtime_changed')
    require(type(validation_process.get('returncode')) is int and validation_process['returncode'] ==
        (0 if result['assertion_status'] == 'passed' else 1), 'closed_collection_validation_process_outcome')
    expected = {name:{'path':fixture_bindings[name], 'files':len(row['files']), 'fingerprint':row['fingerprint']}
        for name,row in fixture_snapshot.items()}
    require(result['fixtures'] == expected, 'closed_collection_result_fixture_changed')


def _inventory(root, maximum):
    rows = {};total = 0
    for path in sorted(root.rglob('*')):
        if path.is_dir() and not path.is_symlink():continue
        require(len(rows) < 4096 and path.lstat().st_size <= maximum-total, 'closed_collection_capture_budget')
        _, record = provenance._frozen(path, max(maximum-total, 1));total += record['bytes']
        rows[path.relative_to(root).as_posix()] = {'bytes':record['bytes'], 'sha256':record['sha256']}
    require(sum(r['bytes'] for r in rows.values()) <= maximum, 'closed_collection_capture_budget')
    return rows


def _namespace(manifest):
    require(provenance._canonical(Path(manifest['collector_tool']['path'])) == ROOT, 'closed_collection_collector_namespace')
    for module in (provenance, contained_process, owned_python_job, portable_primary, publisher, resource_reservations, runtime):
        require(Path(module.__file__).resolve().is_relative_to(ROOT/'Scripts/StructTrain/TimeLearner'),
            'closed_collection_import_namespace')
    return owned_python_job._source_snapshot(ROOT, manifest['collector_tool']['commit'])


def _closed_observation(value, ledger_snapshot, supervisor):
    job = value['job'];path = Path(job['path']);binding = job['binding']
    current = contained_process.inspect(path/'process/contained')
    require(current['binding'] == binding == supervisor.descriptor['binding'] and current['all_processes_closed'] and
        current['state']['MainPID'] == '0' and not current['state']['ControlGroup'] and
        not Path('/sys/fs/cgroup'+binding['control_group']).exists(), 'closed_collection_kernel_not_closed_or_wrong_binding')
    unit = _load(path/'process/contained/request.json');held = _load(path/'worker/reservation.json')
    saved = _load(path/'closure-and-reservation.json')
    require(saved['closure']['binding'] == binding and saved['closure']['all_processes_closed'] is True and
        saved['closure']['state']['MainPID'] == '0' and not saved['closure']['state']['ControlGroup'], 'closed_collection_saved_closure')
    rows = [r for r in ledger_snapshot['leases'] if r['job_id'] == job['id']]
    require(len(rows) == len(saved['leases']) == 1 and rows[0]['token'] == job['lease_token'], 'closed_collection_lease_binding')
    compare_released_lease(saved['leases'][0], rows[0])
    for key in ('token', 'job_id', 'owner', 'resources'):require(rows[0][key] == held[key], 'closed_collection_worker_lease_changed')
    owner = rows[0]['owner']
    require(owner['pid'] == binding['initial_main_pid'] and owner['start_ticks'] == binding['initial_start_ticks'] and
        owner['boot_id'] == unit['boot_id'] == Path('/proc/sys/kernel/random/boot_id').read_text().strip() and
        owner['uid'] == unit['uid'] == os.getuid(), 'closed_collection_worker_identity')
    observed_runtime = _load(path/'process/runtime.json')
    identity = runtime.runtime_content_identity(observed_runtime)
    require(identity == observed_runtime['runtime_identity'] and runtime.digest_json(identity) ==
        observed_runtime['runtime_fingerprint'] == unit['runtime_fingerprint'], 'closed_collection_runtime_fingerprint')
    require(owner['executable'] == observed_runtime['executable']['path'] and
        observed_runtime['source_closure']['tool_root'] == job['original_tool']['commit'] and
        observed_runtime['app_ini']['sha256'] == job['request_sha256'], 'closed_collection_original_tool_runtime')
    return {'closure':current, 'released_lease':rows[0], 'runtime_fingerprint':observed_runtime['runtime_fingerprint'],
        'reservation_snapshot_SQL_access':ledger_snapshot['SQL_access']}


@dataclass(frozen=True)
class PreparedClosedCollection:
    manifest_path: Path
    manifest_sha256: str
    manifest: dict
    captured: provenance.CapturedFileRoles
    supervisor: provenance.CapturedCollectorInputs
    literal_inventory: dict
    git_capabilities: dict
    source_snapshots: dict
    fixture_snapshot: dict
    original_inventory: dict
    archive_paths: dict
    observation: dict
    outcome: dict
    read_roots: tuple


def prepare_closed_collection(manifest_path, expected_sha256):
    """Read-only complete preflight. No output directories or leases are created."""
    require(type(expected_sha256) is str and SHA.fullmatch(expected_sha256), 'closed_collection_manifest_digest')
    path = provenance._canonical(Path(manifest_path));raw, record = provenance._frozen(path, 1024**2)
    require(record['sha256'] == expected_sha256, 'closed_collection_manifest_changed')
    value = validate_manifest(provenance._json(raw));collector = _namespace(value)
    require(sys.platform == 'linux' and socket.gethostname() == value['worker_host'], 'closed_collection_worker_required')
    job = value['job'];j = provenance._canonical(Path(job['path']));base = provenance._canonical(Path(value['execution_root']))
    request_raw, request_record = provenance._frozen(j/'request.json', 1024**2)
    require(request_record['sha256'] == job['request_sha256'], 'closed_collection_job_request_changed')
    request = owned_python_job.validate_request(provenance._json(request_raw))
    require(request['job_id'] == job['id'] and request['worker_host'] == value['worker_host'] and request['execution_root'] == str(base) and
        request['tool_commit'] == job['original_tool']['commit'] and request['operation']['kind'] == 'python-validation' and
        request['operation']['source'] == job['source'] and request['operation']['suite'] ==
        {'path':str(Path(job['plan']['path'])/'suite.json'), 'sha256':job['suite_sha256']}, 'closed_collection_request_role_mismatch')
    unit = _load(j/'process/contained/request.json')
    require(all(unit[key] == request['limits'][key] for key in ('memory_bytes', 'tasks', 'maximum_wall_seconds')) and
        unit['working_directory'] == job['original_tool']['path'], 'closed_collection_original_limits_or_tool')
    suite_raw, suite_record = provenance._frozen(Path(job['plan']['path'])/'suite.json', 1024**2)
    require(suite_record['sha256'] == job['suite_sha256'], 'closed_collection_suite_digest')
    suite = provenance._json(suite_raw)
    literal = provenance.capture_python_selection_inventory(Path(job['source']['path']), job['source']['commit'],
        suite['modules'], value['expected']['test_ids'])
    roles = [provenance.GitInputRole(**{k:(Path(v) if k == 'repository' else v) for k,v in row.items()}) for row in value['git']]
    capabilities = provenance.verify_git_input_roles(roles, maximum_total_bytes=value['limits']['maximum_git_bytes'])
    for row in value['projections']:
        repository = provenance._canonical(Path(row['repository']))
        require(provenance._git(repository, 'rev-parse', 'HEAD').decode().strip() == row['commit'], 'closed_collection_projection_epoch')
        validate_projection_patterns(row['patterns'], provenance._git(repository, 'sparse-checkout', 'list').decode().splitlines())
    original = _inventory(j, value['limits']['maximum_capture_bytes'])
    require(set(REQUIRED_JOB_FILES) <= set(original), 'closed_collection_required_metadata_missing')
    require(not any(Path(n).suffix.lower() in ('.csv', '.png', '.svg', '.pdf', '.gguf', '.xz', '.tar') for n in original),
        'closed_collection_original_job_is_not_metadata_only')
    supervisor = provenance.capture_owned_supervisor(j/'process/contained', supervisor_log=j/'supervisor.log', worker_stdout=j/'process/contained/stdout.log')
    ledger_snapshot = resource_reservations.Reservations.read_snapshot(base/'resource-reservations.sqlite3')
    observation = _closed_observation(value, ledger_snapshot, supervisor)
    outcome = validate_python_outcome(value['expected'], suite, _load(j/'worker/validation/result.json'),
        provenance._frozen(j/'worker/validation/unittest.log', 16*1024**2)[0], _load(j/'controller-result.json'), _load(j/'worker/terminal.json'))
    exception = j/'worker/exception.json'
    if outcome['gate_outcome'] == 'failed':
        require(exception.is_file() and _load(exception)['reason'] == 'owned_job_validation_failed', 'closed_collection_failure_reason_not_validation')
    else:require(not exception.exists(), 'closed_collection_unexpected_worker_exception')
    snapshots = {'collector':collector}
    for role, key in (('original_tool', 'tool'), ('source', 'validation')):
        binding = job[role];snapshot = owned_python_job._source_snapshot(Path(binding['path']), binding['commit'])
        require(snapshot == _load(j/('worker/'+key+'-source-before.json')) == _load(j/('worker/'+key+'-source-after.json')),
            'closed_collection_saved_source_changed')
        snapshots[role] = snapshot
    package = {name.removeprefix('Scripts/StructTrain/TimeLearner/'):row['sha256']
        for name,row in snapshots['source']['files'].items()
        if name.startswith('Scripts/StructTrain/TimeLearner/') and name.endswith('.py')}
    require(package and runtime.digest_json(package) == value['expected']['package_fingerprint'], 'closed_collection_source_package_fingerprint')
    fixtures = owned_python_job._fixture_snapshot(suite, request['operation']['fixtures'])
    require(fixtures == _load(j/'worker/fixtures-before.json') == _load(j/'worker/fixtures-after.json'), 'closed_collection_fixture_changed')
    require(not fixtures or value['fixture_reference_roles'], 'closed_collection_fixture_Git_reference_required')
    validate_saved_joins(suite, _load(j/'worker/validation/suite.json'), _load(j/'worker/validation/result.json'),
        _load(j/'controller-result.json'), _load(j/'worker/validation-process.json'), observation,
        fixtures, request['operation']['fixtures'])
    files = [provenance.RequiredFileRole('collection-manifest', path.parent, path.name, len(raw), record['sha256'], 1024**2, 'collection-manifest.json')]
    archive = {'collection-manifest':'observer/collection-manifest.json'}
    for index,(name,row) in enumerate(original.items()):
        role = 'original.%04d'%index
        files.append(provenance.RequiredFileRole(role, j, name, row['bytes'], row['sha256'], value['limits']['maximum_capture_bytes'], 'job-%04d'%index))
        archive[role] = 'original-job/'+name
    for row in value['files']:
        files.append(provenance.RequiredFileRole(**{k:(Path(v) if k == 'root' else v) for k,v in row.items() if k not in ('archive_path', 'purpose')}))
        require(row['role'] not in archive, 'closed_collection_duplicate_role');archive[row['role']] = row['archive_path']
    read_roots = {str(path.parent), value['collector_tool']['path'], job['path'],
        *(r['root'] for r in value['files']), *(r['repository'] for r in value['git']),
        *(r['repository'] for r in value['projections']), *(job[r]['path'] for r in ('original_tool', 'source', 'plan')),
        *request['operation']['fixtures'].values()}
    for row in value['files']:
        source = Path(row['root'])/row['relative_path']
        registry_path = base/'resource-reservations.sqlite3'
        require(source not in (registry_path, Path(str(registry_path)+'-wal'), Path(str(registry_path)+'-shm')),
            'closed_collection_mutable_own_registry_as_input')
        for fixture in request['operation']['fixtures'].values():
            require(not source.is_relative_to(Path(fixture)), 'closed_collection_fixture_payload_must_be_Git_reference')
    captured = provenance.capture_required_file_roles(files, maximum_total_bytes=value['limits']['maximum_capture_bytes'])
    return PreparedClosedCollection(path, expected_sha256, value, captured, supervisor, literal, capabilities,
        snapshots, fixtures, original, archive, observation, outcome, tuple(sorted(read_roots)))


def _write(path, value):
    raw = (json.dumps(value, indent=2, allow_nan=False)+'\n').encode()
    with path.open('xb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    return {'bytes':len(raw), 'sha256':hashlib.sha256(raw).hexdigest()}


def _materialize_inputs(prepared, stage):
    staged = prepared.captured.materialize(stage, stage/'files')
    sources = {prepared.archive_paths[role]:staged['collector-file-inputs/'+row['staged_name']]
        for role,row in prepared.captured.descriptor['roles'].items()}
    sources.update(prepared.supervisor.materialize(stage, stage/'supervisor'))
    return sources


def _finish_heartbeat(stop, thread, errors):
    stop.set();thread.join(timeout=15)
    require(not thread.is_alive() and not errors, 'closed_collection_heartbeat_failed_after_join')


def _atomic_marker(path, value):
    """Exclusive, fully written last marker; retain failed partials for review."""
    temporary = path.with_name(path.name+'.finalizing-'+uuid.uuid4().hex)
    require(len((json.dumps(value, indent=2, allow_nan=False)+'\n').encode()) <= CONTROL_MAX, 'closed_collection_control_budget')
    record = _write(temporary, value)
    identity = temporary.lstat();linked = False
    descriptor = os.open(path.parent, os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        # link is atomic and refuses an existing destination, unlike replace().
        os.link(temporary, path, follow_symlinks=False);linked = True
        os.fsync(descriptor)
    except BaseException:
        # Remove only this call's new success name. Keep the underlying failed
        # finalization object for diagnosis; never touch an existing marker.
        if linked:
            current = path.lstat()
            if (current.st_dev, current.st_ino) == (identity.st_dev, identity.st_ino):path.unlink()
        raise
    finally:os.close(descriptor)
    # The immutable finalization object is intentionally retained. There is no
    # fallible cleanup after a successfully published last marker.
    return record


def collect_prepared(prepared, output_root):
    """Revalidate public prepared values before any filesystem/publication write."""
    require(type(prepared) is PreparedClosedCollection, 'closed_collection_prepared_required')
    require(isinstance(prepared.manifest_path, Path) and type(prepared.manifest_sha256) is str and
        SHA.fullmatch(prepared.manifest_sha256) and type(prepared.captured) is provenance.CapturedFileRoles,
        'closed_collection_prepared_invalid')
    fresh = prepare_closed_collection(prepared.manifest_path, prepared.manifest_sha256)
    require(fresh.captured.descriptor == prepared.captured.descriptor and fresh.archive_paths == prepared.archive_paths and
        fresh.literal_inventory == prepared.literal_inventory and fresh.git_capabilities == prepared.git_capabilities,
        'closed_collection_prepared_inputs_changed')
    value = fresh.manifest;output = provenance._canonical(Path(output_root), exists=False)
    require(not output.exists() and output.is_relative_to(Path(value['execution_root'])), 'closed_collection_owned_output')
    roots = set(fresh.read_roots)
    for root in roots:
        root = provenance._canonical(Path(root))
        require(not (root == output or root.is_relative_to(output) or output.is_relative_to(root)), 'closed_collection_output_overlaps_input')
    require(shutil.disk_usage(output.parent).free >= value['limits']['minimum_free_bytes']+value['limits']['maximum_output_bytes'], 'closed_collection_space_preflight')
    registry = resource_reservations.Reservations.open_existing(Path(value['execution_root'])/'resource-reservations.sqlite3')
    require(not registry.managed_units, 'closed_collection_managed_registry_not_supported')
    lease = registry.reserve(value['collection_id'], [{'path':str(output), 'access':'write'}]+
        [{'path':r, 'access':'read'} for r in sorted(roots)], ttl_seconds=120,
        demands={'slots':1, 'memory_bytes':536870912, 'disk_bytes':value['limits']['maximum_output_bytes']} if registry.capacity is not None else None)
    stop = threading.Event();errors = []
    def heartbeat():
        while not stop.wait(10):
            try:registry.heartbeat(lease['token'], ttl_seconds=120);registry.validate_paths(lease['token'])
            except BaseException as error:errors.append(str(error));return
    thread = threading.Thread(target=heartbeat, daemon=True);thread.start()
    try:
        registry.validate_paths(lease['token']);output.mkdir();output_identity = (output.stat().st_dev, output.stat().st_ino)
        stage = output/'captured';stage.mkdir()
        sources = _materialize_inputs(fresh, stage)
        observers = {'file-roles.json':fresh.captured.descriptor, 'Git-roles.json':fresh.git_capabilities,
            'literal-inventory.json':fresh.literal_inventory, 'source-snapshots.json':fresh.source_snapshots,
            'fixture-snapshot.json':fresh.fixture_snapshot,
            'collector-provenance.json':provenance.describe_collection(fresh.supervisor, collector_tool_root=ROOT,
                compilation_state='not_started', actual_sdk_source=None, compiled_runtime=None,
                planned_source={'original_tool':value['job']['original_tool'], 'source':value['job']['source'], 'plan':value['job']['plan']})}
        proof = {'kind':'closed_python_validation_capture', 'schema_version':1, 'collection_status':'capture_prepared',
            'original_gate':fresh.outcome, 'original_job_id':value['job']['id'], 'original_inventory':fresh.original_inventory,
            'original_observation':fresh.observation, 'archive_paths':fresh.archive_paths,
            'collection_reservation':lease,
            'extra_metadata_note':value['extra_metadata_note'], 'extra_metadata_semantic_validation':False,
            'nested_kernel_closure_attested':False, 'SDK_source_verified':False, 'scientific_verdict':None}
        observers['capture-proof.json'] = proof
        for name,data in observers.items():
            path = output/name;_write(path, data);sources['observer/'+name] = path
        portable_primary.create_native_bundle(sources, output/'packed', dictionary_bytes=32*1024**2)
        after = prepare_closed_collection(fresh.manifest_path, fresh.manifest_sha256)
        require(after.captured.descriptor == fresh.captured.descriptor and after.source_snapshots == fresh.source_snapshots and
            after.fixture_snapshot == fresh.fixture_snapshot, 'closed_collection_original_inputs_changed')
        compare_released_lease(fresh.observation['released_lease'], after.observation['released_lease'])
        _finish_heartbeat(stop, thread, errors)
        require(shutil.disk_usage(output).free >= value['limits']['minimum_free_bytes']+FINALIZATION_RESERVE, 'closed_collection_disk_floor')
        allocated = sum(p.lstat().st_blocks*512 for p in output.rglob('*'))
        require(allocated+FINALIZATION_RESERVE <= value['limits']['maximum_output_bytes'], 'closed_collection_output_budget')
        artifacts = {'packed/primary.tar.xz':hashlib.sha256((output/'packed/primary.tar.xz').read_bytes()).hexdigest(),
            'packed/bundle.json':hashlib.sha256((output/'packed/bundle.json').read_bytes()).hexdigest(),
            'capture-proof.json':hashlib.sha256((output/'capture-proof.json').read_bytes()).hexdigest()}
    finally:
        stop.set();thread.join(timeout=15)
        registry.release(lease['token'], note='Closed Python validation metadata collected or failed; original job never launched/stopped/recovered by collector.')
    released = [r for r in resource_reservations.Reservations.read_snapshot(registry.path)['leases'] if r['token'] == lease['token']]
    require(len(released) == 1 and released[0]['state'] == 'released' and
        released[0]['owner'] == lease['owner'] and released[0]['resources'] == lease['resources'], 'closed_collection_own_lease_release')
    require(not thread.is_alive() and not errors, 'closed_collection_late_heartbeat_error')
    provenance._canonical(output)
    require((output.stat().st_dev, output.stat().st_ino) == output_identity, 'closed_collection_finalization_directory_changed')
    # Bounded controller finalization tail, as in owned_python_job: bulk writes
    # ended and ownership was released. Only two exclusive JSON control files
    # are now emitted. No original input or archive is written in this tail.
    receipt = {'kind':'closed_python_validation_collection_receipt', 'schema_version':1, 'collection_status':'completed',
        'collection_id':value['collection_id'], 'execution_root':value['execution_root'],
        'original_job_id':value['job']['id'], 'original_gate':fresh.outcome,
        'manifest_sha256':fresh.manifest_sha256, 'artifact_hashes':artifacts,
        'collection_released_lease':released[0], 'nested_kernel_closure_attested':False, 'scientific_verdict':None}
    final_record = _atomic_marker(output/'verification.json', receipt)
    artifacts['verification.json'] = final_record['sha256']
    record = _atomic_marker(output/'artifact-inventory.json', artifacts)  # LAST success marker
    result = {'kind':'closed_python_validation_collection_result', 'schema_version':1,
        'collection_status':'completed', 'original_gate_outcome':fresh.outcome['gate_outcome'],
        'original_tests':fresh.outcome['tests'], 'artifact_inventory':{'path':str(output/'artifact-inventory.json'), **record},
        'final_receipt':{'path':str(output/'verification.json'), **final_record}, 'collection_released_lease':released[0],
        'Git_index_or_ref_mutations':False, 'nested_kernel_closure_attested':False, 'scientific_verdict':None}
    return result


def stage_collection_artifacts(output_root, repository):
    """Require durable final controls before the existing Git staging owner."""
    output = provenance._canonical(Path(output_root));repository = provenance._canonical(Path(repository))
    require(output.is_relative_to(repository), 'closed_collection_stage_repository')
    inventory_raw, inventory_record = provenance._frozen(output/'artifact-inventory.json', 1024**2)
    inventory = provenance._json(inventory_raw)
    require(set(inventory) == {'verification.json', 'capture-proof.json', 'packed/bundle.json', 'packed/primary.tar.xz'},
        'closed_collection_final_inventory_required')
    for name, digest in inventory.items():
        raw, record = provenance._frozen(output/name, 64*1024**2)
        require(record['sha256'] == digest, 'closed_collection_final_artifact_changed')
    receipt = _load(output/'verification.json')
    require(receipt.get('kind') == 'closed_python_validation_collection_receipt' and receipt.get('schema_version') == 1 and
        receipt.get('collection_status') == 'completed' and receipt.get('scientific_verdict') is None and
        receipt.get('nested_kernel_closure_attested') is False, 'closed_collection_final_receipt_required')
    require(receipt['artifact_hashes'] == {k:v for k,v in inventory.items() if k != 'verification.json'}, 'closed_collection_final_receipt_hashes')
    captured = _load(output/'capture-proof.json')
    require(captured['collection_status'] == 'capture_prepared' and captured['original_gate'] == receipt['original_gate'],
        'closed_collection_original_outcome_changed')
    ledger = resource_reservations.Reservations.read_snapshot(Path(receipt['execution_root'])/'resource-reservations.sqlite3')
    rows = [r for r in ledger['leases'] if r['job_id'] == receipt['collection_id']]
    require(len(rows) == 1, 'closed_collection_final_lease_missing')
    compare_released_lease(receipt['collection_released_lease'], rows[0])
    return publisher.stage_artifact_set(repository, (output/'artifact-inventory.json').relative_to(repository).as_posix(), inventory_record['sha256'])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    collect = commands.add_parser('collect')
    collect.add_argument('manifest', type=Path);collect.add_argument('--manifest-sha256', required=True)
    collect.add_argument('--output', required=True, type=Path)
    stage = commands.add_parser('stage')
    stage.add_argument('output', type=Path);stage.add_argument('--repository', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = (collect_prepared(prepare_closed_collection(args.manifest, args.manifest_sha256), args.output)
            if args.action == 'collect' else stage_collection_artifacts(args.output, args.repository))
    except (EvidenceError, OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError) as error:
        print(json.dumps({'kind':'closed_python_validation_collection_result', 'collection_status':'failed',
            'original_gate_outcome':'not_assessed', 'reason':str(error), 'scientific_verdict':None}))
        return 2
    print(json.dumps(result, allow_nan=False));return 0


if __name__ == '__main__':
    raise SystemExit(main())
