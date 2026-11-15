"""A declared real cold Train; valid negative outcomes do not become PASS science."""
import os
from pathlib import Path
import unittest
from unittest.mock import patch
from ..native_evidence import load
from ..uniform_profile_study import declare_case,run


class UniformProfileTrainTest(unittest.TestCase):
    def test_actual_cold_branch_N1_preserves_declared_profile_and_honest_outcome(self):
        controls=Path(os.environ['TIMELEARNER_UNIFORM_TRAIN_CONTROLS']).resolve(strict=True)
        spec=load(controls/'declaration.json');job=load(controls/'job.json')
        expected=declare_case(load(controls/'original.json'),load(controls/'profile.json'),spec['variant'])
        self.assertEqual(job,expected)
        runtime=load(controls/'runtime.json')
        with patch.dict(os.environ,runtime['loader_environment']):
            result=run(controls/'job.json',controls/'runtime.json',spec['controller'],
                       controls/'initial-state.json',spec['output'],finalization_seconds=300.)
        self.assertEqual(result['execution'],'completed')
        self.assertEqual(result['validity'],'valid')
        self.assertIsNotNone(result['package_audit']);self.assertIsNotNone(result['physical_audit'])
        self.assertFalse(result['classification_assessed']);self.assertIsNone(result['scientific_verdict'])
