"""Controlled event DATA and negative primary joins, not native admission."""
from copy import deepcopy
import unittest

from ..candidate_window_recovery_events import (validate_candidate_window_recovery_event,
    audit_candidate_window_recovery_events)
from ..composite_measurement_contract import expected_artifact_document_id
from ..model_identity import canonical_model_sha256 as digest
from ..native_evidence import EvidenceError
from .synthetic_candidate_archive2 import fixture


def resign(event):
    event['event_id']=digest({k:v for k,v in event.items() if k!='event_id'})
    return event


class CandidateWindowRecoveryEventDataTest(unittest.TestCase):
    def make(self):
        archive,configuration,runtime,primary=fixture()
        runtime['schema_version']=3
        runtime['search']['invalid_measurement_recovery']='advance_rejected_candidate_window'
        runtime['search']['maximum_invalid_observations']=2
        record=archive['records'][2];logical=record['logical_request']
        transition=dict(action_serial=1,input_index=logical['input_index'],candidate_input_index=0,sweep=1,
            model_epoch=logical['model_epoch'],invalid_before=0,invalid_after=1,run_id=logical['run_id'],
            trial_id=logical['trial_id'],base_model_revision=logical['base_model_revision'],
            effective_model_revision=record['native_group']['specification']['effective_model_revision'],
            phase='input',validity='missing',full_parameters=deepcopy(record['candidate_binding']['physical_readback']['parameters']),
            capacitance=deepcopy(record['candidate_binding']['physical_readback']['capacitance']),
            disposition='cursor_advanced',status_after='searching',reason_after='')
        event=resign(dict(kind='timelearner_candidate_window_recovery_event',schema_version=1,transition=transition,
            group_id=record['group_id'],rejected_content_id='a'*64,source_origin=record['source_origin'],
            owner_scope=record['owner_family_binding'],candidate_witness_id=record['candidate_witness_id'],
            issued_probes=1,applied_edits=0,accepted_composite_observations=0))
        return event,archive,configuration,runtime,primary

    def test_wire_shape_and_stable_hash_do_not_attest_a_measurement(self):
        event,*_=self.make();original=deepcopy(event)
        self.assertEqual(validate_candidate_window_recovery_event(event)['validity'],'missing')
        self.assertEqual(event,original)

    def test_rehashed_unknown_fields_counter_and_outcome_changes_fail(self):
        for change in ('extra','invalid_increment','accepted','outcome','dimension','policy'):
            event,*_=self.make()
            if change=='extra':event['unknown']=True
            elif change=='invalid_increment':event['transition']['invalid_after']=0
            elif change=='accepted':event['accepted_composite_observations']=2
            elif change=='outcome':event['transition']['status_after']='exact'
            elif change=='dimension':event['transition']['input_index']=2
            else:event['transition']['validity']='valid'
            resign(event)
            with self.subTest(change=change),self.assertRaises(EvidenceError):validate_candidate_window_recovery_event(event)

    def test_missing_ids_and_boolean_or_nonfinite_numbers_fail(self):
        for key,value in [('owner_scope',''),('rejected_content_id','bad'),('issued_probes',True)]:
            event,*_=self.make();event[key]=value;resign(event)
            with self.subTest(key=key),self.assertRaises(EvidenceError):validate_candidate_window_recovery_event(event)
        event,*_=self.make();event['transition']['full_parameters'][0]['resistance']=float('nan')
        with self.assertRaises(EvidenceError):validate_candidate_window_recovery_event(event)

    def test_empty_event_set_audits_primary_but_does_not_claim_ledger_completeness(self):
        _,archive,configuration,runtime,primary=self.make()
        result=audit_candidate_window_recovery_events([],archive,configuration,runtime,external_resolver=primary.__getitem__)
        self.assertEqual(result['events_checked'],0);self.assertGreater(result['primary_files_checked'],0)
        self.assertFalse(result['service_ledger_completeness_verified'])
        self.assertFalse(result['live_authority_restored']);self.assertFalse(result['training_certificate_verified'])

    def test_real_valid_geometry_without_measurement_cannot_authorize_recovery(self):
        event,archive,configuration,runtime,primary=self.make()
        archive['records'][2].update(consumed=False,measurement=None)
        archive['artifact_document_sha256']=expected_artifact_document_id(archive)
        with self.assertRaisesRegex(EvidenceError,'requires_unassigned_peak'):
            audit_candidate_window_recovery_events([event],archive,configuration,runtime,external_resolver=primary.__getitem__)

    def test_rehashed_event_cannot_point_outside_closed_archive(self):
        event,archive,configuration,runtime,primary=self.make();event['group_id']='absent';resign(event)
        with self.assertRaisesRegex(EvidenceError,'group_missing'):
            audit_candidate_window_recovery_events([event],archive,configuration,runtime,external_resolver=primary.__getitem__)

    def test_changed_external_primary_is_rejected_even_with_no_claimed_events(self):
        _,archive,configuration,runtime,primary=self.make()
        with self.assertRaises(EvidenceError):
            audit_candidate_window_recovery_events([],archive,configuration,runtime,external_resolver=lambda name:primary[name]+b'changed')

    def test_legacy_runtime_cannot_be_relabelled_as_recovery_execution(self):
        _,archive,configuration,runtime,primary=self.make();runtime['schema_version']=2
        with self.assertRaises(EvidenceError):
            audit_candidate_window_recovery_events([],archive,configuration,runtime,external_resolver=primary.__getitem__)
