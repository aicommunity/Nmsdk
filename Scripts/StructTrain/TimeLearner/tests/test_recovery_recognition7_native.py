"""Actual C++ source7 recognition corpus; never synthesize missing models."""
from copy import deepcopy
import os
from pathlib import Path
import tempfile
import unittest

from ..candidate_window_package_evidence import audit_candidate_window_recovery_package
from ..composite_primary import filesystem_primary_resolver
from ..diagnostic_recognition_evidence import audit_diagnostic_recognition, audit_diagnostic_recognition_trial
from ..model_identity import canonical_model_sha256 as digest
from ..native_evidence import EvidenceError, load, require
from ..portable_primary import restore_native_bundle
from ..recognition_evidence import audit_recognition_derivation
from ..recognition_trial_evidence import audit_recognition_trial


CASES = (
    'ClassicCompletedN0FrozenTargetAndFoil', 'BranchCompletedN0FrozenTargetAndFoil',
    'ClassicStoppedN0DiagnosticTargetAndFoil', 'BranchStoppedN0DiagnosticTargetAndFoil',
    'ClassicCompletedN1FrozenTargetAndFoil', 'BranchCompletedN1ScaledTargetAndFoil',
    'ClassicStoppedN1DiagnosticTargetAndFoil', 'BranchStoppedN1ScaledDiagnosticTargetAndFoil',
    'ClassicAsymmetricC0FrozenTargetAndFoil', 'BranchAsymmetricC0FrozenTargetAndFoil',
)


def resign(document):
    document['sha256'] = digest({k: v for k, v in document.items() if k != 'sha256'})


class RecoveryRecognition7NativeTest(unittest.TestCase):
    fixture_environment = 'TIMELEARNER_RECOVERY_RECOGNITION7_NATIVE_BUNDLE'
    archive_prefix = 'case'

    @classmethod
    def setUpClass(cls):
        value = os.environ.get(cls.fixture_environment)
        require(value is not None, 'recovery_recognition7_actual_bundle_required')
        cls.bundle_root = Path(value)
        require(cls.bundle_root.is_dir() and not cls.bundle_root.is_symlink(), 'recovery_recognition7_bundle_missing')
        cls.scratch = tempfile.TemporaryDirectory(); cls.addClassCleanup(cls.scratch.cleanup)
        cls.restored = Path(cls.scratch.name)/'original'
        cls.restoration = restore_native_bundle(cls.bundle_root/'bundle.json', cls.restored)
        cls.directories = tuple(cls.restored/f'{cls.archive_prefix}/native-{i:03d}/native-composite/package7/NativeRecoveryRecognition7/{name}'
                                for i, name in enumerate(CASES, 1))
        require(all(p.is_dir() for p in cls.directories), 'recovery_recognition7_actual_case_missing')

    def case(self, index):
        directory = self.directories[index]
        source, summary = load(directory/'source-package.json'), load(directory/'source-summary.json')
        require(source['schema_version'] == 7, 'recovery_recognition7_original_schema')
        # Embedded data is not a fallback for an absent or modified mirror.
        audit_candidate_window_recovery_package(source, summary,
            external_resolver=filesystem_primary_resolver(directory))
        model = load(directory/'recognition-model.json')
        return directory, model, (source, summary, {}, {})

    def audit(self, model, case):
        return (audit_diagnostic_recognition(model, case) if case[0]['kind'] == 'timelearner_stopped_state'
                else audit_recognition_derivation(model, case))

    def test_entire_original_bundle_is_restored_without_execution_claim(self):
        self.assertEqual(self.restoration['archive_members_verified'], len(load(self.bundle_root/'bundle.json')['members']))
        self.assertFalse(self.restoration['source_archive_modified'])
        self.assertFalse(self.restoration['native_execution_attested'])

    def test_actual_ten_conversions_and_twenty_whole_pattern_trials(self):
        count = 0
        for index, name in enumerate(CASES):
            with self.subTest(case=name):
                directory, model, case = self.case(index)
                audit = self.audit(model, case)
                self.assertTrue(audit['conversion_math_verified']); self.assertTrue(audit['other_physics_preserved'])
                self.assertFalse(audit['native_import_verified']); self.assertIsNone(audit['evaluation_verdict'])
                repeated = load(directory/'recognition-repeat-model.json')
                self.audit(repeated, case)
                for field in ('model_revision', 'conversion_record', 'recognition_inputs', 'source_solo'):
                    self.assertEqual(repeated[field], model[field])
                self.assertIsNone(model['recognition_certificate'])
                scope = load(directory/'recognition-scope.json')
                self.assertFalse(scope['assigned_Train_window_applied']); self.assertFalse(scope['classification_success_claimed'])
                self.assertEqual(scope['diagnostic'], case[0]['kind'] == 'timelearner_stopped_state')
                self.assertEqual([row['trial_id'] for row in scope['trials']], ['target', 'foil'])
                for label, declared in zip(('target', 'foil'), scope['trials']):
                    observation = load(directory/f'recognition-{label}-trial.json')
                    checked = (audit_diagnostic_recognition_trial(observation, model, case) if scope['diagnostic'] else
                               audit_recognition_trial(observation, model))
                    self.assertTrue(checked['valid_observation']); self.assertTrue(observation['complete'])
                    self.assertEqual(observation['label'], label); self.assertIsNone(checked['evaluation_verdict'])
                    self.assertEqual(observation['model_before'], model['model_revision'])
                    self.assertEqual(observation['model_after'], model['model_revision'])
                    samples = observation['samples']; self.assertTrue(samples)
                    self.assertEqual(declared['recorded_frames'], len(samples))
                    self.assertEqual(declared['actual_spikes'], len(observation['spike_times']))
                    self.assertEqual(declared['global_threshold_potential'], max(s['lt_potential'] for s in samples))
                    self.assertEqual(declared['global_soma_maxima'],
                                     [max(s['soma'][i] for s in samples) for i in range(len(samples[0]['soma']))])
                    count += 1
        self.assertEqual(count, 20)

    def test_scaled_source7_uses_primary_references_without_legacy_summary(self):
        _, model, case = self.case(5)
        self.assertEqual(model['conversion_spec']['mode'], 'historical_branch_n1_v1')
        result = audit_recognition_derivation(model, (case[0], None, {}, {}))
        self.assertTrue(result['conversion_math_verified']); self.assertIsNone(result['evaluation_verdict'])

    def test_rehashed_wrong_factor_is_rejected_as_conversion_math(self):
        _, original, case = self.case(5); model = deepcopy(original)
        model['conversion_record']['decisions'][0]['factor'] *= 1.1
        metadata = model['neuron']['metadata']['conversion']
        metadata['record'] = deepcopy(model['conversion_record']); metadata['factors'][0] *= 1.1
        resign(model['neuron']); resign(model)
        with self.assertRaisesRegex(EvidenceError, 'conversion_decision_not_derived_from_solo'):
            audit_recognition_derivation(model, case)

    def test_stopped_source_cannot_be_coherently_relabelled_as_ordinary_recognition(self):
        _, original, case = self.case(7); model = deepcopy(original)
        self.assertEqual(case[0]['kind'], 'timelearner_stopped_state')
        model['kind'] = 'timelearner_recognition_state'; model['state_kind'] = 'recognition'
        model['neuron']['metadata']['state_kind'] = 'recognition'
        resign(model['neuron']); resign(model)
        with self.assertRaisesRegex(EvidenceError, 'recognition_requires_completed_solo'):
            audit_recognition_derivation(model, case)

    def test_full_window_trial_rejects_spike_count_or_frozen_model_corruption(self):
        directory, model, _ = self.case(0)
        for field, value, reason in (
                ('spike_count', load(directory/'recognition-target-trial.json')['spike_count']+1,
                 'recognition_spike_count_mismatch'),
                ('model_after', '0'*64, 'recognition_frozen_model_changed')):
            with self.subTest(field=field):
                changed = load(directory/'recognition-target-trial.json'); changed[field] = value
                with self.assertRaisesRegex(EvidenceError, reason):
                    audit_recognition_trial(changed, model)
