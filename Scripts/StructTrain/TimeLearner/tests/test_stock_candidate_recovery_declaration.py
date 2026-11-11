"""Declaration regressions only; actual stock storage/preflight runs separately."""
from copy import deepcopy
import unittest

from ..composite_configuration import project_training_configuration
from ..n1_protocol_robustness import _signed
from ..native_evidence import EvidenceError
from ..stock_candidate_window_study import recovery_declaration
from .test_candidate_window_training_job import cold7, job


def source_job(branch=False):
    configuration = cold7(branch=branch, n=4)
    configuration['model']['normalization'] = 'N1'
    return job(configuration)


class StockCandidateRecoveryDeclarationTest(unittest.TestCase):
    def test_only_recovery_envelope_and_attempt_identity_change(self):
        for branch in (False, True):
            original = source_job(branch);before = deepcopy(original)
            result = recovery_declaration(original, 'new-cold-attempt')
            self.assertEqual(original, before)
            expected = deepcopy(original)
            expected['configuration'].update(schema_version=8, run_id='new-cold-attempt',
                invalid_measurement_recovery='advance_rejected_candidate_window')
            self.assertEqual(result, _signed(expected))
            left = project_training_configuration(original['configuration'])
            right = project_training_configuration(result['configuration'])
            left.pop('run_id');right.pop('run_id')
            self.assertEqual(left, right)

    def test_corrupt_job_digest_is_rejected(self):
        original = source_job();original['configuration']['run_id'] += '/tampered'
        with self.assertRaises(EvidenceError):
            recovery_declaration(original, 'new-attempt')

    def test_technical_N2_or_relaxed_tolerance_cannot_be_called_strict_N4(self):
        for change in ('N2', 'N0', 'tolerance', 'minimum_amplitude', 'no_invalid_budget'):
            original = source_job()
            if change == 'N2':
                configuration = cold7(n=2);configuration['model']['normalization'] = 'N1'
                original = job(configuration)
            elif change == 'N0': original['configuration']['model']['normalization'] = 'N0'
            elif change == 'tolerance': original['configuration']['search']['tolerances']['sync'] = .2
            elif change == 'minimum_amplitude': original['configuration']['minimum_amplitude'] = 1e-5
            else: original['configuration']['search']['maximum_invalid_observations'] = 0
            original = _signed(original)
            with self.subTest(change=change), self.assertRaises(EvidenceError):
                recovery_declaration(original, 'new-attempt')

    def test_repeated_upgrade_is_not_silently_reinterpreted(self):
        original = recovery_declaration(source_job(), 'first')
        with self.assertRaises(EvidenceError):
            recovery_declaration(original, 'second')
