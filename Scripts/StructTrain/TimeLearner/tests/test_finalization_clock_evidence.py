"""Four real clock-only native entry receipts and malformed-time controls."""
from copy import deepcopy
import os
from pathlib import Path
import unittest
from ..finalization_clock_evidence import audit_clock_handoff
from ..learned_evidence import load_case
from ..native_evidence import EvidenceError,load


class FinalizationClockEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=os.environ.get("TIMELEARNER_FINALIZATION_CLOCK_NATIVE")
        fixtures=os.environ.get("TIMELEARNER_FINALIZATION_ORIGINAL_FIXTURES")
        if not root or not fixtures:raise unittest.SkipTest("requires actual four native clock entry records and original Train primaries")
        cls.paths=sorted(Path(root).glob("*_clock_gap.json"))
        if len(cls.paths)!=4:raise RuntimeError("requires Classic/Branch CalculateMode0/1")
        cls.sources={}
        for top,name in (("Classic","Classic-auto_metric"),("Branch","Branch-synthetic")):
            paths=list((Path(fixtures)/name/"input/source").glob("*_learned_state.json"))
            if len(paths)!=1:raise RuntimeError("requires exactly one original source with complete primaries")
            cls.sources[top]=load_case(paths[0])

    def test_actual_clock_and_complete_conversion(self):
        seen=set()
        for p in self.paths:
            top=p.name.split("_")[0];record=load(p)
            with self.subTest(case=p.name):
                result=audit_clock_handoff(record,self.sources[top])
                self.assertTrue(result["clock_record_consistent"])
                self.assertFalse(result["native_clock_only_execution_attested"])
                seen.add((top,record["calculate_mode"]))
        self.assertEqual(seen,{(t,m) for t in ("Classic","Branch") for m in (0,1)})

    def test_corrupt_clock_mode_and_overclaimed_execution_reject(self):
        for p in self.paths:
            record=load(p);source=self.sources[p.name.split("_")[0]]
            for name,mutate in (
                ("no_step",lambda r:r.update(entry_time=r["capture_time"])),
                ("two_steps",lambda r:r.update(entry_time=r["capture_time"]+2*(r["entry_time"]-r["capture_time"]))),
                ("nonfinite",lambda r:r.update(entry_time=float("nan"))),
                ("mode",lambda r:r.update(calculate_mode=1-r["calculate_mode"])),
                ("live_claim",lambda r:r.update(live_train_handoff_implemented=True)),
                ("verdict",lambda r:r.update(scientific_verdict=True)),
                ("clock_claim",lambda r:r.update(clock_only_advance=False)),
                ("schema",lambda r:r.update(schema_version=99)),
            ):
                changed=deepcopy(record);mutate(changed)
                with self.subTest(case=p.name,corruption=name):
                    with self.assertRaises(EvidenceError):audit_clock_handoff(changed,source)
