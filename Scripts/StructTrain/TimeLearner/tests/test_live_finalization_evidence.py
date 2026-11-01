"""Fresh live Train source traces, full native phase and frozen replay records."""
from copy import deepcopy
import os
from pathlib import Path
import re
import unittest

from ..learned_evidence import load_case
from ..live_finalization_evidence import audit_completed_live_finalization, audit_pre_entry_live_finalization
from ..stopped_evidence import load_case as load_stopped_case
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


class LiveFinalizationRejectionEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("TIMELEARNER_LIVE_FINALIZATION_NATIVE")
        if not root:
            raise unittest.SkipTest("requires all twelve real pre-entry native controls")
        cls.paths = [p for p in sorted(Path(root).glob("*.json")) if
                     re.fullmatch(r"(?:Classic|Branch)_live_finalization_[01]_(?:local|connected)_[2-7]\.json", p.name)]
        if len(cls.paths) != 12:
            raise RuntimeError("requires both topologies and all six pre-entry negative scenarios")

    @staticmethod
    def source(p, record):
        if record["scenario"] in (6, 7):
            if list(p.parent.glob(p.stem+"_state_trial_*.json")) or list(p.parent.glob(p.stem+"_stopped_trial_*.json")):
                raise RuntimeError("preflight rejected condition unexpectedly produced Train probes")
            return None
        if record["scenario"] == 2:
            return load_stopped_case(p.with_name(p.stem+"_stopped_state.json"))
        return load_case(p.with_name(p.stem+"_learned_state.json"))

    def test_all_rejections_and_real_primary_sources(self):
        seen = set()
        for p in self.paths:
            record = load(p)
            with self.subTest(case=p.name):
                result = audit_pre_entry_live_finalization(record, self.source(p, record))
                self.assertTrue(result["no_recognition_evidence"])
                self.assertFalse(result["actual_control_and_physics_interventions_attested"])
                seen.add((p.name.split("_")[0], record["scenario"]))
        self.assertEqual(seen, {(top, s) for top in ("Classic", "Branch") for s in range(2, 8)})

    def test_resigned_early_stop_and_false_evaluation_controls_reject(self):
        for p in self.paths:
            record = load(p);source = self.source(p, record)
            for name, mutate in (
                ("false_model", lambda r: r.update(final_package={"unexpected": True})),
                ("false_completion", lambda r: r["live"].update(status="completed")),
                ("false_entry", lambda r: r["live"].update(entry_model_time=0)),
                ("false_reason", lambda r: r["live"].update(reason="exact")),
                ("false_verdict", lambda r: r.update(scientific_verdict=True)),
            ):
                changed = deepcopy(record);mutate(changed)
                changed["live"]["sha256"] = sha({k: v for k, v in changed["live"].items() if k != "sha256"})
                with self.subTest(case=p.name, corruption=name):
                    with self.assertRaises(EvidenceError):audit_pre_entry_live_finalization(changed, source)


class LiveFinalizationCancellationEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("TIMELEARNER_LIVE_CANCEL_NATIVE")
        if not root:
            raise unittest.SkipTest("requires eight actual native cancellation controls")
        cls.paths = [p for p in sorted(Path(root).glob("*.json")) if re.fullmatch(
            r"(?:Classic|Branch)_live_finalization_[01]_(?:local|connected)_(?:[89]|1[01])\.json", p.name)]
        if len(cls.paths) != 8:
            raise RuntimeError("requires Classic/Branch and all four cancellation boundaries")

    @staticmethod
    def source(p, record):
        if record["scenario"] == 8:
            if list(p.parent.glob(p.stem+"_*trial_*.json")):
                raise RuntimeError("cancelled armed plan unexpectedly produced probes")
            return None
        if record["scenario"] == 9:
            return load_stopped_case(p.with_name(p.stem+"_stopped_state.json"))
        return load_case(p.with_name(p.stem+"_learned_state.json"))

    def test_actual_cancelled_boundaries_and_primary_data(self):
        from ..live_finalization_evidence import audit_cancelled_live_finalization
        seen = set()
        for p in self.paths:
            r = load(p)
            with self.subTest(case=p.name):
                result = audit_cancelled_live_finalization(r, self.source(p, r))
                self.assertIsNone(result["scientific_verdict"])
                self.assertTrue(result.get("no_recognition_evidence") or result.get("no_frozen_evaluation"))
                seen.add((p.name.split("_")[0], r["scenario"]))
        self.assertEqual(seen, {(top, s) for top in ("Classic", "Branch") for s in range(8, 12)})

    def test_resigned_false_completion_and_discarded_data_rejected(self):
        from ..live_finalization_evidence import audit_cancelled_live_finalization
        for p in self.paths:
            r = load(p);source = self.source(p, r)
            for name, mutate in (
                ("false_model", lambda r: r.update(final_package={"unexpected": True})),
                ("false_reason", lambda r: r["live"].update(reason="exact")),
                ("false_entry", lambda r: r["live"].update(entry_model_time=-1)),
                ("false_summary", lambda r: r.update(training_summary={"invented": True})),
                ("false_frozen", lambda r: r["frozen_replay"]["observations"].append({})),
                ("false_verdict", lambda r: r.update(scientific_verdict=True)),
            ):
                changed = deepcopy(r);mutate(changed)
                changed["live"]["sha256"] = sha({k: v for k, v in changed["live"].items() if k != "sha256"})
                with self.subTest(case=p.name, corruption=name):
                    with self.assertRaises(EvidenceError):audit_cancelled_live_finalization(changed, source)
