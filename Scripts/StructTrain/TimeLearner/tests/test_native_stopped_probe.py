"""Actual full stopped graph replay and native bank resistance interventions."""
from pathlib import Path
import os
import shutil
import struct
import tempfile
import unittest

from ..model_identity import canonical_model_sha256 as sha
from ..native_calibration_worker import _record, _signed, _write
from ..native_characterization import audit_execution, expected_import_model, validate_job
from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import audit_run_manifest


class NativeStoppedProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_STOPPED_PROBE_CORPUS')
        if not value:
            raise unittest.SkipTest('requires actual stock source replay and Rs intervention runs')
        cls.root = Path(value);cls.rows = load(cls.root/'index.json')['rows']

    def test_both_topologies_import_full_graph_and_only_declared_resistance_changes(self):
        self.assertEqual({(r['branch'], r['variant']) for r in self.rows},
                         {(b, v) for b in (False, True) for v in ('baseline', 'resistance')})
        for row in self.rows:
            folder = self.root/'runs'/row['name']
            with self.subTest(name=row['name']):
                self.assertTrue(audit_run_manifest(folder/'run-manifest.json')['run_evidence_consistent'])
                result = audit_execution(folder/'native')
                self.assertEqual(result['execution'], 'completed');self.assertTrue(result['observation_complete'])
                job = load(folder/'input/job.json');source = job['source_stopped']
                self.assertTrue(load(folder/'run-manifest.json')['preflight']['source_primary_checked'])
                imported = load(folder/'native/source-import.json')
                self.assertEqual(imported['identity'], source['neuron']['graph']['identity'])
                actual = load(folder/'native/initial-state.json')['identity']['model']
                self.assertEqual(actual, expected_import_model(job))
                self.assertEqual(len(actual['nodes']), 71 if row['branch'] else 306)
                self.assertFalse(result['training_started']);self.assertIsNone(result['evaluation_verdict'])

    def test_imported_history_is_retained_without_starting_or_advancing_training(self):
        for row in self.rows:
            folder = self.root/'runs'/row['name']/'native';job = load(folder/'job.json')
            before, after = load(folder/'controller-before.json'), load(folder/'controller-after.json')
            self.assertEqual(before, after)
            self.assertGreater(before['observed_packet_count'], 0)
            self.assertEqual(before['observed_packets_sha256'], sha(job['source_stopped']['observed_packets']))
            self.assertEqual(before['summary']['state'], 'idle')
            self.assertEqual(before['summary']['reference_probes'], 0)
            self.assertIsNone(before['summary']['certificate'])

    def test_interventions_follow_a_real_complete_consumed_source_probe(self):
        for row in self.rows:
            if row['variant'] != 'resistance':continue
            folder = self.root/'runs'/row['name']/'native';job = load(folder/'job.json')
            baseline, main = load(folder/'baseline_trial_1.json'), load(folder/'probe_trial_1.json')
            self.assertEqual(baseline['native_status'], 'completed')
            self.assertTrue(baseline['observation']['complete'])
            self.assertEqual(baseline['prepared']['base_model_revision'], job['source_stopped']['model_revision'])
            self.assertNotEqual(baseline['requested_specification']['trial_id'], main['requested_specification']['trial_id'])
            self.assertGreater(main['observation']['specification']['begin'], baseline['observation']['specification']['end'])

    def test_a_rehashed_partial_shared_bank_intervention_is_rejected(self):
        row = next(r for r in self.rows if r['branch'] and r['variant'] == 'resistance')
        job = load(self.root/'runs'/row['name']/'input/job.json');job.pop('sha256')
        job['resistance_intervention'] = [job['resistance_intervention'][-1]]
        with self.assertRaisesRegex(EvidenceError, 'characterization_shared_bank_intervention_inconsistent'):
            validate_job(_signed(job))

    def _mutated(self, edit):
        row = self.rows[0]
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)/'native';shutil.copytree(self.root/'runs'/row['name']/'native', folder)
            edit(folder)
            p = folder/'execution.json';execution = load(p);execution.pop('sha256')
            execution['artifacts'] = [_record(folder/r['path'], folder) for r in execution['artifacts']]
            p.unlink();_write(p, _signed(execution))
            with self.assertRaises(EvidenceError):audit_execution(folder)

    def test_rehashed_hidden_capacity_change_is_not_an_rs_only_intervention(self):
        def edit(folder):
            for name in ('initial-state.json', 'final-state.json'):
                p = folder/name;state = load(p);state.pop('sha256')
                model = state['identity']['model']
                node = next(n for n in model['nodes'] if 'Capacity' in n['parameters'])
                data = node['parameters']['Capacity']['data'];value = struct.unpack('>d', bytes.fromhex(data['value']))[0]
                data['value'] = struct.pack('>d', value*1.1).hex();state['identity']['sha256'] = sha(model)
                p.unlink();_write(p, _signed(state))
            p = folder/'execution.json';execution = load(p);execution.pop('sha256')
            execution['model_revision'] = load(folder/'initial-state.json')['identity']['sha256']
            p.unlink();_write(p, _signed(execution))
        self._mutated(edit)

    def test_rehashed_empty_history_cannot_claim_native_reset_preserved_source_evidence(self):
        def edit(folder):
            for name in ('controller-before.json', 'controller-after.json'):
                p = folder/name;record = load(p);record.pop('sha256')
                record['observed_packet_count'] = 0;record['observed_packets_sha256'] = sha([])
                p.unlink();_write(p, _signed(record))
        self._mutated(edit)
