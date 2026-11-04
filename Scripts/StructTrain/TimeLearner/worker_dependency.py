"""Read-only resource readiness of one exact, bound worker invocation.

Closed processes are not successful training. This module never releases a
lease, adopts a unit, reads a scientific verdict or starts the next job.
"""
from pathlib import Path

from .contained_process import inspect as inspect_contained, _request
from .native_evidence import require


def inspect_worker_dependency(directory, registry, job_id, *, reservation_optional=False):
    """Inspect the initial worker's lease in its declared persistent registry.

    A missing receipt file is not used as evidence. Registry history distinguishes
    a never-created reservation from a held/released one. Optional reservations
    are explicit for workers that may stop at a prerequisite before reserving.
    Business success must be checked separately using the producer's auditor.
    """
    require(type(job_id) is str and 1 <= len(job_id) <= 128 and
            not any(ord(c) < 32 for c in job_id), 'invalid_dependency_job_id')
    require(type(reservation_optional) is bool, 'invalid_dependency_reservation_policy')
    directory = Path(directory).resolve(strict=True)
    closure = inspect_contained(directory)
    _, request = _request(directory)
    binding = closure['binding']
    require(binding['request_sha256'] == request['sha256'], 'dependency_invocation_changed')
    # The declared job id is an attempt identifier. It must not ambiguously
    # select another owner or two reservations made by the same invocation.
    leases = registry.inspect()['leases']
    rows = [row for row in leases if row['job_id'] == job_id]
    expected = {'pid': binding['initial_main_pid'], 'start_ticks': binding['initial_start_ticks'],
                'boot_id': request['boot_id'], 'uid': request['uid']}
    result = {'kind': 'timelearner_worker_dependency_state', 'schema_version': 1,
              'job_id': job_id, 'contained_directory': str(directory),
              'registry': str(registry.path.resolve()), 'closure': closure,
              'reservation_optional': reservation_optional,
              'reservation_state': None, 'reservation_token': None,
              'state': 'pending', 'reason': None,
              'successful_execution_attested': False, 'scientific_verdict': None}
    if not closure['all_processes_closed']:
        return {**result, 'reason': 'dependency_worker_group_still_live'}
    if len(rows) > 1:
        return {**result, 'state': 'refused', 'reason': 'dependency_reservation_ambiguous'}
    if not rows:
        if any(all(row['owner'].get(k) == v for k, v in expected.items()) for row in leases):
            return {**result, 'state': 'refused', 'reason': 'dependency_job_id_mismatch'}
        return {**result, 'reservation_state': 'not_created',
                'state': 'ready' if reservation_optional else 'refused',
                'reason': 'dependency_closed_without_reservation' if reservation_optional else
                          'dependency_required_reservation_missing'}
    lease = rows[0]
    owner = lease['owner']
    require(type(owner) is dict, 'dependency_reservation_owner_missing')
    if any(owner.get(k) != v for k, v in expected.items()):
        return {**result, 'state': 'refused', 'reason': 'dependency_reservation_owner_mismatch'}
    result.update(reservation_state=lease['state'], reservation_token=lease['token'])
    if lease['state'] == 'held':
        return {**result, 'reason': 'dependency_closed_lease_still_held'}
    require(lease['state'] == 'released', 'dependency_unknown_reservation_state')
    return {**result, 'state': 'ready', 'reason': 'dependency_closed_lease_released'}
