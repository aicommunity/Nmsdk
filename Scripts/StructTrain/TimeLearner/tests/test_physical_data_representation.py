"""Representation identity over an actual native DATA3 document, not a model copy."""
import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256 as sha
from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError
from Scripts.StructTrain.TimeLearner.physical_data_representation import describe_candidate_representation


class PhysicalDataRepresentationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = json.loads(Path(os.environ['TIMELEARNER_ACTUAL_DATA3_MODEL']).read_bytes())

    def test_actual_model_is_audited_and_unchanged_without_execution_authority(self):
        before = sha(self.model)
        value = describe_candidate_representation(self.model)
        self.assertEqual(before, sha(self.model))
        self.assertEqual(value['model_revision'], self.model['model_revision'])
        self.assertEqual(value['document_sha256'], self.model['sha256'])
        self.assertFalse(value['native_import_verified'])
        self.assertFalse(value['native_execution_verified'])
        self.assertIsNone(value['scientific_verdict'])

    def test_original_source_remains_part_of_the_declared_identity(self):
        value = describe_candidate_representation(self.model)
        self.assertEqual(value['original_DATA1_sha256'],
                         self.model['source_recognition_data']['source_model_data']['sha256'])

    def test_valid_xml_line_ending_encoding_changes_document_but_not_identity(self):
        changed = copy.deepcopy(self.model)
        graph = changed['neuron']['graph']
        text = graph['native_xml']
        self.assertIn('\n', text)
        graph['native_xml'] = text.replace('\r\n', '\n').replace('\n', '\r\n')
        if graph['native_xml'] == text:
            graph['native_xml'] = text.replace('\r\n', '\n')
        graph['native_xml_sha256'] = hashlib.sha256(graph['native_xml'].encode()).hexdigest()
        for node in (changed['neuron'], changed):
            node.pop('sha256');node['sha256'] = sha(node)
        left, right = (describe_candidate_representation(v) for v in (self.model, changed))
        self.assertNotEqual(left['document_sha256'], right['document_sha256'])
        self.assertEqual(left['declared_identity_sha256'], right['declared_identity_sha256'])

    def test_invalid_xml_digest_is_rejected_before_representation_comparison(self):
        changed = copy.deepcopy(self.model)
        changed['neuron']['graph']['native_xml'] += '\n'
        for node in (changed['neuron'], changed):
            node.pop('sha256');node['sha256'] = sha(node)
        with self.assertRaises(EvidenceError):
            describe_candidate_representation(changed)

    def test_changed_physical_parameter_is_not_hidden_by_representation_identity(self):
        changed = copy.deepcopy(self.model)
        changed['parameters'][0]['resistance'] *= 1.01
        changed.pop('sha256');changed['sha256'] = sha(changed)
        with self.assertRaises(EvidenceError):
            describe_candidate_representation(changed)
