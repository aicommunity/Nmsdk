"""All actual profile-probe somas remain visible with the declared factor."""
import os
from pathlib import Path
import unittest
from ..channel_diagnostic_reports import chart
from ..native_evidence import load


@unittest.skipUnless(os.environ.get('TIMELEARNER_FEEDBACK_PROFILE_CORPUS'), 'requires actual feedback profile study')
class FeedbackProfileChartsTest(unittest.TestCase):
    def test_all_recorded_somas_clock_input_and_profile_provenance(self):
        root=Path(os.environ['TIMELEARNER_FEEDBACK_PROFILE_CORPUS'])
        rows=load(root/'feedback-design.json')['rows']
        self.assertEqual(len(rows),12)
        checked=0
        for row in rows:
            folder=root/'runs'/row['name']/'native';job=load(folder/'job.json')
            for i in range(1 if job['model']['branch'] else len(job['model']['inputs'])):
                data=chart(folder,i);checked+=1
                self.assertEqual(len(data['times']),3601)
                self.assertEqual(len(data['stimulus']),len(data['times']))
                self.assertEqual(data['threshold'],.0117)
                self.assertEqual(data['soma_path'],'$.Soma'+str(i+1))
                self.assertEqual(data['raw_initial_channel_values'],{'Exc':-1.,'Inh':1.})
                self.assertEqual(data.get('diagnostic_purpose'), 'single_pulse_characterization' if row['presentation']=='single' else None)
                self.assertEqual(data.get('storage_profile_intervention'),job.get('profile_intervention'))
        self.assertEqual(checked,30)
