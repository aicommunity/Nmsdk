"""Declared cadence matrix on an actual confirmed frozen Linux model."""
from copy import deepcopy
import os
from pathlib import Path
import sys
import unittest

from ..linux_frozen_physical_followups import (CADENCE_PHASES, declared_job, phases, validate_request, whole_wall_seconds)
from ..native_evidence import EvidenceError, load


class ActualLinuxCadenceMatrix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture = os.environ.get('TIMELEARNER_ITI_SOURCE')
        if sys.platform != 'linux' or not fixture:
            raise unittest.SkipTest('requires the actual frozen eight-trial cadence fixture')
        cls.original = load(Path(fixture)/'job.json')
        cls.runtime = load(Path(fixture)/'runtime.json')

    def test_all_32_cases_cover_every_position_under_both_cadences_and_reset_policies(self):
        from Scripts.StructTrain.TimeLearner.frozen_physical_iti_study import condition as cadence_condition
        before = deepcopy(self.original); fingerprints = set(); positions = {}
        threshold = self.original['source_model_data']['neuron']['metadata']['calibration']['threshold']
        for phase in CADENCE_PHASES:
            job, design = declared_job(self.original, 'cadence-preparation/'+phase, phase)
            self.assertEqual(len(job['trials']), 8)
            self.assertEqual(job['source_model_data'], self.original['source_model_data'])
            self.assertEqual(job['coverage_policy'], 'continuous_native_stream')
            self.assertEqual(job['trials'][0]['reset_policy'], 'reset_per_trial')
            self.assertIsNone(design['expected_response_counts'])
            self.assertFalse(design['training_performed'])
            positions.setdefault((design['cadence'], design['following_trial_reset_policy']), set()).add(
                design['target_position'])
            fingerprints.add(cadence_condition(job, design, self.runtime,
                threshold=threshold)['condition_fingerprint'])
        self.assertEqual(len(CADENCE_PHASES), 32)
        self.assertEqual(len(fingerprints), 32)
        self.assertEqual(len(positions), 4)
        self.assertTrue(all(v == set(range(8)) for v in positions.values()))
        self.assertEqual(self.original, before)

    def test_paired_first_observations_have_identical_conditions_and_reset_precedes_preserve(self):
        for reset, preserve in zip(CADENCE_PHASES[::2], CADENCE_PHASES[1::2]):
            self.assertTrue(reset.endswith('-reset'))
            self.assertEqual(preserve, reset.removesuffix('-reset')+'-preserve')
            a, _ = declared_job(self.original, 'paired-attempt', reset)
            b, _ = declared_job(self.original, 'paired-attempt', preserve)
            self.assertEqual(a['trials'][0], b['trials'][0])
            self.assertEqual(a['source_model_data'], b['source_model_data'])
            for left, right in zip(a['trials'][1:], b['trials'][1:]):
                self.assertEqual({k:v for k,v in left.items() if k != 'reset_policy'},
                                 {k:v for k,v in right.items() if k != 'reset_policy'})


class LinuxCadenceMatrixRequest(unittest.TestCase):
    def request(self):
        from .test_actual_linux_frozen_followup_jobs import ActualLinuxFrozenFollowupJobs
        return ActualLinuxFrozenFollowupJobs().request()

    def test_version2_requires_every_declared_integer_budget_without_legacy_phase_substitution(self):
        q = self.request()
        q.update(schema_version=2, native_wall_seconds={phase:5400 for phase in CADENCE_PHASES})
        self.assertEqual(validate_request(q), q)
        self.assertEqual(phases(q), CADENCE_PHASES)
        self.assertEqual(whole_wall_seconds(q), 189200)
        self.assertEqual(whole_wall_seconds(self.request()), 118000)
        for mutation in ('missing', 'legacy', 'float'):
            changed = deepcopy(q)
            if mutation == 'missing': changed['native_wall_seconds'].pop(CADENCE_PHASES[-1])
            elif mutation == 'legacy': changed['native_wall_seconds']['repeat'] = 5400
            else: changed['native_wall_seconds'][CADENCE_PHASES[0]] = 5400.
            with self.subTest(mutation=mutation), self.assertRaisesRegex(EvidenceError, 'wall_budgets'):
                validate_request(changed)


