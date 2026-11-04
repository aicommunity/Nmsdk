"""Real worker-local SQLite/process/path reservation controls; no neural runs."""
import json
import multiprocessing
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest

from ..resource_reservations import ReservationError, Reservations


def _contend(database, resource, ready, release, results, name):
    registry = Reservations(database)
    ready.wait(10)
    try:
        lease = registry.reserve(name, [{'path': resource, 'access': 'write'}])
    except ReservationError as error:
        results.put(('refused', str(error)))
        return
    results.put(('held', name))
    if not release.wait(10):
        raise RuntimeError('test did not release its private writer')
    registry.release(lease['token'], note='test operation completed')


@unittest.skipUnless(sys.platform == 'linux', 'actual Linux /proc worker identity required')
class ResourceReservationsTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='timelearner-reservations-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.database = self.root/'ledger.sqlite'
        self.registry = Reservations(self.database)
        self.resource = self.root/'runtime';self.resource.mkdir()

    def reserve(self, name, access='write', path=None, **kwargs):
        return self.registry.reserve(name, [{'path': str(path or self.resource), 'access': access}], **kwargs)

    def test_readers_share_immutable_runtime_but_prevent_redeployment(self):
        one, two = self.reserve('probe-one', 'read'), self.reserve('probe-two', 'read')
        with self.assertRaisesRegex(ReservationError, 'resource_conflict'):self.reserve('deploy')
        self.registry.release(one['token'], note='probe completed')
        with self.assertRaisesRegex(ReservationError, 'resource_conflict'):self.reserve('deploy')
        self.registry.release(two['token'], note='probe completed')
        self.assertEqual(self.reserve('deploy')['state'], 'held')

    def test_descendant_write_blocks_parent_read_and_sibling_is_independent(self):
        self.reserve('build', path=self.resource/'build')
        with self.assertRaisesRegex(ReservationError, 'resource_conflict'):self.reserve('source-reader', 'read')
        self.reserve('other-tree', path=self.root/'runtime-other')
        self.assertEqual(len(self.registry.inspect()['leases']), 2)

    def test_expired_heartbeat_keeps_the_reservation_and_can_be_renewed_by_owner(self):
        lease = self.reserve('slow-probe', ttl_seconds=.001)
        time.sleep(.02)
        row = self.registry.inspect()['leases'][0]
        self.assertTrue(row['heartbeat_expired']);self.assertTrue(row['inspection_required'])
        self.assertEqual(row['owner_status'], 'identity_live')
        with self.assertRaisesRegex(ReservationError, 'resource_conflict'):self.reserve('replacement')
        self.registry.heartbeat(lease['token'], ttl_seconds=60)
        self.assertFalse(self.registry.inspect()['leases'][0]['heartbeat_expired'])

    def test_job_identity_cannot_be_silently_reused_after_release(self):
        lease = self.reserve('attempt-one')
        self.registry.release(lease['token'], note='operation ended; no science claim')
        with self.assertRaisesRegex(ReservationError, 'job_already_recorded'):self.reserve('attempt-one')
        with self.assertRaisesRegex(ReservationError, 'not_held'):self.registry.heartbeat(lease['token'])
        self.assertEqual(self.reserve('attempt-two')['state'], 'held')

    def test_symlink_alias_conflicts_with_its_actual_runtime(self):
        alias = self.root/'runtime-alias';alias.symlink_to(self.resource, target_is_directory=True)
        lease = self.reserve('probe', 'read', alias)
        self.assertEqual(lease['resources'][0]['canonical_path'], str(self.resource))
        with self.assertRaisesRegex(ReservationError, 'resource_conflict'):self.reserve('deploy')

    def test_changed_path_alias_is_rejected_before_using_the_lease(self):
        alias = self.root/'alias';alias.symlink_to(self.resource, target_is_directory=True)
        lease = self.reserve('probe', 'read', alias)
        alias.unlink();alias.symlink_to(self.root/'different-runtime', target_is_directory=True)
        with self.assertRaisesRegex(ReservationError, 'path_alias_changed'):self.registry.validate_paths(lease['token'])

    def test_a_new_directory_can_be_created_without_changing_its_reserved_identity(self):
        path = self.root/'new-runtime';lease = self.reserve('deploy', path=path)
        path.mkdir()
        self.assertTrue(self.registry.validate_paths(lease['token']))

    def test_a_crashed_owner_does_not_grant_permission_to_replace_its_runtime(self):
        code = ('import sys,json;from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations;'
                'r=Reservations(sys.argv[1]);print(json.dumps(r.reserve("crashed-owner",'
                '[{"path":sys.argv[2],"access":"read"}],ttl_seconds=.001)),flush=True)')
        result = subprocess.run([sys.executable, '-c', code, str(self.database), str(self.resource)],
                                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=20)
        lease = json.loads(result.stdout)
        row = Reservations(self.database).inspect()['leases'][0]
        self.assertIn(row['owner_status'], ('missing', 'exited'))
        self.assertTrue(row['inspection_required']);self.assertEqual(row['state'], 'held')
        with self.assertRaisesRegex(ReservationError, 'resource_conflict'):self.reserve('replacement')
        with self.assertRaisesRegex(ReservationError, 'not_owned_by_caller'):
            self.registry.release(lease['token'], note='caller is not the exited supervisor')

    def test_another_live_process_cannot_use_the_owners_token(self):
        lease = self.reserve('owner')
        code = ('import sys;from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations;'
                'Reservations(sys.argv[1]).release(sys.argv[2],note="foreign caller")')
        result = subprocess.run([sys.executable, '-c', code, str(self.database), lease['token']],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=20)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('reservation_not_owned_by_caller', result.stderr)
        self.assertEqual(self.registry.inspect()['leases'][0]['state'], 'held')

    def test_two_real_contenders_cannot_both_own_the_same_build_tree(self):
        context = multiprocessing.get_context('spawn')
        ready, release, results = context.Event(), context.Event(), context.Queue()
        processes = [context.Process(target=_contend, args=(str(self.database), str(self.resource), ready, release, results, str(i))) for i in range(2)]
        try:
            for process in processes:process.start()
            ready.set();rows = [results.get(timeout=20) for _ in processes]
            self.assertEqual(sorted(r[0] for r in rows), ['held', 'refused'])
            self.assertEqual(next(r[1] for r in rows if r[0] == 'refused'), 'reservation_resource_conflict')
            release.set()
            for process in processes:process.join(timeout=20);self.assertEqual(process.exitcode, 0)
        finally:
            release.set()
            for process in processes:
                if process.is_alive():process.terminate();process.join(timeout=5)
            results.close();results.join_thread()

    def test_failed_transaction_does_not_leave_a_partial_reservation(self):
        self.reserve('one')
        with self.assertRaisesRegex(ReservationError, 'resource_conflict'):self.reserve('two')
        self.assertEqual([r['job_id'] for r in self.registry.inspect()['leases']], ['one'])

    def test_unknown_schema_or_worker_is_refused_by_existing_and_new_connections(self):
        with sqlite3.connect(self.database) as connection:
            connection.execute('UPDATE metadata SET value=\'unknown\' WHERE key=\'schema_version\'')
        for call in (lambda:Reservations(self.database), self.registry.inspect):
            with self.assertRaisesRegex(ReservationError, 'schema_or_worker_changed'):call()

    def test_database_symlink_is_not_an_independent_ledger(self):
        alias = self.root/'other.sqlite';alias.symlink_to(self.database)
        with self.assertRaisesRegex(ReservationError, 'database_symlink'):Reservations(alias)

    def test_invalid_requests_never_create_a_reservation(self):
        for ttl in (True, 0, float('nan'), float('inf')):
            with self.assertRaises(ReservationError):self.reserve('invalid', ttl_seconds=ttl)
        for resources in ([], [{'path': str(self.resource), 'access': 'exclusive'}],
                          [{'path': str(self.resource), 'access': 'read'}, {'path': str(self.resource), 'access': 'write'}]):
            with self.assertRaises(ReservationError):self.registry.reserve('invalid', resources)
        self.assertEqual(self.registry.inspect()['leases'], [])
