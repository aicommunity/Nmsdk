"""Independent replay of actual production service exports; no invented traces."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..composite_measurement_evidence import audit_composite_measurement_archive
from ..composite_measurement_contract import expected_artifact_document_id
from ..composite_primary import capture_primary_blobs, filesystem_primary_resolver
from ..native_evidence import EvidenceError, load

CASES = ('classic-service','branch-service','classic-partial','branch-C0','classic-warm','branch-ambiguous')
# Exact metadata inventory from Git b4feb38a primary.tar.xz, six index.json only.
# Expected coverage is checked against independently replayed measurements below.
MEASURED = {'classic-service':6,'branch-service':6,'branch-C0':6,'classic-warm':6,
            'classic-partial':0,'branch-ambiguous':0}


class CompositeNativeArchiveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value=os.environ.get('TIMELEARNER_COMPOSITE_NATIVE_ARCHIVES')
        if not value: raise unittest.SkipTest('requires six actual production composite service exports')
        cls.root=Path(value);cls.cases={}
        for name in CASES:
            root=cls.root/name
            cls.cases[name]=(root,load(root/'composite-measurements/index.json'),
                load(root/'initial-configuration.json'),load(root/'runtime-plan.json'))

    def audit(self, case, document=None, resolver=None):
        root,index,config,plan=case
        return audit_composite_measurement_archive(index if document is None else document,config,
            runtime_plan=plan,external_resolver=filesystem_primary_resolver(root) if resolver is None else resolver)

    def test_actual_six_service_exports_replay_all_retained_primary_and_counters(self):
        for name,case in self.cases.items():
            with self.subTest(case=name):
                result=self.audit(case)
                self.assertTrue(result['archive_counters_recomputed']);self.assertTrue(result['attempt_membership_recomputed'])
                self.assertFalse(result['native_execution_verified']);self.assertIsNone(result['scientific_verdict'])
                self.assertEqual(len(result['groups']),len(case[1]['records']))
                self.assertEqual(sum(row['measured'] for row in result['groups']),MEASURED[name])
                for row in result['groups']:
                    if row['measured']:
                        self.assertTrue(row['native_closure_recomputed']);self.assertTrue(row['geometry_recomputed'])
                        self.assertEqual(row['geometry_validity'],'valid')

    def test_actual_partial_and_ambiguous_exports_do_not_promote_invalid_measurements(self):
        partial=self.audit(self.cases['classic-partial']);ambiguous=self.audit(self.cases['branch-ambiguous'])
        self.assertTrue(any(not row['native_closure_recomputed'] and not row['measured'] for row in partial['groups']))
        self.assertTrue(any(row.get('geometry_validity') not in (None,'valid') and not row['measured'] for row in ambiguous['groups']))
        for result in (partial,ambiguous):
            self.assertIsNone(result['scientific_verdict']);self.assertFalse(result['training_certificate_verified'])

    def test_actual_sidecars_match_each_retained_record_without_filename_identity_claim(self):
        for name,(root,index,_,_) in self.cases.items():
            for ordinal,record in enumerate(index['records'],1):
                with self.subTest(case=name,ordinal=ordinal):
                    self.assertEqual(load(root/f'composite-measurements/group-{ordinal:06d}.json'),record)

    def test_actual_existing_C0_and_warm_accounting_are_retained(self):
        c0=self.cases['branch-C0'][1];warm=self.cases['classic-warm'][1]
        self.assertIsNotNone(c0['source_binding']['optional_C0_witness'])
        self.assertTrue(any(record['capacitance_witnesses'] for record in c0['records']))
        self.assertGreaterEqual(len({record['attempt_id'] for record in warm['records']}),2)
        self.assertTrue(any(record['attempt_id']!=warm['current_attempt_id'] for record in warm['records']))
        self.audit(self.cases['branch-C0']);self.audit(self.cases['classic-warm'])

    def test_supplied_external_mirror_cannot_fall_back_to_good_embedded_primary(self):
        case=self.cases['classic-service'];index=case[1]
        refs=[trial['primary_ref'] for record in index['records'] for trial in record['raw_trials']]
        primary=capture_primary_blobs(index['primary_blobs'],refs,index['maximum_total_primary_bytes'])
        self.assertTrue(primary);path=next(iter(primary));missing=dict(primary);del missing[path]
        with self.assertRaises(EvidenceError):self.audit(case,resolver=missing)
        corrupt=dict(primary);corrupt[path]+=b'corrupt'
        with self.assertRaises(EvidenceError):self.audit(case,resolver=corrupt)

    def test_csv_relocation_preserves_actual_measurement_proofs_but_changes_document_identity(self):
        for name in ('classic-service','branch-service'):
            case=self.cases[name];original=case[1];changed=deepcopy(original)
            refs=[trial['primary_ref'] for record in original['records'] for trial in record['raw_trials']]
            primary=capture_primary_blobs(original['primary_blobs'],refs,original['maximum_total_primary_bytes'])
            renamed={'relocated/'+path:raw for path,raw in primary.items()}
            for record in changed['records']:
                for trial in record['raw_trials']:trial['primary_ref']['relative_path']='relocated/'+trial['primary_ref']['relative_path']
                if record['native_group'] is not None:
                    for trace in record['native_group']['traces']:trace['relative_path']='relocated/'+trace['relative_path']
            changed['artifact_document_sha256']=expected_artifact_document_id(changed)
            self.assertNotEqual(changed['artifact_document_sha256'],original['artifact_document_sha256'])
            result=self.audit(case,changed,resolver=renamed)
            self.assertTrue(result['archive_counters_recomputed'])
            self.assertEqual([r['measurement'] for r in changed['records']],[r['measurement'] for r in original['records']])

    def test_resigned_incomplete_native_group_or_counter_changes_fail(self):
        case=self.cases['classic-service']
        for mutation in ('raw','counter'):
            changed=deepcopy(case[1]);record=next(r for r in changed['records'] if r['complete_group'])
            if mutation=='raw':record['raw_trials'].pop()
            else:record['counters']['sampled_frames']+=1
            changed['artifact_document_sha256']=expected_artifact_document_id(changed)
            with self.subTest(mutation=mutation),self.assertRaises(EvidenceError):self.audit(case,changed)
