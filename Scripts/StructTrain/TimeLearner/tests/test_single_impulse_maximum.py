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
        cls.tmp=tempfile.TemporaryDirectory();cls.rows=[];cls.faults=[]
        for path in sorted(Path(os.environ['TIMELEARNER_SINGLE_IMPULSE_MAXIMUM_CORPUS']).glob('single-pulse-*.json')):
            if path.name.endswith('-samples.json'):continue
            if any(path.name.startswith('single-pulse-'+name+'-') for name in
                   ('ClassicPhysicalMatrix2000','BranchPhysicalMatrix2000',
                    'ClassicPhysicalMatrix20000','BranchPhysicalMatrix20000')):continue
            packet=load(path)
            if packet['requested_specification']['schema_version']!=5:continue
            observation=packet['observation'];values=load_json(path.with_name(path.stem+'-samples.json'))
            trace=Path(cls.tmp.name)/(path.stem+'.csv')
            with trace.open('w',newline='',encoding='utf-8') as stream:
                writer=csv.writer(stream)
                channels=len(observation['specification']['baseline']) if observation else 1
                writer.writerow(['time','stimulus']+[f'soma{i}' for i in range(channels)])
                for row in values:writer.writerow([observation['specification']['begin']+row[0],*row[1:]])
            (cls.rows if packet['native_status']=='completed' else cls.faults).append((packet,trace))
        if len(cls.rows)!=4:raise AssertionError('four topology/frequency schema-5 native fixtures required')
        if len(cls.faults)!=6:raise AssertionError('six native schema-5 fault captures required')

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

    def test_fault_captures_remain_partial_diagnostics_without_training_claims(self):
        for packet,trace in self.faults:
            _,_,_,_,_,quality=read_single_pulse(packet,trace)
            self.assertEqual(packet['native_status'],'rejected');self.assertTrue(quality['diagnostic_only'])
            self.assertFalse(quality['training_eligible']);self.assertIsNone(quality['evaluation_verdict'])

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


@unittest.skipUnless(os.environ.get('TIMELEARNER_SINGLE_IMPULSE_MAXIMUM_CORPUS'), 'requires actual expanded schema-5 native fixtures')
class SingleImpulseMaximumDimensionReaderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.rows=[]
        corpus=Path(os.environ['TIMELEARNER_SINGLE_IMPULSE_MAXIMUM_CORPUS'])
        prefixes=tuple('single-pulse-'+name+'-' for name in
                       ('ClassicPhysicalMatrix2000','BranchPhysicalMatrix2000',
                        'ClassicPhysicalMatrix20000','BranchPhysicalMatrix20000'))
        for path in sorted(corpus.glob('single-pulse-*.json')):
            if path.name.endswith('-samples.json') or not path.name.startswith(prefixes):continue
            packet=load(path)
            if packet['requested_specification']['schema_version']!=5:continue
            if packet['native_status']!='completed':raise AssertionError('expanded positive fixture must complete')
            observation=packet['observation'];values=load_json(path.with_name(path.stem+'-samples.json'))
            trace=Path(cls.tmp.name)/(path.stem+'.csv')
            with trace.open('w',newline='',encoding='utf-8') as stream:
                writer=csv.writer(stream);writer.writerow(['time','stimulus']+[f'soma{i}' for i in range(len(observation['specification']['baseline']))])
                for row in values:writer.writerow([observation['specification']['begin']+row[0],*row[1:]])
            cls.rows.append((path,packet,trace,values))
        if len(cls.rows)!=12:raise AssertionError('twelve expanded native observations required')

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def test_actual_dimensions_topologies_frequencies_and_selected_input(self):
        coverage=set()
        for path,packet,trace,values in self.rows:
            observation,spec,frequency,samples,_,quality=read_single_pulse(packet,trace)
            n=spec['characterization']['physical_input_count'];branch=packet['prepared']['routing']=='branch_solo_burst'
            coverage.add((branch,n,frequency))
            self.assertEqual(spec['characterization']['selected_input_index'],2 if n>2 else n-1)
            self.assertEqual(len(spec['baseline']),1 if branch else n)
            self.assertTrue(observation['valid']);self.assertTrue(quality['diagnostic_only'])
            self.assertFalse(quality['training_eligible'])
        self.assertEqual(coverage,{(branch,n,f) for branch in (False,True) for n in (1,4,6) for f in (2000,20000)})

    def test_measured_winner_matches_actual_samples_for_every_dimension(self):
        for path,packet,trace,values in self.rows:
            observation,spec,_,samples,_,_=read_single_pulse(packet,trace)
            channel=spec['windows'][0]['channel'];peak=observation['peaks'][0]
            self.assertEqual(peak['raw_potential'],max(s['soma'][channel] for s in samples))
            with self.assertRaises(EvidenceError):audit_probe(packet,trace)

    def test_policy_AB_preserves_every_physical_channel_and_model_revision(self):
        for path,packet,trace,after in self.rows:
            old_path=path.with_name(path.name.replace('-2_feedback_','-1_feedback_'))
            self.assertNotEqual(old_path,path);old=load(old_path)
            self.assertEqual(old['requested_specification']['schema_version'],4)
            for key in ['base_model_revision','effective_model_revision']:
                self.assertEqual(old['prepared'][key],packet['prepared'][key])
            before=load_json(old_path.with_name(old_path.stem+'-samples.json'))
            self.assertEqual(len(before),len(after))
            for a,b in zip(before,after):
                self.assertEqual(a[1:],b[1:]);self.assertLessEqual(abs(a[0]-b[0]),1e-12)

    def test_losing_a_recorded_physical_channel_cannot_pass_reader(self):
        for path,packet,trace,values in self.rows:
            damaged=deepcopy(packet);damaged['observation']['specification']['baseline'].pop()
            with self.assertRaises(EvidenceError):read_single_pulse(damaged,trace)
