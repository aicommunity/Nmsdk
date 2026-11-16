"""Actual PSI seed shift must not inherit Stock's reference-relative guards."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from ..presynaptic_storage_study import characterize_window, make_rebased_case, prepare_train


class PresynapticWindowCharacterizationTest(unittest.TestCase):
    def test_recorded_PSI_refusal_is_rebased_without_changing_physics_or_search(self):
        controls = Path(os.environ["TIMELEARNER_PSI_WINDOW_CONTROLS"]).resolve(strict=True)
        native = Path(os.environ["TIMELEARNER_PSI_WINDOW_REFERENCE_SOURCE"]).resolve(strict=True)
        original, previous = load(controls/"original.json"), load(controls/"previous-job.json")
        declaration = load(controls/"declaration.json")
        proof = characterize_window(native, previous)
        self.assertEqual(proof["frames"], declaration["expected_frames"])
        self.assertEqual(proof["initial_model_revision"], declaration["initial_model_revision"])
        self.assertFalse(proof["references_imported_into_train"])
        old = previous["configuration"]["composite_measurement"]["candidate_window_policy"]["inputs"]
        self.assertEqual([[f["first_frame"]-p["base_left_guard_frames"],
                           f["last_frame"]+p["base_right_guard_frames"]]
                          for f, p in zip(proof["frames"], old)], [[12, 3612]]*4)
        revised = make_rebased_case(original, "psi", declaration["run_label"], proof["frames"])
        prepared = Path(os.environ["TMPDIR"])/"psi-characterized-train"
        prepared_result = prepare_train(controls/"original.json", native, "psi", prepared,
                                        run_label=declaration["run_label"])
        self.assertEqual(load(prepared/"job.json"), revised)
        self.assertEqual(load(prepared/"window-characterization.json"), proof)
        self.assertFalse(prepared_result["references_imported_into_train"])
        policies = revised["configuration"]["composite_measurement"]["candidate_window_policy"]["inputs"]
        self.assertEqual([[f["first_frame"]-p["base_left_guard_frames"],
                           f["last_frame"]+p["base_right_guard_frames"]]
                          for f, p in zip(proof["frames"], policies)], [[0, 3600]]*4)
        a, b = deepcopy(previous), deepcopy(revised)
        for job in (a, b):
            job.pop("sha256")
            job["configuration"].pop("run_id")
            for p in job["configuration"]["composite_measurement"]["candidate_window_policy"]["inputs"]:
                p.pop("base_left_guard_frames")
                p.pop("base_right_guard_frames")
        self.assertEqual(a, b)
        for change in ("class", "target"):
            wrong = deepcopy(revised)
            if change == "class":
                wrong["configuration"]["model"]["neuron_class"] = "NSPNeuronGen"
            else:
                wrong["configuration"]["model"]["initial_isi"][1] = .09
            with self.assertRaisesRegex(ValueError, "psi_study_window_source_factors_changed"):
                characterize_window(native, wrong)
