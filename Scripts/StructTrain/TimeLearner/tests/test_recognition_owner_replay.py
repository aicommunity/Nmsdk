"""Real ModelSpec2 replay and corruption of its original portable evidence."""
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from xml.etree import ElementTree as ET

from ..native_evidence import EvidenceError, load
from ..recognition_owner_replay import audit_case_replay
from .native_declared_corpus import audit_model_spec2_recognition_replay


class RecognitionOwnerReplayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = os.environ.get("TIMELEARNER_MODELSPEC2_OWNER_SOURCE")
        replay = os.environ.get("TIMELEARNER_MODELSPEC2_FRESH_OWNER_REPLAY")
        if not source or not replay:
            raise unittest.SkipTest("requires actual eight native ModelSpec2 owner replays")
        cls.source, cls.replay = Path(source), Path(replay)
        cls.index = load(cls.replay/"index.json")
        if len(cls.index["cases"]) != 8:
            raise RuntimeError("requires all eight actual ModelSpec2 replay cases")

    def clone(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        result = Path(temporary.name)/"replay"
        shutil.copytree(self.replay, result, symlinks=True)
        return result

    def test_all_eight_declared_models_have_actual_exact_fresh_process_waveforms(self):
        for row in self.index["cases"]:
            path = self.source/row["source_filename"]
            solo_path = path.with_name(path.name.removesuffix("_owner_recognition_state.json")+"_learned_state.json")
            with self.subTest(case=row["id"]):
                audit = audit_model_spec2_recognition_replay(solo_path, load(path)["source_solo"])
                self.assertTrue(audit["waveform_bytes_exact"])
                self.assertIsNone(audit["evaluation_verdict"])

    def test_changed_source_binding_cannot_reuse_a_passed_native_gate(self):
        replay = self.clone()
        index = load(replay/"index.json")
        index["cases"][0]["source_solo_sha256"] = "0"*64
        (replay/"index.json").write_text(json.dumps(index))
        with self.assertRaisesRegex(EvidenceError, "owner_replay_source_changed"):
            audit_case_replay(self.source/index["cases"][0]["source_filename"], replay)

    def test_a_saved_pass_does_not_override_skipped_native_junit(self):
        replay = self.clone()
        row = self.index["cases"][0]
        path = replay/row["id"]/"gate/native.xml"
        tree = ET.parse(path)
        test = next(tree.getroot().iter("testcase"))
        test.set("status", "notrun")
        tree.write(path)
        with self.assertRaisesRegex(EvidenceError, "native_gate_skipped_or_unfinished_case"):
            audit_case_replay(self.source/row["source_filename"], replay)

    def test_nonfinite_actual_soma_cannot_reuse_the_transport_summary(self):
        replay = self.clone()
        row = self.index["cases"][0]
        path = replay/row["id"]/"actual.json.csv"
        lines = path.read_text().splitlines()
        values = lines[1].split(",")
        values[2] = "nan"
        lines[1] = ",".join(values)
        path.write_text("\n".join(lines)+"\n")
        with self.assertRaisesRegex(EvidenceError, "invalid_fresh_transport_samples"):
            audit_case_replay(self.source/row["source_filename"], replay)
