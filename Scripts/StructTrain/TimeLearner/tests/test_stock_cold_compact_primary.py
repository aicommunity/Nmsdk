"""Actual archived cold N4 data; no synthetic waveform or fresh model run."""
import json
import hashlib
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..collector_provenance import frozen_digest
from ..native_evidence import EvidenceError, load, require
from ..portable_primary import ALIAS_ADAPTER, restore_native_bundle
from ..stock_cold_primary import audit_result, render_result


class StockColdCompactPrimaryTest(unittest.TestCase):
    def test_complete_archive_and_real_assigned_peaks_and_corruption_control(self):
        value = os.environ.get('TIMELEARNER_STOCK_COLD_COMPACT_PRIMARY')
        require(value is not None, 'stock_cold_compact_fixture_required')
        source = Path(value).resolve(strict=True)
        expected = {'bundle.json', 'primary.tar.xz', 'collection-proof.json',
            'collection-controller.json', 'collection-closure.json', 'collection-terminal.json'}
        self.assertEqual({p.name for p in source.iterdir()}, expected)
        before = {n: frozen_digest(source/n, 16*1024**2) for n in expected}
        bundle = load(source/'bundle.json')
        self.assertEqual(len(bundle['members']), 342)
        self.assertTrue(load(source/'collection-terminal.json')['operation_passed'])
        collection = load(source/'collection-proof.json')
        for stage in ('before', 'after'):
            self.assertEqual(len(collection[stage]), 9)
            self.assertTrue(all(row['observation']['all_processes_closed'] for row in collection[stage]))
        with tempfile.TemporaryDirectory(prefix='stock-cold-independent-primary-') as temporary:
            root = Path(temporary)/'restored'
            restored = restore_native_bundle(source/'bundle.json', root, compatibility=ALIAS_ADAPTER)
            self.assertEqual(restored['archive_members_verified'], 342)
            self.assertEqual(restored['retained_regular_files'], 334)
            self.assertEqual(len(restored['omitted_redundant_aliases']), 8)
            self.assertFalse(restored['native_execution_attested'])
            original = root/'stock-cold4-original'
            self.assertEqual(load(original/'process/result.json')['execution'], 'completed')
            self.assertTrue(load(original/'worker/terminal.json')['operation_passed'])
            directory = original/'worker/native-stock-cold4/result'
            audit = audit_result(directory)
            self.assertEqual(audit['complete_probes'], 8)
            self.assertFalse(audit['training_started'])
            self.assertIsNone(audit['scientific_verdict'])
            # Damage actual source CSV: an archived successful index must not
            # override missing/corrupted physical observations.
            broken = Path(temporary)/'damaged'
            shutil.copytree(directory, broken)
            trace = broken/'runs/Classic-cold-stock-input0/native/probe_trial_1.csv'
            trace.write_text(trace.read_text()+'corrupted,NaN\n')
            with self.assertRaises(EvidenceError):
                audit_result(broken)
            proof = dict(restoration=restored, audit=audit, corruption_rejected=True,
                new_model_execution=False, scientific_verdict=None)
            # Plot cache stays outside Git and expanded restoration remains a
            # disposable, fully checked copy of the compact primary fixture.
            controls = os.environ.get('TIMELEARNER_STOCK_COLD_REPORT_CONTROLS')
            render_output = None
            if controls is not None:
                require(load(Path(controls)/'render.json') == {'render': True},
                    'stock_cold_report_controls_schema')
                render_output = str(Path(os.environ['TMPDIR'])/'stock-cold-reports')
            if render_output is not None:
                rendered = render_result(directory, Path(render_output))
                self.assertEqual(len(rendered['reports']), 8)
                self.assertEqual(rendered['trial_soma_pairs'], 20)
                from PIL import Image
                for report in rendered['reports']:
                    folder = Path(render_output)/report['name']
                    item = load(folder/'manifest.json')
                    topology = 'Branch' if report['name'].startswith('Branch-') else 'Classic'
                    self.assertEqual(len(item['figures']), 1 if topology == 'Branch' else 4)
                    self.assertFalse(item['spike_recording_enabled'])
                    self.assertIsNone(item['scientific_verdict'])
                    for figure in item['figures']:
                        views = figure['views']
                        self.assertEqual(views[0]['view'], 'overview')
                        self.assertTrue(any(view['view'].startswith('zoom-') for view in views))
                        for view in views:
                            if view['y_scale'] == 'shared':
                                self.assertEqual(view['y_limits'],
                                    rendered['common_y_limits'][topology][figure['channel']])
                            if view['view'].startswith('zoom-'):
                                self.assertGreaterEqual(view['minimum_native_tick_pixels_on_zoom'], 8.)
                            self.assertFalse(view['downsampling'])
                            with Image.open(folder/view['files'][0]) as image:
                                self.assertEqual(image.size, (1920, 960))
                    for name, digest in load(folder/'SHA256SUMS.json').items():
                        self.assertEqual(hashlib.sha256((folder/name).read_bytes()).hexdigest(), digest)
                proof['rendered'] = dict(output=render_output, reports=8, trial_soma_pairs=20,
                    visual_acceptance_complete=False)
            target = Path(os.environ['TMPDIR'])/'stock-cold-independent-primary.json'
            target.write_text(json.dumps(proof, indent=2, allow_nan=False)+'\n')
        self.assertEqual(before, {n: frozen_digest(source/n, 16*1024**2) for n in expected})
