"""Real source-import interruptions must identify the phase that actually ran."""
from pathlib import Path
import os
import shutil
import tempfile
import unittest

from ..native_calibration_worker import _record, _signed, _write
from ..native_characterization import audit_execution
from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import audit_run_manifest


class NativeProbePhasesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_PROBE_PHASE_CORPUS')
        if not value:
            raise unittest.SkipTest('requires actual stopped-source baseline/main interruptions')
        cls.root = Path(value);cls.rows = load(cls.root/'index.json')['rows']

    def test_both_topologies_and_every_declared_phase_have_real_packets(self):
        modes = {'completed', 'baseline-timeout', 'baseline-cancel', 'baseline-ticks', 'main-cancel', 'main-ticks'}
        self.assertEqual({(r['branch'], r['mode']) for r in self.rows}, {(b, m) for b in (False, True) for m in modes})
        for row in self.rows:
            with self.subTest(name=row['name']):
                run = self.root/'runs'/row['name'];native = run/'native'
                self.assertTrue(audit_run_manifest(run/'run-manifest.json')['run_evidence_consistent'])
                result = audit_execution(native)
                self.assertEqual(result['execution'], row['expected_execution'])
                self.assertEqual(result['terminal_phase'], row['expected_phase'])
                execution = load(native/'execution.json')
                self.assertEqual(execution['schema_version'], 3)
                self.assertEqual(execution['resistance_intervention_applied'], row['expected_phase'] == 'main_probe')
                prefix = 'baseline' if row['expected_phase'] == 'source_baseline' else 'probe'
                packet = load(native/(prefix+'_trial_1.json'))
                self.assertGreater(packet['observation']['sample_count'], 0)
                self.assertEqual(packet['observation']['complete'], row['mode'] == 'completed')
                if prefix == 'baseline':
                    self.assertFalse((native/'probe_trial_1.json').exists())
                    self.assertFalse((native/'probe_trial_1.csv').exists())
                    self.assertEqual(load(native/'initial-state.json')['identity'], load(native/'source-import.json')['identity'])
                self.assertEqual(load(native/'controller-before.json'), load(native/'controller-after.json'))

    def _mutated(self, mode, edit):
        row = next(r for r in self.rows if r['mode'] == mode)
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/'native';shutil.copytree(self.root/'runs'/row['name']/'native', folder)
            execution = load(folder/'execution.json');execution.pop('sha256');edit(folder, execution)
            execution['artifacts'] = [_record(folder/r['path'], folder) for r in execution['artifacts'] if (folder/r['path']).exists()]
            (folder/'execution.json').unlink();_write(folder/'execution.json', _signed(execution))
            with self.assertRaises(EvidenceError):audit_execution(folder)

    def test_partial_baseline_cannot_claim_intervention_was_applied(self):
        self._mutated('baseline-ticks', lambda folder, execution: execution.update(resistance_intervention_applied=True))

    def test_partial_baseline_cannot_claim_a_main_probe(self):
        self._mutated('baseline-ticks', lambda folder, execution: execution.update(terminal_phase='main_probe'))

    def test_main_interruption_cannot_hide_the_required_consumed_boundary(self):
        self._mutated('main-ticks', lambda folder, execution: (folder/'baseline_trial_1.json').unlink())

    def test_baseline_cancellation_requires_the_original_request(self):
        self._mutated('baseline-cancel', lambda folder, execution: (folder/'cancel.request').unlink())

    def test_baseline_timeout_requires_its_actual_wall_budget(self):
        self._mutated('baseline-timeout', lambda folder, execution: execution.update(probe_wall_seconds=0))

    def test_partial_baseline_cannot_be_promoted_to_completed(self):
        self._mutated('baseline-ticks', lambda folder, execution: execution.update(execution='completed'))
