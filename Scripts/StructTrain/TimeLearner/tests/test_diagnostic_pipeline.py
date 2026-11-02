"""Portable readers of actual public stopped-Train diagnostic executions."""
from copy import deepcopy
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import audit_run_manifest
from ..recognition_metrics import (load_diagnostic_evaluation, load_evaluation,
                                   score_diagnostic_recognition_evaluation, score_recognition_evaluation)
from ..stopped_evidence import load_case
from .test_native_pipeline_worker import save, resign


class DiagnosticPipelineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_DIAGNOSTIC_PIPELINE_DIR")
        if not directory:
            raise unittest.SkipTest("requires actual public diagnostic-regression output")
        cls.root = Path(directory)

    def folder(self, topology, interrupted=False):
        return self.root/"runs"/(topology+("-interrupted" if interrupted else "-completed"))

    def case(self, topology, interrupted=False):
        root = self.folder(topology, interrupted)
        spec, observations = load_diagnostic_evaluation(root/"native/evaluation.json")
        model = load(root/"native/model.json")
        source = load_case(root/"input/source/train_stopped_state.json")
        return root, spec, observations, model, source

    def test_all_four_portable_closures_and_frozen_state(self):
        for topology in ("Classic", "Branch"):
            for interrupted in (False, True):
                root, spec, observations, model, source = self.case(topology, interrupted)
                with self.subTest(topology=topology, interrupted=interrupted):
                    result = audit_run_manifest(root/"run-manifest.json")
                    self.assertTrue(result["run_evidence_consistent"])
                    self.assertIsNone(result["evaluation_verdict"])
                    self.assertEqual(model, load(root/"native/model-after.json"))
                    self.assertEqual(model["source_solo"], source[0])
                    self.assertIsNone(source[0]["certificate"])
                    self.assertEqual(len(spec["trials"]), 4)
                    self.assertEqual(len(observations), 4)

    def test_completed_responses_keep_unfinished_training_role(self):
        for topology in ("Classic", "Branch"):
            _, spec, observations, model, source = self.case(topology)
            metrics = score_diagnostic_recognition_evaluation(spec, observations, model, source)
            self.assertEqual(metrics["validity"], "valid")
            self.assertTrue(metrics["diagnostic_only"])
            self.assertFalse(metrics["training_completed"])
            self.assertFalse(metrics["training_certificate_present"])
            self.assertEqual(metrics["declared_training_outcome"], source[0]["training_outcome"])
            self.assertIsNone(metrics["evaluation_verdict"])

    def test_row_permutation_does_not_change_score(self):
        for topology in ("Classic", "Branch"):
            _, spec, observations, model, source = self.case(topology)
            before = score_diagnostic_recognition_evaluation(spec, observations, model, source)
            shuffled = deepcopy(spec);shuffled["trials"].reverse()
            after = score_diagnostic_recognition_evaluation(shuffled, list(reversed(observations)), model, source)
            self.assertEqual(before, after)

    def test_partial_design_is_retained_and_never_scored_complete(self):
        for topology in ("Classic", "Branch"):
            root, spec, observations, model, source = self.case(topology, True)
            manifest = load(root/"run-manifest.json")
            self.assertEqual(manifest["execution"], "process_error")
            self.assertIsNone(manifest["analysis"]["metrics"])
            metrics = score_diagnostic_recognition_evaluation(spec, observations, model, source)
            self.assertEqual(metrics["validity"], "incomplete")
            self.assertTrue(metrics["invalid_trial_ids"])
            self.assertNotIn("pooled_counts", metrics)
            self.assertEqual(sum(bool(o["samples"]) for o in observations), 1)

    def test_missing_duplicate_nonfinite_observations_rejected(self):
        for topology in ("Classic", "Branch"):
            _, spec, observations, model, source = self.case(topology)
            nonfinite = deepcopy(observations);nonfinite[0]["samples"][0]["soma"][0] = float("nan")
            for changed in (observations[:-1], observations+[observations[0]], nonfinite):
                with self.subTest(topology=topology, count=len(changed)):
                    with self.assertRaises(EvidenceError):
                        score_diagnostic_recognition_evaluation(spec, changed, model, source)

    def test_ordinary_readers_remain_strict(self):
        for topology in ("Classic", "Branch"):
            root, spec, observations, model, _ = self.case(topology)
            with self.assertRaises(EvidenceError):load_evaluation(root/"native/evaluation.json")
            with self.assertRaises(EvidenceError):score_recognition_evaluation(spec, observations, model)

    def test_re_signed_manifest_cannot_claim_convergence_or_alter_metrics(self):
        for mutation in ("certificate", "counts"):
            with tempfile.TemporaryDirectory() as temporary:
                folder = Path(temporary)/"run";shutil.copytree(self.folder("Classic"), folder)
                manifest = load(folder/"run-manifest.json")
                metrics = manifest["analysis"]["metrics"]
                if mutation == "certificate":metrics["training_certificate_present"] = True
                else:metrics["pooled_counts"]["TP"] += 1
                save(folder/"run-manifest.json", resign(manifest))
                with self.assertRaises(EvidenceError):audit_run_manifest(folder/"run-manifest.json")
