"""Compare the production projection with genuine native graph exports."""
from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load
from ..physical_data_projection import project_physical_model_data, project_file
from ..physical_model_data_evidence import audit_physical_model_data
from ..runtime import file_record


class PhysicalDataProjectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(os.environ['TIMELEARNER_PHYSICAL_DATA_DIR']).resolve(strict=True)
        cls.cases = []
        for topology in ('Classic', 'Branch'):
            stem = 'physical-data-frozen-'+topology
            cls.cases.append((topology, load(root/(stem+'-source.json')),
                              load(root/(stem+'-model-data.json'))))

    def test_both_native_graphs_images_and_effective_inputs_are_preserved(self):
        for topology, source, native in self.cases:
            with self.subTest(topology=topology):
                actual = project_physical_model_data(source)
                for key in native.keys()-{'sha256','configuration_text'}:
                    self.assertEqual(actual[key], native[key], key)
                self.assertEqual(json.loads(actual['configuration_text']),
                                 json.loads(native['configuration_text']))
                report = audit_physical_model_data(actual, frozen=True)
                self.assertFalse(report['source_training_evidence_checked'])
                self.assertFalse(report['native_import_verified'])
                self.assertFalse(report['training_certificate_transferred'])
                self.assertFalse(report['calibration_confirmed'])

    def test_solo_projection_keeps_its_role_and_cannot_be_frozen_implicitly(self):
        for topology, source, _ in self.cases:
            with self.subTest(topology=topology):
                solo = source['source_solo']
                data = project_physical_model_data(solo)
                self.assertEqual(data['neuron'], solo['neuron'])
                self.assertEqual(data['parameters'], solo['trained_inputs'])
                self.assertIsNone(data['conversion_record'])
                with self.assertRaises(EvidenceError):
                    audit_physical_model_data(data, frozen=True)

    def test_output_mutations_cannot_change_the_original_source(self):
        for _, source, _ in self.cases:
            before = sha(source)
            data = project_physical_model_data(source)
            data['configuration']['run_id'] = 'changed-output-only'
            data['neuron']['class_definitions'].clear()
            self.assertEqual(sha(source), before)
            for key in ('historical_state','source_solo','search_history','observed_packets','certificate'):
                if key == 'certificate':
                    self.assertIsNone(data[key])
                else:
                    self.assertNotIn(key, data)

    def test_outer_or_nested_damage_cannot_acquire_valid_projection(self):
        source = self.cases[0][1]
        for resign in (False, True):
            damaged = deepcopy(source)
            damaged['source_solo']['configuration']['run_id'] = 'changed-nested-source'
            if resign:
                damaged['sha256'] = sha({k:v for k,v in damaged.items() if k != 'sha256'})
            with self.subTest(resign=resign), self.assertRaises(EvidenceError):
                project_physical_model_data(damaged)

    def test_file_binding_limits_and_existing_destination_are_enforced(self):
        source = self.cases[0][1]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder);path = root/'source.json';path.write_bytes(json.dumps(source).encode())
            original = file_record(path);destination = root/'data.json'
            with self.assertRaises(EvidenceError):
                project_file(path, destination, expected_bytes=original['size'], expected_sha256='0'*64)
            with self.assertRaises(EvidenceError):
                project_file(path, destination, expected_bytes=original['size'], expected_sha256=original['sha256'],
                             maximum_source_bytes=original['size']-1)
            self.assertFalse(destination.exists())
            receipt = project_file(path, destination, expected_bytes=original['size'],
                                   expected_sha256=original['sha256'])
            self.assertTrue(receipt['source_unchanged']);self.assertFalse(receipt['native_import_verified'])
            self.assertEqual(file_record(path), original)
            with self.assertRaises(EvidenceError):
                project_file(path, destination, expected_bytes=original['size'], expected_sha256=original['sha256'])


if __name__ == '__main__':
    unittest.main()
