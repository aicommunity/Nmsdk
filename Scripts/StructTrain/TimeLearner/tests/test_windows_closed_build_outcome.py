"""Admission policy in the actual Windows audit worker, without kernel claims."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest


WORKER = Path(__file__).resolve().parents[1]/'workers/windows-vs2026/audit-closed-build.py'
SPEC = importlib.util.spec_from_file_location('actual_windows_build_audit', WORKER)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def records(accepted=True):
    terminal = {'kind': 'timelearner_windows_sdk_build', 'build_accepted': accepted}
    result = {'kind': 'timelearner_windows_process_result', 'schema_version': 1,
              'returncode': 0, 'validity': 'valid', 'all_processes_closed': True,
              'execution': 'completed' if accepted else 'descendants_remaining'}
    return terminal, result


class WindowsClosedBuildOutcomeTest(unittest.TestCase):
    def test_healthy_build_is_admitted_with_its_actual_original_result(self):
        terminal, result = records()
        before = deepcopy((terminal, result))
        self.assertEqual(AUDIT.original_build_outcome(terminal, result),
                         {'original_execution': 'completed', 'original_build_accepted': True})
        self.assertEqual((terminal, result), before)

    def test_recovery_never_promotes_the_original_negative_acceptance(self):
        terminal, result = records(False)
        before = deepcopy((terminal, result))
        self.assertEqual(AUDIT.original_build_outcome(terminal, result),
                         {'original_execution': 'descendants_remaining', 'original_build_accepted': False})
        self.assertEqual((terminal, result), before)

    def test_success_cannot_be_inferred_from_exit_zero_or_an_inconsistent_terminal(self):
        for accepted in (True, False):
            for execution in ('timeout', 'process_error', 'interrupted',
                              'descendants_remaining' if accepted else 'completed'):
                terminal, result = records(accepted)
                result['execution'] = execution
                with self.subTest(accepted=accepted, execution=execution), self.assertRaises(RuntimeError):
                    AUDIT.original_build_outcome(terminal, result)

    def test_invalid_or_incomplete_process_records_remain_ineligible(self):
        defects = [('returncode', 1), ('returncode', True), ('validity', 'invalid'),
                   ('all_processes_closed', False), ('all_processes_closed', 1),
                   ('schema_version', True), ('kind', 'another_process')]
        for key, value in defects:
            terminal, result = records()
            result[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(RuntimeError):
                AUDIT.original_build_outcome(terminal, result)
        terminal, result = records()
        terminal['build_accepted'] = 1
        with self.assertRaises(RuntimeError):
            AUDIT.original_build_outcome(terminal, result)
        for missing in ('returncode', 'all_processes_closed', 'execution'):
            terminal, result = records()
            result.pop(missing)
            with self.subTest(missing=missing), self.assertRaises(RuntimeError):
                AUDIT.original_build_outcome(terminal, result)
