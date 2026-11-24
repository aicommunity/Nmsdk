"""One declared search factor; no physical execution or convergence claim."""
from copy import deepcopy
import unittest

from ..cold_budget import coverage,declare_candidate_limit
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError
from ..native_pipeline_worker import validate_job
from .test_cold_budget import template


class CandidateLimitTrainingTest(unittest.TestCase):
    def test_only_local_limit_and_attempt_identity_change_for_both_topologies_and_normalizers(self):
        for branch in (False,True):
          for normalization in ('N0','N1'):
            with self.subTest(branch=branch,normalization=normalization):
                source=template(branch,normalization=normalization)
                source['configuration']['search'].update(maximum_candidates_per_input=24,maximum_probes=160)
                source['sha256']=sha({k:v for k,v in source.items()if k!='sha256'})
                before=deepcopy(source)
                actual=declare_candidate_limit(source,run_id='candidate-cap-eight',candidates_per_input=8)
                expected=deepcopy(source)
                expected['configuration']['run_id']='candidate-cap-eight'
                expected['configuration']['search']['maximum_candidates_per_input']=8
                expected['sha256']=sha({k:v for k,v in expected.items()if k!='sha256'})
                self.assertEqual(actual,expected)
                self.assertEqual(source,before)
                self.assertEqual(validate_job('train',actual)['job_sha256'],actual['sha256'])
                self.assertEqual(coverage(source)['valid_search_probe_upper_bound_per_sweep'],154)
                self.assertEqual(coverage(actual)['valid_search_probe_upper_bound_per_sweep'],58)
                self.assertFalse(coverage(actual)['convergence_verified'])

    def test_same_limit_is_an_explicit_fresh_baseline_not_forced_physical_difference(self):
        source=template();cap=source['configuration']['search']['maximum_candidates_per_input']
        actual=declare_candidate_limit(source,run_id='fresh-baseline',candidates_per_input=cap)
        self.assertEqual(actual['configuration']['search'],source['configuration']['search'])
        self.assertEqual(actual['configuration']['model'],source['configuration']['model'])

    def test_invalid_values_and_foreign_signature_cannot_create_declarations(self):
        source=template();before=deepcopy(source)
        for cap in (0,-1,True,False,8.0,float('nan'),'8'):
            with self.subTest(cap=cap),self.assertRaises(EvidenceError):
                declare_candidate_limit(source,run_id='invalid-cap',candidates_per_input=cap)
        for run in ('',' ',None,True):
            with self.subTest(run=run),self.assertRaises(EvidenceError):
                declare_candidate_limit(source,run_id=run,candidates_per_input=8)
        damaged=deepcopy(source);damaged['configuration']['model']['inputs'][0]['resistance']*=2
        with self.assertRaises(EvidenceError):
            declare_candidate_limit(damaged,run_id='bad-source',candidates_per_input=8)
        self.assertEqual(source,before)

    def test_existing_N0_turn_must_fit_without_silent_reduction(self):
        source=template();source['configuration']['search'].update(
            maximum_candidates_per_input=24,maximum_n0_length_proposals=4)
        source['sha256']=sha({k:v for k,v in source.items()if k!='sha256'})
        before=deepcopy(source)
        actual=declare_candidate_limit(source,run_id='valid-length-policy',candidates_per_input=8)
        self.assertEqual(actual['configuration']['search']['maximum_n0_length_proposals'],4)
        with self.assertRaisesRegex(EvidenceError,'invalid_n0_length_proposal_budget'):
            declare_candidate_limit(source,run_id='unfunded-length-policy',candidates_per_input=3)
        self.assertEqual(source,before)
