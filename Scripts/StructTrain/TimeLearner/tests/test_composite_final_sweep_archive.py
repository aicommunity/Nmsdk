"""Controls use two real exported sweeps, without manufacturing measurements."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..composite_measurement_contract import expected_artifact_document_id
from ..composite_measurement_evidence import audit_composite_measurement_archive
from ..composite_primary import filesystem_primary_resolver
from ..native_evidence import EvidenceError, load


class CompositeFinalSweepArchiveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value=os.environ.get('TIMELEARNER_COMPOSITE_NATIVE_ARCHIVES')
        if not value: raise unittest.SkipTest('requires actual classic-two-final-sweeps production export')
        cls.root=Path(value)/'classic-two-final-sweeps'
        cls.index=load(cls.root/'composite-measurements/index.json')
        cls.configuration=load(cls.root/'initial-configuration.json');cls.plan=load(cls.root/'runtime-plan.json')

    def audit(self, index):
        return audit_composite_measurement_archive(index,self.configuration,runtime_plan=self.plan,
            external_resolver=filesystem_primary_resolver(self.root))

    def sweeps(self):
        runs={}
        for record in self.index['records']:
            if record['purpose']=='final' and record['attempt_id']==self.index['current_attempt_id']:
                run=record['logical_request']['run_id'];runs.setdefault(run,{})[record['logical_request']['input_index']]=record
        ordered=sorted(runs,key=lambda run:int(run.rsplit('/',1)[1]))
        self.assertGreaterEqual(len(ordered),2);n=len(self.index['protocol']['inputs'])
        first,last=(runs[run] for run in (ordered[0],ordered[-1]))
        self.assertEqual(set(first),set(range(n)));self.assertEqual(set(last),set(range(n)))
        for record in list(first.values())+list(last.values()):
            self.assertTrue(record['complete_group']);self.assertTrue(record['consumed']);self.assertIsNotNone(record['measurement'])
        self.assertEqual(len({r['logical_request']['base_model_revision'] for r in list(first.values())+list(last.values())}),1)
        self.assertEqual(len({r['logical_request']['model_epoch'] for r in list(first.values())+list(last.values())}),1)
        return first,last,n

    def test_real_latest_final_set_replays_without_claiming_live_authority(self):
        self.sweeps();result=self.audit(self.index)
        self.assertTrue(result['archive_counters_recomputed']);self.assertFalse(result['live_authority_restored'])
        self.assertIsNone(result['scientific_verdict'])

    def test_real_same_model_epoch_sweeps_cannot_be_mixed(self):
        first,last,n=self.sweeps();changed=deepcopy(self.index)
        changed['final_group_ids']=[first[0]['group_id']]+[last[i]['group_id'] for i in range(1,n)]
        changed['artifact_document_sha256']=expected_artifact_document_id(changed)
        with self.assertRaisesRegex(EvidenceError,'composite_archive_final_generation_mixed'):self.audit(changed)

    def test_entire_real_old_final_set_is_not_latest_observed_generation(self):
        first,_,n=self.sweeps();changed=deepcopy(self.index)
        changed['final_group_ids']=[first[i]['group_id'] for i in range(n)]
        changed['artifact_document_sha256']=expected_artifact_document_id(changed)
        with self.assertRaisesRegex(EvidenceError,'composite_archive_final_generation_stale'):self.audit(changed)
