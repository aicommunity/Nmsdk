"""Declaration controls; no claim of physical or native convergence."""
import unittest
from ..n0_length_policy import audit_n0_length_policy, bind_n0_length_policy
from ..native_evidence import EvidenceError


class N0LengthPolicyTest(unittest.TestCase):
    def test_absence_preserves_legacy_without_fabricating_a_factor(self):
        search=dict(normalization='N0',maximum_candidates_per_input=8)
        self.assertEqual(audit_n0_length_policy(search),0)
        self.assertNotIn('maximum_n0_length_proposals',search)

    def test_positive_bounded_N0_factor_is_bound_to_observed_configuration(self):
        declared=dict(normalization='N0',maximum_candidates_per_input=8,maximum_n0_length_proposals=4)
        observed=dict(declared,normalization='synapse_count')
        self.assertEqual(bind_n0_length_policy(declared,observed),4)
        observed.pop('maximum_n0_length_proposals')
        with self.assertRaises(EvidenceError):bind_n0_length_policy(declared,observed)

    def test_zero_boolean_fraction_negative_and_excess_budget_are_rejected(self):
        for value in (0,True,1.5,-1,9):
            with self.subTest(value=value),self.assertRaises(EvidenceError):
                audit_n0_length_policy(dict(normalization='N0',maximum_candidates_per_input=8,
                                            maximum_n0_length_proposals=value))

    def test_N1_cannot_claim_the_N0_factor(self):
        for normalization in ('N1','tip_resistance'):
            with self.subTest(normalization=normalization),self.assertRaises(EvidenceError):
                audit_n0_length_policy(dict(normalization=normalization,maximum_candidates_per_input=8,
                                            maximum_n0_length_proposals=4))
