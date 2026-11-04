"""Actual Linux unit/SQLite dependency states, no mocks or neural execution."""
import json
import os
from pathlib import Path
import shutil
import sys
import unittest

from . import test_contained_process as fixtures
from ..contained_process import inspect as inspect_contained, stop
from ..resource_reservations import Reservations
from ..worker_dependency import inspect_worker_dependency


@unittest.skipUnless(sys.platform == 'linux', 'real Linux worker required')
class WorkerDependencyTest(unittest.TestCase):
    setUp = fixtures.ContainedProcessTest.setUp
    manifest = fixtures.ContainedProcessTest.manifest
    launch = fixtures.ContainedProcessTest.launch
    wait = fixtures.ContainedProcessTest.wait

    def close_units(self):
        fixtures.ContainedProcessTest.close_units(self)
        evidence = os.environ.get('TIMELEARNER_CONTAINED_EVIDENCE_DIR')
        database = self.root/'leases.sqlite3'
        if evidence and database.is_file():
            destination = Path(evidence)/self._testMethodName
            shutil.copyfile(database, destination/'leases.sqlite3')
            registry = self.registry()
            (destination/'lease-readback.json').write_text(json.dumps(registry.inspect(), indent=2))
            (destination/'recovery-history.json').write_text(json.dumps(registry.recovery_history(), indent=2))

    def observe(self, output, registry, job_id, **options):
        result = inspect_worker_dependency(output, registry, job_id, **options)
        number = len(list(self.root.glob('dependency-*.json')))
        (self.root/('dependency-'+str(number)+'.json')).write_text(json.dumps(result, indent=2))
        return result

    def registry(self):
        return Reservations(self.root/'leases.sqlite3')

    def reserving_worker(self, *, twice=False, child=False):
        script = self.root/'reserve.py'
        script.write_text('import json,sys,subprocess\nfrom pathlib import Path\n'
            'sys.path.insert(0,'+repr(str(Path(__file__).resolve().parents[4]))+')\n'
            'from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations,ReservationError\n'
            'r=Reservations('+repr(str(self.root/'leases.sqlite3'))+')\n'
            'values=[]\n'
            'for i in range('+str(2 if twice else 1)+'):\n'
            ' try:\n'
            '  values.append(r.reserve("actual-dependency",[{"path":'+repr(str(self.root))+
            '+"/scratch-"+str(i),"access":"write"}],ttl_seconds=.001))\n'
            ' except ReservationError as error:\n'
            '  Path('+repr(str(self.root/'duplicate-rejection.json'))+').write_text(json.dumps({"reason":str(error)}))\n'
            '  break\n'
            'Path('+repr(str(self.root/'leases.json'))+').write_text(json.dumps(values))\n'+
            ('subprocess.Popen(["/bin/sleep","20"],start_new_session=True)\n' if child else ''))
        output = self.launch([str(script)], manifest=self.manifest('worker.rs2', sys.executable))
        self.wait((self.root/'leases.json').exists)
        self.wait(lambda:inspect_contained(output)['state'].get('MainPID') == '0')
        return output, self.registry(), json.loads((self.root/'leases.json').read_text())

    def test_live_unreserved_worker_is_never_ready(self):
        output = self.launch()
        result = self.observe(output, self.registry(), 'unreserved', reservation_optional=True)
        self.assertEqual(result['state'], 'pending')
        self.assertEqual(result['reason'], 'dependency_worker_group_still_live')

    def test_closed_worker_without_optional_reservation_is_explicit(self):
        output = self.launch(['.05']);self.wait(lambda:inspect_contained(output)['all_processes_closed'])
        registry = self.registry()
        result = self.observe(output, registry, 'unreserved', reservation_optional=True)
        self.assertEqual((result['state'], result['reservation_state']), ('ready', 'not_created'))
        self.assertFalse(result['successful_execution_attested'])
        self.assertEqual(registry.inspect()['leases'], [])
        self.assertEqual(registry.recovery_history(), [])

    def test_required_missing_reservation_refuses_closed_worker(self):
        output = self.launch(['.05']);self.wait(lambda:inspect_contained(output)['all_processes_closed'])
        result = self.observe(output, self.registry(), 'unreserved')
        self.assertEqual(result['state'], 'refused')
        self.assertEqual(result['reason'], 'dependency_required_reservation_missing')

    def test_held_expired_lease_requires_explicit_recovery(self):
        output, registry, leases = self.reserving_worker()
        self.wait(lambda:registry.inspect()['leases'][0]['heartbeat_expired'])
        before = registry.inspect()
        self.assertTrue(before['leases'][0]['heartbeat_expired'])
        result = self.observe(output, registry, 'actual-dependency')
        self.assertEqual((result['state'], result['reservation_state']), ('pending', 'held'))
        self.assertEqual(registry.recovery_history(), [])
        self.assertEqual([x['state'] for x in registry.inspect()['leases']], [x['state'] for x in before['leases']])
        registry.recover_closed_worker(leases[0]['token'], output, note='explicit test recovery after fresh closure')
        result = self.observe(output, registry, 'actual-dependency')
        self.assertEqual((result['state'], result['reservation_state']), ('ready', 'released'))
        self.assertEqual(result['reservation_token'], leases[0]['token'])

    def test_matching_job_id_cannot_select_a_different_owner(self):
        actual, registry, leases = self.reserving_worker()
        other = self.launch(['.05']);self.wait(lambda:inspect_contained(other)['all_processes_closed'])
        result = self.observe(other, registry, 'actual-dependency', reservation_optional=True)
        self.assertEqual(result['state'], 'refused')
        self.assertEqual(result['reason'], 'dependency_reservation_owner_mismatch')
        registry.recover_closed_worker(leases[0]['token'], actual, note='correct original unit')

    def test_wrong_job_id_cannot_hide_an_existing_worker_reservation(self):
        output, registry, leases = self.reserving_worker()
        result = self.observe(output, registry, 'wrong-attempt', reservation_optional=True)
        self.assertEqual((result['state'], result['reason']), ('refused', 'dependency_job_id_mismatch'))
        registry.recover_closed_worker(leases[0]['token'], output, note='original reservation retained')

    def test_registry_rejects_duplicate_job_without_losing_original_reservation(self):
        output, registry, leases = self.reserving_worker(twice=True)
        self.assertEqual(json.loads((self.root/'duplicate-rejection.json').read_text())['reason'],
                         'reservation_job_already_recorded')
        self.assertEqual(len(leases), 1)
        self.assertEqual(len(registry.inspect()['leases']), 1)
        result = self.observe(output, registry, 'actual-dependency')
        self.assertEqual((result['state'], result['reservation_state']), ('pending', 'held'))
        self.assertEqual(result['reservation_token'], leases[0]['token'])
        registry.recover_closed_worker(leases[0]['token'], output, note='original lease retained after duplicate refusal')

    def test_live_descendant_prevents_dependency_readiness(self):
        output, registry, leases = self.reserving_worker(child=True)
        self.assertFalse(inspect_contained(output)['all_processes_closed'])
        result = self.observe(output, registry, 'actual-dependency')
        self.assertEqual(result['state'], 'pending')
        stop(output)
        registry.recover_closed_worker(leases[0]['token'], output, note='entire original group closed')
        self.assertEqual(self.observe(output, registry, 'actual-dependency')['state'], 'ready')

    def test_nonzero_exit_is_not_manufactured_into_business_success(self):
        output = self.launch(['-c', 'raise SystemExit(7)'], manifest=self.manifest('failure.rs1', sys.executable))
        self.wait(lambda:inspect_contained(output)['all_processes_closed'])
        result = self.observe(output, self.registry(), 'unreserved', reservation_optional=True)
        self.assertEqual(result['state'], 'ready')
        self.assertFalse(result['successful_execution_attested'])
        self.assertIsNone(result['scientific_verdict'])
