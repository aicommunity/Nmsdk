"""Validate actual native channel captures and reject tampered derived evidence."""
from copy import deepcopy
from pathlib import Path
import os
import tempfile
import unittest

from ..native_evidence import EvidenceError, load
from ..native_characterization import validate_job
from ..probe_channel_diagnostics import audit


class ProbeChannelDiagnosticsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get('TIMELEARNER_CHANNEL_DIAGNOSTIC_CORPUS')
        if not root:
            raise unittest.SkipTest('requires actual matched native channel runs')
        cls.root = Path(root)
        cls.cases = [cls.root/'runs'/(name+'-on')/'native' for name in
                     ('Classic-threshold-low-retry32', 'Branch-threshold-low-retry32')]

    def actual(self, folder):
        return audit(folder, load(folder/'job.json'), load(folder/'execution.json'),
                     load(folder/'initial-state.json')['identity'])

    def test_actual_captures_bind_all_soma_values_and_include_actual_lt_events(self):
        counts = []
        for folder in self.cases:
            result = self.actual(folder);counts.append(result['probes'][0]['signals'])
            self.assertTrue(result['enabled'])
            self.assertTrue(result['probes'][0]['complete'])
            self.assertTrue(result['probes'][0]['soma_values_match_primary'])
            self.assertGreater(len(result['probes'][0]['recorded_lt_spike_times']), 0)
            self.assertIsNone(result['scientific_verdict'])
        self.assertEqual(counts, [26, 8])

    def test_observer_does_not_change_primary_waveform_or_original_response(self):
        rows = load(self.root/'analysis.json')['rows']
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertTrue(row['off_on_primary_csv_bytes_equal'])
            self.assertTrue(row['observer_off_on']['exact_waveform_reproduced'])
            self.assertTrue(row['observer_off_matches_original']['exact_waveform_reproduced'])

    def mutated(self, edit):
        folder = self.cases[0]
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw)
            for name in ('job.json', 'execution.json', 'initial-state.json', 'probe_trial_1.json',
                         'probe_trial_1.csv', 'probe_diagnostics_1.json'):
                (target/name).write_bytes((folder/name).read_bytes())
            data = load(target/'probe_diagnostics_1.json');edit(data)
            import json
            (target/'probe_diagnostics_1.json').write_text(json.dumps(data))
            with self.assertRaises(EvidenceError):
                self.actual(target)

    def test_changed_soma_value_is_rejected_against_primary_csv(self):
        self.mutated(lambda d: d['samples'][2]['values'].__setitem__(2, 99.))

    def test_changed_component_class_is_rejected_against_actual_graph(self):
        self.mutated(lambda d: d['descriptors'][0].__setitem__('component_class', 'WrongClass'))

    def test_future_spike_is_rejected(self):
        self.mutated(lambda d: d['samples'][0].__setitem__('new_lt_spike_times', [999.]))

    def test_missing_sample_cannot_claim_complete_capture(self):
        self.mutated(lambda d: d['samples'].pop())

    def test_duplicate_time_is_rejected_against_primary_clock(self):
        self.mutated(lambda d: d['samples'][2].__setitem__('time', d['samples'][1]['time']))

    def test_enable_factor_is_boolean_and_required_by_new_schema(self):
        job = load(self.cases[0]/'job.json')
        from ..n1_protocol_robustness import _signed
        for value in (1, 'true', None):
            changed = deepcopy(job);changed['channel_diagnostics'] = value
            with self.assertRaises(EvidenceError):
                validate_job(_signed(changed))
