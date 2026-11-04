"""Durable worker-local read/write reservations for source/build/runtime trees.

Expiry and a missing supervisor never release resources automatically. This is
the reservation layer, not a dispatcher, child-process recovery or a scientific
result. Clients must hold it for the entire operation and validate path aliases
before using them. Unregistered filesystem writers are outside its authority.
"""
from contextlib import contextmanager
import json
import math
import os
from pathlib import Path
import socket
import sqlite3
import time
import uuid


class ReservationError(RuntimeError):
    pass


def _require(value, reason):
    if not value:
        raise ReservationError(reason)


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def _ttl(value):
    _require(type(value) in (int, float) and math.isfinite(value) and value > 0, 'invalid_reservation_ttl')
    return value


def _quantities(value, *, capacity=False):
    _require(type(value) is dict and set(value) == {'slots', 'memory_bytes', 'disk_bytes'} and
             all(type(v) is int and 0 <= v <= 2**63-1 for v in value.values()) and
             value['slots'] > 0 and (not capacity or all(v > 0 for v in value.values())),
             'invalid_reservation_capacity' if capacity else 'invalid_reservation_demands')
    return dict(value)


def _identity():
    _require(os.name == 'posix' and Path('/proc/self/stat').exists(), 'linux_worker_required')
    pid = os.getpid()
    return {'pid': pid, 'start_ticks': Path(f'/proc/{pid}/stat').read_text().rsplit(') ', 1)[1].split()[19],
            'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(), 'uid': os.getuid(),
            'executable': str(Path(f'/proc/{pid}/exe').resolve(strict=True))}


def _owner_status(owner):
    try:
        if owner['boot_id'] != Path('/proc/sys/kernel/random/boot_id').read_text().strip():
            return 'boot_changed'
        proc = Path('/proc', str(owner['pid']))
        fields = (proc/'stat').read_text().rsplit(') ', 1)[1].split()
        if fields[19] != owner['start_ticks']:
            return 'pid_reused'
        if fields[0] in ('Z', 'X'):
            return 'exited'
        if proc.stat().st_uid != owner['uid'] or str((proc/'exe').resolve(strict=True)) != owner['executable']:
            return 'identity_changed'
        return 'identity_live'
    except (FileNotFoundError, ProcessLookupError):
        return 'missing'
    except (PermissionError, OSError):
        return 'unknown'


def _resources(values):
    _require(type(values) is list and 1 <= len(values) <= 64, 'invalid_reservation_resources')
    result, seen = [], set()
    for value in values:
        _require(type(value) is dict and set(value) == {'path', 'access'} and value['access'] in ('read', 'write') and
                 type(value['path']) is str and value['path'] and '\0' not in value['path'], 'invalid_reservation_resource')
        requested = Path(value['path']).absolute()
        canonical = requested.resolve(strict=False)
        _require(not canonical.exists() or canonical.is_dir(), 'reservation_requires_directory_tree')
        _require(str(canonical) not in seen, 'duplicate_reservation_resource')
        seen.add(str(canonical))
        result.append({'requested_path': str(requested), 'canonical_path': str(canonical), 'access': value['access']})
    return sorted(result, key=lambda row: row['canonical_path'])


def _overlap(left, right):
    a, b = Path(left), Path(right)
    return a == b or a.is_relative_to(b) or b.is_relative_to(a)


def _disk_device(path):
    path = Path(path)
    while not path.exists():
        path = path.parent
    return path.stat().st_dev


class Reservations:
    """One SQLite WAL ledger on a local filesystem per worker; never on NFS."""
    @property
    def capacity(self):
        return dict(self._capacity) if self._capacity is not None else None

    def __init__(self, database, *, capacity=None):
        _identity()  # Reject unsupported workers before creating any ledger files.
        self.requested_path = Path(database).absolute()
        _require(not self.requested_path.is_symlink(), 'reservation_database_symlink')
        self.path = self.requested_path.resolve(strict=False)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.host = socket.gethostname()
        self._capacity = _quantities(capacity, capacity=True) if capacity is not None else None
        self.disk_device = self.path.parent.stat().st_dev if capacity is not None else None
        self.schema = '2' if self.capacity is not None else '1'
        self.metadata = {'schema_version': self.schema, 'worker_host': self.host}
        if self.capacity is not None:
            self.metadata['capacity'] = _json(self.capacity)
            self.metadata['disk_device'] = str(self.disk_device)
        self._initialized = False
        with self._transaction() as connection:
            connection.execute('CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
            connection.execute('CREATE TABLE IF NOT EXISTS leases ('
                               'token TEXT PRIMARY KEY, job_id TEXT UNIQUE NOT NULL, owner TEXT NOT NULL, '
                               'resources TEXT NOT NULL, state TEXT NOT NULL CHECK(state IN (\'held\',\'released\')), '
                               'created REAL NOT NULL, deadline REAL NOT NULL, updated REAL NOT NULL, release_note TEXT'+
                               (', demands TEXT NOT NULL' if self.capacity is not None else '')+')')
            for key, value in self.metadata.items():
                connection.execute('INSERT OR IGNORE INTO metadata VALUES (?,?)', (key, value))
                _require(connection.execute('SELECT value FROM metadata WHERE key=?', (key,)).fetchone()[0] == value,
                         'reservation_ledger_schema_or_worker_changed')
        self._initialized = True

    @contextmanager
    def _transaction(self):
        _require(not self.requested_path.is_symlink(), 'reservation_database_symlink')
        _require(self.requested_path.resolve(strict=False) == self.path, 'reservation_database_alias_changed')
        if self.capacity is not None:
            _require(self.path.parent.stat().st_dev == self.disk_device, 'reservation_database_filesystem_changed')
        connection = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        connection.row_factory = sqlite3.Row
        try:
            _require(connection.execute('PRAGMA journal_mode=WAL').fetchone()[0] == 'wal', 'reservation_wal_unavailable')
            connection.execute('PRAGMA synchronous=FULL')
            connection.execute('BEGIN IMMEDIATE')
            if self._initialized:
                for key, expected in self.metadata.items():
                    row = connection.execute('SELECT value FROM metadata WHERE key=?', (key,)).fetchone()
                    _require(row is not None and row[0] == expected, 'reservation_ledger_schema_or_worker_changed')
            yield connection
            connection.execute('COMMIT')
        except BaseException:
            if connection.in_transaction:
                connection.execute('ROLLBACK')
            raise
        finally:
            connection.close()

    @staticmethod
    def _decode(row):
        value = dict(row)
        try:
            value['owner'], value['resources'] = json.loads(value['owner']), json.loads(value['resources'])
            owner = value['owner']
            _require(set(owner) == {'pid', 'start_ticks', 'boot_id', 'uid', 'executable'} and
                     type(owner['pid']) is int and owner['pid'] > 0 and type(owner['uid']) is int and owner['uid'] >= 0 and
                     type(owner['start_ticks']) is str and owner['start_ticks'].isdigit() and
                     str(uuid.UUID(owner['boot_id'])) == owner['boot_id'] and
                     type(owner['executable']) is str and Path(owner['executable']).is_absolute(), 'corrupt_reservation_owner')
            _require(value['state'] in ('held', 'released') and type(value['resources']) is list and value['resources'] and
                     all(type(r) is dict and set(r) == {'requested_path', 'canonical_path', 'access'} and
                         all(type(r[k]) is str and Path(r[k]).is_absolute() for k in ('requested_path', 'canonical_path')) and
                         '..' not in Path(r['canonical_path']).parts and r['access'] in ('read', 'write') for r in value['resources']),
                     'corrupt_reservation_resources')
            if 'demands' in value:
                value['demands'] = _quantities(json.loads(value['demands']))
        except (ValueError, TypeError, KeyError) as error:
            raise ReservationError('corrupt_reservation_record') from error
        return value

    def reserve(self, job_id, resources, *, ttl_seconds=30, demands=None):
        _require(type(job_id) is str and 1 <= len(job_id) <= 128 and
                 not any(ord(c) < 32 for c in job_id), 'invalid_reservation_job_id')
        resources = _resources(resources);ttl_seconds = _ttl(ttl_seconds)
        if self.capacity is None:
            _require(demands is None, 'reservation_budget_policy_required')
        else:
            demands = _quantities(demands)
            self._validate_disk_resources(resources)
        owner, now, token = _identity(), time.time(), str(uuid.uuid4())
        with self._transaction() as connection:
            _require(connection.execute('SELECT 1 FROM leases WHERE job_id=?', (job_id,)).fetchone() is None,
                     'reservation_job_already_recorded')
            used = {key: 0 for key in self.capacity or {}}
            for row in connection.execute('SELECT * FROM leases WHERE state=\'held\''):
                held = self._decode(row)
                _require(not any(_overlap(a['canonical_path'], b['canonical_path']) and
                                 'write' in (a['access'], b['access']) for a in resources for b in held['resources']),
                         'reservation_resource_conflict')
                for key in used:
                    used[key] += held['demands'][key]
            if self.capacity is not None:
                _require(all(used[key]+demands[key] <= self.capacity[key] for key in used),
                         'reservation_capacity_exhausted')
            values = (token, job_id, _json(owner), _json(resources), 'held', now, now+ttl_seconds, now)
            connection.execute('INSERT INTO leases VALUES (?,?,?,?,?,?,?,?,NULL'+
                               (',?' if self.capacity is not None else '')+')',
                               values+((_json(demands),) if self.capacity is not None else ()))
        return {'token': token, 'job_id': job_id, 'owner': owner, 'resources': resources, 'state': 'held',
                **({'demands': demands} if self.capacity is not None else {}), 'scientific_verdict': None}

    def _owned(self, connection, token):
        _require(type(token) is str, 'invalid_reservation_token')
        row = connection.execute('SELECT * FROM leases WHERE token=?', (token,)).fetchone()
        _require(row is not None, 'reservation_token_unknown')
        value = self._decode(row)
        _require(value['state'] == 'held', 'reservation_not_held')
        _require(value['owner'] == _identity(), 'reservation_not_owned_by_caller')
        return value

    def heartbeat(self, token, *, ttl_seconds=30):
        ttl_seconds = _ttl(ttl_seconds)
        with self._transaction() as connection:
            self._owned(connection, token)
            now = time.time()
            connection.execute('UPDATE leases SET updated=?,deadline=? WHERE token=?', (now, now+ttl_seconds, token))

    def validate_paths(self, token):
        with self._transaction() as connection:
            value = self._owned(connection, token)
            _require(all(str(Path(r['requested_path']).resolve(strict=False)) == r['canonical_path']
                         for r in value['resources']), 'reservation_path_alias_changed')
            if self.capacity is not None:
                self._validate_disk_resources(value['resources'])
        return True

    def _validate_disk_resources(self, resources):
        # One disk budget covers one actual filesystem, not the sum of free
        # space on unrelated system and archive disks. Multi-volume jobs need
        # an explicit future policy; they must not silently borrow this budget.
        _require(all(r['access'] == 'read' or _disk_device(r['canonical_path']) == self.disk_device
                     for r in resources), 'reservation_disk_filesystem_mismatch')

    def release(self, token, *, note):
        _require(type(note) is str and bool(note.strip()) and len(note) <= 1024, 'reservation_release_reason_required')
        with self._transaction() as connection:
            self._owned(connection, token)
            connection.execute('UPDATE leases SET state=\'released\',updated=?,release_note=? WHERE token=?',
                               (time.time(), note, token))

    def inspect(self):
        with self._transaction() as connection:
            values = [self._decode(row) for row in connection.execute('SELECT * FROM leases ORDER BY created,token')]
        now = time.time()
        for value in values:
            value['heartbeat_expired'] = value['deadline'] < now
            value['owner_status'] = _owner_status(value['owner'])
            value['inspection_required'] = value['state'] == 'held' and (value['heartbeat_expired'] or value['owner_status'] != 'identity_live')
            value['scientific_verdict'] = None
        result = {'kind': 'timelearner_worker_resource_reservations', 'schema_version': int(self.schema), 'worker_host': self.host,
                'leases': values, 'automatic_release_on_expiry': False, 'execution_attested': False, 'scientific_verdict': None}
        if self.capacity is not None:
            used = {key: sum(v['demands'][key] for v in values if v['state'] == 'held') for key in self.capacity}
            _require(all(used[key] <= self.capacity[key] for key in used), 'reservation_capacity_exhausted')
            result.update(capacity=dict(self.capacity), reserved=used,
                          available={key: self.capacity[key]-used[key] for key in used},
                          disk_device=self.disk_device,
                          os_resource_limits_enforced=False)
        return result
