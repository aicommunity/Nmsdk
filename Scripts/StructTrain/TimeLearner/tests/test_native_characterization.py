"""Primary evidence from actual native characterization jobs, never fake traces."""
from copy import deepcopy
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..native_calibration_worker import _record, _signed, _write
from ..native_characterization import audit_execution, prepare_job, validate_job
from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import audit_run_manifest


class NativeCharacterizationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_CHARACTERIZATION_CORPUS')
        if not value:
            raise unittest.SkipTest('requires actual native characterization corpus')
        cls.root = Path(value)
        cls.rows = load(cls.root/'index.json')['rows']

    def test_actual_jobs_bind_idle_controller_model_and_full_or_partial_observations(self):
        self.assertTrue(self.rows)
        self.assertEqual({r['branch'] for r in self.rows}, {False, True})
        self.assertEqual({r['model_schema'] for r in self.rows}, {1, 2})
        self.assertTrue(any(r['input_index'] > 0 for r in self.rows))
        for row in self.rows:
            with self.subTest(name=row['name']):
                folder = self.root/'runs'/row['name']
                self.assertTrue(audit_run_manifest(folder/'run-manifest.json')['run_evidence_consistent'])
                result = audit_execution(folder/'native')
                self.assertEqual(result['execution'], row['expected_execution'])
                self.assertEqual(result['observation_complete'], row['expected_complete'])
                self.assertEqual(result['observation_valid'], row['expected_valid'])
                self.assertFalse(result['training_started'])
                self.assertIsNone(result['evaluation_verdict'])

    def test_job_rejects_rehashed_unknown_schema_invalid_index_and_spike_claim(self):
        job = load(self.root/'runs'/self.rows[0]['name']/'input/job.json')
        for factor, value in [('schema_version', 2), ('input_index', len(job['model']['inputs'])),
                              ('record_spikes', True), ('maximum_sample_gap', .5/job['model']['frequency_hz'])]:
            bad = deepcopy(job);bad.pop('sha256')
            (bad if factor == 'schema_version' else bad['probe'])[factor] = value
            with self.subTest(factor=factor), self.assertRaises(EvidenceError):
                validate_job(_signed(bad))

    def _mutated(self, edit):
        row = next(r for r in self.rows if r['expected_valid'])
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp)/'native'
            shutil.copytree(self.root/'runs'/row['name']/'native', destination)
            edit(destination)
            execution = load(destination/'execution.json');execution.pop('sha256')
            execution['artifacts'] = [_record(destination/r['path'], destination) for r in execution['artifacts']]
            (destination/'execution.json').unlink();_write(destination/'execution.json', _signed(execution))
            with self.assertRaises(EvidenceError):
                audit_execution(destination)

    def test_rehashed_csv_change_cannot_preserve_an_observation(self):
        def edit(folder):
            p = folder/'probe_trial_1.csv';lines = p.read_text().splitlines()
            cells = lines[len(lines)//2].split(',');cells[2] = 'nan';lines[len(lines)//2] = ','.join(cells)
            p.write_text('\n'.join(lines)+'\n')
        self._mutated(edit)

    def test_rehashed_final_parameter_loss_is_not_a_frozen_probe(self):
        def edit(folder):
            p = folder/'final-state.json';value = load(p);value.pop('sha256');value['parameters'][0]['resistance'] *= 2
            p.unlink();_write(p, _signed(value))
        self._mutated(edit)

    def test_rehashed_selected_input_change_cannot_relabel_a_trace(self):
        def edit(folder):
            p = folder/'job.json';value = load(p);value.pop('sha256')
            value['probe']['input_index'] = (value['probe']['input_index']+1) % len(value['model']['inputs'])
            value = _signed(value);p.unlink();_write(p, value)
            p = folder/'execution.json';execution = load(p);execution.pop('sha256');execution['job_sha256'] = value['sha256']
            p.unlink();_write(p, _signed(execution))
        self._mutated(edit)
