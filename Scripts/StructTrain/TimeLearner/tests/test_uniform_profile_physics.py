"""Real native profile readbacks and corruption controls; no new model execution."""
from copy import deepcopy
import os
from pathlib import Path
import struct
import unittest
from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError, load
from ..uniform_profile_physics import audit_uniform_profile


class UniformProfilePhysicsTest(unittest.TestCase):
    def inputs(self):
        d=load(Path(os.environ['TIMELEARNER_UNIFORM_PROFILE_CONTROLS'])/'declaration.json')
        return [load(Path(p))['identity'] for p in d['initial']],load(Path(d['grown']))['identity']

    def test_all_actual_profiles_and_native_grown_bank_keep_uniform_physics(self):
        initial,grown=self.inputs()
        self.assertEqual(len(initial),5)
        for identity in initial:
            self.assertTrue(audit_uniform_profile(identity,identity)['uniform_physics_preserved'])
        result=audit_uniform_profile(initial[1],grown)
        self.assertGreater(result['membranes_checked']['final'],result['membranes_checked']['initial'])
        self.assertFalse(result['native_execution_verified'])
        self.assertFalse(result['training_certificate_verified'])

    def test_hash_consistent_corruption_cannot_pass_as_fixed_profile(self):
        initial,grown=self.inputs();source=initial[1]
        changes=[('$.Dendrite1_27.ExcChannel','Capacity',2e-9),
                 ('$.Dendrite1_27.ExcSynapse1','DissociationTC',.003),
                 ('$.LTZone','Threshold',.02),
                 ('$.Soma1','FeedbackGain',.125),
                 ('
        for path,field,value in changes:
            with self.subTest(path=path,field=field):
                corrupt=deepcopy(grown)
                node=next(n for n in corrupt['model']['nodes'] if n['path']==path)
                self.assertEqual(node['parameters'][field]['data']['type'],'binary64')
                node['parameters'][field]['data']['value']=struct.pack('>d',value).hex()
                corrupt['sha256']=canonical_model_sha256(corrupt['model'])
                with self.assertRaises(EvidenceError):audit_uniform_profile(source,corrupt)
        corrupt=deepcopy(grown)
        root=next(n for n in corrupt['model']['nodes'] if n['path']==' in corrupt['model']['nodes'] if n['path']!='$.Dendrite1_27.ExcChannel']
        corrupt['sha256']=canonical_model_sha256(corrupt['model'])
        with self.assertRaises(EvidenceError):audit_uniform_profile(source,corrupt)
,'TimeStep',.00075)]
        for path,field,value in changes:
            with self.subTest(path=path,field=field):
                corrupt=deepcopy(grown)
                node=next(n for n in corrupt['model']['nodes'] if n['path']==path)
                self.assertEqual(node['parameters'][field]['data']['type'],'binary64')
                node['parameters'][field]['data']['value']=struct.pack('>d',value).hex()
                corrupt['sha256']=canonical_model_sha256(corrupt['model'])
                with self.assertRaises(EvidenceError):audit_uniform_profile(source,corrupt)
        corrupt=deepcopy(grown)
        corrupt['model']['nodes']=[n for n in corrupt['model']['nodes'] if n['path']!='$.Dendrite1_27.ExcChannel']
        corrupt['sha256']=canonical_model_sha256(corrupt['model'])
        with self.assertRaises(EvidenceError):audit_uniform_profile(source,corrupt)
)
        self.assertEqual(root['parameters']['TimeStep']['data']['type'],'unsigned_integer')
        root['parameters']['TimeStep']['data']['value']='1000'
        corrupt['sha256']=canonical_model_sha256(corrupt['model'])
        with self.assertRaises(EvidenceError):audit_uniform_profile(source,corrupt)
        corrupt=deepcopy(grown)
        corrupt['model']['nodes']=[n for n in corrupt['model']['nodes'] if n['path']!='$.Dendrite1_27.ExcChannel']
        corrupt['sha256']=canonical_model_sha256(corrupt['model'])
        with self.assertRaises(EvidenceError):audit_uniform_profile(source,corrupt)
,'TimeStep',.00075)]
        for path,field,value in changes:
            with self.subTest(path=path,field=field):
                corrupt=deepcopy(grown)
                node=next(n for n in corrupt['model']['nodes'] if n['path']==path)
                self.assertEqual(node['parameters'][field]['data']['type'],'binary64')
                node['parameters'][field]['data']['value']=struct.pack('>d',value).hex()
                corrupt['sha256']=canonical_model_sha256(corrupt['model'])
                with self.assertRaises(EvidenceError):audit_uniform_profile(source,corrupt)
        corrupt=deepcopy(grown)
        corrupt['model']['nodes']=[n for n in corrupt['model']['nodes'] if n['path']!='$.Dendrite1_27.ExcChannel']
        corrupt['sha256']=canonical_model_sha256(corrupt['model'])
        with self.assertRaises(EvidenceError):audit_uniform_profile(source,corrupt)
