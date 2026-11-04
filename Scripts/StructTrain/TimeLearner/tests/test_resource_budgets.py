"""Actual local SQLite and competing-process controls, without neural models."""
import json
import multiprocessing
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest

from ..resource_reservations import ReservationError, Reservations


def _contend_budget(database, capacity, resource, ready, release, results, name):
    registry = Reservations(database, capacity=capacity)
    ready.wait(10)
    try:
        lease = registry.reserve(name, [{'path': resource, 'access': 'write'}],
                                 demands={'slots': 1, 'memory_bytes': 7, 'disk_bytes': 0})
    except ReservationError as error:
        results.put(('refused', str(error)))
        return
    results.put(('held', name))
    if not release.wait(10):
        raise RuntimeError('test did not close its budgeted operation')
    registry.release(lease['token'], note='budgeted operation completed')


@unittest.skipUnless(sys.platform == 'linux', 'actual Linux worker required')
class ResourceBudgetsTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='timelearner-budgets-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.database = self.root/'ledger.sqlite'
        self.capacity = {'slots': 4, 'memory_bytes': 10, 'disk_bytes': 20}
        self.registry = Reservations(self.database, capacity=self.capacity)

    def reserve(self, name, **demands):
        return self.registry.reserve(name, [{'path': str(self.root/name), 'access': 'write'}],
                                     demands={'slots': 1, 'memory_bytes': 0, 'disk_bytes': 0, **demands})

    def test_each_dimension_is_an_independent_limit(self):
        for dimension in self.capacity:
            with self.subTest(dimension=dimension):
                lease = self.reserve('full-'+dimension, **{dimension: self.capacity[dimension]})
                with self.assertRaisesRegex(ReservationError, 'capacity_exhausted'):
                    self.reserve('excess-'+dimension, **{dimension: 1})
                self.registry.release(lease['token'], note='dimension control complete')
        self.assertEqual(self.registry.inspect()['reserved'], dict.fromkeys(self.capacity, 0))

    def test_equality_fits_and_one_more_byte_is_refused_without_a_record(self):
        self.reserve('one', memory_bytes=4, disk_bytes=9)
        self.reserve('two', memory_bytes=6, disk_bytes=11)
        with self.assertRaisesRegex(ReservationError, 'capacity_exhausted'):
            self.reserve('three', memory_bytes=1)
        result = self.registry.inspect()
        self.assertEqual(result['reserved'], {'slots': 2, 'memory_bytes': 10, 'disk_bytes': 20})
        self.assertEqual(result['available'], {'slots': 2, 'memory_bytes': 0, 'disk_bytes': 0})
        self.assertEqual(len(result['leases']), 2)
        self.assertFalse(result['os_resource_limits_enforced'])

    def test_reopen_keeps_capacity_and_reservations(self):
        self.reserve('one', memory_bytes=10)
        reopened = Reservations(self.database, capacity=self.capacity)
        self.assertEqual(reopened.inspect(), self.registry.inspect())
        with self.assertRaisesRegex(ReservationError, 'capacity_exhausted'):
            reopened.reserve('two', [{'path': str(self.root/'two'), 'access': 'read'}],
                             demands={'slots': 1, 'memory_bytes': 1, 'disk_bytes': 0})

    def test_mutating_policy_or_returned_demands_cannot_change_the_ledger(self):
        self.capacity['slots'] = 999
        self.registry.capacity['slots'] = 999
        lease = self.reserve('one', memory_bytes=10)
        lease['demands']['memory_bytes'] = 0
        self.assertEqual(self.registry.inspect()['capacity']['slots'], 4)
        self.assertEqual(self.registry.inspect()['reserved']['memory_bytes'], 10)
        with self.assertRaisesRegex(ReservationError, 'capacity_exhausted'):
            self.reserve('two', memory_bytes=1)

    def test_budgeted_and_unbudgeted_clients_cannot_share_a_ledger(self):
        with self.assertRaisesRegex(ReservationError, 'schema_or_worker_changed'):
            Reservations(self.database)
        old = self.root/'old.sqlite'
        Reservations(old)
        with self.assertRaisesRegex(ReservationError, 'schema_or_worker_changed'):
            Reservations(old, capacity=self.capacity)
        self.assertEqual(Reservations(old).inspect()['schema_version'], 1)
        self.assertEqual(self.registry.inspect()['schema_version'], 2)

    def test_changing_any_capacity_requires_an_explicit_new_policy(self):
        for key in self.capacity:
            changed = dict(self.capacity);changed[key] += 1
            with self.assertRaisesRegex(ReservationError, 'schema_or_worker_changed'):
                Reservations(self.database, capacity=changed)
        with sqlite3.connect(self.database) as connection:
            connection.execute('UPDATE metadata SET value=? WHERE key=\'capacity\'', ('{}',))
        with self.assertRaisesRegex(ReservationError, 'schema_or_worker_changed'):
            self.registry.inspect()

    def test_invalid_capacities_and_demands_are_not_silently_coerced(self):
        for field in self.capacity:
            for invalid in (True, -1, 1.5, float('inf'), 2**63, '1'):
                value = dict(self.capacity);value[field] = invalid
                with self.assertRaises(ReservationError):
                    Reservations(self.root/'invalid.sqlite', capacity=value)
                with self.assertRaises(ReservationError):
                    self.registry.reserve('invalid', [{'path': str(self.root/'invalid'), 'access': 'read'}], demands=value)
        for invalid in (None, {}, {'slots': 1}, {**self.capacity, 'gpu': 1}, {**self.capacity, 'slots': 0}):
            with self.assertRaises(ReservationError):
                self.registry.reserve('invalid', [{'path': str(self.root/'invalid'), 'access': 'read'}], demands=invalid)
        self.assertEqual(self.registry.inspect()['leases'], [])

    def test_legacy_api_refuses_demands_without_budget_policy(self):
        legacy = Reservations(self.root/'legacy.sqlite')
        with self.assertRaisesRegex(ReservationError, 'budget_policy_required'):
            legacy.reserve('one', [{'path': str(self.root/'one'), 'access': 'write'}], demands=self.capacity)
        self.assertEqual(legacy.inspect()['leases'], [])

    def test_write_on_a_different_actual_filesystem_cannot_borrow_this_disk_budget(self):
        other = Path('/dev/shm')
        self.assertTrue(other.is_dir())
        self.assertNotEqual(other.stat().st_dev, self.root.stat().st_dev)
        with self.assertRaisesRegex(ReservationError, 'disk_filesystem_mismatch'):
            self.registry.reserve('foreign-write', [{'path': str(other/'timelearner-no-write'), 'access': 'write'}],
                                  demands={'slots': 1, 'memory_bytes': 0, 'disk_bytes': 1})
        self.assertEqual(self.registry.inspect()['leases'], [])
        # Reading an immutable source on another volume does not consume its space.
        self.registry.reserve('foreign-read', [{'path': str(other), 'access': 'read'}],
                              demands={'slots': 1, 'memory_bytes': 0, 'disk_bytes': 0})

    def test_copying_a_ledger_to_another_actual_filesystem_does_not_rebind_its_policy(self):
        with tempfile.TemporaryDirectory(prefix='timelearner-ledger-', dir='/dev/shm') as directory:
            target = Path(directory)/'copied.sqlite'
            self.assertNotEqual(target.parent.stat().st_dev, self.root.stat().st_dev)
            target.write_bytes(self.database.read_bytes())
            with self.assertRaisesRegex(ReservationError, 'schema_or_worker_changed'):
                Reservations(target, capacity=self.capacity)

    def test_expiry_preserves_all_demands_until_owner_releases(self):
        lease = self.registry.reserve('slow', [{'path': str(self.root/'slow'), 'access': 'read'}],
                                      demands=self.capacity, ttl_seconds=.001)
        time.sleep(.02)
        self.assertTrue(self.registry.inspect()['leases'][0]['heartbeat_expired'])
        with self.assertRaisesRegex(ReservationError, 'capacity_exhausted'):
            self.reserve('replacement')
        self.registry.heartbeat(lease['token'])
        self.registry.release(lease['token'], note='all owned work ended')
        self.assertEqual(self.reserve('new')['state'], 'held')

    def test_crashed_supervisor_keeps_its_capacity(self):
        code = ('import sys,json;from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations;'
                'r=Reservations(sys.argv[1],capacity=json.loads(sys.argv[2]));'
                'print(json.dumps(r.reserve("crashed",[{"path":sys.argv[3],"access":"read"}],'
                'demands=json.loads(sys.argv[2]))),flush=True)')
        result = subprocess.run([sys.executable, '-c', code, str(self.database), json.dumps(self.capacity), str(self.root/'crashed')],
                                check=True, capture_output=True, text=True, timeout=20)
        lease = json.loads(result.stdout)
        with self.assertRaisesRegex(ReservationError, 'capacity_exhausted'):
            self.reserve('replacement')
        self.assertTrue(self.registry.inspect()['leases'][0]['inspection_required'])
        with self.assertRaisesRegex(ReservationError, 'not_owned_by_caller'):
            self.registry.release(lease['token'], note='not the owner')

    def test_path_conflict_and_budget_are_one_atomic_decision(self):
        self.reserve('one', memory_bytes=1)
        with self.assertRaisesRegex(ReservationError, 'resource_conflict'):
            self.registry.reserve('refused', [{'path': str(self.root/'one'), 'access': 'read'}], demands=self.capacity)
        self.assertEqual(len(self.registry.inspect()['leases']), 1)
        self.assertEqual(self.registry.inspect()['reserved']['memory_bytes'], 1)
        self.assertEqual(self.reserve('refused', memory_bytes=9)['state'], 'held')

    def test_corrupt_demands_cannot_be_ignored_to_grant_another_job(self):
        self.reserve('one')
        for value in ('[]', '{}', '{"slots":true,"memory_bytes":0,"disk_bytes":0}', 'broken'):
            with sqlite3.connect(self.database) as connection:
                original = connection.execute('SELECT demands FROM leases').fetchone()[0]
                connection.execute('UPDATE leases SET demands=?', (value,))
            with self.assertRaises(ReservationError):self.reserve('replacement')
            with self.assertRaises(ReservationError):self.registry.inspect()
            with sqlite3.connect(self.database) as connection:
                connection.execute('UPDATE leases SET demands=?', (original,))

    def test_two_real_processes_cannot_overcommit_memory_on_distinct_paths(self):
        context = multiprocessing.get_context('spawn')
        ready, release, results = context.Event(), context.Event(), context.Queue()
        processes = [context.Process(target=_contend_budget, args=(str(self.database), self.capacity,
                     str(self.root/str(i)), ready, release, results, str(i))) for i in range(2)]
        try:
            for process in processes:process.start()
            ready.set();rows = [results.get(timeout=20) for _ in processes]
            self.assertEqual(sorted(r[0] for r in rows), ['held', 'refused'])
            self.assertEqual(next(r[1] for r in rows if r[0] == 'refused'), 'reservation_capacity_exhausted')
            release.set()
            for process in processes:process.join(timeout=20);self.assertEqual(process.exitcode, 0)
            self.assertEqual(self.registry.inspect()['reserved'], dict.fromkeys(self.capacity, 0))
        finally:
            release.set()
            for process in processes:
                if process.is_alive():process.terminate();process.join(timeout=5)
            results.close();results.join_thread()
