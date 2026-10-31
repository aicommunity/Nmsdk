"""Audit actual native grid transactions and adversarially altered records."""
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import unittest

from ..calibration_transaction_evidence import audit_native_calibration_transaction
from ..learned_evidence import load_case
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load


def resign(value):
    value.pop("sha256", None);value["sha256"] = sha(value)
    return value


class NativeCalibrationTransactionEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("TIMELEARNER_CALIBRATION_TRANSACTION_DIR")
        if not root: raise unittest.SkipTest("requires actual Classic/Branch grid native execution")
        cls.root = Path(root)
        sources = {load(p)["sha256"]: load_case(p) for p in cls.root.glob("*_learned_state.json")}
        if len(sources) != 2: raise RuntimeError("requires two actual source solo packages")
        cls.cases = []
        for p in sorted(cls.root.glob("*_grid_transaction.json")):
            report = load(p)
            source = sources[report["source_recognition"]["source_solo"]["sha256"]]
            cls.cases.append((p, report, source))
        counts = {}
        for _, report, _ in cls.cases:
            counts[report["status"]] = counts.get(report["status"], 0)+1
        if counts != {"calibrated": 2, "nonseparable": 2, "budget_exhausted": 2, "cancelled": 4, "recovery_required": 2}:
            raise RuntimeError("requires every native commit/rollback/cancel/reset control")

    def successful(self):
        return [(p, r, s) for p, r, s in self.cases if r["status"] == "calibrated"]

    def test_all_actual_transactions_and_primary_source_data(self):
        for _, report, source in self.cases:
            result = audit_native_calibration_transaction(report, source)
            self.assertTrue(result["transaction_evidence_consistent"])
            self.assertEqual(result["calibrated"], report["status"] == "calibrated")
            self.assertFalse(result["native_execution_verified"])
            self.assertFalse(result["owner_restoration_verified"])
            self.assertIsNone(result["evaluation_verdict"])

    def test_rehashed_wrong_selected_index_is_rejected(self):
        for _, report, source in self.successful():
            bad = copy.deepcopy(report);bad["selected_index"] = 0
            with self.assertRaisesRegex(EvidenceError, "wrong_selection"):
                audit_native_calibration_transaction(resign(bad), source)

    def test_missing_grid_candidate_cannot_support_calibration(self):
        for _, report, source in self.successful():
            bad = copy.deepcopy(report);bad["candidates"].pop()
            with self.assertRaisesRegex(EvidenceError, "missing_candidates"):
                audit_native_calibration_transaction(resign(bad), source)

    def test_search_data_cannot_replace_fresh_confirmation(self):
        for _, report, source in self.successful():
            bad = copy.deepcopy(report);bad["confirmation"] = bad["candidates"][1]["matrix"]
            with self.assertRaisesRegex(EvidenceError, "confirmation_changed"):
                audit_native_calibration_transaction(resign(bad), source)

    def test_modified_primary_frames_in_grid_are_rejected(self):
        for _, report, source in self.successful():
            bad = copy.deepcopy(report)
            bad["candidates"][0]["matrix"]["observations"][0]["samples"][0]["soma"][0] += .001
            with self.assertRaises(EvidenceError):
                audit_native_calibration_transaction(resign(bad), source)

    def test_diagnostic_or_cancelled_state_cannot_be_relabelled_calibrated(self):
        for _, report, source in self.cases:
            if report["status"] == "calibrated": continue
            bad = copy.deepcopy(report);bad["calibrated"] = True
            with self.assertRaisesRegex(EvidenceError, "unsupported_calibration_transaction_claim"):
                audit_native_calibration_transaction(resign(bad), source)

    def test_full_grid_nonseparable_is_distinct_from_budget_exhaustion(self):
        for _, report, source in self.cases:
            if report["status"] not in {"nonseparable", "budget_exhausted"}: continue
            bad = copy.deepcopy(report)
            bad["status"] = "budget_exhausted" if report["status"] == "nonseparable" else "nonseparable"
            with self.assertRaisesRegex(EvidenceError, "wrong_negative_status"):
                audit_native_calibration_transaction(resign(bad), source)

    def test_cli_uses_primary_source_and_never_claims_test_pass(self):
        from ..__main__ import main
        sources = {load(p)["sha256"]: p for p in self.root.glob("*_learned_state.json")}
        for path, report, _ in self.successful():
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = main(["analyze", str(path), "--format", "calibration-transaction", "--source-solo",
                               str(sources[report["source_recognition"]["source_solo"]["sha256"]])])
            self.assertEqual(status, 0)
            result = json.loads(output.getvalue())
            self.assertTrue(result["analysis"]["calibrated"])
            self.assertIsNone(result["evaluation_verdict"])
