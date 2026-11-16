"""Fixed-physics studies must reject a genuine versioned C-search declaration."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..capacitance_policy import audit_capacitance_search_policy
from ..composite_configuration import project_training_configuration
from ..native_calibration_worker import _signed, _write
from ..native_evidence import load
from ..native_pipeline_worker import validate_job
from ..presynaptic_storage_study import make_cases
from ..uniform_profile_study import declare_case, prepare_cold, run


class FixedPhysicsModePreflightTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(os.environ['TIMELEARNER_FIXED_PHYSICS_DECLARATIONS']).resolve(strict=True)
        cls.original = load(cls.root/'uniform-original.json')
        cls.profile = load(cls.root/'uniform-profile.json')
        cls.psi = load(cls.root/'psi-original.json')
        cls.policy = load(cls.root/'capacitance-policy.json')

    def with_capacitance(self, original, search):
        job = deepcopy(original)
        c = job['configuration']
        self.assertEqual(c['base_schema_version'], 1)
        c['base_schema_version'] = 4 if search else 3
        c['capacitance_history'] = dict(record=True, maximum_relative_change=.2)
        c['search']['n0_candidate_repeats'] = 1
        if search:
            c['capacitance_search'] = deepcopy(self.policy)
            audit_capacitance_search_policy(self.policy, maximum_relative_change=.2,
                                           configuration=c['search'])
        job = _signed({k: v for k, v in job.items() if k != 'sha256'})
        validate_job('train', job)
        self.assertEqual(project_training_configuration(c)['schema_version'], 4 if search else 3)
        self.assertEqual(job['optional_modes']['sync_capacitance_trim'], 0)
        return job

    def test_unchanged_fixed_physics_declarations_equal_production_baseline(self):
        expected = load(self.root/'positive-expected.json')
        self.assertEqual(declare_case(self.original, self.profile, 3,
                                     run_label='mode-guard-control'), expected['uniform'])
        self.assertEqual(make_cases(self.psi, 'mode-guard-control'), expected['psi'])

    def test_uniform_generator_refuses_explicit_C_search_with_legacy_flag_zero(self):
        with self.assertRaisesRegex(ValueError, 'fixed_physics_experiment_disallows_capacitance_search'):
            declare_case(self.with_capacitance(self.original, True), self.profile, 3,
                         run_label='mode-guard-control')

    def test_stock_PSI_generator_refuses_explicit_C_search_with_legacy_flag_zero(self):
        with self.assertRaisesRegex(ValueError, 'fixed_physics_experiment_disallows_capacitance_search'):
            make_cases(self.with_capacitance(self.psi, True), 'mode-guard-control')

    def test_C0_history_without_search_remains_an_admissible_fixed_physics_mode(self):
        uniform = declare_case(self.with_capacitance(self.original, False), self.profile, 3,
                               run_label='mode-guard-control')
        psi = make_cases(self.with_capacitance(self.psi, False), 'mode-guard-control')
        for job in [uniform, *psi.values()]:
            self.assertNotIn('capacitance_search', job['configuration'])
            self.assertEqual(job['configuration']['capacitance_history'],
                             dict(record=True, maximum_relative_change=.2))
            self.assertEqual(project_training_configuration(job['configuration'])['schema_version'], 3)

    def test_general_pipeline_still_accepts_the_explicit_C_search_declaration(self):
        for original in (self.original, self.psi):
            job = self.with_capacitance(original, True)
            validate_job('preflight', job)
            validate_job('train', job)
            self.assertEqual(project_training_configuration(job['configuration'])['capacitance_search'],
                             self.policy)

    def test_prepare_and_run_refuse_before_reference_runtime_or_controller_work(self):
        root = Path(os.environ['TMPDIR'])/'fixed-physics-mode-early-refusal'
        root.mkdir(exist_ok=False)
        active = root/'active-search-job.json'
        _write(active, self.with_capacitance(self.original, True))
        runtime, initial = root/'unused-runtime.json', root/'unused-initial.json'
        _write(runtime, {}); _write(initial, {})
        prepared, executed = root/'prepared', root/'executed'
        reason = 'fixed_physics_experiment_disallows_capacitance_search'
        with self.assertRaisesRegex(ValueError, reason):
            prepare_cold(active, self.root/'uniform-profile.json', self.root,
                         prepared, variant=3)
        with self.assertRaisesRegex(ValueError, reason):
            run(active, runtime, root/'unused-controller', initial, executed)
        self.assertFalse(prepared.exists())
        self.assertFalse(executed.exists())
