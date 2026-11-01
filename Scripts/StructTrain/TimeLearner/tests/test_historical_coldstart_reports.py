"""Actual historical native gate exports, transfer integrity and rejected setups."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..native_evidence import EvidenceError, load
from .historical_phasea_coldstart import readback
from .historical_phasea_coldtrain import validate_coldstart_gate


class HistoricalColdstartReports(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(os.environ["TL_HISTORICAL_COLDSTART"])
        cls.gate = cls.root/"s11-august-coldstart-elder-a2"
        cls.runtime = load(cls.gate/"native_state_reset/process/runtime.json")

    def test_four_actual_native_exports(self):
        for mode, count in (("trained_control", 116), ("native_state_reset", 4),
                            ("explicit_cold", 116), ("state_disabled", 116)):
            with self.subTest(mode=mode):
                actual = readback(self.gate/mode/"work")
                self.assertEqual(actual, load(self.gate/mode/"readback.json"))
                self.assertEqual(actual["effective_dendrite_segments"], count)
        data = load(self.gate/"progress.json")
        self.assertEqual(data["explicit_cold"]["configuration_validity"], "graph_parameter_mismatch")
        self.assertFalse(data["explicit_cold"]["training_allowed"])

    def test_all_original_prepared_input_hashes(self):
        count = 0
        for attempt in ("a1", "a2"):
            for path in (self.root/("s11-august-coldstart-elder-"+attempt)).glob("*/pre-run-files.json"):
                for record in json.loads(path.read_text()):
                    rel = Path(record["path"]).relative_to("work")
                    raw = (path.parent/"prepared"/rel).read_bytes()
                    self.assertEqual(hashlib.sha256(raw).hexdigest(), record["sha256"]);count += 1
        self.assertEqual(count, 49)

    def test_real_gate_admitted(self):
        self.assertEqual(len(validate_coldstart_gate(self.gate, self.runtime)), 7)

    def reject_modified(self, path, mutate, reason):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)/"gate";shutil.copytree(self.gate, directory)
            target = directory/path;record = json.loads(target.read_text())
            mutate(record);target.write_text(json.dumps(record))
            with self.assertRaisesRegex(EvidenceError, reason):validate_coldstart_gate(directory, self.runtime)

    def test_false_gate_rejected(self):
        self.reject_modified("validation.json", lambda x: x.update(native_cold_start_verified=False),
                             "native_coldstart_gate_not_completed")

    def test_forged_readback_metadata_rejected(self):
        self.reject_modified("native_state_reset/readback.json", lambda x: x.update(effective_dendrite_segments=116),
                             "coldstart_gate_export_disagrees_with_metadata")

    def test_failed_process_rejected(self):
        self.reject_modified("native_state_reset/process/result.json", lambda x: x.update(execution="timeout"),
                             "coldstart_gate_process_not_completed")

    def test_different_runtime_rejected(self):
        self.reject_modified("native_state_reset/process/runtime.json", lambda x: x.update(runtime_fingerprint="changed"),
                             "coldstart_gate_runtime_changed")


if __name__ == "__main__":
    unittest.main()
