"""Actual Console and actual GoogleTest executables on a worker; no mocks."""
import copy
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..native_cli import inspect_native_cli, OPERATIONS
from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import run_job as run_native_job
from ..managed_pipeline import run_pipeline
from ..process_runner import verify_runtime
from ..runtime import file_record, resolved_libraries, runtime_content_identity, digest_json


class NativeFileSourceCliTest(unittest.TestCase):
    """Explicit new/old real runtimes; a help check never claims model execution."""
    @classmethod
    def setUpClass(cls):
        spec=load(Path(os.environ['TIMELEARNER_JOB_SOURCE_CLI_FIXTURES'])/'runtimes.json')
        cls.legacy_path=Path(spec['legacy_runtime'])
        cls.current=load(Path(spec['current_runtime']))
        cls.legacy=load(Path(spec['legacy_runtime']))
        verify_runtime(cls.current);verify_runtime(cls.legacy)

    def test_current_console_advertises_checked_source_file_transport(self):
        result=inspect_native_cli(self.current,['export','evaluate','diagnostic-evaluate'],require_file_source=True)
        self.assertIn('checked-file-source-v1',result['help_text'])
        self.assertFalse(result['native_job_executed'])

    def test_legacy_console_is_rejected_before_any_file_source_job(self):
        # Its ordinary diagnostic interface is valid; the missing transport
        # capability, rather than the executable type, is the rejecting factor.
        inspect_native_cli(self.legacy,['diagnostic-evaluate'])
        with self.assertRaisesRegex(EvidenceError,'native_cli_missing_file_source_transport'):
            inspect_native_cli(self.legacy,['diagnostic-evaluate'],require_file_source=True)

    def test_unknown_transport_selector_is_rejected_before_runtime_access(self):
        with self.assertRaisesRegex(EvidenceError,'native_cli_unknown_source_transport'):
            inspect_native_cli({},['diagnostic-evaluate'],require_file_source='auto')

    def test_recorded_case_accepts_json_string_runtime_path_and_rejects_legacy_before_source_access(self):
        from ..recorded_diagnostic_matrix import run_case
        with tempfile.TemporaryDirectory(prefix='tl-source-path-') as temporary:
            output=Path(temporary)/'not-created'
            # Actual legacy Console reaches the production capability refusal.
            # The absent case/source declarations must never be read first.
            with self.assertRaisesRegex(EvidenceError,'native_cli_missing_file_source_transport'):
                run_case({}, {'job_source_transport':'checked-file-source-v1'},
                         str(self.legacy_path), output)
            self.assertFalse(output.exists())


class NativeCliInterfaceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        declaration = os.environ.get('TIMELEARNER_NATIVE_CLI_FIXTURES')
        if not declaration:
            raise unittest.SkipTest('requires immutable actual Console/gtest runtime and completed job declarations')
        cls.spec = load(Path(declaration))
        cls.console = load(Path(cls.spec['console_runtime']))
        cls.gtest = load(Path(cls.spec['test_runtime']))
        verify_runtime(cls.console);verify_runtime(cls.gtest)

    def test_console_advertises_every_native_operation_without_a_job(self):
        result = inspect_native_cli(self.console, sorted(OPERATIONS))
        self.assertEqual(result['operations'], sorted(OPERATIONS))
        self.assertEqual(result['arguments'], ['--help'])
        self.assertFalse(result['native_job_executed'])
        self.assertNotIn('[ RUN      ]', result['help_text'])
        self.assertEqual(result['executable_sha256'], self.console['executable']['sha256'])

    def test_gtest_executable_cannot_be_a_native_job_runtime(self):
        with self.assertRaisesRegex(EvidenceError, 'native_cli_missing_advertised_operation'):
            inspect_native_cli(self.gtest, ['train'])

    def test_duplicate_operations_are_canonicalized(self):
        result = inspect_native_cli(self.console, ['train', 'train', 'evaluate'])
        self.assertEqual(result['operations'], ['evaluate', 'train'])

    def test_console_with_another_executable_name_remains_supported(self):
        with tempfile.TemporaryDirectory(prefix='tl-cli-rename-') as temporary:
            executable = Path(temporary)/'model-runner.rs2'
            shutil.copy2(self.console['executable']['path'], executable)
            runtime = copy.deepcopy(self.console)
            runtime['executable'] = file_record(executable)
            runtime['resolved_libraries'] = resolved_libraries(executable)
            runtime['loaded_process_files'] = None
            runtime['runtime_identity'] = runtime_content_identity(runtime)
            runtime['runtime_fingerprint'] = digest_json(runtime['runtime_identity'])
            result = inspect_native_cli(runtime, ['train', 'evaluate'])
            self.assertEqual(result['executable_sha256'], self.console['executable']['sha256'])

    def test_wrong_runtime_is_rejected_before_native_job_output_exists(self):
        with tempfile.TemporaryDirectory(prefix='tl-cli-wrong-native-') as temporary:
            output = Path(temporary)/'not-created'
            with self.assertRaisesRegex(EvidenceError, 'native_cli_missing_advertised_operation'):
                run_native_job('train', Path(self.spec['train_job']), None,
                               Path(self.spec['test_runtime']), output, 60)
            self.assertFalse(output.exists())

    def test_wrong_runtime_is_rejected_before_managed_pipeline_output_exists(self):
        with tempfile.TemporaryDirectory(prefix='tl-cli-wrong-pipeline-') as temporary:
            output = Path(temporary)/'not-created'
            with self.assertRaisesRegex(EvidenceError, 'native_cli_missing_advertised_operation'):
                run_pipeline(Path(self.spec['pipeline_job']), Path(self.spec['test_runtime']),
                             load(Path(self.spec['pipeline_policy'])), output)
            self.assertFalse(output.exists())

    def test_unknown_or_empty_operations_are_refused_before_inspection(self):
        for operations in ([], ['unknown'], ['TRAIN'], 'train', [True]):
            with self.subTest(operations=operations), self.assertRaisesRegex(EvidenceError, 'native_cli_unknown_operation'):
                inspect_native_cli(self.console, operations)
