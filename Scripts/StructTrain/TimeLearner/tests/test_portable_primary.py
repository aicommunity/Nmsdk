"""Archive corruption and the actual dereferenced glog-alias regression."""
import contextlib
from copy import deepcopy
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

from ..model_identity import canonical_model_sha256 as signed_digest
from ..native_evidence import EvidenceError
from ..portable_primary import ALIAS_ADAPTER, main, restore_native_bundle


class PortablePrimaryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        fixture = Path(__file__).parent/'fixtures/portable_primary'
        self.provenance = json.loads((fixture/'source.json').read_text())
        self.files = {}
        for row in self.provenance['members']:
            compressed = (fixture/row['path']).read_bytes()
            self.assertEqual(hashlib.sha256(compressed).hexdigest(), row['gzip_sha256'])
            raw = gzip.decompress(compressed)
            self.assertEqual(len(raw), row['raw_bytes'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['raw_sha256'])
            self.files[row['source_member']] = raw
        self.alias = next(n for n in self.files if n.endswith('/NeuroModeler.INFO'))
        self.target = next(n for n in self.files if '.log.INFO.' in n)
        self.manifest = next(n for n in self.files if n.endswith('/run-manifest.json'))
        self.owner = next(n for n in self.files if n.endswith('/owned-process.json'))

    def bundle(self, files=None, entries=None, inventory=None):
        files = self.files if files is None else files
        entries = list(files) if entries is None else entries
        archive = self.root/'primary.tar.xz'
        with tarfile.open(archive, 'w:xz') as stream:
            for entry in entries:
                if isinstance(entry, tarfile.TarInfo):
                    stream.addfile(entry)
                else:
                    data = files[entry]; member = tarfile.TarInfo(entry); member.size = len(data)
                    stream.addfile(member, io.BytesIO(data))
        bundle = {'members': {n: {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
                              for n, raw in files.items()},
                  'archive_bytes': archive.stat().st_size, 'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest()}
        if inventory is not None:
            bundle['members'] = inventory
        path = self.root/'bundle.json'; path.write_text(json.dumps(bundle))
        return path

    def reject(self, bundle, reason):
        with self.assertRaisesRegex(EvidenceError, reason):
            restore_native_bundle(bundle, self.root/'out', compatibility=ALIAS_ADAPTER)

    def changed_manifest(self, files, change):
        manifest = json.loads(files[self.manifest]); change(manifest)
        manifest.pop('sha256'); manifest['sha256'] = signed_digest(manifest)
        files[self.manifest] = json.dumps(manifest).encode()

    def test_real_archived_alias_is_redundant_and_source_bytes_stay_unchanged(self):
        bundle = self.bundle(); before = (self.root/'primary.tar.xz').read_bytes()
        result = restore_native_bundle(bundle, self.root/'out', compatibility=ALIAS_ADAPTER)
        self.assertEqual(result['archive_members_verified'], 4)
        self.assertEqual(len(result['omitted_redundant_aliases']), 1)
        self.assertFalse(result['omitted_redundant_aliases'][0]['original_symlink_target_attested'])
        self.assertFalse(result['native_execution_attested'])
        self.assertFalse((self.root/'out'/self.alias).exists())
        for name, raw in self.files.items():
            if name != self.alias:
                self.assertEqual((self.root/'out'/name).read_bytes(), raw)
        self.assertEqual((self.root/'primary.tar.xz').read_bytes(), before)

    def test_adapter_requires_explicit_selection_and_refuses_unknown_version(self):
        bundle = self.bundle()
        for adapter, reason in [(None, 'explicit_adapter'), ('guessed', 'unknown_bundle_restoration_adapter')]:
            with self.assertRaisesRegex(EvidenceError, reason):
                restore_native_bundle(bundle, self.root/'out', compatibility=adapter)
        self.assertFalse((self.root/'out').exists())

    def test_plain_bundle_needs_no_adapter(self):
        files = {n: v for n, v in self.files.items() if n != self.alias}
        result = restore_native_bundle(self.bundle(files), self.root/'out')
        self.assertIsNone(result['compatibility'])
        self.assertEqual(result['omitted_redundant_aliases'], [])

    def test_archive_hash_mismatch_is_rejected_before_output_creation(self):
        path = self.bundle(); value = json.loads(path.read_text()); value['archive_sha256'] = '0'*64
        path.write_text(json.dumps(value)); self.reject(path, 'archive_hash_mismatch')
        self.assertFalse((self.root/'out').exists())

    def test_corrupt_member_hash_and_missing_member_are_rejected(self):
        path = self.bundle(entries=[n for n in self.files if n != self.alias])
        self.reject(path, 'bundle_member_missing')

    def test_member_digest_is_checked_even_if_archive_hash_matches(self):
        path = self.bundle(); value = json.loads(path.read_text()); value['members'][self.target]['sha256'] = '0'*64
        path.write_text(json.dumps(value)); self.reject(path, 'member_hash_mismatch')

    def test_parent_escape_and_absolute_member_paths_are_rejected(self):
        for name in ('../outside', '/outside', 'x\\outside', 'x/../outside'):
            with self.subTest(name=name):
                path = self.bundle(files={name: b'x'}); self.reject(path, 'member_path_invalid')
        self.assertFalse((self.root/'out').exists())

    def test_duplicate_archive_member_is_rejected(self):
        self.reject(self.bundle(entries=list(self.files)+[self.alias]), 'type_duplicate_or_unknown')

    def test_symlink_archive_member_cannot_introduce_external_target(self):
        member = tarfile.TarInfo(self.alias); member.type = tarfile.SYMTYPE; member.linkname = '/outside'
        self.reject(self.bundle(entries=[member]), 'type_duplicate_or_unknown')

    def test_alias_bytes_must_match_retained_owner_log(self):
        files = dict(self.files); files[self.alias] += b'changed'
        self.reject(self.bundle(files), 'target_missing_or_ambiguous')

    def test_alias_cannot_remove_a_declared_primary_artifact(self):
        files = dict(self.files)
        self.changed_manifest(files, lambda m: m['artifacts'].append(
            {'path': 'native.events-log/EventsLog/NeuroModeler.INFO', 'bytes': len(files[self.alias]),
             'sha256': hashlib.sha256(files[self.alias]).hexdigest()}))
        self.reject(self.bundle(files), 'alias_not_redundant')

    def test_owner_pid_and_owner_inventory_are_mandatory(self):
        files = dict(self.files); owner = json.loads(files[self.owner]); owner['pid'] += 1
        files[self.owner] = json.dumps(owner).encode()
        self.reject(self.bundle(files), 'owner_inventory_mismatch')

    def test_two_matching_retained_targets_are_ambiguous(self):
        files = dict(self.files); other = self.target.replace('20261106-075133', '20261106-075134')
        files[other] = files[self.target]
        self.changed_manifest(files, lambda m: m['artifacts'].append(
            {'path': other.split('/phases/train/', 1)[1], 'bytes': len(files[other]),
             'sha256': hashlib.sha256(files[other]).hexdigest()}))
        self.reject(self.bundle(files), 'target_missing_or_ambiguous')

    def test_existing_output_is_never_modified_and_cli_returns_structured_failure(self):
        bundle = self.bundle(); output = self.root/'out'; output.mkdir(); (output/'keep').write_bytes(b'keep')
        capture = io.StringIO()
        with contextlib.redirect_stdout(capture):
            status = main([str(bundle), str(output), '--compatibility', ALIAS_ADAPTER])
        self.assertEqual(status, 2)
        self.assertEqual(json.loads(capture.getvalue())['reason'], 'bundle_output_already_exists')
        self.assertEqual((output/'keep').read_bytes(), b'keep')
