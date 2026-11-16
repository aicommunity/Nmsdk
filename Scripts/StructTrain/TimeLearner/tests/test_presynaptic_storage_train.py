"""One declared stock/PSI cold condition; negative training is a valid result."""
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from ..native_evidence import load
from ..presynaptic_storage_study import make_cases
from ..uniform_profile_study import run


class PresynapticStorageTrainTest(unittest.TestCase):
    def test_actual_matched_cold_condition_keeps_physics_and_honest_outcome(self):
        controls = Path(os.environ["TIMELEARNER_PSI_TRAIN_CONTROLS"]).resolve(strict=True)
        declaration = load(controls/"declaration.json")
        self.assertEqual(set(declaration), {"role", "run_label", "controller", "output"})
        self.assertIn(declaration["role"], ("stock", "psi"))
        expected = make_cases(load(controls/"original.json"), declaration["run_label"])
        self.assertEqual(load(controls/"job.json"), expected[declaration["role"]])
        runtime = load(controls/"runtime.json")
        with patch.dict(os.environ, runtime["loader_environment"]):
            result = run(controls/"job.json", controls/"runtime.json", declaration["controller"],
                         controls/"initial-state.json", declaration["output"],
                         finalization_seconds=300.)
        self.assertEqual((result["execution"], result["validity"]), ("completed", "valid"))
        self.assertIsNotNone(result["package_audit"])
        self.assertIsNotNone(result["physical_audit"])
        self.assertTrue(result["physical_audit"]["uniform_physics_preserved"])
        self.assertFalse(result["classification_assessed"])
        self.assertIsNone(result["scientific_verdict"])
