"""Recorded C/D workspace selection for the production Windows build readers."""
import importlib.util
import json
import os
from pathlib import Path, PureWindowsPath
import tempfile
import unittest

PROFILE = Path(__file__).resolve().parents[1]/'workers/windows-vs2026'


def module(name):
    spec = importlib.util.spec_from_file_location('workspace_test_'+name.replace('-', '_'), PROFILE/(name+'.py'))
    value = importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value


class DeclaredWindowsWorkerRootTest(unittest.TestCase):
    def test_legacy_spec_keeps_C_independently_of_current_directory(self):
        helper = module('worker-workspace')
        self.assertEqual(helper.declared_worker_root({}), PureWindowsPath('C:/Projects/TimeLearnerWorker'))

    def test_D_requires_explicit_record_and_matching_override(self):
        helper = module('worker-workspace');root = 'D:/Projects/TimeLearnerWorker'
        self.assertEqual(helper.declared_worker_root({'worker_root': root}, root), PureWindowsPath(root))
        with self.assertRaisesRegex(RuntimeError, 'differs_from_specification'):
            helper.declared_worker_root({}, root)

    def test_wrong_drive_relative_personal_and_parent_paths_are_refused(self):
        helper = module('worker-workspace')
        for root in ('E:/Science-Repo/nmsdk-git', 'D:Projects/TimeLearnerWorker',
                     'D:/Projects/Nmsdk', 'D:/Projects/TimeLearnerWorker/../TimeLearnerWorker'):
            with self.subTest(root=root), self.assertRaisesRegex(RuntimeError, 'unsupported_private_worker_root'):
                helper.declared_worker_root({'worker_root': root})

    def test_nontext_declarations_cannot_select_a_workspace(self):
        helper = module('worker-workspace')
        for value in (None, 1, True, []):
            with self.subTest(value=value), self.assertRaisesRegex(RuntimeError, 'invalid_declared_worker_root'):
                helper.declared_worker_root({'worker_root': value})


class WindowsWorkerRootActualTest(unittest.TestCase):
    """Run on the declared server workspace, using real files and readers."""
    def test_real_build_and_closed_audit_readers_bind_the_declared_root(self):
        root = Path(os.environ['TIMELEARNER_WORKER_METADATA_ROOT']).resolve(strict=True)
        self.assertIn(PureWindowsPath(str(root)), module('worker-workspace').ALLOWED_WORKER_ROOTS)
        with tempfile.TemporaryDirectory(prefix='workspace-reader-', dir=root/'jobs') as temporary:
            path = Path(temporary)/'specification.json'
            value = dict(worker_root=str(root), kind='metadata_reader_control', schema_version=1)
            path.write_text(json.dumps(value), encoding='utf-8')
            for name in ('sdk-build', 'audit-closed-build'):
                reader = module(name)
                resolved, specification = reader.read_specification(path, root)
                self.assertEqual(resolved, path.resolve())
                self.assertEqual(specification, value)
                self.assertEqual(reader.BASE, root)
                # Root selection does not relax the actual component reader's
                # scope: an unrelated source path still fails before any write.
                with self.assertRaises(RuntimeError):reader.private_path(root.parent/'Nmsdk')

    def test_cross_root_specification_is_rejected_without_an_output(self):
        root = Path(os.environ['TIMELEARNER_WORKER_METADATA_ROOT']).resolve(strict=True)
        other = 'D:/Projects/TimeLearnerWorker' if root.drive.upper() == 'C:' else 'C:/Projects/TimeLearnerWorker'
        with tempfile.TemporaryDirectory(prefix='workspace-cross-root-', dir=root/'jobs') as temporary:
            path = Path(temporary)/'specification.json';raw=json.dumps(dict(worker_root=other)).encode();path.write_bytes(raw)
            helper = module('worker-workspace')
            with self.assertRaisesRegex(RuntimeError, 'outside_declared_worker_root'):
                helper.load_specification(path)
            self.assertEqual(path.read_bytes(), raw)
            self.assertEqual({p.name for p in Path(temporary).iterdir()}, {'specification.json'})
