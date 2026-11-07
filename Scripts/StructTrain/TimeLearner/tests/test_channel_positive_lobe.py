"""Actual low-threshold waveforms keep negative feedback in a paired full-range view."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..channel_diagnostic_reports import chart, render_figure


class PositiveLobeNativeReportTest(unittest.TestCase):
    def render_case(self, case, focused):
        native=Path(os.environ['TIMELEARNER_MAXIMUM_REPLAY_NATIVE'])/case
        data=chart(native,0)
        packet=json.loads((native/'probe_trial_1.json').read_text())
        peak=packet['observation']['peaks'][0]
        index=min(range(len(data['times'])),key=lambda i:abs(data['times'][i]-peak['time']))
        left,right=data['times'][index-10],data['times'][index+10]
        before=json.dumps(data,sort_keys=True)
        with tempfile.TemporaryDirectory(dir=os.environ['TIMELEARNER_REPORT_TEST_DIR']) as folder:
            result=render_figure(data,'positive-lobe' if focused else 'full-range',left,right,Path(folder),local=True,positive_lobe=focused)
            from PIL import Image
            with Image.open(Path(folder)/result['files'][0]) as image:
                self.assertEqual(image.size,(1920,1920))
            for name in result['files']:
                self.assertGreater((Path(folder)/name).stat().st_size,1000)
        self.assertEqual(before,json.dumps(data,sort_keys=True))
        self.assertGreaterEqual(result['minimum_visible_text_fontsize_pt'],12)
        self.assertGreaterEqual(min(result['legend_layout']['title_gap_pixels'],result['legend_layout']['first_panel_gap_pixels']),12)
        self.assertLess(result['panel_y_limits'][0][0],peak['raw_potential'])
        self.assertGreater(result['panel_y_limits'][0][1],peak['raw_potential'])
        raw=data['panels'][0]['series'][0][1]
        visible=[i for i,t in enumerate(data['times']) if left<=t<=right]
        self.assertLess(min(raw[i] for i in visible),data['soma_baseline'])
        if focused:
            focus=result['positive_lobe_focus']
            self.assertEqual(focus['baseline'],data['soma_baseline'])
            self.assertEqual(focus['clipped_below_times'],[data['times'][i] for i in visible if raw[i]<result['panel_y_limits'][0][0]])
            self.assertTrue(focus['clipped_below_times'])
            self.assertTrue(focus['negative_excursion_preserved_in_paired_full_range_view'])
            self.assertGreater(result['panel_y_limits'][0][0],min(raw[i] for i in visible))
        else:
            self.assertNotIn('positive_lobe_focus',result)
            self.assertLess(result['panel_y_limits'][0][0],min(raw[i] for i in visible))
        return result

    def test_classic_positive_crest_remains_visible_without_hiding_clipped_samples(self):
        self.render_case('Classic',True)

    def test_branch_positive_crest_remains_visible_without_hiding_clipped_samples(self):
        self.render_case('Branch',True)

    def test_paired_full_range_preserves_actual_negative_feedback_excursion(self):
        self.render_case('Branch',False)
