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
