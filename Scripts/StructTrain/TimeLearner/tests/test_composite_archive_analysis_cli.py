"""CLI transport controls and separately gated actual six-case persistence."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ..__main__ import main
from ..composite_archive_case import _read_documents
from ..native_evidence import EvidenceError
from .test_composite_native_archive import CASES, MEASURED


def invoke(*args):
    output,error=io.StringIO(),io.StringIO()
    with contextlib.redirect_stdout(output),contextlib.redirect_stderr(error):code=main(['analyze',*map(str,args)])
    return code,output.getvalue(),error.getvalue()


def write_wire_case(root):
    """Only a loader/wiring fixture; it has no native semantic audit validity."""
    (root/'composite-measurements').mkdir()
    for name,value in [('initial-configuration.json',dict(schema_version=7)),('runtime-plan.json',dict(run_id='wire')),
        ('composite-measurements/index.json',dict(schema_version=2,records=[]))]:
        (root/name).write_text(json.dumps(value),encoding='utf-8')


class CompositeArchiveAnalysisCliTest(unittest.TestCase):
    def test_format_wires_mandatory_documents_and_real_filesystem_resolver(self):
        # Mock only the semantic auditor boundary to test CLI transport. This
        # does not count as a positive archive2/numerical/native acceptance.
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);write_wire_case(root);(root/'retained.csv').write_bytes(b'exact-primary')
            audit=dict(groups=[],native_execution_verified=False,training_certificate_verified=False,scientific_verdict=None)
            with patch('Scripts.StructTrain.TimeLearner.composite_archive_case.audit_composite_measurement_archive',return_value=audit) as called:
                code,output,error=invoke(root,'--format','native-composite-measurements')
                self.assertEqual(code,0,error);args,kwargs=called.call_args
                self.assertEqual(args[0],dict(schema_version=2,records=[]));self.assertEqual(args[1],dict(schema_version=7))
                self.assertEqual(kwargs['runtime_plan'],dict(run_id='wire'))
                self.assertEqual(kwargs['external_resolver']('retained.csv'),b'exact-primary')
                with self.assertRaises(EvidenceError):kwargs['external_resolver']('missing.csv')
            value=json.loads(output);self.assertEqual(value['format'],'native-composite-measurements')
            self.assertIsNone(value['evaluation_verdict']);self.assertEqual(value['analysis']['coverage']['measured_groups'],0)
            self.assertNotIn('primary_blobs',json.dumps(value));self.assertEqual(set(value['analysis']['input_documents']),
                {'initial-configuration.json','runtime-plan.json','composite-measurements/index.json'})

    def test_missing_original_json_never_uses_embedded_or_legacy_flat_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);write_wire_case(root);(root/'runtime-plan.json').unlink()
            (root/'train_state_trial_1.json').write_text('{}',encoding='utf-8')
            code,output,error=invoke(root,'--format','native-composite-measurements')
            self.assertEqual(code,2);self.assertFalse(output);self.assertEqual(json.loads(error)['validity'],'invalid')

    def test_unknown_archive_schema_and_malformed_duplicate_json_fail_explicitly(self):
        for raw in ('{"schema_version":999}', '{"schema_version":2,"schema_version":1}'):
            with tempfile.TemporaryDirectory() as directory:
                root=Path(directory);write_wire_case(root);(root/'composite-measurements/index.json').write_text(raw,encoding='utf-8')
                code,output,error=invoke(root,'--format','native-composite-measurements')
                self.assertEqual(code,2);self.assertFalse(output);self.assertEqual(json.loads(error)['validity'],'invalid')

    def test_new_report_cannot_be_written_inside_immutable_case(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);write_wire_case(root);output=root/'report.json'
            code,text,error=invoke(root,'--format','native-composite-measurements','--output',output)
            self.assertEqual(code,2);self.assertFalse(text);self.assertFalse(output.exists())
            self.assertEqual(json.loads(error)['reason'],'composite_analysis_output_overlaps_original_case')

    def test_existing_report_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/'case';root.mkdir();write_wire_case(root)
            output=Path(directory)/'report.json';output.write_text('preserve',encoding='utf-8')
            audit=dict(groups=[],native_execution_verified=False,training_certificate_verified=False,scientific_verdict=None)
            with patch('Scripts.StructTrain.TimeLearner.composite_archive_case.audit_composite_measurement_archive',return_value=audit):
                code,text,error=invoke(root,'--format','native-composite-measurements','--output',output)
            self.assertEqual(code,2);self.assertEqual(output.read_text(),'preserve');self.assertFalse(text)
            self.assertEqual(json.loads(error)['execution'],'process_error')

    def test_exact_original_document_bytes_are_bound_without_reencoding(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);write_wire_case(root)
            raw=b'{ "schema_version" : 7 }\n';(root/'initial-configuration.json').write_bytes(raw)
            _,documents,bindings=_read_documents(root)
            self.assertEqual(documents['initial-configuration.json'],dict(schema_version=7))
            self.assertEqual(bindings['initial-configuration.json'],dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))


class CompositeArchiveActualCliTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value=os.environ.get('TIMELEARNER_COMPOSITE_NATIVE_ARCHIVES')
        if not value:raise unittest.SkipTest('requires six original native service exports; no synthetic fallback')
        cls.root=Path(value)

    def test_six_actual_case_reports_persist_full_audits_and_nonzero_positive_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            for name in CASES:
                output=Path(directory)/(name+'.json')
                code,text,error=invoke(self.root/name,'--format','native-composite-measurements','--output',output)
                self.assertEqual(code,0,error);self.assertFalse(text);value=json.loads(output.read_text(encoding='utf-8'))['analysis']
                self.assertEqual(value['coverage']['measured_groups'],MEASURED[name]);self.assertEqual(len(value['measurements']),MEASURED[name])
                self.assertFalse(value['native_execution_verified']);self.assertFalse(value['training_certificate_verified'])
                self.assertIsNone(value['scientific_verdict']);self.assertTrue(value['audit']['archive_counters_recomputed'])
                self.assertLess(output.stat().st_size,1024*1024)


if __name__=='__main__':unittest.main()
