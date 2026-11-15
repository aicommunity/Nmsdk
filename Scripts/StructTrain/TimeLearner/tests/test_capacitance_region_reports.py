"""Render every real intervention; reject incomplete or mislabeled primary sets."""
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..capacitance_region_reports import render_capacitance_region
from ..native_evidence import EvidenceError, load


class CapacitanceRegionReportsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get('TIMELEARNER_CAPACITANCE_REGION_DIR')
        if not directory:
            raise unittest.SkipTest('requires all eight actual native C-region fixtures')
        cls.records = sorted(Path(directory).glob('*_capacitance_region_region.json'))
        profiles = {(load(p)['branch'], load(p)['normalization'], load(p)['frequency_hz']) for p in cls.records}
        if len(cls.records) != 8 or profiles != {(b, n, f) for b in (False, True) for n in (0, 1) for f in (2000, 20000)}:
            raise RuntimeError('requires complete Classic/Branch N0/N1 2000/20000 native corpus')

    def test_all_actual_before_after_inputs_render_with_common_scales(self):
        # Full report cache persists on the worker; Git retains compact primaries.
        cache = os.environ.get('TIMELEARNER_CAPACITANCE_REGION_REPORT_CACHE')
        if not cache:
            raise RuntimeError('requires a new persistent M40 report cache directory')
        total_trials = total_somas = 0
        for source in self.records:
            with self.subTest(source=source.name):
                output = Path(cache)/source.stem
                result = render_capacitance_region(source, output)
                manifest = load(output/'manifest.json')
                record = load(source)
                self.assertFalse(manifest['visual_acceptance_complete'])
                self.assertIsNone(result['scientific_verdict'])
                self.assertEqual({(x['phase'], x['input_index']) for x in manifest['trial_context']},
                                 {(phase, i) for phase in ('before', 'after') for i in range(len(record['input_parameters']))})
                set_manifest = load(output/'probes/manifest.json')
                for entry in set_manifest['reports']:
                    trial = load(output/'probes'/entry['folder']/'manifest.json')
                    self.assertEqual(trial['comparison_scope'], 'explicit shared probe set')
                    self.assertEqual(trial['primary_audit']['valid_observation'], True)
                    for figure in trial['figures']:
                        self.assertTrue(figure['views'])
                        for view in figure['views']:
                            for name in view['files']:
                                self.assertGreater((output/'probes'/entry['folder']/name).stat().st_size, 0)
                self.assertEqual((output/'primary/region.json').read_bytes(), source.read_bytes())
                total_trials += result['trials'];total_somas += result['trial_soma_pairs']
        self.assertEqual((total_trials, total_somas), (32, 48))

    def test_missing_input_is_rejected_before_report_creation(self):
        for source in self.records:
            with self.subTest(source=source.name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                record = load(source);record['probes'].pop()
                broken = root/'region.json'
                broken.write_text(json.dumps(record), encoding='utf-8')
                with self.assertRaisesRegex(EvidenceError, 'capacitance_region_incomplete_probe_set'):
                    render_capacitance_region(broken, root/'report')
                self.assertFalse((root/'report').exists())

    def test_unsafe_primary_is_rejected_before_report_creation(self):
        source = self.records[0]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);record = load(source)
            for probe in record['probes']:
                for field in ('record_file', 'trace_file'):
                    shutil.copyfile(source.parent/probe[field], root/probe[field])
            record['probes'][0]['trace_file'] = '../outside.csv'
            broken = root/'region.json'
            broken.write_text(json.dumps(record), encoding='utf-8')
            with self.assertRaisesRegex(EvidenceError, 'capacitance_region_unsafe_or_duplicate_primary_path'):
                render_capacitance_region(broken, root/'report')
            self.assertFalse((root/'report').exists())
