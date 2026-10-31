"""Fresh live Train source traces, full native phase and frozen replay records."""
from copy import deepcopy
import os
from pathlib import Path
import re
import unittest

from ..learned_evidence import load_case
from ..live_finalization_evidence import audit_completed_live_finalization
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load


class LiveFinalizationEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("TIMELEARNER_LIVE_FINALIZATION_NATIVE")
        if not root:
            raise unittest.SkipTest("requires real cold Train / owned phase / frozen replay")
        cls.paths = [p for p in sorted(Path(root).glob("*.json")) if
                     re.fullmatch(r"(?:Classic|Branch)_live_finalization_[01]_(?:local|connected)_[01]\.json", p.name)]
        if len(cls.paths) < 2:
            raise RuntimeError("requires both actual cold topology records")

    def test_actual_completed_phases_and_fresh_training_primaries(self):
        seen = set()
        for p in self.paths:
            with self.subTest(case=p.name):
                source = load_case(p.with_name(p.stem+"_learned_state.json"))
                result = audit_completed_live_finalization(load(p), source)
                self.assertTrue(result["frozen_replay_audit"]["all_observations_valid"])
                self.assertFalse(result["cold_construction_and_native_execution_attested"])
                seen.add(p.name.split("_")[0])
        self.assertEqual(seen, {"Classic", "Branch"})

    def test_resigned_handoff_design_source_and_frozen_corruption_reject(self):
        for p in self.paths:
            original = load(p);source = load_case(p.with_name(p.stem+"_learned_state.json"))
            for label, mutate in (
                ("same_tick", lambda r: r["live"].update(entry_model_time=r["live"]["captured_model_time"])),
                ("execution_clock", lambda r: r["live"]["post_tune_execution"]["advance_times"].__setitem__(0, -1)),
                ("request", lambda r: r["live"]["training_request"].update(session_attempt=999)),
                ("plan_trials", lambda r: r["live"]["plan"]["trials"].pop()),
                ("outcome", lambda r: r["live"].update(reason="exact")),
                ("missing_frozen", lambda r: r["frozen_replay"]["observations"].pop()),
                ("duplicate_frozen", lambda r: r["frozen_replay"]["observations"].append(deepcopy(r["frozen_replay"]["observations"][0]))),
                ("verdict", lambda r: r.update(scientific_verdict=True)),
            ):
                changed = deepcopy(original);mutate(changed)
                for value in (changed["live"]["plan"], changed["live"]):
                    value["sha256"] = sha({k: v for k, v in value.items() if k != "sha256"})
                with self.subTest(case=p.name, corruption=label):
                    with self.assertRaises(EvidenceError):
                        audit_completed_live_finalization(changed, source)
