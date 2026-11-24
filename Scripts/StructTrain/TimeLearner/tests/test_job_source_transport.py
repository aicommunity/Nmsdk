import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ..job_source_transport import make_envelope,verify_envelope,SOURCE_FIELDS
from ..native_evidence import EvidenceError
from ..model_identity import canonical_model_sha256 as sha


class JobSourceTransportTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve();(self.root/'source').mkdir()
        self.path=self.root/'source'/'state.json'
        self.package={'kind':'transport-only-test','history':['retained reference','retained candidate']}
        self.package['sha256']=sha(self.package)
        self.path.write_text(json.dumps(self.package,indent=2),encoding='utf-8')

    def job(self,kind):
        body={'kind':kind,'schema_version':1,'implementation_id':'transport-test',
              SOURCE_FIELDS[kind]:self.package}
        return {**body,'sha256':sha(body)}

    def test_complete_source_and_resolved_digest_survive_all_declared_roles(self):
        for kind,field in SOURCE_FIELDS.items():
            job=self.job(kind);envelope=make_envelope(job,self.path,self.root)
            self.assertNotIn(field,envelope['job'])
            self.assertEqual(envelope['source']['path'],'source/state.json')
            restored=dict(envelope['job']);restored[field]=json.loads(self.path.read_bytes())
            self.assertEqual(restored,job)
            self.assertEqual(restored[field]['history'],self.package['history'])
            self.assertEqual(verify_envelope(envelope,job,self.path,self.root)['resolved_job_sha256'],job['sha256'])

    def test_changed_bytes_are_rejected_even_if_json_values_remain_equal(self):
        job=self.job(next(iter(SOURCE_FIELDS)));envelope=make_envelope(job,self.path,self.root)
        self.path.write_text(json.dumps(self.package,separators=(',',':')),encoding='utf-8')
        with self.assertRaisesRegex(EvidenceError,'job_source_transport_changed'):
            verify_envelope(envelope,job,self.path,self.root)

    def test_physical_model_evaluation_has_a_distinct_lossless_data_role(self):
        body={'kind':'timelearner_native_physical_model_evaluation_job','schema_version':1,
              'implementation_id':'transport-test','source_model_data':self.package}
        job={**body,'sha256':sha(body)}
        envelope=make_envelope(job,self.path,self.root)
        self.assertEqual(envelope['source']['field'],'source_model_data')
        self.assertNotIn('source_model_data',envelope['job'])
        restored={**envelope['job'],'source_model_data':json.loads(self.path.read_bytes())}
        self.assertEqual(restored,job)
        self.assertEqual(verify_envelope(envelope,job,self.path,self.root)['resolved_job_sha256'],job['sha256'])
        changed=json.loads(json.dumps(envelope));changed['source']['field']='source_recognition'
        with self.assertRaises(EvidenceError):verify_envelope(changed,job,self.path,self.root)

    def test_physical_conversion_binds_the_source_and_the_declared_edit(self):
        body={'kind':'timelearner_native_physical_model_conversion_job','schema_version':1,
              'implementation_id':'transport-test','source_model_data':self.package,
              'conversion_spec':{'schema_version':1,'mode':'identity','resistance_bounds':[]},
              'reference_amplitudes':[]}
        job={**body,'sha256':sha(body)}
        envelope=make_envelope(job,self.path,self.root)
        restored={**envelope['job'],'source_model_data':json.loads(self.path.read_bytes())}
        self.assertEqual(restored,job)
        self.assertEqual(envelope['source']['field'],'source_model_data')
        self.assertEqual(verify_envelope(envelope,job,self.path,self.root)['resolved_job_sha256'],job['sha256'])
        changed=json.loads(json.dumps(envelope));changed['job']['reference_amplitudes']=[1.]
        with self.assertRaises(EvidenceError):verify_envelope(changed,job,self.path,self.root)

    def test_projection_role_metadata_and_history_changes_are_rejected(self):
        job=self.job(next(iter(SOURCE_FIELDS)));envelope=make_envelope(job,self.path,self.root)
        for section,key,value in [('job','implementation_id','changed'),('source','field','source_recognition'),
                                  ('source','bytes',0),('source','package_sha256','0'*64)]:
            modified=json.loads(json.dumps(envelope));modified[section][key]=value
            with self.assertRaises(EvidenceError):verify_envelope(modified,job,self.path,self.root)

    def test_source_cannot_escape_input_root(self):
        job=self.job(next(iter(SOURCE_FIELDS)))
        other=self.root/'other';other.mkdir()
        with self.assertRaisesRegex(EvidenceError,'job_source_path_escape'):
            make_envelope(job,self.path,other)

    def test_cold_job_cannot_import_a_file_source(self):
        with self.assertRaisesRegex(EvidenceError,'job_source_unsupported_operation'):
            make_envelope({'kind':'timelearner_native_training_job'},self.path,self.root)

    def test_size_guard_runs_before_reading(self):
        job=self.job(next(iter(SOURCE_FIELDS)));self.path.write_bytes(b'')
        with self.assertRaisesRegex(EvidenceError,'job_source_declared_size'):make_envelope(job,self.path,self.root)
        self.path.write_bytes(b'x'*17)
        with patch('Scripts.StructTrain.TimeLearner.job_source_transport.MAXIMUM_SOURCE_BYTES',16):
            with self.assertRaisesRegex(EvidenceError,'job_source_declared_size'):make_envelope(job,self.path,self.root)
