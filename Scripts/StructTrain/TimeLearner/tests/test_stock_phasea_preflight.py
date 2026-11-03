"""Actual stock native preflight and rejection of the modified fixture physics."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import audit_run_manifest
from ..stock_phasea_preflight import TARGET, audit_stock_profile


class StockPhaseAPreflightTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_STOCK_PHASEA_PREFLIGHT')
        if not value:
            raise unittest.SkipTest('requires actual stock NSPNeuronGen preflights for both topologies')
        cls.root = Path(value)
        cls.rows = load(cls.root/'index.json')['rows']

    def test_both_actual_native_graphs_have_the_declared_original_physics_without_calculation(self):
        self.assertEqual({r['name'] for r in self.rows},
                         {t+'-stock-nspneurongen-inputs4' for t in ('Classic', 'Branch')})
        for row in self.rows:
            folder = self.root/'runs'/row['name']
            self.assertTrue(audit_run_manifest(folder/'run-manifest.json')['run_evidence_consistent'])
            job = load(folder/'input/job.json')
            self.assertEqual(job['profile_archives'], [])
            self.assertEqual(job['configuration']['model']['initial_isi'], TARGET)
            actual = audit_stock_profile(load(folder/'native/initial-state.json')['identity'],
                                         branch=job['configuration']['model']['branch'])
            self.assertEqual(actual, row['profile'])
            self.assertFalse(actual['lt_membrane'])
            self.assertFalse(actual['training_started'])
            self.assertIsNone(actual['scientific_verdict'])

    def test_modified_integration_fixture_cannot_claim_the_stock_scientific_profile(self):
        for top in ('Classic', 'Branch'):
            prior = load(self.root/'source/corpus/runs'/f'{top}-grid/native/transaction.json')
            identity = deepcopy(prior['source_recognition']['source_solo']['neuron']['graph']['identity'])
            # A familiar class label and refreshed hash cannot hide actual LT nodes.
            next(n for n in identity['model']['nodes'] if n['path'] == '$')['class'] = 'NSPNeuronGen'
            identity['sha256'] = sha(identity['model'])
            with self.assertRaisesRegex(EvidenceError, 'stock_profile_unexpected_lt_membrane'):
                audit_stock_profile(identity, branch=top == 'Branch')

    def test_rehashed_channel_and_synapse_drift_are_rejected(self):
        for row in self.rows:
            folder = self.root/'runs'/row['name']
            original = load(folder/'native/initial-state.json')['identity']
            branch = row['name'].startswith('Branch')
            for classname, property_name, reason in [
                ('NPExcChannelBio', 'Capacity', 'stock_profile_channel_physics_mismatch'),
                ('NPSynapseBio', 'DissociationTC', 'stock_profile_synapse_physics_mismatch')]:
                changed = deepcopy(original)
                node = next(n for n in changed['model']['nodes'] if n['class'] == classname)
                node['parameters'][property_name]['data']['value'] = '3f50624dd2f1a9fc'  # 0.001
                changed['sha256'] = sha(changed['model'])
                with self.assertRaisesRegex(EvidenceError, reason):
                    audit_stock_profile(changed, branch=branch)
