"""Production cold Train under the existing finite native ownership protocol.

Only signed training jobs are admitted. The host lease charges owner plus one
sequential native child and survives owner failure until all finite groups close.
An observed budget stop is distinct from a converged training result.
"""
import hashlib
from pathlib import Path

from .collector_provenance import _frozen, _json
from .native_evidence import load, require
from .native_pipeline_worker import run_job, validate_job


def validate_declaration(request):
    require(request['operation'] == 'train', 'finite_train_operation')
    cases = request['cases']
    names = {row['name'] for row in request['inputs']}
    require(type(cases) is list and 1 <= len(cases) <= 8 and
            all(type(row) is dict and set(row) == {'name', 'job_name'} and
                type(row['job_name']) is str and row['job_name'] in names for row in cases),
            'finite_train_cases')
    used = [row['job_name'] for row in cases]
    require(len(used) == len(set(used)) and set(used) == names, 'finite_train_input_roles')


def _bound_job(record, path):
    raw, observed = _frozen(path, 64*1024**2)
    require(observed['bytes'] == record['bytes'] and
            hashlib.sha256(raw).hexdigest() == record['sha256'], 'finite_train_job_changed')
    job = _json(raw)
    preflight = validate_job('train', job)
    return job, preflight


def preflight_jobs(request):
    """No allocation, native execution or generated code before these checks."""
    records = {row['name']: row for row in request['inputs']}
    return {case['name']: _bound_job(records[case['job_name']],
                Path(records[case['job_name']]['path']))[1] for case in request['cases']}


def run_case(request, row, runtime_path, output):
    output = Path(output)
    record = next(r for r in request['inputs'] if r['name'] == row['job_name'])
    job_path = output/'native-inputs'/row['job_name']
    _bound_job(record, job_path)
    policy = dict(kind='timelearner_native_process_policy', schema_version=1,
        backend='bound_cgroup', memory_bytes=request['limits']['leaf_memory_bytes'],
        tasks=request['limits']['leaf_tasks'], cooperative_capture=True)
    result = run_job('train', job_path, None, runtime_path, output/row['name'],
                     request['limits']['leaf_wall_seconds'], process_policy=policy)
    # The production auditor accepts a structured training budget stop, but a
    # timeout, OOM, missing model or incomplete observation cannot become valid.
    require(result['validity'] == 'valid' and result['analysis'] is not None and
            result['execution'] in ('completed', 'process_error'), 'finite_train_execution_unverified')
    from .uniform_profile_study import _condition
    from .native_calibration_worker import _write
    job, _ = _bound_job(record, job_path)
    initial = load(output/row['name']/'native/initial-state.json')['identity']
    condition = _condition(job, initial, load(Path(runtime_path)),
        native_memory_bytes=request['limits']['leaf_memory_bytes'],
        native_tasks=request['limits']['leaf_tasks'],
        process_wall_seconds=request['limits']['leaf_wall_seconds'])
    _write(output/(row['name']+'-condition.json'), condition)
    return result
