"""Actual Windows path admission for a separately declared worker drive."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError
from Scripts.StructTrain.TimeLearner.prepared_physical_evaluation import evaluation_limits, worker_root
from Scripts.StructTrain.TimeLearner.prepared_physical_study import preparation_limits


@unittest.skipUnless(os.name == 'nt', 'requires actual Windows path semantics')
class WindowsPhysicalWorkerRoot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture = Path(os.environ['TIMELEARNER_WINDOWS_ROOT_FIXTURE']).resolve(strict=True)
        cls.temporary = tempfile.TemporaryDirectory(prefix='worker-root-', dir=fixture)
        cls.root = Path(cls.temporary.name)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_declared_existing_D_tree_is_the_effective_owner(self):
        self.assertEqual(self.root.drive.upper(), 'D:')
        for schema, legacy in ((3, (1, 2)), (2, (1,))):
            with self.subTest(schema=schema):
                declared = dict(schema_version=schema, worker_root=str(self.root))
                self.assertEqual(worker_root(declared, explicit_schema=schema,
                    legacy_schemas=legacy), self.root)

    def test_legacy_documents_cannot_silently_change_the_owner(self):
        for version in (1, 2):
            with self.subTest(version=version), self.assertRaisesRegex(
                    EvidenceError, 'physical_legacy_worker_root_override'):
                worker_root(dict(schema_version=version, worker_root=str(self.root)),
                    explicit_schema=3, legacy_schemas=(1, 2))

    def test_new_schema_requires_an_explicit_root_and_exact_integer_version(self):
        for declaration, reason in ((dict(schema_version=3), 'physical_worker_root_required'),
                (dict(schema_version=True), 'physical_worker_root_schema'),
                (dict(schema_version=4), 'physical_worker_root_schema')):
            with self.subTest(declaration=declaration), self.assertRaisesRegex(EvidenceError, reason):
                worker_root(declaration, explicit_schema=3, legacy_schemas=(1, 2))

    def test_relative_UNC_drive_root_and_parent_traversal_are_rejected(self):
        for value in ('D:/', 'D:relative', 'relative', '//server/share/worker',
                      str(self.root/'..'/self.root.name)):
            with self.subTest(value=value), self.assertRaisesRegex(
                    EvidenceError, 'physical_worker_root_must_be_local_absolute_tree'):
                worker_root(dict(schema_version=3, worker_root=value),
                    explicit_schema=3, legacy_schemas=(1, 2))

    def test_missing_worker_tree_is_rejected_before_preparation(self):
        with self.assertRaisesRegex(EvidenceError, 'physical_worker_root_alias_or_missing'):
            worker_root(dict(schema_version=3, worker_root=str(self.root/'missing')),
                explicit_schema=3, legacy_schemas=(1, 2))

    def test_actual_junction_cannot_alias_the_declared_worker(self):
        alias = self.root/'alias'
        created = subprocess.run(['cmd.exe', '/d', '/c', 'mklink', '/J', str(alias), str(self.root)],
            capture_output=True, timeout=15, creationflags=subprocess.CREATE_NO_WINDOW)
        self.assertEqual(created.returncode, 0, created.stderr)
        try:
            self.assertTrue(alias.is_junction())
            with self.assertRaisesRegex(EvidenceError, 'physical_worker_root_alias_or_missing'):
                worker_root(dict(schema_version=3, worker_root=str(alias)),
                    explicit_schema=3, legacy_schemas=(1, 2))
        finally:
            # Remove only this directory entry, never recurse through its target.
            self.assertEqual(alias.parent, self.root)
            self.assertTrue(alias.is_junction())
            alias.rmdir()

    def test_evaluation_schema_binds_root_and_preserves_declared_limits(self):
        base = dict(kind='timelearner_prepared_physical_evaluation_plan', schema_version=3,
            job_id='actual-D-root-control', source_data={}, runtime_manifest={},
            sdk_source='', worker_origin={}, job={}, worker_root=str(self.root),
            execution_limits=dict(memory_bytes=16*1024**3, maximum_wall_seconds=7200))
        self.assertEqual(evaluation_limits(base), base['execution_limits'])
        for changed in (dict(base, schema_version=2),
                        {k:v for k,v in base.items() if k != 'worker_root'},
                        dict(base, unknown='ignored')):
            with self.subTest(changed=changed), self.assertRaisesRegex(
                    EvidenceError, 'physical_evaluation_preparation_scope'):
                evaluation_limits(changed)
        legacy = {k:v for k,v in base.items() if k not in ('worker_root', 'execution_limits')}
        legacy['schema_version'] = 1
        self.assertEqual(evaluation_limits(legacy),
            dict(memory_bytes=8*1024**3, maximum_wall_seconds=3600))

    def test_study_resource_limits_are_not_weakened_for_a_new_drive(self):
        limits = dict(memory_bytes=8*1024**3, maximum_wall_seconds=5400)
        self.assertEqual(preparation_limits(dict(schema_version=3, execution_limits=limits)),
            (8*1024**3, 5400))
        for changed in ({}, dict(memory_bytes=0, maximum_wall_seconds=5400),
                        dict(memory_bytes=8*1024**3, maximum_wall_seconds=False)):
            with self.subTest(changed=changed), self.assertRaisesRegex(
                    EvidenceError, 'physical_study_explicit_execution_limits'):
                preparation_limits(dict(schema_version=3, execution_limits=changed))


if __name__ == '__main__':
    unittest.main()
