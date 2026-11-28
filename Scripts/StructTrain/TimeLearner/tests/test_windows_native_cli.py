"""Actual Windows Console help and owned-process capability refusals."""
import copy
import json
import os
from pathlib import Path
import sys
import unittest

from ..native_cli import inspect_native_cli
from ..native_evidence import EvidenceError
from ..runtime import file_record,runtime_content_identity,digest_json
from .. import windows_process


class WindowsNativeCliTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.name!='nt':raise unittest.SkipTest('requires the actual Windows worker')
        source=os.environ.get('TIMELEARNER_WINDOWS_NATIVE_RUNTIME')
        output=os.environ.get('TIMELEARNER_WINDOWS_CLI_OUTPUT')
        if not source or not output:raise unittest.SkipTest('requires immutable Console runtime and fresh evidence paths')
        cls.root=Path(output);cls.root.mkdir(parents=True,exist_ok=False)
        cls.runtime=json.loads(Path(source).read_bytes())
        backend=file_record(Path(windows_process.__file__))
        cls.runtime['windows_backend']=backend
        cls.runtime['build_flags']=dict(cls.runtime['build_flags'],windows_backend_sha256=backend['sha256'])
        cls.runtime['runtime_identity']=runtime_content_identity(cls.runtime)
        cls.runtime['runtime_fingerprint']=digest_json(cls.runtime['runtime_identity'])

    def test_console_advertises_export_and_evaluation_in_a_closed_owned_job(self):
        output=self.root/'actual-console';output.mkdir()
        result=inspect_native_cli(self.runtime,['physical-model-export','physical-model-evaluate','diagnostic-evaluate'],
            require_file_source=True,evidence_output=output)
        self.assertEqual(result['operations'],['diagnostic-evaluate','physical-model-evaluate','physical-model-export'])
        self.assertFalse(result['native_job_executed'])
        self.assertNotIn('[ RUN      ]',result['help_text'])
        process=json.loads((output/'cli-process/result.json').read_bytes())
        self.assertTrue(process['all_processes_closed'])
        self.assertEqual(process['execution'],'completed')

    def test_non_console_executable_is_rejected_after_owned_help(self):
        runtime=copy.deepcopy(self.runtime)
        runtime['executable']=file_record(Path(sys.executable))
        runtime['loaded_process_files']=None
        runtime['runtime_identity']=runtime_content_identity(runtime)
        runtime['runtime_fingerprint']=digest_json(runtime['runtime_identity'])
        output=self.root/'wrong-executable';output.mkdir()
        with self.assertRaisesRegex(EvidenceError,'native_cli_missing_advertised_operation'):
            inspect_native_cli(runtime,['physical-model-export'],require_file_source=True,evidence_output=output)
        self.assertTrue(json.loads((output/'cli-process/result.json').read_bytes())['all_processes_closed'])

    def test_unknown_operation_is_rejected_before_runtime_or_output_access(self):
        output=self.root/'unknown-operation'
        with self.assertRaisesRegex(EvidenceError,'native_cli_unknown_operation'):
            inspect_native_cli({},['unknown-operation'],evidence_output=output)
        self.assertFalse(output.exists())
