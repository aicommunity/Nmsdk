"""Real native interruption packets and their production process manifests."""
from pathlib import Path
import os
import shutil
import tempfile
import unittest

from ..native_calibration_worker import _record, _signed, _write
from ..native_characterization import audit_execution
from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import audit_run_manifest


class NativeProbeInterruptionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_PROBE_INTERRUPTION_CORPUS')
        if not value:
            raise unittest.SkipTest('requires actual native cancel/timeout controls')
        cls.root = Path(value);cls.rows = load(cls.root/'index.json')['rows']

    def test_real_interruptions_restore_both_topologies_and_keep_actual_samples(self):
        self.assertEqual({(r['branch'], r['expected_execution']) for r in self.rows},
                         {(b, e) for b in (False, True) for e in ('cancelled', 'timeout', 'completed')})
        for row in self.rows:
            folder = self.root/'runs'/row['name']
            with self.subTest(name=row['name']):
                self.assertTrue(audit_run_manifest(folder/'run-manifest.json')['run_evidence_consistent'])
                audit = audit_execution(folder/'native')
                self.assertEqual(audit['execution'], row['expected_execution'])
                self.assertEqual(audit['observation_complete'], row['expected_execution'] == 'completed')
                packet = load(folder/'native/probe_trial_1.json')
                self.assertGreater(packet['observation']['sample_count'], 0)
                if row['expected_execution'] != 'completed':
                    self.assertFalse(audit['observation_valid'])
                    self.assertLess(packet['observation']['sample_count'], packet['observation']['specification']['maximum_samples'])

    def _mutated(self, status, edit):
        row = next(r for r in self.rows if r['expected_execution'] == status)
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)/'native';shutil.copytree(self.root/'runs'/row['name']/'native', folder)
            edit(folder)
            execution = load(folder/'execution.json');execution.pop('sha256')
            execution['artifacts'] = [_record(folder/r['path'], folder) for r in execution['artifacts'] if (folder/r['path']).exists()]
            (folder/'execution.json').unlink();_write(folder/'execution.json', _signed(execution))
            with self.assertRaises(EvidenceError):audit_execution(folder)

    def test_rehashed_cancellation_cannot_drop_the_actual_external_request(self):
        self._mutated('cancelled', lambda folder: (folder/'cancel.request').unlink())

    def test_rehashed_timeout_cannot_claim_a_shorter_wall_duration_than_its_budget(self):
        def edit(folder):
            p = folder/'execution.json';execution = load(p);execution.pop('sha256');execution['probe_wall_seconds'] = 0
            p.unlink();_write(p, _signed(execution))
        self._mutated('timeout', edit)

    def test_rehashed_interruption_cannot_be_promoted_to_completed_execution(self):
        def edit(folder):
            p = folder/'execution.json';execution = load(p);execution.pop('sha256');execution['execution'] = 'completed'
            p.unlink();_write(p, _signed(execution))
        self._mutated('cancelled', edit)
