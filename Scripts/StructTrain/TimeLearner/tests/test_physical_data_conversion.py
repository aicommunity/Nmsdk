"""Audit actual schema2 DATA exported by the native integration fixtures."""
import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256 as digest
from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError
from Scripts.StructTrain.TimeLearner.physical_model_data_evidence import audit_physical_model_data


def signed(value):
    result = copy.deepcopy(value)
    result.pop('sha256', None)
    result['sha256'] = digest(result)
    return result


class NativePhysicalDataConversion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_NATIVE_DATA_CONVERSION_FIXTURE')
        if not value:
            raise unittest.SkipTest('requires actual native DATA conversion fixtures')
        cls.root = Path(value)
        cls.models = {name: json.loads((cls.root / ('physical-data-converted-' + name + '-model-data.json')).read_bytes())
                      for name in ('Classic', 'Branch')}

    def test_native_graphs_and_all_post_tune_modes_retain_data_only_scope(self):
        files = [self.root / ('physical-data-converted-' + name + '-model-data.json')
                 for name in ('Classic', 'Branch')]
        files += [self.root / ('physical-data-post-' + name + '-' + str(mode) + '.json')
                  for name in ('Classic', 'Branch') for mode in range(5)]
        files.append(self.root / 'physical-data-historical-Branch.json')
        self.assertEqual(len(files), 13)
        for path in files:
            with self.subTest(file=path.name):
                model = json.loads(path.read_bytes())
                result = audit_physical_model_data(model, frozen=True)
                self.assertTrue(result['explicit_conversion_data'])
                for key in ('native_conversion_verified', 'source_training_evidence_checked',
                            'native_import_verified', 'training_certificate_transferred', 'calibration_confirmed'):
                    self.assertFalse(result[key])
                self.assertIsNone(result['evaluation_verdict'])
                self.assertEqual(model['source_boundary'], model['source_model_data']['source_boundary'])

    def test_source_is_immutable_and_solo_remains_ineligible_for_frozen_evaluation(self):
        for model in self.models.values():
            original = copy.deepcopy(model)
            audit_physical_model_data(model, frozen=True)
            self.assertEqual(model, original)
            with self.assertRaises(EvidenceError):
                audit_physical_model_data(model['source_model_data'], frozen=True)

    def test_resigned_authority_and_source_relabelling_are_rejected(self):
        for field, value in (('certificate', {}), ('data_only', False), ('dynamic_checkpoint', True)):
            changed = copy.deepcopy(self.models['Branch'])
            changed[field] = value
            with self.subTest(field=field), self.assertRaises(EvidenceError):
                audit_physical_model_data(signed(changed), frozen=True)
        changed = copy.deepcopy(self.models['Branch'])
        changed['source_boundary']['kind'] = 'timelearner_recognition_state'
        changed['source_boundary']['state_kind'] = 'recognition'
        with self.assertRaises(EvidenceError):
            audit_physical_model_data(signed(changed), frozen=True)

    def test_unknown_nested_or_inconsistent_source_is_rejected(self):
        for fault in range(3):
            changed = copy.deepcopy(self.models['Classic'])
            if fault == 0:
                changed['source_model_data'] = copy.deepcopy(self.models['Classic'])
            elif fault == 1:
                changed['schema_version'] = 3
            else:
                changed['source_solo_revision'] = '0' * 64
            with self.subTest(fault=fault), self.assertRaises(EvidenceError):
                audit_physical_model_data(signed(changed), frozen=True)

    def test_unused_reference_data_or_damaged_transition_record_is_rejected(self):
        for fault in range(3):
            changed = copy.deepcopy(self.models['Branch'])
            if fault == 0:
                changed['reference_amplitudes'] = [1.0, 2.0]
            elif fault == 1:
                changed['conversion_record']['source_solo_sha256'] = '0' * 64
            else:
                changed['conversion_spec'] = None
            with self.subTest(fault=fault), self.assertRaises(EvidenceError):
                audit_physical_model_data(signed(changed), frozen=True)

    def test_storage_serialization_is_distinct_from_storage_physics(self):
        changed=copy.deepcopy(self.models['Branch'])
        for image in changed['neuron']['class_definitions']:
            snapshot=image['snapshot'];snapshot['native_xml']+='\n'
            snapshot['native_xml_sha256']=hashlib.sha256(snapshot['native_xml'].encode()).hexdigest()
        changed['neuron']=signed(changed['neuron'])
        self.assertTrue(audit_physical_model_data(signed(changed),frozen=True)['explicit_conversion_data'])
        # A newly signed semantic change must still fail the source comparison.
        for image in changed['neuron']['class_definitions']:
            identity=image['snapshot']['identity']
            parameters=identity['model']['nodes'][0]['parameters']
            parameter=next((v for v in parameters.values() if v['data']['type']=='binary64'),None)
            if parameter is not None:
                parameter['data']['value']='3ff0000000000000' if parameter['data']['value']!='3ff0000000000000' else '4000000000000000'
                identity['sha256']=digest(identity['model'])
                break
        else:self.fail('native storage fixture has no scalar physical parameter')
        changed['neuron']=signed(changed['neuron'])
        with self.assertRaisesRegex(EvidenceError,'physical_data_conversion_changed_storage_physics'):
            audit_physical_model_data(signed(changed),frozen=True)


if __name__ == '__main__':
    unittest.main()
