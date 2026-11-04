"""Actual Git snapshots using whole, pinned Pulse headers/sources; no models."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from ..inventory import build_inventory
from ..native_evidence import EvidenceError


class InventorySnapshotTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = os.environ.get('TIMELEARNER_INVENTORY_PULSE_SOURCE')
        if not source:
            raise unittest.SkipTest('requires pinned whole Pulse source files from an actual Git repository')
        cls.source = Path(source).resolve(strict=True)
        cls.source_commit = subprocess.check_output(['git', '-C', str(cls.source), 'rev-parse', 'HEAD'], text=True).strip()
        cls.raw_sources = {}
        for component in ('NNeuronTimeLearner', 'NNeuronTimeLearnerBranch'):
            for suffix in ('.h', '.cpp'):
                path = 'Core/'+component+suffix
                cls.raw_sources[path] = subprocess.check_output(['git', '-C', str(cls.source), 'show', cls.source_commit+':'+path])

    def git(self, repository, *args):
        return subprocess.check_output(['git', '-C', str(repository), *args], stderr=subprocess.PIPE).decode().strip()

    def commit(self, repository):
        self.git(repository, 'add', '.')
        self.git(repository, '-c', 'user.name=Inventory Fixture', '-c', 'user.email=inventory@localhost',
                 'commit', '-qm', 'Immutable Git metadata fixture')
        return self.git(repository, 'rev-parse', 'HEAD')

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='timelearner-inventory-')
        self.addCleanup(temporary.cleanup)
        self.temporary = Path(temporary.name)
        self.root = self.temporary/'root';self.root.mkdir()
        self.bin = self.root/'Bin';self.bin.mkdir()
        self.pulse = self.root/'Libraries/Nmsdk-PulseLib';self.pulse.mkdir(parents=True)
        for repo in (self.root, self.bin, self.pulse):self.git(repo, 'init', '-q')
        self.script = 'Configs/SpikeSamples/StructTrain/scripts/old.py'
        path = self.bin/self.script;path.parent.mkdir(parents=True)
        path.write_text('raise RuntimeError("must never execute archived code")\n')
        self.bin_commit = self.commit(self.bin)
        for name, raw in self.raw_sources.items():
            path = self.pulse/name;path.parent.mkdir(parents=True, exist_ok=True);path.write_bytes(raw)
        self.pulse_commit = self.commit(self.pulse)
        (self.root/'.gitmodules').write_text(
            '[submodule "Bin"]\n\tpath = Bin\n\turl = fixture-bin\n'
            '[submodule "Pulse"]\n\tpath = Libraries/Nmsdk-PulseLib\n\turl = fixture-pulse\n')
        path = self.root/'Docs/StructTrain/TimeLearner/tool.py';path.parent.mkdir(parents=True)
        path.write_text('raise RuntimeError("catalog only")\n')
        self.root_commit = self.commit(self.root)

    def test_clean_snapshot_has_exact_gitlinks_full_property_sources_and_content_hashes(self):
        value = build_inventory(self.root)
        self.assertEqual(value['schema_version'], 2)
        self.assertEqual(value['root_revision'], self.root_commit)
        self.assertEqual(value['repositories']['Bin']['commit'], self.bin_commit)
        self.assertEqual(value['repositories']['PulseLib']['commit'], self.pulse_commit)
        self.assertEqual(len(value['properties']), 217)
        self.assertEqual(len(value['property_sources']), 4)
        for row in value['property_sources']:
            self.assertEqual(row['commit'], self.pulse_commit)
            self.assertEqual(row['sha256'], hashlib.sha256(self.raw_sources[row['path']]).hexdigest())
        row = next(r for r in value['scripts'] if r['repository']=='Bin')
        raw = self.git(self.bin, 'show', self.bin_commit+':'+self.script).encode()+b'\n'
        self.assertEqual(row['content_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(row['bytes'], len(raw))

    def test_staged_new_script_and_dirty_content_do_not_enter_a_committed_catalog(self):
        before = build_inventory(self.root)
        (self.bin/self.script).write_text('uncommitted replacement')
        new = self.bin/'Configs/SpikeSamples/StructTrain/scripts/staged.py';new.write_text('not committed')
        self.git(self.bin, 'add', '.')
        after = build_inventory(self.root)
        self.assertEqual(after['scripts'], before['scripts'])
        self.assertTrue(after['repositories']['Bin']['tracked_working_tree_status'])

    def test_different_child_head_is_reported_but_root_recorded_commit_supplies_scripts(self):
        new = self.bin/'Configs/SpikeSamples/StructTrain/scripts/new.py';new.write_text('another commit')
        actual = self.commit(self.bin)
        value = build_inventory(self.root)
        self.assertEqual(value['repositories']['Bin']['checkout_head'], actual)
        self.assertFalse(value['repositories']['Bin']['checkout_matches_snapshot'])
        self.assertEqual(value['repositories']['Bin']['commit'], self.bin_commit)
        self.assertNotIn(new.relative_to(self.bin).as_posix(), {r['old_path'] for r in value['scripts']})

    def test_invalid_working_header_cannot_corrupt_the_committed_property_catalog(self):
        before = build_inventory(self.root)
        (self.pulse/'Core/NNeuronTimeLearner.h').write_text('invalid working file: not a component declaration')
        after = build_inventory(self.root)
        self.assertEqual(before['properties'], after['properties'])
        self.assertEqual(before['property_sources'], after['property_sources'])
        self.assertTrue(after['repositories']['PulseLib']['tracked_working_tree_status'])

    def test_explicit_old_root_revision_pins_both_root_and_child_trees(self):
        (self.bin/'Configs/SpikeSamples/StructTrain/scripts/new.py').write_text('new revision')
        self.commit(self.bin)
        new = self.root/'Docs/StructTrain/TimeLearner/later.py';new.write_text('later root')
        self.commit(self.root)
        value = build_inventory(self.root, self.root_commit)
        self.assertEqual(value['repositories']['Bin']['commit'], self.bin_commit)
        self.assertFalse(value['repositories']['root']['checkout_matches_snapshot'])
        self.assertNotIn(new.relative_to(self.root).as_posix(), {r['old_path'] for r in value['scripts']})

    def test_child_directory_alias_to_root_is_rejected(self):
        self.pulse.rename(self.temporary/'saved-pulse');self.pulse.mkdir()
        with self.assertRaisesRegex(EvidenceError, 'inventory_repository_alias_mismatch:PulseLib'):
            build_inventory(self.root)

    def test_missing_recorded_commit_is_not_replaced_by_the_available_child_head(self):
        self.bin.rename(self.temporary/'saved-bin');self.bin.mkdir()
        self.git(self.bin, 'init', '-q')
        (self.bin/'README').write_text('unrelated object store')
        self.commit(self.bin)
        with self.assertRaisesRegex(EvidenceError, 'inventory_git_read_failed:cat-file'):build_inventory(self.root)

    def test_executable_shebang_without_suffix_and_unicode_spaces_are_catalogued_without_execution(self):
        path = self.root/'Docs/StructTrain/TimeLearner/печать модели'
        path.write_text('#!/usr/bin/env python3\nraise RuntimeError("read only")\n')
        self.git(self.root, 'add', '.')
        self.git(self.root, 'update-index', '--chmod=+x', path.relative_to(self.root).as_posix())
        self.git(self.root, '-c', 'user.name=Inventory Fixture', '-c', 'user.email=inventory@localhost',
                 'commit', '-qm', 'Executable shebang fixture')
        value = build_inventory(self.root)
        row = next(r for r in value['scripts'] if r['old_path']==path.relative_to(self.root).as_posix())
        self.assertEqual(row['mode'], '100755')
        self.assertFalse(row['symlink'])

    def test_public_cli_writes_schema_two_and_bad_revision_creates_no_receipt(self):
        output = self.temporary/'inventory.json'
        args = [sys.executable, '-m', 'Scripts.StructTrain.TimeLearner', 'inventory', '--root', str(self.root),
                '--revision', self.root_commit, '--output', str(output)]
        completed = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(output.read_text())['root_revision'], self.root_commit)
        output.unlink();args[args.index(self.root_commit)] = 'HEAD'
        completed = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assertEqual(json.loads(completed.stderr)['reason'], 'inventory_full_root_commit_required')
        self.assertFalse(output.exists())
