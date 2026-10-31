"""Replay genuine native five-mode parent/child transactions and corruptions."""
import contextlib
import copy
import io
import os
from pathlib import Path
import unittest

from Scripts.StructTrain.TimeLearner.learned_evidence import load_case
from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256 as sha
from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError, load
from Scripts.StructTrain.TimeLearner.posttune_transaction_evidence import audit_posttune_transaction


class PostTuneTransactionEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("TIMELEARNER_POSTTUNE_TRANSACTION_DIR")
        if not value:
            raise unittest.SkipTest("requires actual native PostTune transaction primaries")
        root = Path(value)
        cls.sources = {load(p)["sha256"]: (p, load_case(p)) for p in root.glob("*_learned_state.json")}
        if len(cls.sources) != 2:
            raise RuntimeError("requires both real Classic/Branch primary training sources")
        cls.records = [(p, load(p)) for p in root.glob("*_post_tune_*.json")
                       if load(p).get("kind") == "native_post_tune_transaction"]
        if len(cls.records) != 24:
            raise RuntimeError("requires five modes, two metric variants and five negative/cancel/ownership controls per topology")

    def audit(self, report):
        return audit_posttune_transaction(report, self.sources[report["source_recognition"]["source_solo"]["sha256"]][1])

    def example(self, *, calibrated=False, synthetic=False):
        return copy.deepcopy(next(r for _, r in self.records if (not calibrated or r["status"] == "calibrated") and
                                  (r["mode"] == "search_synthetic" if synthetic else r["mode"] == "keep_done" and r["candidates"])))

    def reject(self, report):
        report["sha256"] = sha({k: v for k, v in report.items() if k != "sha256"})
        with self.assertRaises(EvidenceError):
            self.audit(report)

    def test_all_twenty_four_actual_reports(self):
        for _, r in self.records:
            with self.subTest(mode=r["mode"], status=r["status"]):
                a = self.audit(r)
                self.assertTrue(a["recorded_search_consistent"])
                self.assertFalse(a["native_execution_verified"])
                self.assertFalse(a["owner_restoration_verified"])
                self.assertIsNone(a["evaluation_verdict"])

    def test_actual_cli(self):
        from Scripts.StructTrain.TimeLearner.__main__ import main
        path, report = next((p, r) for p, r in self.records if r["status"] == "calibrated")
        source = self.sources[report["source_recognition"]["source_solo"]["sha256"]][0]
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            code = main(["analyze", str(path), "--format", "posttune-transaction", "--source-solo", str(source)])
        self.assertEqual(code, 0, error.getvalue())

    def test_observation_permutation_does_not_change_gap(self):
        r = self.example(calibrated=True)
        for row in r["candidates"]:
            row["matrix"]["observations"].reverse()
        r["sha256"] = sha({k: v for k, v in r.items() if k != "sha256"})
        self.assertTrue(self.audit(r)["recorded_search_consistent"])

    def test_forged_finite_gap(self):
        r = self.example();r["candidates"][0]["measured_gap"] += .1;self.reject(r)

    def test_missing_foil(self):
        r = self.example();r["candidates"][0]["matrix"]["observations"].pop();self.reject(r)

    def test_changed_actual_metric_samples(self):
        r = self.example();r["candidates"][0]["matrix"]["observations"][0]["samples"][0]["lt_potential"] += 100.
        self.reject(r)

    def test_changed_declared_search_condition(self):
        r = self.example(synthetic=True);r["canonical_floor"] *= 1.1;self.reject(r)

    def test_wrong_selected_candidate(self):
        r = self.example(synthetic=True)
        self.assertGreater(len(r["candidates"]), 1)
        r["selected_index"] = (r["selected_index"]+1) % len(r["candidates"]);self.reject(r)

    def test_changed_child_criterion(self):
        r = self.example(calibrated=True);r["confirmation_specification"]["criterion"]["begin_offset"] += .01
        self.reject(r)

    def test_unknown_schema(self):
        r = self.example();r["schema_version"] = 2;self.reject(r)

    def test_missing_accepted_proposal(self):
        r = self.example(synthetic=True);r["candidates"].pop();self.reject(r)
