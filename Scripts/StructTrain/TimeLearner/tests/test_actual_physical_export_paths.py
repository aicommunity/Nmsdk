"""Path rejection through the production runner and actual export controls.

These metadata tests use the real prepared input directory. They never start
the model; the positive export has its own native roundtrip acceptance.
"""
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..native_evidence import EvidenceError
from ..prepared_physical_export import run


class ActualPhysicalExportPaths(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.name != 'posix':
            raise ValueError('actual_Linux_export_controls_required')
        controls = Path(os.environ['TIMELEARNER_PHYSICAL_EXPORT_CONTROLS']).resolve(strict=True)
        cls.spec = json.loads((controls/'specification.json').read_bytes())
        cls.base = Path(cls.spec['execution_root'])
        if cls.base != Path('/home/user/Nmsdk-experiments') or not Path(cls.spec['inputs']).is_dir():
            raise ValueError('actual_approved_Branch_export_fixture_required')

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='physical-export-paths-', dir=self.base/'readbacks')
        self.root = Path(self.temporary.name)
        self.controls = self.root/'controls'; self.controls.mkdir()
        self.output = self.root/'never-created-output'

    def tearDown(self):
        self.assertEqual(self.root.parent, self.base/'readbacks')
        self.temporary.cleanup()

    def reject(self, changed, reason):
        document = {**self.spec, 'output': str(self.output), **changed}
        (self.controls/'specification.json').write_bytes((json.dumps(document)+'\n').encode())
        with self.assertRaisesRegex(EvidenceError, reason):
            run(self.controls)
        self.assertFalse(self.output.exists())
        self.assertEqual(sorted(p.name for p in self.controls.iterdir()), ['specification.json'])

    def test_existing_unapproved_root_is_rejected_before_output_creation(self):
        self.reject(dict(execution_root=str(self.root)), 'physical_export_paths')

    def test_sibling_with_the_same_prefix_is_outside_the_owner(self):
        escaped = self.base.parent/(self.base.name+'-escape')/'readbacks'/self.root.name
        self.reject(dict(output=str(escaped)), 'physical_export_paths')
        self.assertFalse(escaped.exists())

    def test_parent_traversal_is_not_a_lexically_admitted_output(self):
        self.reject(dict(output=str(self.root/'..'/'..'/'outside-readbacks'/self.root.name)),
                    'physical_export_noncanonical_paths')

    def test_worker_root_symlink_cannot_alias_an_approved_root(self):
        alias = self.root/'worker-alias'; alias.symlink_to(self.base, target_is_directory=True)
        self.reject(dict(execution_root=str(alias)), 'physical_export_noncanonical_paths')

    def test_input_directory_symlink_is_rejected_before_native_import(self):
        alias = self.root/'input-alias'; alias.symlink_to(self.spec['inputs'], target_is_directory=True)
        self.reject(dict(inputs=str(alias)), 'physical_export_noncanonical_paths')

    def test_output_symlink_cannot_write_into_an_existing_directory(self):
        target = self.root/'retained'; target.mkdir(); sentinel = target/'sentinel'
        sentinel.write_bytes(b'unchanged')
        alias = self.root/'output-alias'; alias.symlink_to(target, target_is_directory=True)
        self.reject(dict(output=str(alias)), 'physical_export_noncanonical_paths')
        self.assertEqual(sentinel.read_bytes(), b'unchanged')
        self.assertEqual(list(target.iterdir()), [sentinel])

    def test_existing_output_is_not_reused(self):
        target = self.root/'retained'; target.mkdir(); sentinel = target/'sentinel'
        sentinel.write_bytes(b'unchanged')
        self.reject(dict(output=str(target)), 'physical_export_paths')
        self.assertEqual(sentinel.read_bytes(), b'unchanged')
        self.assertEqual(list(target.iterdir()), [sentinel])


if __name__ == '__main__':
    unittest.main()
