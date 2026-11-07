"""Independent reader checks against actual schema-5 native fixtures only."""
from copy import deepcopy
import csv
import os
from pathlib import Path
import tempfile
import unittest

from ..native_evidence import EvidenceError, audit_probe, load, load_json
from ..single_pulse_evidence import read_single_pulse


@unittest.skipUnless(os.environ.get('TIMELEARNER_SINGLE_IMPULSE_MAXIMUM_CORPUS'), 'requires schema-5 native fixtures')
class SingleImpulseMaximumNativeReaderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.rows=[]
        for path in sorted(Path(os.environ['TIMELEARNER_SINGLE_IMPULSE_MAXIMUM_CORPUS']).glob('single-pulse-*.json')):
            if path.name.endswith('-samples.json'):continue
            packet=load(path)
            if packet['requested_specification']['schema_version']!=5:continue
            observation=packet['observation'];values=load_json(path.with_name(path.stem+'-samples.json'))
            trace=Path(cls.tmp.name)/(path.stem+'.csv')
            with trace.open('w',newline='',encoding='utf-8') as stream:
                writer=csv.writer(stream)
                writer.writerow(['time','stimulus']+[f'soma{i}' for i in range(len(observation['specification']['baseline']))])
                for row in values:writer.writerow([observation['specification']['begin']+row[0],*row[1:]])
            cls.rows.append((packet,trace))
        if len(cls.rows)!=4:raise AssertionError('four topology/frequency schema-5 native fixtures required')

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def test_actual_frequency_topology_matrix_and_measured_argmax(self):
        coverage=set()
        for packet,trace in self.rows:
            observation,spec,frequency,samples,_,quality=read_single_pulse(packet,trace)
            coverage.add((packet['prepared']['routing'],frequency))
            self.assertTrue(observation['valid']);self.assertTrue(quality['diagnostic_only'])
            self.assertFalse(quality['training_eligible']);self.assertIsNone(quality['evaluation_verdict'])
            channel=spec['windows'][0]['channel'];peak=observation['peaks'][0]
            self.assertEqual(peak['raw_potential'],max(s['soma'][channel] for s in samples))
        self.assertEqual(coverage,{(r,f) for r in ('classic_burst','branch_solo_burst') for f in (2000,20000)})

    def test_modified_measured_winner_cannot_pass_independent_reader(self):
        for original,trace in self.rows:
            packet=deepcopy(original);packet['observation']['peaks'][0]['amplitude']*=1.1
            with self.assertRaises(EvidenceError):read_single_pulse(packet,trace)

    def test_schema_relabel_does_not_silently_change_selection_policy(self):
        for original,trace in self.rows:
            packet=deepcopy(original);packet['requested_specification']['schema_version']=4
            packet['observation']['schema_version']=4;packet['observation']['specification']['schema_version']=4
            with self.assertRaises(EvidenceError):read_single_pulse(packet,trace)

    def test_native_training_reader_refuses_diagnostic_maximum(self):
        for packet,trace in self.rows:
            with self.assertRaises(EvidenceError):audit_probe(packet,trace)

    def test_measured_peak_before_actual_input_cannot_be_claimed_valid(self):
        for original,trace in self.rows:
            packet=deepcopy(original);observation=packet['observation']
            with trace.open(newline='',encoding='utf-8') as stream:rows=list(csv.reader(stream))
            samples=[[float(v) for v in row] for row in rows[1:]]
            peak=observation['peaks'][0]
            index=next(i for i,row in enumerate(samples) if row[0]>peak['time'])+2
            pulse=[row[1] for row in samples if row[1]>0]
            self.assertLess(index+len(pulse),len(samples))
            for row in samples:row[1]=0.
            for offset,value in enumerate(pulse):samples[index+offset][1]=value
            event=observation['stimuli'][0];event['time']=samples[index][0]
            event['relative_to_trial_start']=event['time']-observation['specification']['begin']
            observation['first_stimulus_time']=event['time'];peak['delay_from_stimulus']=peak['time']-event['time']
            damaged=Path(self.tmp.name)/(trace.stem+'-delayed-input.csv')
            with damaged.open('w',newline='',encoding='utf-8') as stream:
                writer=csv.writer(stream);writer.writerow(rows[0]);writer.writerows(samples)
            with self.assertRaisesRegex(EvidenceError,'single_pulse_pre_stimulus_peak_claim'):
                read_single_pulse(packet,damaged)
