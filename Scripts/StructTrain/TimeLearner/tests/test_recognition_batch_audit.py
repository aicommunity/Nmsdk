"""Real native observations, strict batch guards and legacy result equivalence."""
from copy import deepcopy
import os
from pathlib import Path
import time
import unittest
from unittest.mock import patch

from ..model_identity import canonical_model_sha256 as sha
from ..native_calibration_worker import _write
from ..native_evidence import EvidenceError, load
from ..recognition_metrics import load_diagnostic_evaluation, score_diagnostic_recognition_evaluation
from ..recognition_trial_evidence import _audit_recognition_trial, _recognition_trial_batch
from .. import threshold_candidate_evidence as candidate_audit


class RecognitionBatchAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(os.environ['TIMELEARNER_BATCH_NATIVE_CASES'])
        declaration = load(root/'cases.json')
        cls.cases = []
        for row in declaration['cases']:
            package = load(root/row['package'])
            observations = [load(root/name) for name in row['observations']]
            cls.cases.append((package, observations, row['diagnostic']))
        kinds = {p['kind'] for p, _, _ in cls.cases}
        if kinds != {'timelearner_recognition_state', 'timelearner_recognition_threshold_candidate',
                     'timelearner_diagnostic_threshold_candidate', 'timelearner_calibrated_recognition_state'}:
            raise RuntimeError('requires actual ordinary/candidate/diagnostic/calibrated native models')
        cls.diagnostics = [c for c in cls.cases if c[2]]
        if len(cls.diagnostics) != 2:
            raise RuntimeError('requires both actual Classic and Branch diagnostic models')

    def test_batch_matches_standalone_audits_in_all_declared_native_modes(self):
        for package, observations, diagnostic in self.cases:
            expected = [_audit_recognition_trial(o, package, diagnostic=diagnostic) for o in observations]
            with _recognition_trial_batch(package, diagnostic=diagnostic) as audit:
                self.assertEqual([audit(o) for o in observations], expected)

    def test_threshold_derivation_is_checked_once_per_scope_and_again_next_call(self):
        for package, observations, diagnostic in self.diagnostics:
            original = candidate_audit.audit_diagnostic_threshold_candidate
            with patch.object(candidate_audit, 'audit_diagnostic_threshold_candidate', wraps=original) as counted:
                with _recognition_trial_batch(package, diagnostic=True) as audit:
                    for o in observations:
                        audit(o)
                self.assertEqual(counted.call_count, 1)
                with _recognition_trial_batch(package, diagnostic=True) as audit:
                    audit(observations[0])
                self.assertEqual(counted.call_count, 2)

    def test_late_corruption_is_not_hidden_by_earlier_valid_observations(self):
        for package, observations, diagnostic in self.diagnostics:
            broken = []
            o = deepcopy(observations[-1]);o['spike_count'] += 1;broken.append(o)
            o = deepcopy(observations[-1]);o['samples'][-1]['soma'][0] = float('nan');broken.append(o)
            o = deepcopy(observations[-1]);o['samples'][-1]['time'] += 2/o['frequency_hz'];broken.append(o)
            o = deepcopy(observations[-1]);o['model_after'] = 'changed';broken.append(o)
            for bad in broken:
                with self.assertRaises(EvidenceError):
                    with _recognition_trial_batch(package, diagnostic=True) as audit:
                        for earlier in observations[:-1]:
                            audit(earlier)
                        audit(bad)

    def test_changed_or_resigned_package_cannot_leave_the_scope(self):
        for package, observations, diagnostic in self.diagnostics:
            for resign in (False, True):
                changed = deepcopy(package)
                with self.assertRaisesRegex(EvidenceError, 'recognition_model_changed_during_batch'):
                    with _recognition_trial_batch(changed, diagnostic=True) as audit:
                        audit(observations[0])
                        changed['implementation_id'] += '-changed'
                        if resign:
                            changed['sha256'] = sha({k:v for k,v in changed.items() if k != 'sha256'})
                        audit(observations[-1])

    def test_a_new_call_never_reuses_an_old_model_proof(self):
        for package, observations, diagnostic in self.diagnostics:
            changed = deepcopy(package)
            with _recognition_trial_batch(changed, diagnostic=True) as audit:
                audit(observations[0])
            changed['threshold'] += 1.
            changed['sha256'] = sha({k:v for k,v in changed.items() if k != 'sha256'})
            with self.assertRaises(EvidenceError):
                with _recognition_trial_batch(changed, diagnostic=True) as audit:
                    audit(observations[0])

    def test_observation_physics_uses_an_isolated_immutable_projection(self):
        for package, observations, diagnostic in self.diagnostics:
            changed = deepcopy(package)
            expected = _audit_recognition_trial(observations[0], changed, diagnostic=True)
            model = changed['source_recognition']['source_solo']['configuration']['model']
            old_frequency = model['frequency_hz']
            with _recognition_trial_batch(changed, diagnostic=True) as audit:
                model['frequency_hz'] *= 10
                self.assertEqual(audit(observations[0]), expected)
                model['frequency_hz'] = old_frequency


class LargeNativeBatchEquivalenceTest(unittest.TestCase):
    def test_actual_eight_pattern_metrics_equal_original_production_result(self):
        from ..stopped_evidence import load_case
        source = Path(os.environ['TIMELEARNER_BATCH_LARGE_CANDIDATE'])
        manifest = load(source/'run-manifest.json')
        expected = manifest['analysis']['metrics']
        self.assertEqual(expected['pooled_counts']['TP'], 1)
        self.assertEqual(expected['pooled_counts']['FP'], 1)
        spec, observations = load_diagnostic_evaluation(source/'native/evaluation.json')
        package = load(source/'native/model.json')
        case = load_case(source/'input/source/train_stopped_state.json')
        start = time.perf_counter()
        original = candidate_audit.audit_diagnostic_threshold_candidate
        with patch.object(candidate_audit, 'audit_diagnostic_threshold_candidate', wraps=original) as counted:
            actual = score_diagnostic_recognition_evaluation(spec, observations, package, case)
        self.assertEqual(actual, expected)
        # One full source/derivation proof and one batch model binding; no
        # repeated package proof for each of the eight actual observations.
        self.assertEqual(counted.call_count, 2)
        _write(Path(os.environ['TMPDIR'])/'large-batch-equivalence.json',
            dict(kind='native_large_batch_equivalence', schema_version=1, trials=len(observations),
                 model_revision=actual['model_revision'], counts=actual['pooled_counts'],
                 full_metrics_equal_original=True, threshold_derivation_calls=counted.call_count,
                 scoring_wall_seconds=time.perf_counter()-start, new_native_calculation=False,
                 controlled_speedup_claim=False, scientific_verdict=None))
