"""Actual stock failures: wave loss, selection integrity and readable reports."""
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..native_evidence import EvidenceError, load
from ..probe_diagnostics import read_partial_probe
from ..stock_failure_reports import select_failure_boundary


class StockFailureBoundaryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_STOCK_THRESHOLD_STUDY')
        if not value:
            raise unittest.SkipTest('requires four real stock cold threshold controls')
        cls.source = Path(value)
        cls.native = {p.name: p/'native' for p in (cls.source/'runs').iterdir()}
        if len(cls.native) != 4:
            raise RuntimeError('requires all four actual stock threshold runs')
        cls.selected = {name: select_failure_boundary(p) for name, p in cls.native.items()}

    def subset(self, name):
        temporary = tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
        folder = Path(temporary.name)
        for filename in ['execution.json', 'train_stopped_summary.json']:
            shutil.copyfile(self.native[name]/filename, folder/filename)
        for row in self.selected[name]['probes']:
            for kind in ('packet', 'trace'):
                shutil.copyfile(self.native[name]/row[kind], folder/row[kind])
        return folder

    def test_all_actual_terminal_probes_preserve_invalid_training_role_and_input(self):
        for result in self.selected.values():
            self.assertEqual(result['training_outcome'], 'invalid_observation')
            self.assertIsNone(result['certificate'])
            self.assertEqual(result['probes'][-1]['role'], 'terminal-invalid')
            self.assertFalse(result['probes'][-1]['valid'])
            for row in result['probes']:
                self.assertEqual(row['input_id'], result['input_id'])
                self.assertEqual(row['input_index'], result['input_index'])
            if result['has_preceding_valid_same_input_probe']:
                self.assertEqual(len(result['probes']), 2)
                self.assertTrue(result['probes'][0]['valid'])

    def test_actual_high_threshold_missing_wave_has_complete_nonzero_membrane_response(self):
        for name in ('Classic-threshold-training100', 'Branch-threshold-training100'):
            selected = self.selected[name];row = selected['probes'][-1]
            self.assertTrue(row['complete'])
            self.assertEqual(row['stimulus_count'], 4)
            channel = selected['input_index'] if name.startswith('Classic') else 0
            assignment = next(a for a in row['burst_assignments'] if a['channel'] == channel)
            self.assertEqual(assignment['validity'], 'missing')
            self.assertEqual(len(assignment['waves']), 3)
            self.assertGreater(min(w['amplitude'] for w in assignment['waves']), 1e-6)
            self.assertFalse(row['audit']['valid_observation'])
            diagnostic = row['invalid_probe_diagnostics']
            self.assertTrue(diagnostic['trace_quality']['recorded_window_complete'])
            self.assertTrue(diagnostic['wave_arrays']['recorded_waves_checked'])
            self.assertFalse(diagnostic['wave_arrays']['valid_observation'])

    def test_absolute_time_window_roundoff_preserves_the_actual_late_branch_trace(self):
        name = 'Branch-threshold-training100';selected = self.selected[name]['probes'][-1]
        folder = self.native[name];packet = load(folder/selected['packet'])
        self.assertGreater(packet['observation']['specification']['begin'], 800)
        _, _, _, samples, _, quality = read_partial_probe(packet, folder/selected['trace'])
        self.assertEqual(len(samples), 3601)
        self.assertTrue(quality['recorded_window_complete'])

    def test_one_tick_window_change_is_not_accepted_as_floating_roundoff(self):
        name = 'Branch-threshold-training100';selected = self.selected[name]['probes'][-1]
        folder = self.native[name];packet = load(folder/selected['packet'])
        packet['requested_specification']['end'] += 1/2000
        with self.assertRaisesRegex(EvidenceError, 'partial_requested_window_mismatch'):
            read_partial_probe(packet, folder/selected['trace'])

    def test_changed_recorded_wave_does_not_survive_the_diagnostic_csv_crosscheck(self):
        name = 'Branch-threshold-training100';folder = self.subset(name)
        path = folder/self.selected[name]['probes'][-1]['packet']
        packet = load(path)
        packet['observation']['burst_assignments'][0]['waves'][0]['amplitude'] *= 2
        path.write_text(json.dumps(packet))
        with self.assertRaisesRegex(EvidenceError, 'diagnostic_trace_wave_value_mismatch'):
            select_failure_boundary(folder)

    def test_missing_predecessor_is_explicit_and_never_replaced_by_another_input(self):
        name = 'Classic-threshold-training100';folder = self.subset(name)
        previous = self.selected[name]['probes'][0]
        for kind in ('packet', 'trace'):
            (folder/previous[kind]).unlink()
        result = select_failure_boundary(folder)
        self.assertFalse(result['has_preceding_valid_same_input_probe'])
        self.assertEqual(len(result['probes']), 1)
        self.assertEqual(result['probes'][0]['role'], 'terminal-invalid')

    def test_duplicate_trial_id_is_rejected_before_selection(self):
        name = 'Classic-threshold-training100';folder = self.subset(name)
        path = folder/self.selected[name]['probes'][-1]['packet']
        packet = load(path)
        packet['observation']['specification']['trial_id'] = self.selected[name]['probes'][0]['trial_id']
        path.write_text(json.dumps(packet))
        with self.assertRaisesRegex(EvidenceError, 'duplicate_trial_id'):
            select_failure_boundary(folder)

    def test_corrupt_primary_timestamp_is_rejected(self):
        name = 'Branch-threshold-training100';folder = self.subset(name)
        trace = folder/self.selected[name]['probes'][-1]['trace']
        with trace.open(newline='') as stream:
            rows = list(csv.reader(stream))
        rows[1][0] = 'not-a-time'
        with trace.open('w', newline='') as stream:
            csv.writer(stream).writerows(rows)
        with self.assertRaises(EvidenceError):
            select_failure_boundary(folder)

    def test_terminal_claimed_valid_cannot_be_reported_as_a_failure(self):
        name = 'Branch-threshold-training100';folder = self.subset(name)
        path = folder/self.selected[name]['probes'][-1]['packet']
        packet = load(path);packet['observation']['valid'] = True
        path.write_text(json.dumps(packet))
        with self.assertRaisesRegex(EvidenceError, 'last_probe_is_not_invalid'):
            select_failure_boundary(folder)


class StockFailureReportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_STOCK_FAILURE_REPORT')
        if not value:
            raise unittest.SkipTest('requires completed production failure-boundary report')
        cls.root = Path(value);cls.manifest = load(cls.root/'manifest.json')

    def test_four_conditions_keep_explicit_diagnostic_role(self):
        m = self.manifest
        self.assertEqual(m['kind'], 'stock_training_failure_temporal_report')
        self.assertEqual(len(m['reports']), 4)
        self.assertEqual({(r['topology'], r['initial_threshold']) for r in m['reports']},
                         {(t, v) for t in ('Classic', 'Branch') for v in (.0117, 100.)})
        for flag in ('native_rerun', 'training_completed', 'calibration_performed', 'visual_acceptance_complete'):
            self.assertFalse(m[flag])
        self.assertIsNone(m['scientific_verdict'])
        self.assertGreater(m['trial_soma_pairs'], 0)

    def test_primary_copies_all_somas_and_common_numeric_axes(self):
        for row in self.manifest['reports']:
            name = row['name'];folder = self.root/name
            index = load(folder/'manifest.json');limits = None
            self.assertEqual(len(index['reports']), len(row['selection']['probes']))
            for entry, selected in zip(index['reports'], row['selection']['probes']):
                report = folder/entry['folder'];m = load(report/'manifest.json')
                packet = self.root/'primary'/name/selected['packet']
                trace = self.root/'primary'/name/selected['trace']
                self.assertEqual((report/'primary/probe.json').read_bytes(), packet.read_bytes())
                self.assertEqual((report/'primary/trace.csv').read_bytes(), trace.read_bytes())
                self.assertEqual(m['primary_audit']['valid_observation'], selected['valid'])
                self.assertEqual(len(m['figures']), 4 if row['topology'] == 'Classic' else 1)
                actual = [f['views'][0]['y_limits'] for f in m['figures']]
                if limits is None:
                    limits = actual
                self.assertEqual(actual, limits)

    def test_every_native_zoom_is_readable_and_cache_hashes_match(self):
        from PIL import Image
        pairs = 0
        for row in self.manifest['reports']:
            folder = self.root/row['name']
            for entry in load(folder/'manifest.json')['reports']:
                report = folder/entry['folder']
                for figure in load(report/'manifest.json')['figures']:
                    pairs += 1;views = figure['views']
                    self.assertTrue(any(v['time_view'] == 'overview' for v in views))
                    self.assertTrue(any(v['time_view'] != 'overview' for v in views))
                    for view in views:
                        self.assertFalse(view['downsampling'])
                        if view['time_view'] != 'overview':
                            self.assertGreaterEqual(view['minimum_native_tick_pixels_on_zoom'], 8)
                        png, svg, pdf = [report/p for p in view['files']]
                        with Image.open(png) as image:
                            self.assertEqual(image.size, (1920, 960))
                        self.assertIn('Actual shared input', svg.read_text())
                        self.assertTrue(pdf.read_bytes().startswith(b'%PDF-'))
        self.assertEqual(pairs, self.manifest['trial_soma_pairs'])
        for name, digest in load(self.root/'SHA256SUMS.json').items():
            self.assertEqual(hashlib.sha256((self.root/name).read_bytes()).hexdigest(), digest)
