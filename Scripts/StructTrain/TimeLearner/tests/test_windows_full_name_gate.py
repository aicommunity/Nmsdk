"""The production Windows gate preserves parameterized native test identities."""
import os
import unittest

from ..gtest_full_names import parse_listing
from ..native_evidence import EvidenceError
from ..native_gate import (_environment, _filter_argument, _loader_environment,
                           supported_specification)


class WindowsFullNameGate(unittest.TestCase):
    def setUp(self):
        self.spec = dict(kind='timelearner_native_test_gate', schema_version=7,
            runtime_manifest='runtime.json', source_root='source',
            expected_test_ids=['TopologiesAndRates/NativeTimingProperties.'
                               'RejectNonfiniteWithoutChangingPreviousValue/0'],
            maximum_wall_seconds=60, asan_options='', cooperative_runtime_capture=True,
            process_limits=dict(memory_bytes=128*1024**2, maximum_processes=4),
            worker_lock='worker.lock', artifact_directories=dict(TL_HOT_READOUT_DIR='hot'))

    def test_explicit_windows_full_name_schema_and_artifact_paths(self):
        self.assertTrue(supported_specification(self.spec))
        for change in (dict(artifact_directories={'PATH': 'bin'}),
                       dict(artifact_directories={'TL_HOT_READOUT_DIR': '../outside'}),
                       dict(data_inputs=[]), dict(cooperative_runtime_capture=False),
                       dict(schema_version=True), dict(unknown=True)):
            self.assertFalse(supported_specification(dict(self.spec, **change)))
        for key in ('artifact_directories', 'worker_lock', 'process_limits'):
            value = dict(self.spec); del value[key]
            self.assertFalse(supported_specification(value))

    def test_windows_process_limits_cannot_be_linux_or_boolean_limits(self):
        for limits in (dict(memory_bytes=128*1024**2, tasks=4),
                       dict(memory_bytes=True, maximum_processes=4),
                       dict(memory_bytes=128*1024**2, maximum_processes=True)):
            self.assertFalse(supported_specification(dict(self.spec, process_limits=limits)))

    def test_parameterized_listing_selection_keeps_both_slash_positions(self):
        names = parse_listing('TopologiesAndRates/NativeTimingProperties.\n'
                              '  RejectNonfiniteWithoutChangingPreviousValue/0  # GetParam() = (false, 2000)\n')
        self.assertEqual(names, self.spec['expected_test_ids'])
        self.assertEqual(_filter_argument(self.spec), '--gtest_filter='+names[0])

    def test_legacy_schema4_is_unchanged_and_requires_legacy_names(self):
        old = dict(self.spec, schema_version=4, expected_test_ids=['Suite/Case'])
        del old['artifact_directories']
        self.assertTrue(supported_specification(old))
        self.assertEqual(_filter_argument(old), '--gtest_filter=Suite.Case')
        self.assertFalse(supported_specification(dict(old, artifact_directories={})))
        with self.assertRaisesRegex(EvidenceError, 'test_ids'):
            _filter_argument(dict(old, expected_test_ids=self.spec['expected_test_ids']))

    def test_invalid_duplicate_and_filter_injection_names_are_rejected(self):
        for names in ([self.spec['expected_test_ids'][0]]*2,
                      ['Suite.Case:Other.Case'], ['Suite.Case*'], ['Suite/Case']):
            with self.assertRaises(EvidenceError):
                _filter_argument(dict(self.spec, expected_test_ids=names))

    def test_windows_argument_budget_is_stricter_than_linux_budget(self):
        names = ['Suite.Case'+str(i)+'x'*500 for i in range(50)]
        with self.assertRaisesRegex(EvidenceError, 'windows_native_gate_filter_budget'):
            _filter_argument(dict(self.spec, expected_test_ids=names))
        self.assertTrue(_filter_argument(dict(self.spec, schema_version=6, expected_test_ids=names)))
        self.assertEqual(_filter_argument(dict(self.spec, expected_test_ids=names[:20])),
                         '--gtest_filter='+':'.join(names[:20]))

    def test_full_name_windows_run_uses_declared_path_and_restores_operator_path(self):
        runtime = dict(loader_environment=dict(PATH='declared-runtime',
            LD_LIBRARY_PATH='not-a-windows-search-path', QT_QPA_PLATFORM='offscreen'))
        with _environment(dict(PATH='operator-path')):
            for version in (4, 7, 8):
                values = _loader_environment(dict(self.spec, schema_version=version), runtime)
                self.assertNotIn('LD_LIBRARY_PATH', values)
                with _environment(values):
                    self.assertEqual(os.environ['PATH'], 'declared-runtime')
                    self.assertEqual(os.environ['QT_QPA_PLATFORM'], 'offscreen')
                    self.assertNotIn('QT_PLUGIN_PATH', os.environ)
                self.assertEqual(os.environ['PATH'], 'operator-path')

    def test_schema8_requires_explicit_bounded_windows_safe_data(self):
        from pathlib import Path
        row = dict(name='classic-package6.qz', path=str(Path('fixture.qz').resolve()),
                   bytes=323020, sha256='d58ce13f3759a9e7c38f65c2cdb3059bb7ddccbd152d7e4144564c1efa36b234')
        spec = dict(self.spec, schema_version=8, data_inputs=[row])
        self.assertTrue(supported_specification(spec))
        self.assertEqual(_filter_argument(spec), _filter_argument(self.spec))
        for bad in ([], [dict(row, name='NUL.qz')], [dict(row, name='COM1')],
                    [dict(row, name='trailing.')], [dict(row, bytes=True)],
                    [dict(row, sha256='bad')], [row, row]):
            self.assertFalse(supported_specification(dict(spec, data_inputs=bad)))
        absent = dict(spec); del absent['data_inputs']
        self.assertFalse(supported_specification(absent))
        for version in (4, 7):
            self.assertFalse(supported_specification(dict(spec, schema_version=version)))

    def test_schema8_retains_windows_filter_budget(self):
        with self.assertRaisesRegex(EvidenceError, 'windows_native_gate_filter_budget'):
            _filter_argument(dict(self.spec, schema_version=8,
                expected_test_ids=['Suite.Case'+str(i)+'x'*500 for i in range(50)]))

    def test_linux_full_names_keep_library_path_and_do_not_replace_path(self):
        runtime = dict(loader_environment=dict(PATH='not-a-linux-loader-variable',
            LD_LIBRARY_PATH='declared-linux-libraries', QT_QPA_PLATFORM='offscreen'))
        values = _loader_environment(dict(self.spec, schema_version=6), runtime)
        self.assertNotIn('PATH', values)
        with _environment(dict(PATH='operator-path')):
            with _environment(values):
                self.assertEqual(os.environ['PATH'], 'operator-path')
                self.assertEqual(os.environ['LD_LIBRARY_PATH'], 'declared-linux-libraries')


if __name__ == '__main__':
    unittest.main()
