"""Verify real Console subset jobs, including rehashed damaged primary data."""
from copy import deepcopy
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..native_calibration_worker import _record, _signed, _write
from ..native_characterization import audit_execution, validate_job
from ..native_evidence import EvidenceError, load


class NativeSubsetConsoleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_SUBSET_CONSOLE_CORPUS')
        if not value:raise unittest.SkipTest('requires real Console schema6 corpus')
        cls.root = Path(value)
        cls.paths = [cls.root/p for p in load(cls.root/'index.json')['native_directories']]
        if len(cls.paths) < 4:raise AssertionError('requires both topologies and multiple presentations')

    def test_actual_console_cases_bind_frozen_model_and_complete_waveforms(self):
        branches = set();presentations = set()
        for path in self.paths:
            job = load(path/'job.json');result = audit_execution(path)
            branches.add(job['model']['branch']);presentations.add(tuple(job['presentation']['source_ordinals']))
            self.assertEqual(result['execution'], 'completed')
            self.assertEqual(result['stimulus_subset_diagnostic']['restoration'], 'validated_readback')
            self.assertIsNone(result['evaluation_verdict'])
        self.assertEqual(branches, {False,True});self.assertGreaterEqual(len(presentations),2)

    def test_invalid_subset_selections_are_not_new_training_targets(self):
        original = load(self.paths[0]/'job.json')
        for indices in ([], [0,0], [1,0], [999], [True]):
            job = deepcopy(original);job.pop('sha256');job['presentation']['source_ordinals'] = indices
            with self.subTest(indices=indices), self.assertRaises(EvidenceError):validate_job(_signed(job))

    def test_peak_and_physics_interventions_are_rejected(self):
        original = load(self.paths[0]/'job.json')
        for mutation in ('window','peak','resistance','profile'):
            job = deepcopy(original);job.pop('sha256')
            if mutation == 'window':job['probe']['window'] = {'begin':0.,'end':.1}
            elif mutation == 'peak':job['probe']['peak_selection'] = 'assigned_burst_wave'
            elif mutation == 'resistance':job['resistance_intervention'] = [{'input_index':0,'resistance':1.}]
            else:job['stimulus_profile']['amplitude'] *= 2
            with self.subTest(mutation=mutation), self.assertRaises(EvidenceError):validate_job(_signed(job))

    def corrupted(self, edit):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)/'native';shutil.copytree(self.paths[0],folder)
            edit(folder)
            execution = load(folder/'execution.json');execution.pop('sha256')
            execution['artifacts'] = [_record(folder/r['path'],folder) for r in execution['artifacts']]
            (folder/'execution.json').unlink();_write(folder/'execution.json',_signed(execution))
            with self.assertRaises(EvidenceError):audit_execution(folder)

    def test_rehashed_lost_restoration_cannot_pass(self):
        def edit(folder):
            path=folder/'subset-restoration.json';record=load(path);record.pop('sha256')
            record['after']['dataset_pattern']=[0.];path.unlink();_write(path,_signed(record))
        self.corrupted(edit)

    def test_rehashed_nonfinite_trace_cannot_pass(self):
        def edit(folder):
            path=folder/'probe_trial_1.csv';rows=path.read_text().splitlines()
            cells=rows[5].split(',');cells[2]='nan';rows[5]=','.join(cells);path.write_text('\n'.join(rows)+'\n')
        self.corrupted(edit)

    def test_rehashed_source_ordinal_cannot_relabel_actual_stimulus(self):
        def edit(folder):
            path=folder/'probe_trial_1.json';packet=load(path)
            packet['observation']['stimuli'][0]['id']='pulse999'
            path.write_text(__import__('json').dumps(packet),encoding='utf-8')
        self.corrupted(edit)
