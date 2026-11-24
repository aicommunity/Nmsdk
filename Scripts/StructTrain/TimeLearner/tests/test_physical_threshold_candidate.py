"""Portable audits over actual native schema3 candidates and paired responses."""
import copy
import json
import os
from pathlib import Path
import unittest

from ..model_identity import canonical_model_sha256 as digest
from ..native_evidence import EvidenceError
from ..physical_model_data_evidence import audit_physical_model_data


def signed(value):
    result=copy.deepcopy(value);result.pop('sha256',None);result['sha256']=digest(result)
    return result


class NativePhysicalThresholdCandidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=os.environ.get('TIMELEARNER_NATIVE_DATA_THRESHOLD_FIXTURE')
        if not root:raise unittest.SkipTest('requires actual native threshold candidates and paired observations')
        cls.root=Path(root)
        cls.models={name:json.loads((cls.root/('physical-data-threshold-'+name+'-model-data.json')).read_bytes())
                    for name in ('Classic','Branch')}

    def test_native_candidates_preserve_source_boundary_and_no_proof_authority(self):
        for model in self.models.values():
            before=copy.deepcopy(model);result=audit_physical_model_data(model,frozen=True)
            self.assertTrue(result['explicit_threshold_candidate_data'])
            for key in ('native_threshold_candidate_verified','source_training_evidence_checked',
                        'native_import_verified','training_certificate_transferred','calibration_confirmed'):
                self.assertFalse(result[key])
            self.assertIsNone(result['evaluation_verdict'])
            self.assertEqual(model['threshold'],1e-5)
            self.assertEqual(model['source_boundary'],model['source_recognition_data']['source_boundary'])
            self.assertEqual(model,before)

    def test_real_target_and_foil_events_and_all_samples_match_full_native_candidate(self):
        for name in ('Classic','Branch'):
            for pattern in ('target','foil'):
                value=json.loads((self.root/('physical-data-threshold-'+name+'-'+pattern+'.json')).read_bytes())
                a=copy.deepcopy(value['full_source']);b=copy.deepcopy(value['physical_data'])
                self.assertTrue(a['complete'] and b['complete'] and a['valid'] and b['valid'])
                self.assertEqual(len(a['samples']),801)
                self.assertGreater(a['spike_count'],0)
                self.assertEqual(a['spike_count'],len(a['spike_times']))
                a.pop('run_id');b.pop('run_id');self.assertEqual(a,b)

    def test_resigned_threshold_source_and_authority_changes_are_rejected(self):
        for fault in range(5):
            model=copy.deepcopy(self.models['Branch'])
            if fault==0:model['threshold']=2e-5
            elif fault==1:model['source_recognition_data']=copy.deepcopy(self.models['Branch'])
            elif fault==2:model['certificate']={}
            elif fault==3:model['parameters'][0]['resistance']*=1.1
            else:
                model['neuron']['metadata']['recognition_verification'].update(status='verified',certificate={})
                model['neuron']=signed(model['neuron'])
            with self.subTest(fault=fault),self.assertRaises(EvidenceError):
                audit_physical_model_data(signed(model),frozen=True)

    def test_resigning_another_graph_parameter_does_not_make_it_a_threshold_candidate(self):
        model=copy.deepcopy(self.models['Classic']);archive=model['neuron'];identity=archive['graph']['identity']
        changed=False
        for node in identity['model']['nodes']:
            for name,parameter in node['parameters'].items():
                if name!='Threshold' and parameter['data']['type']=='binary64':
                    old=parameter['data']['value'];parameter['data']['value']='3ff0000000000000' if old!='3ff0000000000000' else '4000000000000000'
                    changed=True;break
            if changed:break
        self.assertTrue(changed)
        identity['sha256']=digest(identity['model']);model['model_revision']=identity['sha256']
        model['candidate_record']['model_revision']=model['model_revision']
        archive['metadata']['recognition_verification']['model_identity']=model['model_revision']
        archive['metadata']['calibration']['candidate_record']=copy.deepcopy(model['candidate_record'])
        model['neuron']=signed(archive)
        with self.assertRaisesRegex(EvidenceError,'physical_threshold_changed_other_graph_physics'):
            audit_physical_model_data(signed(model),frozen=True)


if __name__=='__main__':unittest.main()
