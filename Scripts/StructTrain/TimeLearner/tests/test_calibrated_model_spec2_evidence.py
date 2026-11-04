"""Read actual native ModelSpec2 calibration and distinct-owner transfers.

Engineering two-input LT profile, primary-pair same-matrix calibration. This
does not turn the fixture into a stock selectivity or independent Test result.
"""
import copy
import os
from pathlib import Path
import unittest

from ..calibrated_evidence import audit_calibrated_state
from ..learned_evidence import audit_learned_state, load_case
from ..native_evidence import EvidenceError, load
from ..recognition_trial_evidence import audit_recognition_trial


class CalibratedModelSpec2EvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_CALIBRATED_MODEL_SPEC2_DIR')
        if not value:
            raise unittest.SkipTest('requires actual native calibration/transport outputs')
        cls.root = Path(value)
        cls.sources = {}
        from ..stopped_evidence import audit_stopped_state
        for path in cls.root.glob('*_learned_state.json'):
            case = load_case(path)
            if case[0]['kind'] == 'timelearner_stopped_state':
                # Legacy precondition controls coexist with the positive
                # matrix. Validate them as diagnostic, never as calibrated.
                audit_stopped_state(*case)
                continue
            cls.sources[case[0]['sha256']] = case
        if len(cls.sources) != 4:
            raise RuntimeError('requires two schema1 and two schema2 genuine learned cases')
        cls.transfers = [(p, load(p)) for p in cls.root.glob('*_calibrated_transfer.json')]
        if len(cls.transfers) != 2 or {r['source_solo']['configuration']['model']['branch']
                                    for _, r in cls.transfers} != {False, True}:
            raise RuntimeError('requires both actual schema2 distinct-owner transfers')

    def test_real_source_training_and_original_schema1_controls(self):
        versions = []
        for case in self.sources.values():
            result = audit_learned_state(*case)
            self.assertTrue(result['exact'])
            model = case[0]['configuration']['model']
            versions.append(model['schema_version'])
            if model['schema_version'] == 2:
                self.assertEqual(model['initial_threshold'], 1.)
        self.assertEqual(sorted(versions), [1, 1, 2, 2])

    def test_complete_calibrated_package_and_source_survive_fresh_owner_import(self):
        for _, record in self.transfers:
            package = record['calibrated_state']
            case = self.sources[record['source_solo']['sha256']]
            self.assertEqual(record['source_solo'], case[0])
            self.assertTrue(audit_calibrated_state(package, case)['calibrated'])
            self.assertEqual(record['destination_state'], package)
            self.assertEqual(record['source_state_after'], package)
            self.assertTrue(record['distinct_owners'])
            self.assertTrue(record['engineering_lt_profile'])
            self.assertEqual(record['construction_threshold'], 1.)
            self.assertEqual(record['effective_threshold'], package['threshold'])
            self.assertNotEqual(package['threshold'], record['construction_threshold'])
            self.assertIsNone(package['recognition_certificate'])
            self.assertIsNone(record['scientific_verdict'])

    def test_fresh_destination_records_complete_native_target_and_foil_windows(self):
        for path, record in self.transfers:
            prefix = path.name.removesuffix('_calibrated_transfer.json')
            observations = [load(path.with_name(prefix+'_frozen_trial_'+str(i)+'.json'))
                            for i in range(4)]
            self.assertEqual([o['label'] for o in observations], ['target', 'foil']*2)
            self.assertEqual(len({o['trial_id'] for o in observations}), 4)
            self.assertEqual(len({o['reset_policy'] for o in observations}), 2)
            for observation in observations:
                result = audit_recognition_trial(observation, record['calibrated_state'])
                self.assertTrue(result['valid_observation'])
                self.assertTrue(result['complete'])
                self.assertIsNone(result['evaluation_verdict'])

    def test_incomplete_or_changed_destination_response_cannot_pass_audit(self):
        for path, record in self.transfers:
            prefix = path.name.removesuffix('_calibrated_transfer.json')
            original = load(path.with_name(prefix+'_frozen_trial_0.json'))
            for key, value in [('complete', False), ('model_after', '0'*64),
                               ('stimulus_times', original['stimulus_times'][:-1]),
                               ('spike_count', original['spike_count']+1)]:
                observation = copy.deepcopy(original)
                observation[key] = value
                with self.subTest(field=key), self.assertRaises(EvidenceError):
                    audit_recognition_trial(observation, record['calibrated_state'])


if __name__ == '__main__':
    unittest.main()
