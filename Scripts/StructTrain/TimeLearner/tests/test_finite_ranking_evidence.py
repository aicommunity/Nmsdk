"""Actual physical baseline/correction, primary recomputation and corruptions."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..finite_ranking_evidence import load_case, audit_finite_timing_ranking
from ..native_evidence import EvidenceError, measured_training_probe


class FiniteRankingEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        keys = ("TIMELEARNER_FINITE_RANK_BASELINE_DIR", "TIMELEARNER_FINITE_RANK_CORRECTION_DIR")
        if not all(os.environ.get(k) for k in keys):
            raise unittest.SkipTest("requires actual native four-case baseline and correction")
        cls.directories = [Path(os.environ[k])/"native" for k in keys]

    def cases(self):
        for corrected, directory in enumerate(self.directories):
            for topology in ("Classic", "Branch"):
                for n in (0, 1):
                    yield bool(corrected), load_case(directory, f"{topology}_2000_N{n}_finite_ranking_zero_sync")

    def test_all_eight_physical_sources_and_measured_selection(self):
        for corrected, case in self.cases():
            audit = audit_finite_timing_ranking(*case)
            self.assertIs(audit["selected_is_measured_minimum"], corrected)
            self.assertLess(audit["minimum_measured_timing_error"], audit["initial_timing_error"])
            self.assertFalse(audit["training_completed"])
            self.assertFalse(audit["certificate_present"])
            self.assertIsNone(audit["evaluation_verdict"])

    def test_candidate_row_order_does_not_change_primary_derived_result(self):
        for _, case in self.cases():
            changed = deepcopy(case[1]);changed["candidates"].reverse()
            self.assertEqual(audit_finite_timing_ranking(*case),
                             audit_finite_timing_ranking(case[0], changed, *case[2:]))

    def test_corrupt_signed_residual_flags_or_numbers_are_rejected(self):
        for _, case in self.cases():
            for mutation in ("residual", "flag", "nonfinite"):
                changed = deepcopy(case[1]);candidate = changed["candidates"][0]
                if mutation == "residual":candidate["timing_low"] += .01
                elif mutation == "flag":candidate["within_timing"] = not candidate["within_timing"]
                else:candidate["amplitude_residual"] = float("nan")
                with self.assertRaises(EvidenceError):
                    audit_finite_timing_ranking(case[0], changed, *case[2:])

    def test_old_revision_anchor_cannot_be_reused(self):
        for _, case in self.cases():
            changed = deepcopy(case[1])
            candidate = next(c for c in changed["candidates"] if c["model_epoch"] != case[0]["capture_epoch"])
            candidate["anchor_trial_id"] = changed["references"][1]["trial_id"]
            with self.assertRaisesRegex(EvidenceError, "stale_finite_ranking_candidate"):
                audit_finite_timing_ranking(case[0], changed, *case[2:])

    def test_missing_primary_trace_is_rejected(self):
        for _, case in self.cases():
            traces = dict(case[3]);traces.pop(next(iter(traces)))
            with self.assertRaises(EvidenceError):audit_finite_timing_ranking(*case[:3], traces)

    def test_missing_measurement_has_a_structured_reason_before_field_access(self):
        for _, case in self.cases():
            candidate = case[1]["candidates"][0];packets = deepcopy(case[2])
            packets[candidate["trial_id"]]["observation"] = None
            with self.assertRaisesRegex(EvidenceError, "unusable_measurement"):
                measured_training_probe(packets, candidate["trial_id"], case[0]["protocol"]["inputs"][0]["id"],
                                        case[0]["protocol"]["origin_stimulus_id"], set())
