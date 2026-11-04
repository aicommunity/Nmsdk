"""Real Linux owner death and cgroup descendants, with production SQLite API."""
import json
from pathlib import Path
import sqlite3
import sys
import unittest
import uuid

from . import test_contained_process as contained_fixture
from ..contained_process import inspect as inspect_contained, stop
from ..resource_reservations import Reservations, ReservationError


@unittest.skipUnless(sys.platform == 'linux', 'actual Linux cgroup worker required')
class ClosedWorkerRecoveryTest(unittest.TestCase):
    setUp = contained_fixture.ContainedProcessTest.setUp
    close_units = contained_fixture.ContainedProcessTest.close_units
    manifest = contained_fixture.ContainedProcessTest.manifest
    launch = contained_fixture.ContainedProcessTest.launch
    wait = contained_fixture.ContainedProcessTest.wait

    def dead_worker(self, *, child=False, budget=False, contained=True):
        database = self.root/'leases.sqlite3'; receipt = self.root/'lease.json'
        capacity = {'slots': 1, 'memory_bytes': 1024, 'disk_bytes': 1024} if budget else None
        program = self.root/'reserve.py'
        program.write_text(
            'from pathlib import Path\nimport json,subprocess,sys\n'
            'sys.path.insert(0,'+repr(str(Path(__file__).resolve().parents[4]))+')\n'
            'from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations\n'
            'r=Reservations('+repr(str(database))+',capacity='+repr(capacity)+')\n'
            'lease=r.reserve("crashed-worker",[{"path":'+repr(str(self.root/'scratch'))+
            ',"access":"write"}],ttl_seconds=.001,demands='+
            repr({'slots': 1, 'memory_bytes': 256, 'disk_bytes': 512} if budget else None)+')\n'
            'Path('+repr(str(receipt))+').write_text(json.dumps(lease))\n'+
            ('subprocess.Popen(["/bin/sleep","20"],start_new_session=True)\n' if child else ''),
            encoding='utf-8')
        if contained:
            output = self.launch([str(program)], manifest=self.manifest('worker.rs2', sys.executable))
        else:
            import subprocess
            subprocess.run([sys.executable, str(program)], check=True)
            output = None
        self.wait(receipt.exists)
        if contained:
            self.wait(lambda:inspect_contained(output)['state'].get('MainPID') == '0')
        return Reservations(database, capacity=capacity), json.loads(receipt.read_text()), output

    def test_live_descendant_refuses_then_closed_group_recovers_and_persists_budget(self):
        registry, lease, output = self.dead_worker(child=True, budget=True)
        with self.assertRaisesRegex(ReservationError, 'descendants_not_closed'):
            registry.recover_closed_worker(lease['token'], output, note='explicit test recovery')
        self.assertEqual(registry.inspect()['reserved']['slots'], 1)
        self.assertEqual(registry.recovery_history(), [])
        stop(output)
        event = registry.recover_closed_worker(lease['token'], output, note='closed entire crashed worker')
        self.assertTrue(event['closure']['all_processes_closed'])
        self.assertIsNone(event['scientific_verdict'])
        self.assertFalse(event['successful_execution_attested'])
        reopened = Reservations(registry.path, capacity=registry.capacity)
        self.assertEqual(reopened.recovery_history(), [event])
        self.assertEqual(reopened.inspect()['reserved'], dict.fromkeys(registry.capacity, 0))
        self.assertEqual(reopened.inspect()['leases'][0]['state'], 'released')
        with self.assertRaisesRegex(ReservationError, 'reservation_not_held'):
            reopened.recover_closed_worker(lease['token'], output, note='duplicate recovery')

    def test_schema_one_closed_worker_recovers_without_capacity_migration(self):
        registry, lease, output = self.dead_worker()
        event = registry.recover_closed_worker(lease['token'], output, note='explicit schema one recovery')
        self.assertEqual(registry.inspect()['schema_version'], 1)
        self.assertEqual(Reservations(registry.path).recovery_history(), [event])

    def test_a_different_closed_unit_cannot_release_the_dead_owner(self):
        registry, lease, actual = self.dead_worker()
        other = self.launch(['.05'])
        self.wait(lambda:inspect_contained(other)['all_processes_closed'])
        with self.assertRaisesRegex(ReservationError, 'unit_does_not_own_worker'):
            registry.recover_closed_worker(lease['token'], other, note='wrong unit')
        self.assertEqual(registry.inspect()['leases'][0]['state'], 'held')
        registry.recover_closed_worker(lease['token'], actual, note='correct unit')

    def test_uncontained_dead_controller_stays_held_despite_a_closed_child_unit(self):
        registry, lease, _ = self.dead_worker(contained=False)
        unrelated = self.launch(['.05'])
        self.wait(lambda:inspect_contained(unrelated)['all_processes_closed'])
        with self.assertRaisesRegex(ReservationError, 'unit_does_not_own_worker'):
            registry.recover_closed_worker(lease['token'], unrelated, note='outside controller is not proven')
        self.assertEqual(registry.inspect()['leases'][0]['state'], 'held')
        self.assertEqual(registry.recovery_history(), [])

    def test_live_owner_and_missing_reason_cannot_be_recovered(self):
        registry = Reservations(self.root/'leases.sqlite3')
        lease = registry.reserve('live', [{'path': str(self.root/'scratch'), 'access': 'write'}])
        unit = self.launch(['.05'])
        self.wait(lambda:inspect_contained(unit)['all_processes_closed'])
        with self.assertRaisesRegex(ReservationError, 'owner_not_closed'):
            registry.recover_closed_worker(lease['token'], unit, note='live owner')
        with self.assertRaisesRegex(ReservationError, 'release_reason_required'):
            registry.recover_closed_worker(lease['token'], unit, note=' ')
        self.assertEqual(registry.recovery_history(), [])
        registry.release(lease['token'], note='normal owner release')

    def test_changed_boot_is_not_accepted_as_a_closed_worker(self):
        registry, lease, output = self.dead_worker()
        # Corrupt only this test fixture to represent an earlier boot; never
        # manually modify a production ledger to release a reservation.
        owner = dict(lease['owner'], boot_id=str(uuid.uuid4()))
        with sqlite3.connect(registry.path) as connection:
            connection.execute('UPDATE leases SET owner=? WHERE token=?', (json.dumps(owner), lease['token']))
        with self.assertRaisesRegex(ReservationError, 'worker_epoch_changed'):
            registry.recover_closed_worker(lease['token'], output, note='unknown previous boot')
        self.assertEqual(registry.inspect()['leases'][0]['state'], 'held')
        self.assertEqual(registry.recovery_history(), [])
