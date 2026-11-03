"""Real fresh-process packages whose last consumer of a C0 image was removed."""
import copy
import os
from pathlib import Path
import unittest

from ..capacitance_evidence import audit_package_capacitance
from ..learned_evidence import audit_learned_state, load_case
from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError, load


class DormantCapacitanceEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_CAPACITANCE_STATE_EVIDENCE_DIR')
        if not value: raise unittest.SkipTest('requires native dormant C0 transport artifacts')
        cls.cases = [(p, load(p)) for p in sorted(Path(value).glob('*_capacitance_state_dormant_learned_state.json'))]
        if len(cls.cases) != 4: raise RuntimeError('requires four dormant native completed transports')

    def test_actual_native_packages_and_fresh_import(self):
        for path, package in self.cases:
            with self.subTest(path=path.name):
                audit = audit_learned_state(*load_case(path))
                self.assertTrue(audit['capacitance_state']['consistent'])
                self.assertIsNone(audit['evaluation_verdict'])
                state = package['capacitance_state']
                self.assertEqual(state['schema_version'], 2)
                self.assertEqual(state['dormant_membrane_scales']['Dendrite1_2'], 1.1)
                image = state['baseline']['channel_classes']['Dendrite1_2.ExcChannel']
                current = package['neuron']['graph']['identity']['model']['nodes']
                self.assertFalse(any(n['class'] == image for n in current))
                self.assertIn(image, [d['name'] for d in package['neuron']['class_definitions']])

    def test_unused_image_cannot_be_omitted_from_actual_archive(self):
        for path, original in self.cases:
            with self.subTest(path=path.name):
                package = copy.deepcopy(original)
                name = package['capacitance_state']['baseline']['channel_classes']['Dendrite1_2.ExcChannel']
                package['neuron']['class_definitions'] = [d for d in package['neuron']['class_definitions'] if d['name'] != name]
                # This auditor checks C0/profile consistency directly; a stale
                # unrelated outer-package digest must not satisfy the control.
                with self.assertRaisesRegex(EvidenceError, '^capacitance_storage_profile_mismatch$'):
                    audit_package_capacitance(package)

    def test_dormant_scale_still_obeys_its_declared_bound(self):
        for path, original in self.cases:
            with self.subTest(path=path.name):
                package = copy.deepcopy(original); state = package['capacitance_state']
                state['dormant_membrane_scales']['Dendrite1_2'] = 1.3
                state['sha256'] = canonical_model_sha256({k: v for k, v in state.items() if k != 'sha256'})
                with self.assertRaisesRegex(EvidenceError, '^invalid_dormant_capacitance_scale$'):
                    audit_package_capacitance(package)


if __name__ == '__main__': unittest.main()
