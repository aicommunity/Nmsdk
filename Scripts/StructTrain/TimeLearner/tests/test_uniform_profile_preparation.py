"""Production preparation must reproduce actual declared cold jobs exactly."""
import os
from pathlib import Path
import unittest

from ..native_calibration_worker import _write
from ..native_evidence import load
from ..n1_protocol_robustness import _signed
from ..uniform_profile_study import main, prepare_cold


class UniformProfilePreparationTest(unittest.TestCase):
    def controls(self, wall):
        return Path(os.environ['TIMELEARNER_UNIFORM_PREP_'+str(wall)]).resolve(strict=True)

    def test_cli_reproduces_both_actual_current_kernel_job_declarations(self):
        reference = Path(os.environ['TIMELEARNER_UNIFORM_PREP_REFERENCE'])
        for wall in (3600, 7200):
            with self.subTest(wall=wall):
                controls = self.controls(wall)
                spec = load(controls/'declaration.json')
                output = Path(os.environ['TMPDIR'])/('production-preparation-'+str(wall))
                self.assertEqual(main(['prepare-cold', str(controls/'original-before-budget.json'),
                    str(controls/'profile.json'), str(reference), str(output), '--variant', '3',
                    '--maximum-wall-seconds', str(wall), '--run-label', spec['run_label']]), 0)
                for name in ('job.json', 'original.json', 'profile.json'):
                    self.assertEqual(load(output/name), load(controls/name))
                expected = {k: v for k, v in spec.items() if k not in ('controller', 'output')}
                self.assertEqual(load(output/'declaration.json'), expected)
                receipt = load(output/'preparation.json')
                self.assertTrue(receipt['characterization']['source_data_audited'])
                self.assertFalse(receipt['amplitude_references_imported'])
                self.assertFalse(receipt['learned_parameters_imported'])
                self.assertFalse(receipt['execution_performed'])
                self.assertIsNone(receipt['scientific_verdict'])
                with self.assertRaisesRegex(ValueError, 'uniform_study_preparation_exists'):
                    prepare_cold(controls/'original-before-budget.json', controls/'profile.json',
                                 reference, output, variant=3)

    def test_foreign_profile_and_changed_target_are_rejected_before_writing(self):
        controls = self.controls(3600)
        reference = Path(os.environ['TIMELEARNER_UNIFORM_PREP_REFERENCE'])
        wrong = Path(os.environ['TIMELEARNER_UNIFORM_PREP_WRONG_REFERENCE'])
        output = Path(os.environ['TMPDIR'])/'foreign-profile-preparation'
        with self.assertRaisesRegex(ValueError, 'uniform_study_reference_class_mismatch'):
            prepare_cold(controls/'original-before-budget.json', controls/'profile.json',
                         wrong, output, variant=3)
        self.assertFalse(output.exists())
        changed = load(controls/'original-before-budget.json')
        changed['configuration']['model']['initial_isi'][-1] += .001
        changed = _signed({k: v for k, v in changed.items() if k != 'sha256'})
        original = Path(os.environ['TMPDIR'])/'changed-target-original.json'
        _write(original, changed)
        output = Path(os.environ['TMPDIR'])/'changed-target-preparation'
        with self.assertRaisesRegex(ValueError, 'uniform_study_reference_protocol_mismatch'):
            prepare_cold(original, controls/'profile.json', reference, output, variant=3)
        self.assertFalse(output.exists())

    def test_invalid_budget_and_reference_tree_output_are_rejected(self):
        controls = self.controls(3600)
        reference = Path(os.environ['TIMELEARNER_UNIFORM_PREP_REFERENCE'])
        output = Path(os.environ['TMPDIR'])/'invalid-budget-preparation'
        for wall in (float('nan'), 0, True):
            with self.subTest(wall=wall):
                with self.assertRaisesRegex(ValueError, 'uniform_study_invalid_wall_budget'):
                    prepare_cold(controls/'original-before-budget.json', controls/'profile.json',
                                 reference, output, variant=3, maximum_wall_seconds=wall)
                self.assertFalse(output.exists())
        with self.assertRaisesRegex(ValueError, 'uniform_study_preparation_overlaps_inputs'):
            prepare_cold(controls/'original-before-budget.json', controls/'profile.json',
                         reference, reference/'must-not-write-preparation', variant=3)
