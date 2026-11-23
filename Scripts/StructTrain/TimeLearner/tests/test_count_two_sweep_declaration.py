"""Production budget declarations using a real completed cold N0 job."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import validate_job
from ..prepared_count_training import doubled_sweep_count_job, factor_control_job, matched_count_job


class CountTwoSweepDeclarationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = Path(os.environ['TIMELEARNER_TWO_SWEEP_SOURCE_JOB']).resolve(strict=True)
        cls.original_bytes = cls.path.read_bytes()
        cls.original = load(cls.path)
        cls.resistance = load(Path(os.environ['TIMELEARNER_TWO_SWEEP_N1_SOURCE_JOB']))

    def changed(self, edit):
        original = deepcopy(self.original)
        edit(original)
        original['sha256'] = sha({k:v for k,v in original.items() if k != 'sha256'})
        return original

    def test_only_declared_search_effort_and_run_identity_change(self):
        actual = doubled_sweep_count_job(self.original, 'two-sweep-validation')
        self.assertEqual(actual['configuration']['search']['maximum_sweeps'], 2)
        self.assertEqual(actual['configuration']['search']['maximum_probes'], 320)
        self.assertEqual(actual['configuration']['maximum_wall_seconds'], 64800)
        restored = deepcopy(actual)
        for key in ('run_id', 'maximum_wall_seconds'):
            restored['configuration'][key] = self.original['configuration'][key]
        for key in ('maximum_sweeps', 'maximum_probes'):
            restored['configuration']['search'][key] = self.original['configuration']['search'][key]
        restored['sha256'] = self.original['sha256']
        self.assertEqual(restored, self.original)

    def test_production_preflight_and_train_accept_the_same_new_declaration(self):
        actual = doubled_sweep_count_job(self.original, 'two-sweep-production-validation')
        for mode in ('preflight', 'train'):
            with self.subTest(mode=mode):
                self.assertEqual(validate_job(mode, actual)['job_sha256'], actual['sha256'])

    def test_source_file_and_decoded_source_remain_unchanged(self):
        before = deepcopy(self.original)
        doubled_sweep_count_job(self.original, 'two-sweep-source-immutability')
        self.assertEqual(self.original, before)
        self.assertEqual(self.path.read_bytes(), self.original_bytes)

    def test_existing_matched_count_declaration_is_unchanged(self):
        actual = matched_count_job(self.resistance, self.original['configuration']['run_id'])
        self.assertEqual(actual, self.original)

    def test_existing_positive_control_still_constructs_a_shared_bank(self):
        actual = doubled_sweep_count_job(self.original, 'two-sweep-factor-validation')
        factor = factor_control_job(actual)
        validate_job('preflight', factor)
        self.assertTrue(actual['configuration']['model']['branch'])
        self.assertEqual([i['synapses'] for i in factor['configuration']['model']['inputs']], [2]*4)
        self.assertEqual(actual['configuration']['model'], self.original['configuration']['model'])

    def test_source_hash_damage_is_rejected(self):
        bad = deepcopy(self.original)
        bad['configuration']['search']['maximum_sweeps'] = 2
        with self.assertRaisesRegex(EvidenceError, 'count_extension_source_digest'):
            doubled_sweep_count_job(bad, 'bad-hash')

    def test_a_second_extension_is_not_an_implicit_budget_escalation(self):
        actual = doubled_sweep_count_job(self.original, 'two-sweeps')
        with self.assertRaisesRegex(EvidenceError, 'count_extension_requires_one_sweep_count_source'):
            doubled_sweep_count_job(actual, 'four-sweeps-forbidden')

    def test_resistance_training_cannot_be_silently_changed_to_count_training(self):
        with self.assertRaisesRegex(EvidenceError, 'count_extension_requires_one_sweep_count_source'):
            doubled_sweep_count_job(self.resistance, 'wrong-normalization')

    def test_a_non_cold_synapse_count_is_rejected(self):
        bad = factor_control_job(self.original)
        with self.assertRaisesRegex(EvidenceError, 'count_extension_requires_original_cold_count_physics'):
            doubled_sweep_count_job(bad, 'warm-graph-forbidden')

    def test_resistance_search_cannot_be_hidden_in_the_source(self):
        bad = self.changed(lambda j: j['configuration']['search']['bounds'][0].update(
            minimum_resistance=1.))
        with self.assertRaisesRegex(EvidenceError, 'count_extension_requires_original_cold_count_physics'):
            doubled_sweep_count_job(bad, 'changed-search-dimension')

    def test_empty_or_nontext_run_identity_is_rejected(self):
        for value in ('', ' ', None, 1, True):
            with self.subTest(value=value), self.assertRaisesRegex(EvidenceError, 'count_extension_run_id'):
                doubled_sweep_count_job(self.original, value)


if __name__ == '__main__':
    unittest.main()
