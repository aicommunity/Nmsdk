"""Verify complete published-style probe figures against native expected trials."""
import hashlib
import os
from pathlib import Path
import unittest

from ..native_evidence import audit_probe, load


class FullProbeReportEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        reports=os.environ.get('TIMELEARNER_FULL_PROBE_REPORT_DIR')
        native=os.environ.get('TIMELEARNER_N0_REPEATS_DIR')
        if not reports or not native:
            raise unittest.SkipTest('requires complete actual native probe figures and primary data')
        cls.root,cls.native=Path(reports),Path(native)

    def test_all_reference_search_anchor_and_final_trials_have_all_somas(self):
        sets=0;trials=0;pairs=0
        for source in sorted(list(self.native.glob('*_training_summary.json'))+list(self.native.glob('*_xml_summary.json'))):
            summary=load(source);prefix=source.name.removesuffix('_training_summary.json').removesuffix('_xml_summary.json')
            expected={r['trial_id'] for r in summary['references']}
            expected.update(r['trial_id'] for r in summary['certificate']['residuals'])
            expected.update(r['trial_id'] for r in summary['candidates'])
            expected.update(r['anchor_trial_id'] for r in summary['candidates'])
            directory=self.root/'cases'/prefix/'report';manifest=load(directory/'manifest.json')
            self.assertEqual({r['trial_id'] for r in manifest['reports']},expected)
            self.assertEqual(len(manifest['reports']),len(expected))
            for entry in manifest['reports']:
                report=directory/entry['folder'];item=load(report/'manifest.json')
                packet=load(report/'primary/probe.json')
                self.assertIs(packet['observation']['specification']['record_spikes'],False)
                self.assertIsNone(packet['observation']['spike_count'])
                self.assertIs(item['spike_recording_enabled'],False)
                self.assertEqual(audit_probe(packet,report/'primary/trace.csv')['trial_id'],entry['trial_id'])
                channels=len(packet['observation']['specification']['baseline'])
                self.assertEqual({f['channel'] for f in item['figures']},set(range(channels)))
                self.assertEqual(item['comparison_scope'],'explicit shared probe set')
                self.assertIsNone(item['scientific_verdict'])
                for figure in item['figures']:
                    shared=[v for v in figure['views'] if v['y_scale']=='shared']
                    self.assertTrue(any(v['view']=='overview' for v in shared))
                    for view in shared:self.assertEqual(view['y_limits'],manifest['common_y_limits'][figure['channel']])
                pairs+=channels
            sets+=1;trials+=len(expected)
        self.assertEqual((sets,trials,pairs),(8,132,198))

    def test_all_figure_and_primary_files_match_stored_hashes(self):
        from PIL import Image
        for directory in sorted((self.root/'cases').glob('*/report')):
            manifest=load(directory/'manifest.json')
            portable=load(directory/'report-spec.json')
            self.assertEqual(portable['trials'],manifest['expected_trials'])
            for entry in portable['trials']:
                self.assertTrue((directory/entry['packet']).is_file())
                self.assertTrue((directory/entry['trace']).is_file())
            for name,sha in load(directory/'SHA256SUMS.json').items():
                self.assertEqual(hashlib.sha256((directory/name).read_bytes()).hexdigest(),sha)
                if name.endswith('.png'):
                    with Image.open(directory/name) as image:self.assertEqual(image.size,(1920,960))
                if name.endswith('.pdf'):self.assertTrue((directory/name).read_bytes().startswith(b'%PDF-'))
                if name.endswith('.svg'):self.assertIn('<svg',(directory/name).read_text())
