import unittest
from copy import deepcopy

from ..candidate_window_recovery_ledger import audit_candidate_window_recovery_ledger
from ..candidate_window_recovery_events import audit_candidate_window_recovery_events
from ..model_identity import canonical_model_sha256 as digest
from ..native_evidence import EvidenceError
from . import test_candidate_window_recovery_events as event_fixture


def resign(ledger):
    ledger['sha256']=digest({k:v for k,v in ledger.items() if k!='sha256'})
    return ledger


class CandidateWindowRecoveryLedgerDataTest(unittest.TestCase):
    def make(self):
        event,archive,config,runtime,primary=event_fixture.CandidateWindowRecoveryEventDataTest().make()
        ledger=resign(dict(kind='timelearner_candidate_window_recovery_ledger',schema_version=1,
            source_origin=archive['source_origin'],owner_family_binding=archive['owner_family_binding'],
            measurement_archive_document_id=archive['artifact_document_sha256'],producer_log_intact=True,
            independent_delivery_completeness_verified=False,deliveries=[]))
        return ledger,event,archive,config,runtime,primary

    def check(self,ledger,archive,config,primary):
        return audit_candidate_window_recovery_ledger(ledger,archive,config,external_resolver=primary.__getitem__)

    def test_empty_ledger_replays_primary_without_claiming_training_or_coverage(self):
        ledger,_,archive,config,_,primary=self.make();before=deepcopy((ledger,archive,config))
        result=self.check(ledger,archive,config,primary)
        self.assertEqual(result['deliveries_checked'],0)
        self.assertGreater(result['primary_files_checked'],0)
        for field in ('service_ledger_completeness_verified','training_certificate_verified','live_authority_restored'):
            self.assertFalse(result[field])
        self.assertIsNone(result['scientific_verdict']);self.assertEqual((ledger,archive,config),before)

    def test_even_empty_ledger_rejects_changed_primary(self):
        ledger,_,archive,config,_,primary=self.make();primary=dict(primary)
        name=next(iter(primary));primary[name]+=b'changed'
        with self.assertRaises(EvidenceError):self.check(ledger,archive,config,primary)

    def test_rehashed_false_producer_and_coverage_claims_fail(self):
        for field,value in [('producer_log_intact',False),('producer_log_intact',1),
                            ('independent_delivery_completeness_verified',True),('schema_version',True)]:
            ledger,_,archive,config,_,primary=self.make();ledger[field]=value;resign(ledger)
            with self.subTest(field=field,value=value),self.assertRaises(EvidenceError):
                self.check(ledger,archive,config,primary)

    def test_foreign_archive_source_owner_and_unknown_field_fail(self):
        for field in ('source_origin','owner_family_binding','measurement_archive_document_id','extra'):
            ledger,_,archive,config,_,primary=self.make();ledger[field]='a'*64;resign(ledger)
            with self.subTest(field=field),self.assertRaises(EvidenceError):self.check(ledger,archive,config,primary)

    def test_unhashed_changes_fail(self):
        ledger,_,archive,config,_,primary=self.make();ledger['deliveries'].append({})
        with self.assertRaisesRegex(EvidenceError,'ledger_digest'):self.check(ledger,archive,config,primary)

    def test_duplicate_delivery_rejected_before_a_fabricated_event_can_admit(self):
        ledger,event,archive,config,runtime,primary=self.make()
        row=dict(event=event,runtime_plan=runtime);ledger['deliveries']=[row,deepcopy(row)];resign(ledger)
        with self.assertRaisesRegex(EvidenceError,'ledger_replay_or_order'):self.check(ledger,archive,config,primary)

    def test_valid_peak_cannot_be_relabelled_as_a_recovery_delivery(self):
        ledger,event,archive,config,runtime,primary=self.make()
        ledger['deliveries']=[dict(event=event,runtime_plan=runtime)];resign(ledger)
        with self.assertRaisesRegex(EvidenceError,'delivery_state'):self.check(ledger,archive,config,primary)

    def test_explicit_historical_attempt_must_exist_and_match_runtime(self):
        _,_,archive,config,runtime,primary=self.make()
        with self.assertRaisesRegex(EvidenceError,'runtime_attempt'):
            audit_candidate_window_recovery_events([],archive,config,runtime,
                external_resolver=primary.__getitem__,attempt_id='absent-attempt')
