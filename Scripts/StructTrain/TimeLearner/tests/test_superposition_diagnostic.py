"""Hypothesis arithmetic and refusal controls, independent of Train acceptance."""
from copy import deepcopy
import unittest
from ..superposition_diagnostic import compare_samples
from ..native_evidence import EvidenceError


class SuperpositionDiagnosticTest(unittest.TestCase):
    def fixture(self):
        spec={'begin':0.,'baseline':[2.],'minimum_amplitude':.01,
              'stimulus_profile':{'frequency_hz':10.}}
        values=[0.,0.,1.,2.,1.,0.,0.,0.,0.,0.]
        single=[{'time':i/10.,'stimulus':float(i==1),'soma':[2.+v]} for i,v in enumerate(values)]
        burst=deepcopy(single)
        for i in range(10):
            burst[i]['stimulus']+=float(i==4)
            burst[i]['soma'][0]+=values[i-3] if i>=3 else 0.
        return spec,burst,single

    def test_exact_constructed_superposition_is_not_a_training_certificate(self):
        s,b,t=self.fixture();r,*_=compare_samples(s,b,s,t,[.1,.4])
        self.assertEqual(r['channels'][0]['max_abs_residual'],0.)
        self.assertEqual(r['native_tick_shifts'],[0,3])
        self.assertFalse(r['linear_superposition_proven'])
        self.assertFalse(r['assigned_impulse_peaks_certified'])

    def test_real_waveform_difference_is_retained_without_tolerance_pass(self):
        s,b,t=self.fixture();b[6]['soma'][0]+=.25
        r,*_=compare_samples(s,b,s,t,[.1,.4])
        self.assertEqual(r['channels'][0]['max_abs_residual'],.25)
        self.assertIsNone(r['scientific_verdict'])

    def test_fractional_shift_wrong_stimulus_and_unsorted_onsets_refused(self):
        for case in ['fractional','stimulus','order']:
            s,b,t=self.fixture();onsets=[.1,.4]
            if case=='fractional':onsets[1]=.41
            elif case=='order':onsets.reverse()
            else:b[4]['stimulus']=0.
            with self.subTest(case=case),self.assertRaises(EvidenceError):compare_samples(s,b,s,t,onsets)

    def test_gaps_nonfinite_and_baseline_changes_refused(self):
        for case in ['gap','nan','baseline']:
            s,b,t=self.fixture();other=deepcopy(s)
            if case=='gap':b[5]['time']+=.01
            elif case=='nan':b[5]['soma'][0]=float('nan')
            else:other['baseline']=[1.]
            with self.subTest(case=case),self.assertRaises(EvidenceError):compare_samples(s,b,other,t,[.1,.4])
