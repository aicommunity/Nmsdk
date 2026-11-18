"""Actual Linux/Windows storage exports, with physical corruption controls."""
from copy import deepcopy
import os
from pathlib import Path
import struct
import unittest

from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError, load_json
from ..recognition_evidence import audit_recognition_images


class RecognitionImagePortabilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_RECOGNITION_IMAGE_PORTABILITY_DIR')
        if not value:
            raise unittest.SkipTest('requires actual retained Elder Linux and Windows image exports')
        root = Path(value)
        cls.source = load_json(root / 'source-class-definitions.json')
        cls.converted = load_json(root / 'recognition-class-definitions.json')
        if len(cls.source) != 31 or len(cls.converted) != 31 or cls.source == cls.converted:
            raise RuntimeError('requires the genuine 31-image cross-platform pair')

    def reject(self, change):
        current = deepcopy(self.converted)
        change(current)
        with self.assertRaises(EvidenceError):
            audit_recognition_images(current, self.source)

    def test_actual_cross_platform_xml_preserves_declared_storage_physics(self):
        result = audit_recognition_images(self.converted, self.source)
        self.assertEqual(result['definitions'], 31)
        self.assertEqual(result['storage_images_sha256'], '9412aafd8b840e93dc2c0d9c91377a145e667798a378e0701648767f7e71e591')
        self.assertFalse(result['xml_documents_byte_equal'])
        self.assertFalse(result['native_xml_reconstruction_verified'])

    def test_identical_documents_still_need_valid_hashes_and_closure(self):
        result = audit_recognition_images(self.source, self.source)
        self.assertTrue(result['xml_documents_byte_equal'])
        broken = deepcopy(self.source)
        broken[0]['snapshot']['native_xml'] += '\n'
        with self.assertRaises(EvidenceError):
            audit_recognition_images(broken, broken)

    def test_independent_dependency_enumeration_order_is_not_physics(self):
        current = deepcopy(self.converted)
        current.reverse()
        for item in current:
            item['dependencies'].reverse()
        self.assertEqual(audit_recognition_images(current, self.source)['definitions'], 31)

    def mutate_identity(self, images, edit):
        for image in images:
            identity = image['snapshot']['identity']
            if edit(identity['model']):
                identity['sha256'] = canonical_model_sha256(identity['model'])
                return
        self.fail('actual image pair has no requested physical property')

    def test_changed_child_capacitance_with_recomputed_identity_is_rejected(self):
        def change(model):
            for node in model['nodes']:
                data = node['parameters'].get('Capacity', {}).get('data', {})
                if data.get('type') == 'binary64':
                    value = struct.unpack('>d', bytes.fromhex(data['value']))[0]
                    if value <= 0:
                        continue
                    data['value'] = struct.pack('>d', value * 2).hex()
                    return True
        self.reject(lambda images: self.mutate_identity(images, change))

    def test_changed_effective_frequency_with_recomputed_identity_is_rejected(self):
        def change(model):
            model['nodes'][0]['frequency_hz'] = '20000'
            return True
        self.reject(lambda images: self.mutate_identity(images, change))

    def test_changed_internal_binding_with_recomputed_identity_is_rejected(self):
        def change(model):
            if model['bindings']:
                model['bindings'][0]['slot'] += '-changed'
                return True
        self.reject(lambda images: self.mutate_identity(images, change))

    def test_missing_and_duplicate_images_are_rejected(self):
        self.reject(lambda images: images.pop())
        self.reject(lambda images: images.append(deepcopy(images[0])))

    def test_missing_dependency_is_rejected(self):
        def change(images):
            image = next(v for v in images if v['dependencies'])
            image['dependencies'].pop()
        self.reject(change)

    def test_snapshot_root_class_cannot_change_behind_unchanged_physics(self):
        self.reject(lambda images: images[0]['snapshot'].__setitem__('component_class', 'OtherNativeClass'))

    def test_invalid_xml_hash_is_rejected_despite_equal_physical_fingerprint(self):
        self.reject(lambda images: images[0]['snapshot'].__setitem__('native_xml_sha256', '0' * 64))

    def test_undeclared_snapshot_field_is_not_silently_discarded(self):
        self.reject(lambda images: images[0]['snapshot'].__setitem__('extra_state', {'unknown': True}))
