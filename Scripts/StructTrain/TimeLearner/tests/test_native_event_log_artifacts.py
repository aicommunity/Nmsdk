"""Private Rdk log aliases must not weaken primary artifact validation."""
import json
from pathlib import Path
import tempfile
import unittest

from ..native_calibration_worker import _artifact_files
from ..native_evidence import EvidenceError


class NativeEventLogArtifactsTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root/"process").mkdir()
        (self.root/"process/owned-process.json").write_text(json.dumps({"pid": 123}))
        self.logs = self.root/"native.events-log/EventsLog"
        self.logs.mkdir(parents=True)
        self.log = self.logs/"NeuroModeler.host.user.log.INFO.20261104-120000.123"
        self.log.write_text("actual process log\n")
        self.alias = self.logs/"NeuroModeler.INFO"

    def test_regular_owned_log_and_portable_copy_without_alias(self):
        self.assertIn(self.log, _artifact_files(self.root))

    def test_native_alias_is_validated_without_duplicate_primary(self):
        self.alias.symlink_to(self.log.name)
        files = _artifact_files(self.root)
        self.assertIn(self.log, files)
        self.assertNotIn(self.alias, files)

    def test_escaping_alias_is_rejected(self):
        self.alias.symlink_to("../../process/owned-process.json")
        with self.assertRaisesRegex(EvidenceError, "alias_escape"):
            _artifact_files(self.root)

    def test_another_process_log_is_rejected(self):
        self.log.rename(self.log.with_suffix(".124"))
        with self.assertRaisesRegex(EvidenceError, "owner_mismatch"):
            _artifact_files(self.root)

    def test_dangling_alias_is_rejected(self):
        self.alias.symlink_to("missing")
        with self.assertRaisesRegex(EvidenceError, "alias_target_invalid"):
            _artifact_files(self.root)

    def test_alias_chain_is_rejected(self):
        self.alias.symlink_to("NeuroModeler.WARNING")
        (self.logs/"NeuroModeler.WARNING").symlink_to(self.log.name)
        with self.assertRaisesRegex(EvidenceError, "alias_target_invalid"):
            _artifact_files(self.root)

    def test_severity_mismatch_is_rejected(self):
        (self.logs/"NeuroModeler.ERROR").symlink_to(self.log.name)
        with self.assertRaisesRegex(EvidenceError, "severity_mismatch"):
            _artifact_files(self.root)

    def test_primary_symlink_is_rejected(self):
        (self.root/"model.json").symlink_to(self.log)
        with self.assertRaisesRegex(EvidenceError, "missing_or_symlink"):
            _artifact_files(self.root)

    def test_directory_symlink_is_rejected(self):
        (self.root/"other").symlink_to(self.logs, target_is_directory=True)
        with self.assertRaisesRegex(EvidenceError, "missing_or_symlink"):
            _artifact_files(self.root)
