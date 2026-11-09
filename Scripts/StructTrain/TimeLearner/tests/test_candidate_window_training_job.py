"""Production job validation regressions; declarations only, WORKERS ONLY."""
from copy import deepcopy
import unittest

from ..composite_configuration import project_composite_configuration, project_training_configuration
from ..model_identity import canonical_model_sha256 as digest
from ..native_evidence import EvidenceError
from ..native_pipeline_worker import validate_job
from .test_composite_configuration import configuration
from .test_candidate_window_archive_evidence import policy


def cold7(base=1, *, branch=False, n=2):
    value = configuration(base, branch=branch, n=n)
    value['schema_version'] = 7
    value['composite_measurement']['schema_version'] = 2
    value['composite_measurement']['candidate_window_policy'] = policy(n)
    return value


def job(config):
    value = dict(kind='timelearner_native_training_job', schema_version=1,
        owner_class='NNeuronTimeLearner'+('Branch' if config['model']['branch'] else ''),
        implementation_id='declared-cold7-production-validation-only', configuration=config,
        profile_archives=[], optional_modes=dict(sync_capacitance_trim=0, post_train_tuning=False,
        auto_calibrate_threshold=False), calculate_mode=0, structure_build_mode=1, maximum_model_ticks=20000)
    value['sha256'] = digest(value)
    return value


class CandidateWindowTrainingJobTest(unittest.TestCase):
    def test_actual_train_and_preflight_entry_accept_explicit_cold7(self):
        for branch in (False, True):
            for n in (2, 4, 6):
                for mode in ('train', 'preflight'):
                    value = job(cold7(branch=branch, n=n)); before = deepcopy(value)
                    with self.subTest(branch=branch, n=n, mode=mode):
                        result = validate_job(mode, value)
                        self.assertEqual(value, before)
                        self.assertEqual(result['job_sha256'], value['sha256'])
                        self.assertEqual(result['composite_measurement_declaration']['configuration_schema'], 7)
                        self.assertEqual(result['composite_measurement_declaration']['protocol_schema'], 5)
                        self.assertFalse(result['effective_model_checked'])
                        self.assertTrue(result['native_configuration_validation_required'])

    def test_base_versions_keep_repeats_C_history_and_search_without_changing_the_original(self):
        for base in (1, 2, 3, 4):
            value = cold7(base); before = deepcopy(value)
            view = project_training_configuration(value)
            old = configuration(base); expected = project_composite_configuration(old)
            with self.subTest(base=base):
                self.assertEqual(view, expected)
                self.assertEqual(value, before)
                self.assertEqual(view['model'], value['model'])
                self.assertEqual(view['search']['tolerances'], dict(amplitude_absolute=1e-5, amplitude_relative=0., sync=.02))
                view['model']['initial_isi'][0] = 99.
                self.assertEqual(value, before)

    def test_metadata_preflight_never_creates_training_or_live_admission_proof(self):
        result = validate_job('preflight', job(cold7()))
        scope = result['composite_measurement_declaration']
        self.assertFalse(scope['live_measurement_admission_verified'])
        self.assertFalse(scope['training_certificate_verified'])
        self.assertTrue(scope['native_effective_preflight_required'])
        self.assertFalse(result['primary_source_checked'])

    def test_missing_candidate_policy_fails_in_cold7_contract(self):
        value = cold7(); value['composite_measurement'].pop('candidate_window_policy')
        with self.assertRaisesRegex(EvidenceError, 'candidate_window_native_policy2_fields'):
            validate_job('preflight', job(value))

    def test_policy_and_window_corruption_cannot_fall_back_to_legacy_validation(self):
        for change in ('policy', 'window', 'common_version', 'unknown_field'):
            value = cold7()
            if change == 'policy': value['composite_measurement']['candidate_window_policy']['policy_id'] = 'unknown'
            elif change == 'window': value['windows'][0]['end'] = value['duration']+1
            elif change == 'common_version': value['composite_measurement']['schema_version'] = 1
            else: value['unused_experiment_factor'] = 1
            with self.subTest(change=change), self.assertRaises(EvidenceError):
                validate_job('train', job(value))

    def test_cold6_still_uses_its_own_contract(self):
        value = configuration(); before = deepcopy(value)
        self.assertEqual(project_training_configuration(value), project_composite_configuration(value))
        result = validate_job('train', job(value))
        self.assertEqual(value, before)
        self.assertEqual(result['composite_measurement_declaration']['method_id'], value['composite_measurement']['method_id'])

    def test_cold6_cannot_silently_adopt_candidate_policy2(self):
        value = cold7(); value['schema_version'] = 6
        with self.assertRaises(EvidenceError): validate_job('preflight', job(value))

    def test_legacy_envelopes_do_not_silently_accept_composite_measurement(self):
        for version in (1, 2, 3, 4, 5):
            value = cold7(); value['schema_version'] = version
            with self.subTest(version=version), self.assertRaises(EvidenceError):
                validate_job('train', job(value))
