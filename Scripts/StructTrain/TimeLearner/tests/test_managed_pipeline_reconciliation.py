"""Recovery audits from completed actual coordinator phases, never mock jobs."""
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..__main__ import main
from ..managed_pipeline import audit_pipeline, reconcile_pipeline
from ..native_evidence import EvidenceError, load


class ManagedPipelineReconciliationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = os.environ.get("TIMELEARNER_MANAGED_COORDINATOR_PRIMARY")
        if not source:
            raise unittest.SkipTest("requires actual completed managed coordinator corpus on its original worker")
        cls.source = Path(source)

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="tl-coordinator-reconciliation-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)/"pipeline"

    def copy(self, name="Classic-v1"):
        original = self.source/name/"runs/pipeline"
        self.assertIsNone(audit_pipeline(original)["pending_phase"])
        # Native Rdk event logs contain severity aliases. Preserve their real
        # filesystem type: materializing aliases as regular files would change
        # the audited artifact inventory before testing recovery itself.
        shutil.copytree(original, self.root, symlinks=True)
        self.assertEqual(audit_pipeline(self.root), audit_pipeline(original))
        return self.root

    def lost_final_event(self):
        path = self.root/"journal.jsonl"
        lines = path.read_bytes().splitlines(keepends=True)
        last = json.loads(lines[-1])
        self.assertIn(last["event"], ("finished", "halted"))
        path.write_bytes(b"".join(lines[:-1]))
        return last["phase"]

    def test_closed_complete_phase_is_reconciled_without_new_native_work(self):
        for name in ("Classic-v1", "Branch-v1"):
            with self.subTest(name=name):
                # Each case owns a distinct new temporary copy; native records
                # refer to the real original, already closed unit invocations.
                if self.root.exists():
                    self.root = self.root.parent/(name+"-pipeline")
                self.copy(name)
                expected = audit_pipeline(self.root)
                phase = self.lost_final_event()
                before = load(self.root/"phases"/phase/"process/contained/owned-unit.json")
                result = reconcile_pipeline(self.root)
                self.assertEqual(result, expected)
                self.assertEqual(load(self.root/"phases"/phase/"process/contained/owned-unit.json"), before)
                self.assertEqual(json.loads((self.root/"journal.jsonl").read_bytes().splitlines()[-1])["event"],
                                 "reconciled_finished")

    def test_stopped_training_stays_halted_without_export_or_test(self):
        self.copy("Classic-N0")
        self.assertEqual(self.lost_final_event(), "train")
        result = reconcile_pipeline(self.root)
        self.assertFalse(result["pipeline_complete"])
        self.assertEqual(result["halted_phase"], "train")
        self.assertFalse((self.root/"phases/export").exists())
        self.assertFalse((self.root/"phases/evaluate").exists())
        self.assertEqual(json.loads((self.root/"journal.jsonl").read_bytes().splitlines()[-1])["event"],
                         "reconciled_halted")

    def test_missing_manifest_never_creates_a_completion_record(self):
        self.copy()
        phase = self.lost_final_event()
        (self.root/"phases"/phase/"run-manifest.json").unlink()
        before = (self.root/"journal.jsonl").read_bytes()
        with self.assertRaises((EvidenceError, OSError)):
            reconcile_pipeline(self.root)
        self.assertEqual((self.root/"journal.jsonl").read_bytes(), before)

    def test_changed_native_model_is_not_adopted(self):
        self.copy()
        phase = self.lost_final_event()
        model = self.root/"phases"/phase/"native/model.json"
        model.write_bytes(model.read_bytes()+b" ")
        before = (self.root/"journal.jsonl").read_bytes()
        with self.assertRaises(EvidenceError):
            reconcile_pipeline(self.root)
        self.assertEqual((self.root/"journal.jsonl").read_bytes(), before)

    def test_torn_journal_is_preserved_and_not_silently_repaired(self):
        self.copy()
        path = self.root/"journal.jsonl"
        path.write_bytes(path.read_bytes()[:-1])
        before = path.read_bytes()
        with self.assertRaisesRegex(EvidenceError, "pipeline_journal_torn_record"):
            reconcile_pipeline(self.root)
        self.assertEqual(path.read_bytes(), before)

    def test_repeat_reconciliation_is_rejected_without_extra_events(self):
        self.copy()
        self.lost_final_event()
        reconcile_pipeline(self.root)
        before = (self.root/"journal.jsonl").read_bytes()
        with self.assertRaisesRegex(EvidenceError, "pipeline_no_phase_to_reconcile"):
            reconcile_pipeline(self.root)
        self.assertEqual((self.root/"journal.jsonl").read_bytes(), before)

    def test_public_cli_audits_reconciled_actual_phase(self):
        self.copy()
        self.lost_final_event()
        text = io.StringIO()
        with contextlib.redirect_stdout(text), contextlib.redirect_stderr(text):
            code = main(["pipeline", "reconcile", str(self.root)])
        self.assertEqual(code, 0, text.getvalue())
        self.assertTrue(audit_pipeline(self.root)["pipeline_complete"])
