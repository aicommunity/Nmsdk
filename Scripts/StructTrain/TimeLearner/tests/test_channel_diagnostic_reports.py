"""Actual native traces and immutable-source refusal checks for joint plots."""
from pathlib import Path
import os
import tempfile
import unittest

from ..channel_diagnostic_reports import chart, render
from ..native_evidence import EvidenceError


class ChannelDiagnosticReportsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=os.environ.get('TIMELEARNER_CHANNEL_DIAGNOSTIC_CORPUS')
        repo=os.environ.get('TIMELEARNER_CHANNEL_DIAGNOSTIC_REPOSITORY')
        if not root or not repo:
            raise unittest.SkipTest('requires actual channel corpus and its committed Git archive')
        cls.root=Path(root);cls.repo=Path(repo)
        cls.classic=cls.root/'runs/Classic-threshold-low-retry32-on/native'
        cls.branch=cls.root/'runs/Branch-threshold-low-retry32-on/native'
        cls.reference={'commit':'e98df4eaaf0d9d4cb38511cab26b7ddaec355e4f',
            'archive_path':'Reports/StructTrain/TimeLearner/s07-native-channel-diagnostics-normal-m40-a2/primary.tar.xz',
            'native_member_prefix':'channels/runs/Classic-threshold-low-retry32-on/native'}

    def test_actual_channel_rest_is_not_assumed_zero(self):
        for folder in (self.classic,self.branch):
            data=chart(folder,0)
            self.assertEqual(data['raw_initial_channel_values'],{'Exc':-1.,'Inh':1.})
            self.assertEqual(data['threshold'],.0117)
            self.assertFalse(data['peak_observation_valid'])

    def test_actual_lt_events_are_preserved_and_all_classic_somas_exist(self):
        for i in range(4):
            self.assertEqual(len(chart(self.classic,i)['lt_spike_times']),8)
        self.assertEqual(len(chart(self.branch,0)['lt_spike_times']),4)
        with self.assertRaisesRegex(EvidenceError,'soma_out_of_range'):
            chart(self.branch,1)

    def test_existing_report_is_preserved(self):
        with tempfile.TemporaryDirectory() as raw:
            output=Path(raw)/'report';output.mkdir();(output/'keep').write_text('keep')
            with self.assertRaisesRegex(EvidenceError,'output_exists_or_overlaps'):
                render(self.classic,output,self.reference,self.repo)
            self.assertEqual((output/'keep').read_text(),'keep')

    def test_wrong_git_native_prefix_is_rejected_before_creating_report(self):
        with tempfile.TemporaryDirectory() as raw:
            output=Path(raw)/'report';wrong={**self.reference,'native_member_prefix':'not-the-native-run'}
            with self.assertRaisesRegex(EvidenceError,'git_primary_missing'):
                render(self.classic,output,wrong,self.repo)
            self.assertFalse(output.exists())
