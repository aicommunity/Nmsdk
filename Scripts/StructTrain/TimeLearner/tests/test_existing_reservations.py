"""Existing worker ledger policy: actual SQLite, no neural simulations."""
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

from ..resource_reservations import Reservations, ReservationError


@unittest.skipUnless(sys.platform == 'linux', 'actual worker identity required')
class ExistingReservationsTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='timelearner-existing-ledger-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_reopen_all_schemas_preserves_capacity_and_held_ownership(self):
        for schema in (1, 2, 3):
            with self.subTest(schema=schema):
                capacity = None if schema == 1 else {'slots': 2, 'memory_bytes': 2**30, 'disk_bytes': 2**30}
                if schema == 3: capacity['tasks'] = 128
                registry = Reservations(self.root/str(schema), capacity=capacity, managed_units=schema == 3)
                # Schema3 reserve needs an actual managed controller. Its opening
                # contract is checked here; managed graph fixtures cover ownership.
                if schema != 3:
                    kwargs = {} if capacity is None else {'demands': {'slots': 1, 'memory_bytes': 1, 'disk_bytes': 1}}
                    registry.reserve('held', [{'path': str(self.root/'runtime'), 'access': 'read'}], **kwargs)
                reopened = Reservations.open_existing(registry.path, managed_units=schema == 3)
                self.assertEqual(reopened.capacity, capacity)
                self.assertEqual(reopened.inspect()['leases'], registry.inspect()['leases'])

    def test_absent_path_is_not_created_and_alias_is_rejected(self):
        absent = self.root/'missing'/'ledger.sqlite'
        with self.assertRaisesRegex(ReservationError, 'existing_database_required'):
            Reservations.open_existing(absent)
        self.assertFalse(absent.parent.exists())
        registry = Reservations(self.root/'actual')
        alias = self.root/'alias'; alias.symlink_to(registry.path)
        with self.assertRaisesRegex(ReservationError, 'database_symlink'):
            Reservations.open_existing(alias)

    def test_unknown_worker_schema_and_metadata_are_not_adopted(self):
        for key, value in [('worker_host', 'different-worker'), ('schema_version', '99'), ('extra', 'unknown')]:
            database = self.root/key
            Reservations(database)
            with sqlite3.connect(database) as connection:
                connection.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)', (key, value))
                expected = list(connection.execute('SELECT * FROM metadata ORDER BY key'))
            with self.assertRaises(ReservationError): Reservations.open_existing(database)
            with sqlite3.connect(database) as connection:
                self.assertEqual(list(connection.execute('SELECT * FROM metadata ORDER BY key')), expected)

    def test_managed_mode_requires_explicit_agreement(self):
        capacity = {'slots': 1, 'memory_bytes': 2**30, 'disk_bytes': 2**30, 'tasks': 128}
        managed = Reservations(self.root/'managed', capacity=capacity, managed_units=True)
        with self.assertRaisesRegex(ReservationError, 'managed_policy_mismatch'):
            Reservations.open_existing(managed.path)
        legacy = Reservations(self.root/'legacy')
        with self.assertRaisesRegex(ReservationError, 'managed_policy_mismatch'):
            Reservations.open_existing(legacy.path, managed_units=True)

    def test_corrupt_capacity_and_changed_filesystem_are_rejected(self):
        for key, value in [('capacity', '{broken'), ('capacity', json.dumps({'slots': 1})), ('disk_device', '-1')]:
            database = self.root/('ledger-'+str(len(list(self.root.iterdir()))))
            Reservations(database, capacity={'slots': 2, 'memory_bytes': 2**30, 'disk_bytes': 2**30})
            with sqlite3.connect(database) as connection:
                connection.execute('UPDATE metadata SET value=? WHERE key=?', (value, key))
            with self.assertRaises(ReservationError): Reservations.open_existing(database)

    def test_nonledger_database_is_not_initialized(self):
        database = self.root/'empty.sqlite'
        with sqlite3.connect(database) as connection: connection.execute('CREATE TABLE other (x)')
        with self.assertRaisesRegex(ReservationError, 'metadata_unreadable'):
            Reservations.open_existing(database)
        with sqlite3.connect(database) as connection:
            self.assertEqual(list(connection.execute("SELECT name FROM sqlite_master WHERE type='table'")), [('other',)])
