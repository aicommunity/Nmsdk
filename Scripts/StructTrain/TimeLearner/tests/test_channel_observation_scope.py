"""Regression: a packet-level refusal must not label an unselected soma invalid."""
import os
from pathlib import Path
import unittest

from ..channel_diagnostic_reports import chart, observation_caption
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
