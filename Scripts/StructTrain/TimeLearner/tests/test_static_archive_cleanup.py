"""Filesystem and real reservation gates for duplicate static-archive removal."""
import json
from pathlib import Path
import tempfile
import unittest

from ..static_archive_cleanup import make_plan, apply_plan
from ..resource_reservations import Reservations, ReservationError


class StaticArchiveCleanupTest(unittest.TestCase):
    def fixture(self, root):
        for name, raw in [('runtime-old', b'!<arch>\nduplicate'),
                          ('runtime-current', b'!<arch>\nduplicate'),
                          ('runtime-unique', b'!<arch>\nunique')]:
            folder = root/name/'Lib.CMake';folder.mkdir(parents=True)
            (folder/'libx.a').write_bytes(raw)
            (folder/'NeuroModelerConsole').write_bytes(b'keep executable')
        (root/'results.csv').write_text('primary data')
        registry = Reservations(root/'registry.sqlite3')
        lease = registry.reserve('cleanup', [{'path': str(root), 'access': 'write'}])
        return registry, lease['token']

    def test_only_confirmed_retired_duplicate_removed_with_journal_and_retained_copy(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t);registry, token = self.fixture(root)
            plan = make_plan(root, ['runtime-old', 'runtime-unique'])
            self.assertEqual(len(plan['rows']), 1)
            result = apply_plan(plan, registry, token, root/'journal.jsonl')
            self.assertEqual(result['files_removed'], 1)
            self.assertFalse((root/'runtime-old/Lib.CMake/libx.a').exists())
            self.assertEqual((root/'runtime-current/Lib.CMake/libx.a').read_bytes(), b'!<arch>\nduplicate')
            self.assertTrue((root/'runtime-unique/Lib.CMake/libx.a').exists())
            self.assertTrue((root/'runtime-old/Lib.CMake/NeuroModelerConsole').exists())
            self.assertEqual((root/'results.csv').read_text(), 'primary data')
            events = [json.loads(v)['event'] for v in (root/'journal.jsonl').read_text().splitlines()]
            self.assertEqual(events, ['validated_plan', 'unlink_intent', 'unlinked', 'complete'])

    def test_changed_target_or_keeper_refused_before_any_deletion(self):
        for side in ['target', 'keeper']:
            with self.subTest(side=side), tempfile.TemporaryDirectory() as t:
                root = Path(t);registry, token = self.fixture(root)
                plan = make_plan(root, ['runtime-old'])
                (root/plan['rows'][0][side]['path']).write_bytes(b'!<arch>\nchanged!')
                with self.assertRaisesRegex(ValueError, 'archive_preimage_changed'):
                    apply_plan(plan, registry, token, root/'journal.jsonl')
                self.assertTrue((root/'runtime-old/Lib.CMake/libx.a').exists())
                self.assertFalse((root/'journal.jsonl').exists())

    def test_missing_or_read_only_lease_cannot_delete(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t);registry, token = self.fixture(root);plan = make_plan(root, ['runtime-old'])
            registry.release(token, note='negative control')
            with self.assertRaises(ReservationError):
                apply_plan(plan, registry, token, root/'journal.jsonl')
            read = registry.reserve('read', [{'path': str(root), 'access': 'read'}])
            with self.assertRaisesRegex(ValueError, 'whole_root_write_lease'):
                apply_plan(plan, registry, read['token'], root/'journal.jsonl')

    def test_symlink_hardlink_and_thin_archive_are_not_eligible(self):
        for case in ['symlink', 'hardlink', 'thin']:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as t:
                root = Path(t);self.fixture(root);path = root/'runtime-old/Lib.CMake/libx.a'
                if case == 'symlink':
                    path.unlink();path.symlink_to(root/'runtime-current/Lib.CMake/libx.a')
                elif case == 'hardlink':
                    (path.parent/'libalias.a').hardlink_to(path)
                else:
                    path.write_bytes(b'!<thin>\nnot eligible')
                with self.assertRaises(ValueError):
                    make_plan(root, ['runtime-old'])

    def test_plan_cannot_delete_keeper_or_escape_root(self):
        for case in ['keeper', 'escape', 'nonretired']:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as t:
                root = Path(t);registry, token = self.fixture(root);plan = make_plan(root, ['runtime-old'])
                row = plan['rows'][0]
                if case == 'keeper':
                    row['keeper'] = row['target'].copy()
                elif case == 'escape':
                    row['target']['path'] = '../runtime-old/Lib.CMake/libx.a'
                else:
                    plan['retired_runtimes'] = ['runtime-unique']
                with self.assertRaises(ValueError):
                    apply_plan(plan, registry, token, root/'journal.jsonl')
                self.assertTrue((root/'runtime-old/Lib.CMake/libx.a').exists())

    def test_if_all_copies_retired_one_is_still_retained(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t);self.fixture(root)
            plan = make_plan(root, ['runtime-old', 'runtime-current'])
            self.assertEqual(len(plan['rows']), 1)
            self.assertNotEqual(plan['rows'][0]['keeper']['path'], plan['rows'][0]['target']['path'])
