"""Metadata admission for the actual decision target; run on an owned worker."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

from ..collector_provenance import capture_training_algorithm_inventory
from ..native_evidence import EvidenceError


class TrainingAlgorithmInventoryTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="training-inventory-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        actual = Path(__file__).resolve().parents[4]
        self.declaration = Path("Tests/Integration/Libraries/TrainingAlgorithms.cmake")
        names = (
            "BoundedTraining", "N0Geometry", "N0LengthFamily", "MeasuredResistanceSearch",
            "MeasuredSynapseCountSearch", "MeasuredLengthSearch", "ModerateLengthSearch",
            "MeasuredCapacitanceSearch",
        )
        for path in [self.declaration, *(self.declaration.parent/(
                "Test_PulseLib_"+name+".cpp") for name in names)]:
            destination = self.root/path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(actual/path, destination)
        self.git("init", "--quiet")
        self.git("config", "user.name", "Inventory fixture")
        self.git("config", "user.email", "inventory@local")
        self.git("config", "core.autocrlf", "false")
        self.commit()

    def git(self, *arguments):
        return subprocess.check_output(
            ["git", "-c", "gc.auto=0", "-c", "maintenance.auto=false", "-C", str(self.root),
             *arguments], stderr=subprocess.PIPE,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})

    def commit(self):
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "Pin actual decision sources")

    def test_actual_macro_invocations_replace_the_definition_placeholder(self):
        inventory = capture_training_algorithm_inventory(self.root)
        self.assertEqual(len(inventory["sources"]), 8)
        self.assertEqual({identity for identity in inventory["ids"]
                          if identity.startswith("TrainingInvalidBudget/")},
                         {"TrainingInvalidBudget/"+name for name in
                          ("ClassicN0", "ClassicN1", "BranchN0", "BranchN1")})
        self.assertNotIn("TrainingInvalidBudget/name", inventory["ids"])
        self.assertEqual(inventory["count"], len(set(inventory["ids"])))
        self.assertFalse(inventory["compiled_inventory_verified"])
        self.assertFalse(inventory["SDK_source_verified"])
        self.assertIsNone(inventory["scientific_verdict"])

    def test_unmaterialized_declared_translation_unit_is_rejected(self):
        path = self.declaration.parent/"Test_PulseLib_MeasuredCapacitanceSearch.cpp"
        self.git("update-index", "--skip-worktree", str(path))
        (self.root/path).unlink()
        with self.assertRaises((EvidenceError, FileNotFoundError)):
            capture_training_algorithm_inventory(self.root)

    def test_uncommitted_source_change_is_rejected(self):
        path = self.root/self.declaration.parent/"Test_PulseLib_BoundedTraining.cpp"
        path.write_bytes(path.read_bytes()+b"\nTEST(Unexpected, Extra) {}\n")
        with self.assertRaisesRegex(EvidenceError, "source_not_clean"):
            capture_training_algorithm_inventory(self.root)

    def test_cmake_variable_cannot_silently_hide_a_test_translation_unit(self):
        path = self.root/self.declaration
        path.write_bytes(path.read_bytes().replace(
            b"add_executable(Test_PulseLib_TrainingAlgorithms\n",
            b"add_executable(Test_PulseLib_TrainingAlgorithms\n    ${EXTRA_TEST_SOURCES}\n"))
        self.commit()
        with self.assertRaisesRegex(EvidenceError, "cmake_dialect"):
            capture_training_algorithm_inventory(self.root)

    def test_duplicate_identity_in_another_translation_unit_is_rejected(self):
        path = self.root/self.declaration.parent/"Test_PulseLib_MeasuredCapacitanceSearch.cpp"
        path.write_bytes(path.read_bytes()+
                         b"\nTEST(TrainingInvalidBudget, ClassicN0) {}\n")
        self.commit()
        with self.assertRaisesRegex(EvidenceError, "duplicate_case"):
            capture_training_algorithm_inventory(self.root)

    def test_changed_macro_definition_is_rejected_instead_of_guessing_expansion(self):
        path = self.root/self.declaration.parent/"Test_PulseLib_BoundedTraining.cpp"
        before = path.read_bytes()
        after = before.replace(b"TEST(TrainingInvalidBudget,name)",
                               b"TEST(ChangedBudgetSuite,name)")
        self.assertNotEqual(before, after)
        path.write_bytes(after)
        self.commit()
        with self.assertRaisesRegex(EvidenceError, "invalid_budget_macro_changed"):
            capture_training_algorithm_inventory(self.root)
