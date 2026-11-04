"""Actual managed-unit lease, aggregate-cap and crash-recovery controls."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import unittest
import uuid

from ..contained_process import start, inspect, stop
from ..resource_reservations import Reservations, ReservationError
from . import test_process_runner as _process_fixture


MIB = 1024**2
CAPACITY = {"slots": 4, "memory_bytes": 1024*MIB, "disk_bytes": 64*MIB, "tasks": 512}
DEMANDS = {"slots": 1, "memory_bytes": 512*MIB, "disk_bytes": 32*MIB, "tasks": 256}


class ManagedUnitReservationsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        output = os.environ.get("TIMELEARNER_MANAGED_RESERVATION_OUTPUT")
        controller = os.environ.get("TIMELEARNER_TEST_CONTROLLER_DIRECTORY")
        legacy = os.environ.get("TIMELEARNER_LEGACY_RESERVATIONS_SOURCE")
        if not all((output, controller, legacy)):
            raise unittest.SkipTest("requires actual contained Linux owner and isolated registry output")
        cls.output, cls.controller, cls.legacy = Path(output), Path(controller), Path(legacy)
        cls.output.mkdir(parents=True, exist_ok=False)

    def setUp(self):
        self.root = self.output/self._testMethodName
        self.root.mkdir()
        self.owned = self.root/"owned"
        self.owned.mkdir()
        self.ini = self.root/"app.ini"
        self.ini.write_text("actual isolated system process control; no neural model\n")
        self.units = []
        self.addCleanup(self.close_units)

    def close_units(self):
        errors = []
        for directory in reversed(self.units):
            if not (directory/"request.json").exists():
                continue
            try:
                final = stop(directory)
                (directory/"test-final-membership.json").write_text(json.dumps(final, indent=2))
            except Exception as error:
                errors.append(str(error))
        if errors:
            raise RuntimeError(";".join(errors))

    def lease(self):
        registry = Reservations(self.root/"isolated.sqlite3", capacity=CAPACITY, managed_units=True)
        lease = registry.reserve("actual-managed-control", [{"path": str(self.owned), "access": "write"}],
                                 demands=DEMANDS, controller_directory=self.controller, ttl_seconds=300)
        return registry, lease["token"]

    def register(self, registry, token, name="native", *, memory=64*MIB, tasks=16, attempt=None):
        directory, attempt = self.owned/name, attempt or str(uuid.uuid4())
        registry.register_managed_intent(token, directory, attempt,
            memory_bytes=memory, tasks=tasks, maximum_wall_seconds=30)
        return directory, attempt

    def manifest(self, name="sleep.rs2", binary="/bin/sleep"):
        return _process_fixture.OwnedProcessTest.manifest(self, name, binary)

    def test_kernel_controller_and_task_budget_are_recorded(self):
        registry, token = self.lease()
        value = registry.inspect()
        self.assertEqual(value["schema_version"], 3)
        controller = value["leases"][0]["controller"]
        self.assertEqual(controller["binding"]["initial_main_pid"], os.getpid())
        self.assertEqual(controller["memory_bytes"], 256*MIB)
        self.assertEqual(controller["tasks"], 128)
        self.assertEqual(value["reserved"], DEMANDS)
        registry.release(token, note="No managed launch registered; actual controller context verified.")
        self.assertEqual(registry.inspect()["reserved"], dict.fromkeys(CAPACITY, 0))

    def test_old_api_cannot_open_or_release_schema3(self):
        registry, token = self.lease()
        spec = importlib.util.spec_from_file_location("legacy_resource_reservations_control", self.legacy)
        legacy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(legacy)
        before = registry.inspect()
        with self.assertRaises(legacy.ReservationError):
            legacy.Reservations(registry.path, capacity={k: v for k, v in CAPACITY.items() if k != "tasks"})
        self.assertEqual(registry.inspect()["leases"], before["leases"])
        registry.release(token, note="Old API schema refusal verified; no managed process launched.")

    def test_pending_unsubmitted_intent_cannot_release(self):
        registry, token = self.lease()
        _, attempt = self.register(registry, token)
        with self.assertRaisesRegex(ReservationError, "managed_unit_still_live_or_pending"):
            registry.release(token, note="Must refuse while a future launch remains registered.")
        registry.abort_managed_unsubmitted(token, attempt)
        registry.release(token, note="Unsubmitted launch explicitly aborted before release.")
        with self.assertRaisesRegex(ReservationError, "reservation_not_held"):
            registry.mark_managed_submitted(token, attempt)

    def test_live_unit_holds_runtime_until_actual_closure(self):
        registry, token = self.lease()
        directory = self.owned/"native"
        self.units.append(directory)
        binding = start(self.manifest(), ["20"], self.root, directory,
            memory_bytes=64*MIB, tasks=16, maximum_wall_seconds=30,
            managed_reservation=(registry, token))
        self.assertFalse(inspect(directory)["all_processes_closed"])
        record = registry.inspect()["managed_unit_intents"]
        self.assertEqual(len(record), 1)
        self.assertEqual(record[0]["state"], "bound")
        self.assertEqual(record[0]["intent"]["unit"], binding["unit"])
        with self.assertRaisesRegex(ReservationError, "managed_unit_still_live_or_pending"):
            registry.release(token, note="Native managed unit is live; runtime release must fail.")
        self.assertTrue(stop(directory)["all_processes_closed"])
        registry.release(token, note="All registered managed units and their kernel groups closed.")

    def test_aggregate_memory_counts_controller(self):
        registry, token = self.lease()
        with self.assertRaisesRegex(ReservationError, "managed_aggregate_budget_exhausted"):
            self.register(registry, token, memory=512*MIB)
        self.assertFalse((self.owned/"native").exists())
        registry.release(token, note="Oversized managed memory allocation refused before launch.")

    def test_aggregate_tasks_counts_controller(self):
        registry, token = self.lease()
        with self.assertRaisesRegex(ReservationError, "managed_aggregate_budget_exhausted"):
            self.register(registry, token, tasks=200)
        registry.release(token, note="Oversized aggregate task cap refused before launch.")

    def test_registered_launches_already_consume_aggregate_budget(self):
        registry, token = self.lease()
        _, first = self.register(registry, token, "first", memory=160*MIB)
        with self.assertRaisesRegex(ReservationError, "managed_aggregate_budget_exhausted"):
            self.register(registry, token, "second", memory=160*MIB)
        registry.abort_managed_unsubmitted(token, first)
        _, second = self.register(registry, token, "second", memory=160*MIB)
        registry.abort_managed_unsubmitted(token, second)
        registry.release(token, note="Both unused intents explicitly aborted; no native process started.")

    def test_intent_cannot_escape_write_reservation(self):
        registry, token = self.lease()
        with self.assertRaisesRegex(ReservationError, "managed_intent_outside_owned_output"):
            registry.register_managed_intent(token, self.root/"outside", str(uuid.uuid4()),
                memory_bytes=64*MIB, tasks=16, maximum_wall_seconds=30)
        registry.release(token, note="Unowned output path refused before managed launch.")

    def test_duplicate_intent_is_not_a_second_launch(self):
        registry, token = self.lease()
        directory, attempt = self.register(registry, token)
        with self.assertRaisesRegex(ReservationError, "managed_intent_already_registered"):
            registry.register_managed_intent(token, directory, attempt,
                memory_bytes=64*MIB, tasks=16, maximum_wall_seconds=30)
        registry.abort_managed_unsubmitted(token, attempt)
        registry.release(token, note="Duplicate launch registration refused.")

    def test_pre_submission_filesystem_failure_aborts_intent(self):
        registry, token = self.lease()
        manifest = self.manifest()
        self.owned.chmod(0o555)
        try:
            with self.assertRaises(PermissionError):
                start(manifest, ["20"], self.root, self.owned/"native", memory_bytes=64*MIB,
                      tasks=16, maximum_wall_seconds=30, managed_reservation=(registry, token))
        finally:
            self.owned.chmod(0o755)
        values = registry.inspect()["managed_unit_intents"]
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0]["state"], "aborted")
        registry.release(token, note="Actual mkdir failure before submission recorded as an aborted intent.")

    def test_legacy_ledger_cannot_claim_managed_graph(self):
        registry = Reservations(self.root/"legacy.sqlite3")
        lease = registry.reserve("legacy", [{"path": str(self.owned), "access": "write"}])
        with self.assertRaisesRegex(Exception, "managed_unit_ledger_v3_required"):
            start(self.manifest(), ["20"], self.root, self.owned/"native", memory_bytes=64*MIB,
                  tasks=16, maximum_wall_seconds=30, managed_reservation=(registry, lease["token"]))
        self.assertFalse((self.owned/"native").exists())
        registry.release(lease["token"], note="Legacy registry refused managed ownership context before launch.")

    def test_parent_exit_keeps_runtime_until_separate_managed_unit_closes(self):
        parent_unit, child_unit = self.root/"fault-parent-unit", self.owned/"fault-child-unit"
        params = {"source": str(Path(__file__).resolve().parents[4]), "root": str(self.root),
                  "owned": str(self.owned), "ini": str(self.ini),
                  "parent_unit": str(parent_unit), "child_unit": str(child_unit)}
        script = self.root/"fault-parent.py"
        script.write_text("from pathlib import Path\nimport sys,json\np=__PARAMS__\nsys.path.insert(0,p['source'])\nfrom Scripts.StructTrain.TimeLearner.resource_reservations import Reservations\nfrom Scripts.StructTrain.TimeLearner.contained_process import start\nfrom Scripts.StructTrain.TimeLearner.runtime import file_record,resolved_libraries,digest_json,runtime_content_identity\nout=Path(p['root']);capacity={'slots':1,'memory_bytes':512*1024**2,'disk_bytes':16*1024**2,'tasks':128};demands={'slots':1,'memory_bytes':256*1024**2,'disk_bytes':8*1024**2,'tasks':64}\nregistry=Reservations(out/'fault.sqlite3',capacity=capacity,managed_units=True)\nlease=registry.reserve('fault',[{'path':p['owned'],'access':'write'}],demands=demands,controller_directory=p['parent_unit'],ttl_seconds=300)\n(out/'fault-lease.json').write_text(json.dumps(lease,indent=2))\nmanifest={'schema_version':2,'source_closure':{'kind':'managed_unit_recovery_fault_control','native_models_executed':0},'executable':file_record(Path('/bin/sleep')),'app_ini':file_record(Path(p['ini'])),'compiler':file_record(Path('/usr/bin/c++')),'build_flags':{'role':'actual isolated sleep; not a neural model'},'resolved_libraries':resolved_libraries(Path('/bin/sleep')),'loaded_process_files':None,'loader_environment':{}}\nmanifest['runtime_identity']=runtime_content_identity(manifest);manifest['runtime_fingerprint']=digest_json(manifest['runtime_identity'])\nstart(manifest,['20'],out,p['child_unit'],memory_bytes=64*1024**2,tasks=16,maximum_wall_seconds=30,managed_reservation=(registry,lease['token']))\n(out/'parent-exits-with-child-live.json').write_text(json.dumps({'lease':lease['token'],'native_models_executed':0}))\n".replace("__PARAMS__", repr(params)))
        self.units.extend((parent_unit, child_unit))
        start(self.manifest("parent-python.rs2", sys.executable), [str(script)], self.root, parent_unit,
              memory_bytes=128*MIB, tasks=32, maximum_wall_seconds=30)
        deadline = time.monotonic()+20
        while not inspect(parent_unit)["all_processes_closed"]:
            self.assertLess(time.monotonic(), deadline)
            time.sleep(.05)
        self.assertTrue((self.root/"parent-exits-with-child-live.json").exists())
        self.assertFalse(inspect(child_unit)["all_processes_closed"])
        capacity = {"slots": 1, "memory_bytes": 512*MIB, "disk_bytes": 16*MIB, "tasks": 128}
        registry = Reservations(self.root/"fault.sqlite3", capacity=capacity, managed_units=True)
        token = json.loads((self.root/"fault-lease.json").read_text())["token"]
        with self.assertRaisesRegex(ReservationError, "managed_unit_still_live_or_pending") as refused:
            registry.recover_closed_worker(token, parent_unit,
                note="Reproduced baseline: managed child still live, so runtime must remain reserved.")
        (self.root/"recovery-refusal.json").write_text(json.dumps({"reason": str(refused.exception),
            "parent": inspect(parent_unit), "child": inspect(child_unit), "ledger": registry.inspect()}, indent=2))
        self.assertEqual(registry.inspect()["leases"][0]["state"], "held")
        self.assertTrue(stop(child_unit)["all_processes_closed"])
        event = registry.recover_closed_worker(token, parent_unit,
            note="Parent and every registered managed unit now have fresh kernel closure.")
        (self.root/"recovery-event.json").write_text(json.dumps(event, indent=2))
        self.assertTrue(event["managed_unit_graph"]["all_registered_units_closed"])
        self.assertEqual(len(event["managed_unit_graph"]["units"]), 1)
        self.assertEqual(registry.inspect()["leases"][0]["state"], "released")

    def test_changed_reservation_alias_is_rejected_before_direct_unit_launch(self):
        alias = self.root/"owned-link"
        alias.symlink_to(self.owned, target_is_directory=True)
        registry = Reservations(self.root/"alias.sqlite3", capacity=CAPACITY, managed_units=True)
        lease = registry.reserve("aliased-output", [{"path": str(alias), "access": "write"}],
            demands=DEMANDS, controller_directory=self.controller)
        other = self.root/"other"
        other.mkdir()
        alias.unlink()
        alias.symlink_to(other, target_is_directory=True)
        try:
            with self.assertRaisesRegex(ReservationError, "reservation_path_alias_changed"):
                start(self.manifest(), ["20"], self.root, self.owned/"native", memory_bytes=64*MIB,
                    tasks=16, maximum_wall_seconds=30, managed_reservation=(registry, lease["token"]))
            self.assertFalse((self.owned/"native").exists())
            self.assertEqual(registry.inspect()["managed_unit_intents"], [])
        finally:
            alias.unlink()
            alias.symlink_to(self.owned, target_is_directory=True)
        registry.release(lease["token"], note="Actual symlink change rejected before manager submission; alias restored.")
