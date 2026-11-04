"""Render all actual C-search probes and retain their physical context."""
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..capacitance_search_reports import render_capacitance_search
from ..native_evidence import EvidenceError, load


class CapacitanceSearchReportsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get('TIMELEARNER_CAPACITANCE_SEARCH_EVIDENCE_DIR')
        if not directory:
            raise unittest.SkipTest('requires the four actual C-search activation histories')
        cls.sources = sorted(Path(directory).glob('*_csearch_activation_stopped_state.json'))
        profiles = {(load(p)['configuration']['model']['branch'], load(p)['configuration']['model']['normalization'])
                    for p in cls.sources}
        if len(cls.sources) != 4 or profiles != {(b, n) for b in (False, True)
                                              for n in ('N0', 'N1')}:
            raise RuntimeError('requires all four topology/normalization cases')

    def test_all_actual_trials_render_with_shared_scales_and_witness_context(self):
        cache = os.environ.get('TIMELEARNER_CAPACITANCE_SEARCH_REPORT_CACHE')
        if not cache:
            raise RuntimeError('requires a new persistent M40 report cache directory')
        total_trials = total_somas = 0
        for source in self.sources:
            with self.subTest(source=source.name):
                output = Path(cache)/source.stem
                result = render_capacitance_search(source, output)
                manifest = load(output/'manifest.json')
                package = load(source)
                self.assertFalse(manifest['visual_acceptance_complete'])
                self.assertIsNone(result['scientific_verdict'])
                self.assertEqual(manifest['training_outcome'], package['training_outcome'])
                self.assertEqual(len(manifest['trial_context']), len(package['observed_packets']))
                self.assertEqual({c['witness_id'] for c in manifest['trial_context']},
                                 set(package['capacitance_history']['witnesses']))
                self.assertEqual({c['phase'] for c in manifest['trial_context']},
                                 {'reference', 'candidate', 'candidate anchor', 'final verification'})
                for item in load(output/'probes/manifest.json')['reports']:
                    trial = load(output/'probes'/item['folder']/'manifest.json')
                    self.assertEqual(trial['comparison_scope'], 'explicit shared probe set')
                    self.assertTrue(trial['primary_audit']['valid_observation'])
                    for figure in trial['figures']:
                        for view in figure['views']:
                            self.assertTrue(view['files'])
                            for name in view['files']:
                                self.assertGreater((output/'probes'/item['folder']/name).stat().st_size, 0)
                self.assertEqual((output/'primary'/source.name).read_bytes(), source.read_bytes())
                total_trials += result['trials']
                total_somas += result['trial_soma_pairs']
        self.assertEqual((total_trials, total_somas), (48, 72))

    def test_missing_primary_trace_is_rejected_before_report_creation(self):
        source = self.sources[0]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stem = source.name.removesuffix('_stopped_state.json')
            for path in source.parent.glob(stem+'*'):
                if path.is_file():
                    shutil.copyfile(path, root/path.name)
            next(root.glob(stem+'_stopped_trial_*.csv')).unlink()
            with self.assertRaises((EvidenceError, OSError)):
                render_capacitance_search(root/source.name, root/'report')
            self.assertFalse((root/'report').exists())

    def test_conflicting_packet_is_rejected_before_report_creation(self):
        source = self.sources[0]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stem = source.name.removesuffix('_stopped_state.json')
            for path in source.parent.glob(stem+'*'):
                if path.is_file():
                    shutil.copyfile(path, root/path.name)
            packet = next(root.glob(stem+'_stopped_trial_*.json'))
            packet.write_text('{}\n', encoding='utf-8')
            with self.assertRaises(EvidenceError):
                render_capacitance_search(root/source.name, root/'report')
            self.assertFalse((root/'report').exists())
