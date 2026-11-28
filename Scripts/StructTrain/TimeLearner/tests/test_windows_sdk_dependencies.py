"""Check the actual production SDK producer against the installed Windows tree."""
import hashlib
import importlib.util
import os
from pathlib import Path
import unittest


class ActualWindowsSdkDependenciesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.name != 'nt':
            raise RuntimeError('This fixture requires the real Windows worker')
        cls.deps = Path(os.environ['TIMELEARNER_WINDOWS_SHORT_DEPENDENCIES']).resolve(strict=True)
        cls.expected_status = os.environ['TIMELEARNER_WINDOWS_SHORT_DEPENDENCIES_STATUS_SHA256']
        producer = Path(__file__).parents[1]/'workers/windows-vs2026/sdk-build.py'
        spec = importlib.util.spec_from_file_location('actual_sdk_dependency_producer', producer)
        cls.producer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.producer)
        cls.producer.BASE = Path('D:/Projects/TimeLearnerWorker')
        audit_spec = importlib.util.spec_from_file_location('actual_sdk_dependency_audit',
            producer.with_name('audit-closed-build.py'))
        cls.audit = importlib.util.module_from_spec(audit_spec)
        audit_spec.loader.exec_module(cls.audit)
        cls.audit.BASE = cls.producer.BASE

    def test_actual_completed_short_install_is_accepted_without_moving_its_bytes(self):
        before = hashlib.sha256((self.deps/'vcpkg/status').read_bytes()).hexdigest()
        self.assertEqual(before, self.expected_status)
        self.assertEqual(self.producer.installed_dependencies(str(self.deps), 'short_readonly_D'), self.deps)
        self.assertEqual(hashlib.sha256((self.deps/'vcpkg/status').read_bytes()).hexdigest(), before)

    def test_original_layout_does_not_accept_the_external_short_tree(self):
        with self.assertRaisesRegex(RuntimeError, 'path_outside_private_worker'):
            self.producer.installed_dependencies(str(self.deps))

    def test_short_layout_cannot_be_implicitly_enabled_for_C_worker(self):
        self.producer.BASE = Path('C:/Projects/TimeLearnerWorker')
        try:
            with self.assertRaisesRegex(RuntimeError, 'short_dependencies_outside_declared_layout'):
                self.producer.installed_dependencies(str(self.deps), 'short_readonly_D')
        finally:
            self.producer.BASE = Path('D:/Projects/TimeLearnerWorker')

    def test_short_layout_rejects_other_roots_and_incomplete_install_paths(self):
        for candidate in ('C:/tl/deps-fr856/installed', 'D:/tl/deps-fr856',
                          'D:/tl/installed', 'D:/tl/deps-fr856/nested/installed',
                          'D:/tl/deps-fr856/../installed', 'D:/elsewhere/deps-fr856/installed'):
            with self.subTest(candidate=candidate), self.assertRaisesRegex(
                    RuntimeError, 'short_dependencies_outside_declared_layout'):
                self.producer.installed_dependencies(candidate, 'short_readonly_D')

    def test_unknown_layout_and_external_output_are_still_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'unsupported_dependency_layout'):
            self.producer.installed_dependencies(str(self.deps), 'short')
        with self.assertRaisesRegex(RuntimeError, 'path_outside_private_worker'):
            self.producer.private_path('D:/tl/new-runtime')

    def test_closed_build_audit_uses_the_same_explicit_readonly_dependency_boundary(self):
        before = hashlib.sha256((self.deps/'vcpkg/status').read_bytes()).hexdigest()
        self.assertEqual(self.audit.audit_dependencies({
            'schema_version': 2, 'dependency_layout': 'short_readonly_D',
            'installed_dependencies': str(self.deps)}), self.deps)
        self.assertEqual(hashlib.sha256((self.deps/'vcpkg/status').read_bytes()).hexdigest(), before)
        with self.assertRaisesRegex(RuntimeError, 'outside_private_workspace'):
            self.audit.private_path('D:/tl/new-runtime')

    def test_audit_requires_explicit_version_and_preserves_legacy_boundary(self):
        for version, layout in ((1, 'short_readonly_D'), (2, None), (True, None), (3, None)):
            spec = {'schema_version': version, 'installed_dependencies': str(self.deps)}
            if layout is not None:
                spec['dependency_layout'] = layout
            with self.subTest(version=version, layout=layout), self.assertRaises(RuntimeError):
                self.audit.audit_dependencies(spec)
        with self.assertRaisesRegex(RuntimeError, 'path_outside_private_worker'):
            self.audit.audit_dependencies({'schema_version': 1,
                                           'installed_dependencies': str(self.deps)})


if __name__ == '__main__':
    unittest.main()
