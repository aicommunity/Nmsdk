"""Reader controls against real native fixtures; executed on workers only."""
import copy
import csv
import os
from pathlib import Path
import tempfile
import unittest

from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError, load, load_json, audit_probe
from Scripts.StructTrain.TimeLearner.single_pulse_evidence import read_single_pulse


@unittest.skipUnless(os.environ.get('TIMELEARNER_SINGLE_PULSE_NATIVE_CORPUS'), 'requires actual native single-pulse primary')
class SinglePulseEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory();cls.rows = []
        corpus = Path(os.environ['TIMELEARNER_SINGLE_PULSE_NATIVE_CORPUS'])
        for p in sorted(corpus.glob('single-pulse-*.json')):
            if p.name.endswith('-samples.json'):continue
            packet = load(p)
            if packet['requested_specification']['schema_version'] != 4:continue
            observation = packet['observation'];values = load_json(p.with_name(p.stem+'-samples.json'))
            trace = Path(cls.tmp.name)/(p.stem+'.csv')
            channels = len(observation['specification']['baseline']) if observation else (len(values[0])-2 if values else 1)
            with trace.open('w', newline='', encoding='utf-8') as stream:
                w = csv.writer(stream);w.writerow(['time','stimulus']+[f'soma{i}' for i in range(channels)])
                # Fixture stores relative clock and exact native ordinates.
                # This adapter restores the explicitly recorded absolute origin;
                # it is not an independent new model run or fabricated waveform.
                for row in values:w.writerow([observation['specification']['begin']+row[0],*row[1:]])
            cls.rows.append((packet,trace))
        if not cls.rows:raise AssertionError('native single-pulse corpus missing')
        cls.complete = next(row for row in cls.rows if row[0]['native_status']=='completed' and row[0]['observation']['valid'])

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def mutated(self):return copy.deepcopy(self.complete[0]),self.complete[1]

    def rewrite(self, trace, mutate):
        with trace.open(newline='',encoding='utf-8') as stream:rows = list(csv.reader(stream))
        mutate(rows);target = Path(self.tmp.name)/'mutated.csv'
        with target.open('w',newline='',encoding='utf-8') as stream:csv.writer(stream).writerows(rows)
        return target

    def test_every_recorded_single_pulse_is_diagnostic_only(self):
        for packet,trace in self.rows:
            with self.subTest(trial=packet['requested_specification']['trial_id'],trace=trace.name):
                _,_,_,_,_,quality = read_single_pulse(packet,trace)
                self.assertFalse(quality['training_eligible']);self.assertTrue(quality['diagnostic_only'])
                self.assertIsNone(quality['evaluation_verdict'])

    def test_corpus_covers_physical_sizes_and_frequencies(self):
        complete = [p for p,_ in self.rows if p['native_status']=='completed']
        self.assertEqual({p['requested_specification']['characterization']['physical_input_count'] for p in complete},{1,2,4,6})
        self.assertEqual({p['observation']['specification']['stimulus_profile']['frequency_hz'] for p in complete},{2000,20000})
        self.assertEqual({p['prepared']['routing'] for p in complete},{'classic_burst','branch_solo_burst'})

    def test_training_reader_rejects_diagnostic_schema(self):
        packet,trace = self.complete
        with self.assertRaises(EvidenceError):audit_probe(packet,trace)

    def test_unknown_schema_and_purpose_are_rejected(self):
        for field,value in [('schema_version',5),('purpose','training_burst')]:
            packet,trace = self.mutated()
            target = packet['requested_specification']
            (target if field=='schema_version' else target['characterization'])[field]=value
            with self.assertRaises(EvidenceError):read_single_pulse(packet,trace)

    def test_physical_selector_cannot_be_relabelled(self):
        packet,trace = self.mutated();c = packet['requested_specification']['characterization']
        c['selected_input_index']=c['physical_input_count']
        with self.assertRaises(EvidenceError):read_single_pulse(packet,trace)

    def test_source_hash_and_extra_fields_cannot_change(self):
        for field in ('hash','extra'):
            packet,trace = self.mutated()
            if field=='hash':packet['observation']['specification']['characterization']['source_training_pattern_hash']='a'*64
            else:packet['observation']['specification']['characterization']['extra']=1
            with self.assertRaises(EvidenceError):read_single_pulse(packet,trace)

    def test_nonfinite_trace_is_rejected(self):
        packet,trace = self.mutated();bad = self.rewrite(trace,lambda rows:rows[2].__setitem__(2,'NaN'))
        with self.assertRaises(EvidenceError):read_single_pulse(packet,bad)

    def test_duplicate_and_missing_samples_are_rejected(self):
        packet,trace = self.mutated()
        for mutation in (lambda rows:rows.insert(3,rows[2]),lambda rows:rows.pop(3)):
            bad = self.rewrite(trace,mutation)
            with self.assertRaises(EvidenceError):read_single_pulse(packet,bad)

    def test_additional_actual_input_is_rejected(self):
        packet,trace = self.mutated()
        bad = self.rewrite(trace,lambda rows:rows[-1].__setitem__(1,'1'))
        with self.assertRaises(EvidenceError):read_single_pulse(packet,bad)

    def test_peak_measurement_must_match_primary(self):
        packet,trace = self.mutated();packet['observation']['peaks'][0]['raw_potential']+=.125
        with self.assertRaises(EvidenceError):read_single_pulse(packet,trace)

    def test_incomplete_and_rejected_captures_never_become_training_evidence(self):
        partial = [row for row in self.rows if row[0]['native_status']=='rejected']
        self.assertTrue(partial,'requires actual rejected native fixtures')
        for packet,trace in partial:
            _,_,_,_,_,quality = read_single_pulse(packet,trace)
            self.assertFalse(quality['training_eligible'])
            self.assertFalse(packet['observation']['valid'])

    def test_complete_claim_without_actual_stimulus_is_rejected(self):
        packet,trace = self.mutated();packet['observation']['stimuli']=[]
        with self.assertRaises(EvidenceError):read_single_pulse(packet,trace)

    def test_declared_frequency_restricts_sample_gap(self):
        packet,trace = self.mutated()
        for key in ('requested_specification',):packet[key]['maximum_sample_gap']*=10
        packet['observation']['specification']['maximum_sample_gap']*=10
        with self.assertRaises(EvidenceError):read_single_pulse(packet,trace)
