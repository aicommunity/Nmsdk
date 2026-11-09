"""Actual C++ package6 corpus replay; required fixture, workers only.

Missing corpus is an error, never a skip or synthetic fallback. These tests
cannot be declared executed until the new C++ producer gate emits its corpus.
"""
from copy import deepcopy
import hashlib
import os
from pathlib import Path
import unittest

from ..candidate_window_package_evidence import audit_candidate_window_package
from ..composite_package_evidence import audit_composite_package
from ..composite_primary import filesystem_primary_resolver
from ..model_identity import canonical_model_sha256 as digest
from ..native_evidence import EvidenceError, load, require


class CandidateWindowPackage6NativeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value=os.environ.get('TIMELEARNER_NATIVE_PACKAGE6_FIXTURES')
        require(value is not None,'actual_package6_corpus_binding_required')
        cls.root=Path(value);require(cls.root.is_dir() and not cls.root.is_symlink(),'actual_package6_corpus_missing')

    def case(self,relative):
        directory=self.root/relative
        paths=[p for p in (directory/'train_learned_state.json',directory/'train_stopped_state.json') if p.is_file()]
        require(len(paths)==1,'actual_package6_original_package_missing')
        return load(paths[0]),directory

    def audit(self,relative):
        package,directory=self.case(relative)
        return package,audit_candidate_window_package(package,external_resolver=filesystem_primary_resolver(directory))

    def test_classic_complete_actual_model_original_targets_and_cert3(self):
        package,result=self.audit('package6-classic/source-0')
        self.assertTrue(result['exact']);self.assertTrue(result['certificate_consistent'])
        self.assertEqual(package['certificate']['schema_version'],3);self.assertFalse(result['terminal_provenance_verified'])

    def test_branch_reverse_order_actual_model_and_cert3(self):
        _,result=self.audit('package6-branch/source-0')
        self.assertTrue(result['exact']);self.assertFalse(result['native_execution_verified'])

    def test_asymmetric_actual_C0_uses_immutable_origin_and_effective_children(self):
        package,result=self.audit('package6-branch/source-1')
        self.assertIsNotNone(package['capacitance_state']);self.assertIsNotNone(result['capacitance_state'])

    def test_stopped_actual_growth_is_not_reconstructed_from_initial_template(self):
        for topology in ('classic','branch'):
            with self.subTest(topology=topology):
                package,result=self.audit('package6-'+topology+'/source-2')
                self.assertNotEqual(package['model_revision'],package['capture_revision'])
                self.assertIsNone(result['exact']);self.assertFalse(result['certificate_consistent'])

    def test_raw_partials_keep_primary_without_promoting_targets(self):
        for topology in ('classic','branch'):
            with self.subTest(topology=topology):
                package,result=self.audit('package6-'+topology+'/source-3')
                self.assertFalse(package['reference_complete']);self.assertIsNone(result['mathematical_exact'])

    def test_reference_prefix_is_not_allN_capture(self):
        package,result=self.audit('package6-classic/source-4')
        self.assertFalse(package['reference_complete']);self.assertIsNone(result['mathematical_exact'])

    def test_default_sync_actual_finals_remain_nonexact_and_public_null(self):
        package,result=self.audit('package6-classic/source-5')
        self.assertIsNone(package['certificate']);self.assertIs(result['mathematical_exact'],False)
        self.assertIsNone(result['exact'])

    def test_stop_after_exact_final_is_math_exact_but_not_completed(self):
        package,result=self.audit('package6-classic/source-6')
        self.assertIsNone(package['certificate']);self.assertTrue(result['mathematical_exact'])
        self.assertIsNone(result['exact']);self.assertFalse(result['certificate_consistent'])

    def test_imported_warm_keeps_original_family_with_current_runtime(self):
        for relative in ('package6-classic/imported-warm','package6-branch/asymmetric-imported-warm'):
            with self.subTest(relative=relative):
                package,result=self.audit(relative);archive=package['measurement_archive']
                references=set(archive['reference_group_ids'])
                self.assertTrue(any(r['group_id'] in references and r['attempt_id']!=archive['current_attempt_id'] for r in archive['records']))
                self.assertFalse(result['live_authority_restored'])

    def test_started_zero_group_attempt_binds_current_physics(self):
        package,result=self.audit('package6-classic/started-zero-group')
        self.assertEqual(package['measurement_archive']['records'],[]);self.assertEqual(result['logical_groups'],0)
        self.assertIsNone(result['mathematical_exact'])

    def test_declared_external_resolver_cannot_fall_back_to_embedded_primary(self):
        package,_=self.case('package6-classic/source-0')
        with self.assertRaises(EvidenceError):audit_candidate_window_package(package,external_resolver={})

    def test_rehashed_certificate_recipe_tamper_does_not_replace_actual_measurement(self):
        package,_=self.case('package6-classic/source-0');bad=deepcopy(package)
        bad['certificate']['final_window_recipe_ids'][0]='0'*64
        bad['certificate']['semantic_certificate_id']=digest({k:v for k,v in bad['certificate'].items() if k!='semantic_certificate_id'})
        bad['sha256']=digest({k:v for k,v in bad.items() if k!='sha256'})
        with self.assertRaises(EvidenceError):audit_candidate_window_package(bad)

    def test_coherent_public_rewrite_still_cannot_attest_original_completion(self):
        directory=self.root/'package6-classic/coherent-data-only-promotion'
        original=directory/'original-export.json';rewritten=directory/'recomputed-data.json'
        require(original.is_file() and rewritten.is_file(),'actual_coherent_rewrite_counterexample_missing')
        self.assertNotEqual(hashlib.sha256(original.read_bytes()).hexdigest(),hashlib.sha256(rewritten.read_bytes()).hexdigest())
        result=audit_candidate_window_package(load(rewritten))
        self.assertFalse(result['terminal_provenance_verified']);self.assertFalse(result['native_execution_verified'])
        self.assertTrue(result['completed_classification_requires_original_execution_binding'])

    def test_actual_legacy_package5_full_primary_regression_remains_selected(self):
        package,directory=self.case('package5-classic')
        self.assertEqual(package['schema_version'],5)
        result=audit_composite_package(package,external_resolver=filesystem_primary_resolver(directory))
        self.assertTrue(result['certificate_consistent']);self.assertFalse(result['native_execution_verified'])

    def test_actual_summary7_binds_source_groups_model_and_residuals(self):
        for topology in ('classic','branch'):
            package,directory=self.case('package6-'+topology+'/source-0')
            summary=load(directory/'train_learned_summary.json')
            result=audit_candidate_window_package(package,summary,external_resolver=filesystem_primary_resolver(directory))
            self.assertTrue(result['summary_checked']);self.assertTrue(result['summary']['summary_consistent'])
            self.assertFalse(result['native_execution_verified'])

    def test_actual_summary7_cannot_be_relabelled_or_change_source_outcome(self):
        package,directory=self.case('package6-classic/source-0');summary=load(directory/'train_learned_summary.json')
        for field,value in [('schema_version',6),('outcome','external_stop'),('actual_model_revision','different-model')]:
            bad=deepcopy(summary);bad[field]=value
            with self.subTest(field=field), self.assertRaises(EvidenceError):
                audit_candidate_window_package(package,bad,external_resolver=filesystem_primary_resolver(directory))
