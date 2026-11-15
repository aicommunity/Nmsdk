"""Versioned recovery declarations, DATA only; execute on the workers.

These fixtures do not prove native delivery, physical learning or persistence.
The native wire producer is checked separately with the same production readers.
"""
from copy import deepcopy
import unittest

from ..candidate_window_contract import configuration_view, validate_protocol
from ..candidate_window_runtime_plan import (
    audit_candidate_window_runtime_plan, audit_candidate_window_runtime_recovery_plan,
)
from ..native_evidence import EvidenceError
from .synthetic_candidate_archive2 import source_data, runtime2


class CandidateWindowRuntime3DeclarationTest(unittest.TestCase):
    def make(self):
        configuration,protocol,_,binding=source_data()
        runtime=runtime2(configuration,protocol,binding['model_identity']['sha256'])
        configuration['schema_version']=8
        configuration['invalid_measurement_recovery']='advance_rejected_candidate_window'
        configuration['search']['maximum_invalid_observations']=2
        runtime['schema_version']=3
        runtime['search']['invalid_measurement_recovery']='advance_rejected_candidate_window'
        runtime['search']['maximum_invalid_observations']=2
        return runtime,configuration,protocol

    def test_explicit_versions_preserve_original_and_do_not_restore_authority(self):
        plan,configuration,protocol=self.make(); original=deepcopy(configuration)
        result=audit_candidate_window_runtime_recovery_plan(plan,configuration,protocol)
        self.assertEqual(result['runtime_plan_schema_version'],3)
        self.assertFalse(result['live_authority_restored'])
        self.assertFalse(result['training_certificate_verified'])
        self.assertFalse(result['native_execution_verified'])
        self.assertIsNone(result['scientific_verdict'])
        self.assertEqual(configuration,original)
        self.assertEqual(configuration_view(configuration)['schema_version'],6)

    def test_legacy_runtime_reader_rejects_new_policy(self):
        plan,configuration,protocol=self.make()
        with self.assertRaises(EvidenceError):audit_candidate_window_runtime_plan(plan,configuration,protocol)

    def test_version_and_policy_cannot_be_downgraded_or_relabelled(self):
        for version,policy in [(2,'advance_rejected_candidate_window'),(3,'retry_same_candidate'),
                               (4,'advance_rejected_candidate_window'),(3,'advance_unassigned_burst')]:
            plan,configuration,protocol=self.make();plan['schema_version']=version
            plan['search']['invalid_measurement_recovery']=policy
            with self.subTest(version=version,policy=policy),self.assertRaises(EvidenceError):
                audit_candidate_window_runtime_recovery_plan(plan,configuration,protocol)

    def test_recovery_requires_positive_integer_invalid_budgets(self):
        for value in [0,-1,True,0.5,float('nan')]:
            for owner in ['configuration','runtime']:
                plan,configuration,protocol=self.make()
                (configuration if owner=='configuration' else plan)['search']['maximum_invalid_observations']=value
                with self.subTest(value=value,owner=owner),self.assertRaises(EvidenceError):
                    audit_candidate_window_runtime_recovery_plan(plan,configuration,protocol)

    def test_cold8_requires_exact_policy_and_rejects_extra_fields(self):
        for key,value in [('invalid_measurement_recovery','retry_same_candidate'),
                          ('invalid_measurement_recovery',None),('unknown_recovery_field',True)]:
            _,configuration,protocol=self.make();configuration[key]=value
            with self.subTest(key=key,value=value),self.assertRaises(EvidenceError):validate_protocol(protocol,configuration)

    def test_cold7_cannot_silently_carry_new_policy(self):
        _,configuration,protocol=self.make();configuration['schema_version']=7
        with self.assertRaises(EvidenceError):validate_protocol(protocol,configuration)

    def test_runtime_binding_unknown_fields_and_nonfinite_budget_remain_strict(self):
        for key,value in [('protocol_binding','0'*64),('unknown_recovery_field',1),('maximum_wall_seconds',float('inf'))]:
            plan,configuration,protocol=self.make();plan[key]=value
            with self.subTest(key=key),self.assertRaises(EvidenceError):
                audit_candidate_window_runtime_recovery_plan(plan,configuration,protocol)

    def test_legacy_versions_remain_retry_only_and_unchanged(self):
        configuration,protocol,_,binding=source_data()
        plan=runtime2(configuration,protocol,binding['model_identity']['sha256'])
        original=deepcopy((plan,configuration,protocol))
        self.assertEqual(audit_candidate_window_runtime_plan(plan,configuration,protocol)['runtime_plan_schema_version'],2)
        self.assertEqual((plan,configuration,protocol),original)
        with self.assertRaises(EvidenceError):audit_candidate_window_runtime_recovery_plan(plan,configuration,protocol)
