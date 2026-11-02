"""Mutation controls over real schema-2 native transfer packages."""
import copy
import os
import unittest
from pathlib import Path

from Scripts.StructTrain.TimeLearner.capacitance_evidence import audit_package_capacitance
from Scripts.StructTrain.TimeLearner.learned_evidence import audit_learned_state, load_case as learned_case
from Scripts.StructTrain.TimeLearner.stopped_evidence import audit_stopped_state, load_case as stopped_case
from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256
from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError, load


def resign(value):
    value['sha256'] = canonical_model_sha256({k: v for k, v in value.items() if k != 'sha256'})


class CapacitanceEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get('TIMELEARNER_CAPACITANCE_STATE_EVIDENCE_DIR')
        if not root: raise unittest.SkipTest('requires real native C0 transfer artifacts')
        root = Path(root)
        cls.completed = [(p, load(p)) for p in sorted(root.glob('*_learned_state.json'))]
        cls.stopped = [(p, load(p)) for p in sorted(root.glob('*_stopped_state.json'))]
        cls.cases = [(p, v) for p, v in cls.completed+cls.stopped if v['schema_version'] == 2]
        if len(cls.cases) != 8 or sum(v['kind'] == 'timelearner_completed_state' for _, v in cls.cases) != 6:
            raise RuntimeError('requires six completed and two stopped native C0 controls')

    def test_actual_primary_readers_and_bound_C0(self):
        for path, package in self.cases:
            with self.subTest(path=path.name):
                read = learned_case if package['kind'] == 'timelearner_completed_state' else stopped_case
                audit = audit_learned_state if read is learned_case else audit_stopped_state
                result = audit(*read(path))
                self.assertTrue(result['capacitance_state']['consistent'])
                self.assertFalse(result['capacitance_state']['native_import_verified'])
                self.assertIsNone(result['evaluation_verdict'])

    def test_actual_legacy_packages_do_not_invent_C0(self):
        legacy = [v for _, v in self.completed+self.stopped if v['schema_version'] == 1]
        self.assertGreaterEqual(len(legacy), 2)
        for package in legacy: self.assertIsNone(audit_package_capacitance(package))

    def reject(self, edit):
        for _, original in self.cases:
            package = copy.deepcopy(original); state = package['capacitance_state']; baseline = state['baseline']
            edit(package, state, baseline)
            resign(baseline); resign(state); resign(package)
            with self.subTest(kind=original['kind'], revision=original['model_revision']):
                with self.assertRaises(EvidenceError): audit_package_capacitance(package)

    def test_rebased_C0_rejected_despite_new_envelope_digests(self):
        self.reject(lambda p, s, b: b['channels'].__setitem__('Dendrite1_2.ExcChannel', .9e-9*1.1))

    def test_missing_effective_scale(self):
        self.reject(lambda p, s, b: s.__setitem__('membrane_scales', {'Dendrite1_1': 1.}))

    def test_changed_effective_scale(self):
        self.reject(lambda p, s, b: s['membrane_scales'].__setitem__('Dendrite1_2', 1.2))

    def test_scale_beyond_declared_bound(self):
        self.reject(lambda p, s, b: s['membrane_scales'].__setitem__('Dendrite1_2', 1.3))

    def test_wrong_applied_revision(self):
        self.reject(lambda p, s, b: s.__setitem__('applied_model_revision', '0'*64))

    def test_changed_storage_profile(self):
        self.reject(lambda p, s, b: b.__setitem__('storage_images_sha256', '0'*64))

    def test_missing_image_dependency(self):
        self.reject(lambda p, s, b: b['storage_images'].pop())

    def test_invented_new_channel_origin(self):
        self.reject(lambda p, s, b: b['channel_origins'].__setitem__('Dendrite1_2.ExcChannel', 'storage_image'))

    def test_changed_static_channel_physics(self):
        self.reject(lambda p, s, b: b['channel_physics']['Dendrite1_2.ExcChannel'].__setitem__('Type', {'type': 'binary64', 'value': '0000000000000000'}))

    def test_boolean_schema_is_not_version_one(self):
        self.reject(lambda p, s, b: s.__setitem__('schema_version', True))

    def test_unversioned_state_rejected(self):
        self.reject(lambda p, s, b: p.__setitem__('schema_version', 1))


if __name__ == '__main__': unittest.main()
