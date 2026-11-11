"""Regression: a packet-level refusal must not label an unselected soma invalid."""
import os
from pathlib import Path
import tempfile
import unittest

from ..channel_diagnostic_reports import chart, observation_caption, render_figure
from ..native_evidence import EvidenceError


class ChannelObservationCaptionTest(unittest.TestCase):
    def test_missing_scope_cannot_silently_reuse_ambiguous_legacy_caption(self):
        with self.assertRaisesRegex(EvidenceError, 'observation_scope_missing'):
            observation_caption({'peak_observation_valid':False})

    def test_complete_waveform_and_packet_refusal_are_separate_claims(self):
        data={'observation_context':{'complete':True,'packet_valid':False,
                                    'plotted_channel_has_window':False,'window_input_ids':['input0']}}
        caption=observation_caption(data)
        self.assertIn('waveform complete=True',caption)
        self.assertIn('packet observation valid=False',caption)
        self.assertIn('window input(s): input0',caption)
        self.assertIn('plotted channel has window=False',caption)
        self.assertNotIn('peak measurement valid=',caption)


class ChannelObservationScopeNativeTest(unittest.TestCase):
    def test_actual_high_threshold_is_excluded_from_the_full_time_LT_signal_axis(self):
        data=chart(Path(os.environ['TIMELEARNER_HIGH_CLASSIC_NATIVE']),0)
        self.assertEqual(data['threshold'],100.)
        panel=data['panels'][3]
        values=[value for _,signal in panel['series'] for value in signal]
        low,high=panel['shared_limits']
        self.assertLessEqual(low,min(values))
        self.assertGreaterEqual(high,max(values))
        self.assertLess(high,data['threshold'])
        with tempfile.TemporaryDirectory(dir=os.environ.get('TIMELEARNER_REPORT_TEST_DIR')) as folder:
            result=render_figure(data,'overview',data['begin'],data['end'],Path(folder))
            self.assertEqual(result['panel_y_limits'][3],panel['shared_limits'])
            self.assertEqual(result['renderer_version'],3)
            self.assertTrue(result['threshold_outside_displayed_Y'])
            self.assertFalse(result['lt_threshold_display']['line_drawn'])
            self.assertEqual(result['lt_threshold_display']['value'],data['threshold'])
            self.assertIn('Actual LT threshold 100 (above displayed Y)',
                          (Path(folder)/'overview.svg').read_text(encoding='utf-8'))

    def test_actual_additional_classic_soma_is_not_the_selected_peak_window(self):
        native=Path(os.environ['TIMELEARNER_HIGH_CLASSIC_NATIVE'])
        first,other=chart(native,0),chart(native,3)
        self.assertEqual(first['soma_path'],'$.Soma1')
        self.assertEqual(other['soma_path'],'$.Soma4')
        for data in [first,other]:
            context=data['observation_context']
            self.assertTrue(context['complete'])
            self.assertFalse(context['packet_valid'])
            self.assertEqual(context['window_input_ids'],['input0'])
            self.assertEqual(context['window_channels'],[0])
            self.assertTrue(context['packet_reasons'])
            self.assertEqual(context['packet_valid'],data['peak_observation_valid'])
        self.assertTrue(first['observation_context']['plotted_channel_has_window'])
        self.assertFalse(other['observation_context']['plotted_channel_has_window'])
        self.assertNotEqual(first['panels'][0]['series'],other['panels'][0]['series'])
