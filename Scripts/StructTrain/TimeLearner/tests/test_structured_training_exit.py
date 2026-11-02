"""Actual native one-tick runs plus destructive copies; no fabricated success."""
import copy
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..native_calibration_worker import _record, _signed, _write
from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import _structured_training_exit, audit_execution, audit_run_manifest


class StructuredTrainingExitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        corpus = os.environ.get("TIMELEARNER_STRUCTURED_EXIT_DIR")
        legacy = os.environ.get("TIMELEARNER_LEGACY_SCHEMA1_TRAIN_DIR")
        if not corpus or not legacy:
            raise unittest.SkipTest("requires actual new schema-2 and archived schema-1 Train runs")
        cls.corpus, cls.legacy = Path(corpus), Path(legacy)
        cls.current = cls.corpus/"runs/train-Classic-legacy-budget"

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="tl-structured-exit-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)/"run"

    def copied(self, source=None):
        shutil.copytree(source or self.current, self.root)
        return self.root

    def test_actual_schema1_stops_are_audited_without_execution_success(self):
        for topology in ("Classic", "Branch"):
            root = self.corpus/f"runs/train-{topology}-legacy-budget"
            job, manifest, process = (load(root/p) for p in
                                      ("input/job.json", "run-manifest.json", "process/result.json"))
            self.assertEqual(job["schema_version"], 1)
            self.assertEqual(manifest["schema_version"], 2)
            self.assertEqual(process["returncode"], 2)
            self.assertEqual(manifest["execution"], "process_error")
            self.assertEqual(manifest["validity"], "valid")
            self.assertFalse(manifest["analysis"]["completed_boundary"])
            self.assertIsNone(manifest["analysis"]["evaluation_verdict"])
            self.assertEqual(audit_execution("train", root/"native", job), manifest["analysis"])
            self.assertTrue(audit_run_manifest(root/"run-manifest.json")["run_evidence_consistent"])

    def test_archived_schema1_manifest_keeps_its_unverified_interpretation(self):
        record = load(self.legacy/"run-manifest.json")
        self.assertEqual(record["schema_version"], 1)
        self.assertEqual(load(self.legacy/"input/job.json")["schema_version"], 1)
        self.assertEqual(record["validity"], "unverified_execution")
        self.assertIsNone(record["analysis"])
        self.assertTrue(audit_run_manifest(self.legacy/"run-manifest.json")["run_evidence_consistent"])

    def test_changing_only_legacy_version_does_not_upgrade_old_evidence(self):
        root = self.copied(self.legacy)
        record = load(root/"run-manifest.json");record["schema_version"] = 2
        _write(root/"run-manifest.json", _signed({k: v for k, v in record.items() if k != "sha256"}))
        with self.assertRaisesRegex(EvidenceError, "pipeline_run_analysis_changed"):
            audit_run_manifest(root/"run-manifest.json")

    def test_unknown_or_boolean_manifest_version_is_rejected(self):
        root = self.copied();original = load(root/"run-manifest.json")
        for version in (3, True):
            record = {**original, "schema_version": version}
            _write(root/"run-manifest.json", _signed({k: v for k, v in record.items() if k != "sha256"}))
            with self.assertRaisesRegex(EvidenceError, "unknown_native_pipeline_run_manifest"):
                audit_run_manifest(root/"run-manifest.json")

    def mutate_execution(self, change):
        root = self.copied();execution = load(root/"native/execution.json")
        change(execution)
        _write(root/"native/execution.json", _signed({k: v for k, v in execution.items() if k != "sha256"}))
        record = load(root/"run-manifest.json")
        record["artifacts"] = [_record(root/r["path"], root) if r["path"] == "native/execution.json" else r
                               for r in record["artifacts"]]
        _write(root/"run-manifest.json", _signed({k: v for k, v in record.items() if k != "sha256"}))
        return root

    def test_nonzero_exit_cannot_claim_completed_execution(self):
        root = self.mutate_execution(lambda row: row.update(execution="completed"))
        with self.assertRaisesRegex(EvidenceError, "pipeline_nonzero_claims_completed_execution"):
            audit_run_manifest(root/"run-manifest.json")

    def test_stopped_package_cannot_claim_completed_training(self):
        root = self.mutate_execution(lambda row: row.update(completed_boundary=True))
        with self.assertRaises(EvidenceError):
            audit_run_manifest(root/"run-manifest.json")

    def test_other_exit_codes_timeouts_and_preflight_are_not_promoted(self):
        root = self.current;job = load(root/"input/job.json");process = load(root/"process/result.json")
        self.assertTrue(_structured_training_exit("train", job, process, root/"native"))
        for code in (0, 1, -9, None):
            altered = {**process, "returncode": code}
            self.assertFalse(_structured_training_exit("train", job, altered, root/"native"))
        self.assertFalse(_structured_training_exit("train", job, {**process, "execution": "timeout"}, root/"native"))
        self.assertFalse(_structured_training_exit("preflight", job, process, root/"native"))

    def test_missing_native_result_prevents_a_positive_audit(self):
        root = self.copied();(root/"native/execution.json").unlink()
        self.assertFalse(_structured_training_exit("train", load(root/"input/job.json"),
                                                 load(root/"process/result.json"), root/"native"))
        with self.assertRaises(EvidenceError):
            audit_run_manifest(root/"run-manifest.json")
