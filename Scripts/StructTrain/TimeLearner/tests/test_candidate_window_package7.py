"""Version dispatch/runtime DATA checks, separate from native package7 corpus."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from ..candidate_window_archive_evidence import (audit_candidate_window_archive,
                                                audit_candidate_window_recovery_archive)
from ..candidate_window_package_evidence import (audit_candidate_window_package,
                                                audit_candidate_window_recovery_package, _runtime_context)
from ..composite_package_evidence import audit_composite_package
from ..learned_evidence import audit_learned_state, load_case as load_learned
from ..stopped_evidence import audit_stopped_state, load_case as load_stopped
from ..native_evidence import EvidenceError
from .synthetic_candidate_archive2 import fixture


class CandidateWindowPackage7MetadataTest(unittest.TestCase):
    def context(self):
        archive,config,plan,primary=fixture()
        plan['schema_version']=3
        plan['search']['invalid_measurement_recovery']='advance_rejected_candidate_window'
        plan['search']['maximum_invalid_observations']=2
        package=dict(measurement_archive=archive,configuration=config,protocol=archive['protocol'],
            runtime_plan=plan,model_revision=plan['initial_model_revision'],model_epoch=plan['initial_model_epoch'])
        return package,primary

    def test_package7_dispatch_uses_its_own_exact_contract(self):
        with self.assertRaisesRegex(EvidenceError,'candidate_window_package7_fields'):
            audit_composite_package(dict(schema_version=7))

    def test_package6_cannot_enter_explicit_package7_reader(self):
        with self.assertRaises(EvidenceError):audit_candidate_window_recovery_package(dict(schema_version=6))
        with self.assertRaises(EvidenceError):audit_candidate_window_package(dict(schema_version=7))

    def test_flat_legacy_primary_cannot_overlay_package7(self):
        for auditor,kind in ((audit_learned_state,'timelearner_completed_state'),
                             (audit_stopped_state,'timelearner_stopped_state')):
            with self.subTest(kind=kind),self.assertRaisesRegex(EvidenceError,'legacy_primary_overlay'):
                auditor(dict(schema_version=7,kind=kind),None,{'invented':{}},{})

    def test_loaders_preserve_original_package_and_optional_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            for suffix,kind,loader in [('learned','timelearner_completed_state',load_learned),
                                       ('stopped','timelearner_stopped_state',load_stopped)]:
                p=Path(directory)/('train_'+suffix+'_state.json')
                document=dict(schema_version=7,kind=kind)
                p.write_text(json.dumps(document),encoding='utf8')
                package,summary,packets,traces=loader(p)
                self.assertEqual(package,document);self.assertIsNone(summary)
                self.assertEqual((packets,traces),({},{}))

    def test_current_runtime3_binds_without_rewriting_initial_configuration(self):
        package,_=self.context();before=deepcopy(package)
        _runtime_context(package,recovery=True)
        self.assertEqual(package,before)
        with self.assertRaises(EvidenceError):_runtime_context(package)

    def test_warm_runtime2_remains_explicitly_supported(self):
        package,_=self.context();plan=package['runtime_plan']
        plan['schema_version']=2;plan['search']['invalid_measurement_recovery']='retry_same_candidate'
        _runtime_context(package,recovery=True)

    def test_recovery_archive_replays_primary_and_active_runtime3(self):
        package,primary=self.context();before=deepcopy(package)
        result=audit_candidate_window_recovery_archive(package['measurement_archive'],package['configuration'],
            runtime_plan=package['runtime_plan'],external_resolver=primary.__getitem__)
        self.assertTrue(result['current_runtime_budget_binding_checked'])
        self.assertGreater(result['primary_files_checked'],0);self.assertEqual(package,before)
        with self.assertRaises(EvidenceError):
            audit_candidate_window_archive(package['measurement_archive'],package['configuration'],
                runtime_plan=package['runtime_plan'],external_resolver=primary.__getitem__)

    def test_recovery_runtime_cannot_change_actual_archive_group_budgets(self):
        package,primary=self.context()
        package['runtime_plan']['composite_measurement']['attempt_limits']['maximum_groups']+=1
        with self.assertRaises(EvidenceError):
            audit_candidate_window_recovery_archive(package['measurement_archive'],package['configuration'],
                runtime_plan=package['runtime_plan'],external_resolver=primary.__getitem__)

    def test_recovery_archive_rejects_unknown_runtime_versions(self):
        for version in (True,1,4):
            package,primary=self.context();package['runtime_plan']['schema_version']=version
            with self.subTest(version=version),self.assertRaises(EvidenceError):
                audit_candidate_window_recovery_archive(package['measurement_archive'],package['configuration'],
                    runtime_plan=package['runtime_plan'],external_resolver=primary.__getitem__)

    def test_recovery_runtime_initial_model_is_not_reconstructed_from_cold(self):
        package,_=self.context();package['runtime_plan']['initial_model_revision']='other-boundary'
        with self.assertRaisesRegex(EvidenceError,'runtime_initial_model'):_runtime_context(package,recovery=True)
