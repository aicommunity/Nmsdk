"""Actual owner-driven PostTune receipts, source lineage and corruption controls."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..learned_evidence import load_case
from ..native_evidence import EvidenceError, load
from ..owned_posttune_evidence import audit_owned_posttune


class OwnedPostTuneEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_OWNED_POSTTUNE_NATIVE")
        fixtures = os.environ.get("TIMELEARNER_FINALIZATION_ORIGINAL_FIXTURES")
        if not directory or not fixtures:
            raise unittest.SkipTest("requires actual owner-driven records and original Train primaries")
        cls.records = sorted(Path(directory).glob("*_managed_finalization_*_owned_*.json"))
        if len(cls.records) != 10:
            raise RuntimeError("requires eight completed and two interrupted native phases")
        cls.sources = {}
        for topology, source in (("Classic", "Classic-auto_metric"), ("Branch", "Branch-synthetic")):
            paths = list((Path(fixtures)/source/"input/source").glob("*_learned_state.json"))
            if len(paths) != 1:
                raise RuntimeError("requires exactly one original source with full primaries")
            cls.sources[topology] = load_case(paths[0])

    def test_actual_completion_and_interruptions(self):
        seen = set()
        for path in self.records:
            record = load(path)
            topology = path.name.split("_")[0]
            with self.subTest(case=path.name):
                result = audit_owned_posttune(record, self.sources[topology])
                self.assertTrue(result["recorded_phase_sequence_consistent"])
                self.assertFalse(result["native_scheduler_execution_attested"])
                self.assertIsNone(result["scientific_verdict"])
                seen.add((topology, record["calculate_mode"], record["connected"], record["interrupted"]))
        self.assertEqual(seen, {(t, m, c, False) for t in ("Classic", "Branch") for m in (0, 1) for c in (False, True)} |
                         {(t, 0, True, True) for t in ("Classic", "Branch")})

    def test_corrupt_receipts_and_partial_success_reject(self):
        for path in self.records:
            record = load(path)
            source = self.sources[path.name.split("_")[0]]
            for label, mutate in (
                ("binding", lambda r: r.update(connected=not r["connected"])),
                ("mode", lambda r: r.update(calculate_mode=1-r["calculate_mode"])),
                ("phase", lambda r: r["execution"].update(advance_phase="after_children")),
                ("duplicate_tick", lambda r: r["execution"]["advance_times"].__setitem__(1,r["execution"]["advance_times"][0])),
                ("nonfinite", lambda r: r["execution"]["advance_times"].__setitem__(0,float("nan"))),
                ("frequency", lambda r: r["execution"].update(frequency_hz=1)),
                ("done", lambda r: r["execution"].update(done=False)),
                ("scientific_pass", lambda r: r.update(scientific_verdict=True)),
                ("interruption", lambda r: r.update(interrupted=not r["interrupted"])),
                ("selection", lambda r: r.update(selected_package={"not":"the measured model"})),
            ):
                corrupted = deepcopy(record);mutate(corrupted)
                with self.subTest(case=path.name, corruption=label):
                    with self.assertRaises(EvidenceError):
                        audit_owned_posttune(corrupted, source)
