"""Real filesystem regressions for frozen native collection; WORKERS ONLY."""
import hashlib
import gzip
from pathlib import Path
import tempfile
import unittest

from .. import archive_retirement
from ..closed_native_collection import (verify_closed_namespace, _source_namespace,
                                       read_readonly_inventory, validate_original_roles)
from ..native_evidence import EvidenceError


class ClosedNativeNamespaceTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='native-frozen-namespace-')
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name).resolve()/'original'
        self.directory.mkdir()
        self.file = self.directory/'terminal.json'
        self.file.write_bytes(b'{"outcome":"failed"}\n')
        self.record = {'bytes': self.file.stat().st_size,
                       'sha256': hashlib.sha256(self.file.read_bytes()).hexdigest()}
        self.roles = [dict(root=str(self.directory), relative_path=self.file.name,
                          expected_bytes=self.record['bytes'], expected_sha256=self.record['sha256'])]

    def test_exact_regular_namespace_is_preserved(self):
        self.assertEqual(verify_closed_namespace(self.directory, self.roles, {}), {self.file.name: self.record})

    def test_new_undeclared_regular_file_is_not_silently_omitted(self):
        (self.directory/'.ignored-extra.log').write_bytes(b'new original evidence')
        with self.assertRaisesRegex(EvidenceError, 'regular_namespace_changed'):
            verify_closed_namespace(self.directory, self.roles, {})

    def test_missing_original_file_cannot_be_replaced_by_declared_metadata(self):
        self.file.unlink()
        with self.assertRaisesRegex(EvidenceError, 'regular_namespace_changed'):
            verify_closed_namespace(self.directory, self.roles, {})

    def test_modified_original_bytes_fail_without_rewriting_them(self):
        self.file.write_bytes(b'{"outcome":"passed"}\n')
        with self.assertRaisesRegex(EvidenceError, 'regular_namespace_changed'):
            verify_closed_namespace(self.directory, self.roles, {})
        self.assertEqual(self.file.read_bytes(), b'{"outcome":"passed"}\n')

    def test_retained_symlink_is_recorded_without_following_or_flattening(self):
        link = self.directory/'latest'
        link.symlink_to(self.file.name)
        links = {'latest': archive_retirement._link(link)}
        self.assertEqual(verify_closed_namespace(self.directory, self.roles, links), {self.file.name: self.record})
        self.assertTrue(link.is_symlink())

    def test_added_symlink_is_not_hidden_by_a_regular_only_inventory(self):
        (self.directory/'extra').symlink_to(self.file.name)
        with self.assertRaisesRegex(EvidenceError, 'link_namespace_changed'):
            verify_closed_namespace(self.directory, self.roles, {})

    def test_source_namespace_rejects_new_ignored_file(self):
        (self.directory/'__pycache__').mkdir()
        (self.directory/'__pycache__/extra.pyc').write_bytes(b'undeclared')
        with self.assertRaisesRegex(EvidenceError, 'source_namespace_changed'):
            _source_namespace(self.directory, {self.file.name: self.record})

    def test_source_namespace_never_follows_an_extra_file_link(self):
        (self.directory/'extra').symlink_to(self.file.name)
        with self.assertRaisesRegex(EvidenceError, 'source_file_link'):
            _source_namespace(self.directory, {self.file.name: self.record})

    def test_original_role_cannot_read_outside_its_reserved_original_roots(self):
        paths = {'native-output': str(self.directory), 'controller': str(self.directory.parent/'controller')}
        with self.assertRaisesRegex(EvidenceError, 'original_role_scope'):
            validate_original_roles(paths, [dict(root=str(self.directory.parent/'other'),
                relative_path='terminal.json', archive_path='native-output/terminal.json')])

    def test_original_role_cannot_disguise_a_controller_file_as_native_output(self):
        paths = {'native-output': str(self.directory), 'controller': str(self.directory.parent/'controller')}
        with self.assertRaisesRegex(EvidenceError, 'original_role_scope'):
            validate_original_roles(paths, [dict(root=paths['controller'], relative_path='terminal.json',
                                                archive_path='native-output/terminal.json')])

    def test_duplicate_archive_destination_cannot_silently_drop_an_original_role(self):
        paths = {'native-output': str(self.directory), 'controller': str(self.directory.parent/'controller')}
        role = dict(root=str(self.directory), relative_path='terminal.json', archive_path='native-output/terminal.json')
        with self.assertRaisesRegex(EvidenceError, 'original_archive_alias'):
            validate_original_roles(paths, [role, dict(role)])

    def test_inventory_expansion_cannot_exceed_its_declared_length(self):
        raw = b'{"retained":"original"}\n'
        packed = gzip.compress(raw)
        path = self.directory/'inventory.json.gz'; path.write_bytes(packed)
        declaration = dict(path=str(path), compressed_bytes=len(packed),
            compressed_sha256=hashlib.sha256(packed).hexdigest(), raw_bytes=len(raw)-1,
            raw_sha256=hashlib.sha256(raw[:-1]).hexdigest())
        with self.assertRaisesRegex(EvidenceError, 'inventory_expanded_digest'):
            read_readonly_inventory(declaration)

    def test_inventory_exact_bytes_are_read_without_synthesizing_fields(self):
        raw = b'{"retained":"original"}\n'
        packed = gzip.compress(raw)
        path = self.directory/'inventory.json.gz'; path.write_bytes(packed)
        declaration = dict(path=str(path), compressed_bytes=len(packed),
            compressed_sha256=hashlib.sha256(packed).hexdigest(), raw_bytes=len(raw),
            raw_sha256=hashlib.sha256(raw).hexdigest())
        self.assertEqual(read_readonly_inventory(declaration), {'retained': 'original'})

    def test_declared_build_role_allows_only_the_actual_CMake_cache(self):
        paths = {'native-output': str(self.directory), 'controller': str(self.directory.parent/'controller'),
                 'build': str(self.directory.parent/'build')}
        cache = dict(root=paths['build'], relative_path='CMakeCache.txt', archive_path='postclosure-build/CMakeCache.txt')
        validate_original_roles(paths, [cache])
        with self.assertRaisesRegex(EvidenceError, 'build_role_not_cache'):
            validate_original_roles(paths, [dict(root=paths['build'], relative_path='other-file',
                                                archive_path='postclosure-build/other-file')])
