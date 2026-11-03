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
from Scripts.StructTrain.TimeLearner.recognition_owner_evidence import audit_owner_recognition, load_case as owner_case


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
        cls.recognition = [p for p in sorted(root.glob('*_owner_recognition_state.json'))
                           if load(p)['source_solo']['schema_version'] == 2]
        declaration = load(root.parent/'specification.json')
        expected = declaration.get('expected_test_ids')
        if (declaration.get('kind') != 'timelearner_native_test_gate'
                or type(declaration.get('schema_version')) is not int or declaration['schema_version'] not in (1, 2)
                or type(expected) is not list or not all(type(n) is str for n in expected)
                or len(set(expected)) != len(expected)):
            raise RuntimeError('requires the explicit native test declaration for this immutable artifact set')
        dormant = {'NativeDormantCapacitanceTransport/'+name for name in ('ClassicN0', 'ClassicN1', 'BranchN0', 'BranchN1')}
        declared_dormant = set(expected) & dormant
        if declared_dormant and declared_dormant != dormant:
            raise RuntimeError('requires all four declared dormant transport controls')
        # Bind the expected package set to the job declaration, not an ambient
        # environment switch or whichever files happen to be present.
        extra = 4 if declared_dormant else 0
        if len(cls.cases) != 8+extra or sum(v['kind'] == 'timelearner_completed_state' for _, v in cls.cases) != 6+extra:
            raise RuntimeError('requires the declared completed/stopped native C0 inventory, including optional dormant4 controls')
        if len(cls.recognition) != 2: raise RuntimeError('requires identity and scaled C0 recognition controls')

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

    def test_actual_recognition_preserves_source_C0(self):
        for path in self.recognition:
            with self.subTest(path=path.name):
                result = audit_owner_recognition(*owner_case(path))
                self.assertTrue(result['owner_readback_consistent'])
                self.assertIsNone(result['evaluation_verdict'])

    def reject(self, edit):
        for _, original in self.cases:
            package = copy.deepcopy(original); state = package['capacitance_state']; baseline = state['baseline']
            edit(package, state, baseline)
            resign(baseline); resign(state); resign(package)
            with self.subTest(kind=original['kind'], revision=original['model_revision']):
                with self.assertRaises(EvidenceError): audit_package_capacitance(package)

    def test_rebased_C0_rejected_despite_new_envelope_digests(self):
        self.reject(lambda p, s, b: b['channels'].__setitem__('Dendrite1_2.ExcChannel', .9e-9*1.1))

    def test_missing_nonunit_scale(self):
        for path, original in self.cases:
            with self.subTest(path=path.name):
                package = copy.deepcopy(original); state = package['capacitance_state']
                # Unit entries may be implicit in the native parameter codec.
                # Removing them does not lose a correction. In the dormant
                # fixtures the learned1.1 is absent from the active map entirely.
                active = [p for p, value in state['membrane_scales'].items() if value != 1.]
                if active:
                    del state['membrane_scales'][active[0]]
                    reason = 'incomplete_or_changed_capacitance_scales'
                else:
                    dormant = state.get('dormant_membrane_scales', {})
                    nonunit = [p for p, value in dormant.items() if value != 1.]
                    self.assertEqual(len(dormant), 1, 'this control requires the declared single dormant correction')
                    self.assertEqual(len(nonunit), 1)
                    del dormant[nonunit[0]]
                    reason = 'invalid_dormant_capacitance_scales'
                resign(state); resign(package)
                with self.assertRaisesRegex(EvidenceError, '^'+reason+'$'):
                    audit_package_capacitance(package)

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

    def test_missing_growth_selector_dependency(self):
        def remove(package, state, baseline):
            for definition in baseline['storage_images']:
                nodes = definition['snapshot']['identity']['model']['nodes']
                instantiated = {node['class'] for node in nodes}
                for node in nodes:
                    for name, parameter in node['parameters'].items():
                        data = parameter['data']
                        if name.endswith('ClassName') and data['type'] == 'utf8':
                            selected = data['value']
                            if selected and selected not in instantiated and selected != definition['base_class']:
                                definition['dependencies'].remove(selected)
                                return
            self.fail('real profile must exercise a growth-only class dependency')
        self.reject(remove)

    def test_invented_new_channel_origin(self):
        self.reject(lambda p, s, b: b['channel_origins'].__setitem__('Dendrite1_2.ExcChannel', 'storage_image'))

    def test_changed_static_channel_physics(self):
        self.reject(lambda p, s, b: b['channel_physics']['Dendrite1_2.ExcChannel'].__setitem__('Type', {'type': 'binary64', 'value': '0000000000000000'}))

    def test_boolean_schema_is_not_version_one(self):
        self.reject(lambda p, s, b: s.__setitem__('schema_version', True))

    def test_unversioned_state_rejected(self):
        self.reject(lambda p, s, b: p.__setitem__('schema_version', 1))


if __name__ == '__main__': unittest.main()
