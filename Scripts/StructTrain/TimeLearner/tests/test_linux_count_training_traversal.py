"""Linux search-factor declarations, without native/physics admission."""
from copy import deepcopy
import unittest

from ..input_traversal import FIELD, KIND, POLICY, declare_input_traversal_job
from ..linux_count_training import declared_count_job
from ..model_identity import canonical_model_sha256 as digest
from ..n0_length_policy import declare_n0_length_job
from ..native_evidence import EvidenceError
from ..native_pipeline_worker import validate_job
from ..prepared_count_training import matched_count_job, factor_control_job
from .test_candidate_window_training_job import cold7, job


def original_job(*, branch=False):
    config = cold7(branch=branch, n=4)
    config['model']['normalization'] = 'N1'
    for index, bound in enumerate(config['search']['bounds']):
        bound.update(minimum_synapses=1, maximum_synapses=1)
        if index == 3:
            bound.update(minimum_length=1, maximum_length=1,
                         minimum_resistance=1., maximum_resistance=1.)
    value = job(config)
    validate_job('train', value)
    return value


def request(version=3):
    spec = dict(schema_version=version, run_id='declared-linux-factor', maximum_synapses=128)
    if version >= 2:
        spec['maximum_n0_length_proposals'] = 0
    if version == 3:
        spec[FIELD] = dict(kind=KIND, schema_version=1, policy=POLICY,
                          candidates_per_visit=3, maximum_seed_elements=131072)
    return spec


class LinuxCountTrainingTraversalTest(unittest.TestCase):
    def test_legacy_requests_keep_the_same_complete_job(self):
        original = original_job()
        for version in (1, 2):
            spec = request(version)
            baseline = matched_count_job(original, spec['run_id'], maximum_synapses=128)
            self.assertEqual(declared_count_job(original, spec), baseline)
        spec = request(2)
        spec['maximum_n0_length_proposals'] = 4
        self.assertEqual(declared_count_job(original, spec),
                         declare_n0_length_job(baseline, spec['run_id'], 4))

    def test_quantum_is_applied_without_changing_physics_protocol_tolerances_or_budgets(self):
        original = original_job()
        before = deepcopy(original)
        for quantum in (1, 3):
            spec = request()
            spec[FIELD]['candidates_per_visit'] = quantum
            declared = declared_count_job(original, spec)
            baseline = declared_count_job(original, request(2))
            expected = declare_input_traversal_job(baseline, spec['run_id'], policy=POLICY,
                                                   candidates_per_visit=quantum)
            self.assertEqual(declared, expected)
            stripped = deepcopy(declared)
            stripped['configuration']['search'].pop(FIELD)
            stripped['sha256'] = digest({k: v for k, v in stripped.items() if k != 'sha256'})
            self.assertEqual(stripped, baseline)
            self.assertEqual(original, before)

    def test_positive_factor_control_keeps_the_traversal_and_is_a_valid_preflight(self):
        declared = declared_count_job(original_job(), request())
        factor = factor_control_job(declared)
        validate_job('preflight', factor)
        self.assertEqual(factor['configuration']['model']['inputs'][0]['synapses'], 2)
        self.assertEqual(factor['configuration']['search'][FIELD],
                         declared['configuration']['search'][FIELD])

    def test_unknown_or_corrupt_wire_cannot_be_silently_ignored(self):
        original = original_job()
        for defect in ('version', 'extra', 'missing', 'boolean', 'quantum', 'seed', 'sequential'):
            spec = request()
            wire = spec[FIELD]
            if defect == 'version': wire['schema_version'] = 2
            elif defect == 'extra': wire['unapplied_factor'] = 1
            elif defect == 'missing': wire.pop('candidates_per_visit')
            elif defect == 'boolean': wire['candidates_per_visit'] = True
            elif defect == 'quantum': wire['candidates_per_visit'] = 5
            elif defect == 'seed': wire['maximum_seed_elements'] = 1
            else: wire['policy'] = 'sequential'
            with self.subTest(defect=defect), self.assertRaises(EvidenceError):
                declared_count_job(original, spec)

    def test_branch_rejects_classic_only_traversal(self):
        with self.assertRaisesRegex(EvidenceError, 'requires_classic'):
            declared_count_job(original_job(branch=True), request())

    def test_request_version_must_be_supported_and_integral(self):
        original = original_job()
        for version in (0, 4, True, 1.0):
            spec = request()
            spec['schema_version'] = version
            with self.subTest(version=version), self.assertRaisesRegex(EvidenceError, 'request_version'):
                declared_count_job(original, spec)
        for version in (1, 2):
            spec = request(version)
            spec[FIELD] = request()[FIELD]
            with self.subTest(unconsumed_factor_version=version), self.assertRaisesRegex(
                    EvidenceError, 'factor_version'):
                declared_count_job(original, spec)
