"""Declaration integrity and effective readback; no native/physics admission."""
from copy import deepcopy
import unittest

from ..input_traversal import (FIELD, KIND, POLICY, audit_input_traversal,
    bind_input_traversal, optional_fields)
from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError


def search():
    return dict(normalization='N0',maximum_candidates_per_input=8,
        bounds=[dict(minimum_length=1,maximum_length=256,minimum_synapses=1,
            maximum_synapses=128,minimum_resistance=1.,maximum_resistance=100.) for _ in range(4)],
        input_traversal=dict(kind=KIND,schema_version=1,policy=POLICY,
            candidates_per_visit=3,maximum_seed_elements=131072))


class InputTraversalTest(unittest.TestCase):
    def test_omission_is_legacy_and_does_not_invent_a_factor_or_mutate_input(self):
        value=search();value.pop(FIELD);before=deepcopy(value)
        self.assertIsNone(audit_input_traversal(value,branch=True))
        self.assertEqual(optional_fields(value),set());self.assertEqual(value,before)

    def test_round_robin_binds_all_fields_to_actual_configuration(self):
        declared=search();observed=deepcopy(declared);observed['normalization']='synapse_count'
        before=deepcopy(declared)
        self.assertEqual(bind_input_traversal(declared,observed,branch=False),declared[FIELD])
        self.assertEqual(optional_fields(declared),{FIELD});self.assertEqual(declared,before)

    def test_omitted_or_changed_effective_mode_quantum_or_seed_limit_is_refused(self):
        for field in (None,'candidates_per_visit','maximum_seed_elements'):
            declared=search();observed=deepcopy(declared)
            if field is None:observed.pop(FIELD)
            else:observed[FIELD][field]+=1
            with self.subTest(field=field),self.assertRaises(EvidenceError):
                bind_input_traversal(declared,observed,branch=False)
        declared=search();observed=deepcopy(declared);declared.pop(FIELD)
        with self.assertRaises(EvidenceError):bind_input_traversal(declared,observed,branch=False)

    def test_unknown_schema_extra_fields_wrong_kind_and_noop_policy_are_refused(self):
        for defect in ('schema','kind','policy','extra','missing','not_object'):
            value=search();d=value[FIELD]
            if defect=='schema':d['schema_version']=2
            elif defect=='kind':d['kind']='other'
            elif defect=='policy':d['policy']='sequential'
            elif defect=='extra':d['unapplied_factor']=1
            elif defect=='missing':d.pop('candidates_per_visit')
            else:value[FIELD]=None
            with self.subTest(defect=defect),self.assertRaises(EvidenceError):
                audit_input_traversal(value,branch=False)

    def test_branch_cannot_claim_a_classic_only_factor(self):
        with self.assertRaises(EvidenceError):audit_input_traversal(search(),branch=True)

    def test_boolean_fraction_negative_and_inexact_counts_do_not_pass(self):
        for field in ('schema_version','candidates_per_visit','maximum_seed_elements'):
            for bad in (True,False,-1,0,1.5,float('nan'),float('inf'),2**53):
                value=search();value[FIELD][field]=bad
                with self.subTest(field=field,value=bad),self.assertRaises(EvidenceError):
                    audit_input_traversal(value,branch=False)

    def test_quantum_cannot_exceed_the_existing_candidate_allowance(self):
        value=search();value[FIELD]['candidates_per_visit']=9
        with self.assertRaises(EvidenceError):audit_input_traversal(value,branch=False)

    def test_aggregate_budget_counts_every_input_and_capacitance_context(self):
        value=search();value[FIELD]['maximum_seed_elements']=408
        self.assertIsNotNone(audit_input_traversal(value,branch=False))
        value[FIELD]['maximum_seed_elements']=407
        with self.assertRaises(EvidenceError):audit_input_traversal(value,branch=False)
        value[FIELD]['maximum_seed_elements']=408
        with self.assertRaises(EvidenceError):
            audit_input_traversal(value,branch=False,capacitance_search={'maximum_contexts':3})

    def test_N1_keeps_three_initial_resistance_seeds_even_with_one_candidate(self):
        value=search();value.update(normalization='N1',maximum_candidates_per_input=1)
        value[FIELD].update(candidates_per_visit=1,maximum_seed_elements=11)
        with self.assertRaises(EvidenceError):audit_input_traversal(value,branch=False)
        value[FIELD]['maximum_seed_elements']=12
        self.assertIsNotNone(audit_input_traversal(value,branch=False))

    def test_wide_geometry_does_not_enumerate_the_domain(self):
        value=search()
        for bound in value['bounds']:bound['maximum_length']=2**31-1
        self.assertIsNotNone(audit_input_traversal(value,branch=False))

    def test_fingerprint_changes_with_mode_or_quantum_and_is_order_independent(self):
        value=search();before=canonical_model_sha256(value)
        changed=deepcopy(value);changed[FIELD]['candidates_per_visit']=1
        self.assertNotEqual(before,canonical_model_sha256(changed))
        changed=deepcopy(value);changed.pop(FIELD)
        self.assertNotEqual(before,canonical_model_sha256(changed))
        self.assertEqual(before,canonical_model_sha256(dict(reversed(list(value.items())))))
