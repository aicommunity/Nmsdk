"""Audit actual refused-at-consumer Console outputs; no native calculation."""
import copy
import csv
import os
from pathlib import Path
import unittest

from ..matched_resistance_analysis import _trace
from ..native_characterization import audit_execution
from ..native_evidence import EvidenceError, audit_probe, load
from ..stimulus_subset_evidence import audit_subset, audit_subset_observation, read_console_subset_observation


class BurstReadbackRecordedTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(os.environ['TIMELEARNER_BURST_READBACK_RECORDED']).resolve(strict=True)
        cls.folders=[cls.root/name/'native' for name in ('Classic-replay','Classic-matched')]
        cls.observations=[]
        for folder in cls.folders:
            for stem in ('probe_trial_1','baseline_trial_1'):
                if not (folder/(stem+'.json')).exists():continue
                packet=load(folder/(stem+'.json'));job=load(folder/'job.json')
                with (folder/(stem+'.csv')).open(newline='',encoding='utf-8') as f:rows=list(csv.reader(f))
                rows[0]=['native_tick_start_s','stimulus','raw_soma_0','raw_soma_1']
                cls.observations.append((folder,stem,packet,job,rows))
        if len(cls.observations)!=3:raise AssertionError('requires actual replay, warm baseline and matched main')

    def test_complete_console_outputs_pass_full_production_audit(self):
        for folder in self.folders:
            result=audit_execution(folder)
            self.assertTrue(result['primary_evidence_checked'])
            self.assertEqual(result['execution'],'completed')
            self.assertFalse(result['training_started'])

    def test_schema6_reader_does_not_claim_graph_restoration_or_training_peak(self):
        for folder,stem,packet,job,_ in self.observations:
            with self.assertRaises(EvidenceError):audit_probe(packet,folder/(stem+'.csv'))
            observation,spec,samples,quality=read_console_subset_observation(packet,folder/(stem+'.csv'),
                job['model']['initial_isi'],expected_trial_id=packet['requested_specification']['trial_id'])
            self.assertTrue(quality['recorded_window_complete'])
            self.assertEqual(quality['restoration'],'not_checked')
            self.assertEqual(quality['peak_assignment'],'not_performed')
            self.assertIsNone(quality['scientific_verdict'])
            self.assertEqual(len(samples),observation['sample_count'])
            self.assertEqual(spec['schema_version'],6)

    def test_corrupt_waveform_and_window_are_rejected(self):
        for _,_,original,job,source_rows in self.observations:
            trial=original['requested_specification']['trial_id']
            for mutation in ('missing','duplicate','nan','count','complete','event'):
                packet=copy.deepcopy(original);rows=copy.deepcopy(source_rows)
                if mutation=='missing':rows.pop(5)
                elif mutation=='duplicate':rows[5]=rows[4]
                elif mutation=='nan':rows[5][2]='nan'
                elif mutation=='count':packet['observation']['sample_count']+=1
                elif mutation=='complete':packet['observation']['complete']=False
                else:packet['observation']['stimuli'][0]['time']+=.001
                with self.subTest(mutation=mutation),self.assertRaises(EvidenceError):
                    audit_subset_observation(packet,rows,job['model']['initial_isi'],expected_trial_id=trial)

    def test_wrapper_still_requires_native_graph_and_restoration(self):
        folder,stem,packet,job,rows=self.observations[0]
        restore=load(folder/'subset-restoration.json');before=restore['before'];after=restore['after']
        wrapper=dict(kind='native_stimulus_subset_diagnostic',schema_version=2,
            source_pattern=job['model']['initial_isi'],evidence=packet,
            model_before=restore['model_before'],model_after=restore['model_after'],
            training_pattern_after=after['training_pattern'],dataset_pattern_after=after['dataset_pattern'],
            physical_input_count_after=after['physical_input_count'],training_target_restored=restore['restored'],
            scientific_training_result=False)
        trial=packet['requested_specification']['trial_id']
        self.assertEqual(audit_subset(wrapper,rows,expected_trial_id=trial)['restoration'],'validated_readback')
        for mutation in ('graph','restoration'):
            changed=copy.deepcopy(wrapper)
            if mutation=='graph':changed['model_after']['sha256']='0'*64
            else:changed['training_target_restored']=False
            with self.subTest(mutation=mutation),self.assertRaises(EvidenceError):
                audit_subset(changed,rows,expected_trial_id=trial)

    def test_shared_trace_reader_accepts_main_and_source_baseline(self):
        for folder,stem,_,_,_ in self.observations:
            packet,spec,samples=_trace(folder,stem)
            self.assertTrue(packet['observation']['complete'])
            self.assertEqual(len(samples),packet['observation']['sample_count'])
            self.assertEqual(len(spec['baseline']),2)
