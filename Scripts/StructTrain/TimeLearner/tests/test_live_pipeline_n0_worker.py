"""N0 production acceptance uses real Console results, including repeat schema2.

Inherits the complete fourteen-operation closure and corruption checks. Merely
changing the declaration is insufficient: persisted Train summaries and exported
models must confirm the selected normalization and physical candidate domain.
"""
from copy import deepcopy
from pathlib import Path
import tempfile

from ..native_evidence import EvidenceError, load
from .live_pipeline_corpus import make_job, run_corpus
from .test_live_pipeline_worker import LivePipelineWorkerTest as _Base


class N0LivePipelineWorkerTest(_Base):
    corpus_environment = "TIMELEARNER_N0_LIVE_PIPELINE_CORPUS"

    def test_insufficient_storage_rejected_before_any_run_directory_or_console(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)/"must-not-start"
            with self.assertRaisesRegex(EvidenceError, "corpus_insufficient_primary_storage"):
                run_corpus("nonexistent-fixtures", "nonexistent-runtime", output, 1,
                           minimum_free_bytes=2**63)
            self.assertFalse(output.exists())

    def test_declared_factors_survive_actual_training_and_frozen_handoff(self):
        factors = self.index["experiment_factors"]
        self.assertEqual(factors["normalization"], "N0")
        repeats = factors["n0_candidate_repeats"]
        for name in self.completed:
            folder = self.root/"runs"/name
            source = load(folder/"native/train_learned_state.json")
            summary = load(folder/"native/train_learned_summary.json")
            recognition = load(folder/"native/recognition-model.json")
            frozen = load(self.root/"runs"/(name+"-evaluate")/"input/job.json")
            with self.subTest(run=name):
                config = source["configuration"]
                self.assertEqual(config["model"]["normalization"], "N0")
                self.assertEqual(config["schema_version"], 2 if repeats > 1 else 1)
                self.assertEqual(config["search"].get("n0_candidate_repeats", 1), repeats)
                self.assertEqual(summary["configuration"]["normalization"], "synapse_count")
                self.assertEqual(summary["schema_version"], 2 if repeats > 1 else 1)
                self.assertEqual(frozen["source_recognition"], recognition)
                for bound, initial in zip(config["search"]["bounds"], config["model"]["inputs"]):
                    self.assertEqual(bound["minimum_resistance"], initial["resistance"])
                    self.assertEqual(bound["maximum_resistance"], initial["resistance"])
                bounds = config["search"]["bounds"]
                self.assertTrue(all(b["maximum_synapses"] == factors["n0_maximum_synapses"] for b in bounds[:-1]))
                self.assertEqual(bounds[-1]["maximum_synapses"], config["model"]["inputs"][-1]["synapses"])
                candidates = summary["candidates"]
                self.assertTrue(any(c["parameters"]["synapses"] > 1 for c in candidates),
                                "N0 positive control must actually measure a multi-synapse candidate")
                self.assertEqual(summary["resistance_domains"], [])
                for candidate in candidates:
                    self.assertEqual(len(candidate["full_parameters"]), len(config["model"]["inputs"]))
                    for actual, initial in zip(candidate["full_parameters"], config["model"]["inputs"]):
                        self.assertEqual(actual["resistance"], initial["resistance"])
                    anchor = candidate["full_parameters"][-1]
                    self.assertEqual(anchor["length"], config["model"]["inputs"][-1]["attachment"])
                    self.assertEqual(anchor["synapses"], config["model"]["inputs"][-1]["synapses"])
                if repeats > 1:
                    groups = summary["candidate_repeat_groups"]
                    self.assertTrue(groups, "real candidate repeat measurements required")
                    self.assertTrue(all(len(g["trial_ids"]) == repeats for g in groups if g["complete"]))

    def test_invalid_factors_rejected_and_template_is_immutable(self):
        original = load(self.root/"runs/Classic-fixed/input/job.json")
        # An actual newly exported state supplies the same profile/template
        # interface; no fabricated physical neuron is used for this check.
        recognition = load(self.root/"runs/Classic-fixed/native/recognition-model.json")
        template = {"source_recognition": recognition,
                    "owner_class": original["owner_class"], "implementation_id": original["implementation_id"]}
        before = deepcopy(template)
        for changes in ({"normalization": "N9"},
                        {"normalization": "N0", "n0_maximum_synapses": True},
                        {"normalization": "N0", "n0_maximum_synapses": 4, "n0_candidate_repeats": 0},
                        {"normalization": "N1", "n0_candidate_repeats": 2}):
            with self.subTest(changes=changes), self.assertRaises(EvidenceError):
                make_job(template, "invalid", legacy=True, **changes)
        self.assertEqual(template, before)

    def test_default_preparation_preserves_the_entire_existing_n0_declaration(self):
        for name in self.completed:
            folder = self.root/"runs"/name
            original = load(folder/"input/job.json")
            recognition = load(folder/"native/recognition-model.json")
            if recognition["kind"] == "timelearner_calibrated_recognition_state":
                recognition = recognition["source_candidate"]["source_recognition"]
            template = {"source_recognition": recognition, "owner_class": original["owner_class"],
                        "implementation_id": original["implementation_id"]}
            before = deepcopy(template)
            expected = deepcopy(recognition["source_solo"]["configuration"])
            expected["run_id"] = "preserve-existing-declaration"
            job = make_job(template, expected["run_id"], legacy=True)
            with self.subTest(run=name):
                self.assertEqual(job["configuration"], expected)
                self.assertEqual(template, before)
                for factors in ({"n0_maximum_synapses": 4}, {"n0_candidate_repeats": 2}):
                    with self.assertRaisesRegex(EvidenceError, "requires_explicit_normalization"):
                        make_job(template, "ambiguous-factor-change", legacy=True, **factors)

    def test_explicit_factor_preparation_reproduces_every_actual_training_job(self):
        factors = self.index["experiment_factors"]
        for top in ("Classic", "Branch"):
            baseline = load(self.root/"runs"/(top+"-grid")/"input/job.json")
            plan = baseline["finalization_plan"]
            template = {"owner_class": baseline["owner_class"], "implementation_id": baseline["implementation_id"],
                        "source_recognition": {"source_solo": {"configuration": baseline["configuration"],
                            "neuron": baseline["profile_archives"][0]}, "conversion_spec": plan["conversion"]},
                        "post_tune": plan["post_tune"], "specification": plan["confirmation"],
                        "trials": plan["trials"], "thresholds": plan["thresholds"],
                        "maximum_candidates": plan["maximum_calibration_candidates"]}
            before = deepcopy(template)
            for scenario in ("fixed", "grid", "budget", "stopped", "legacy-budget"):
                name = top+"-"+scenario
                expected = load(self.root/"runs"/name/"input/job.json")
                actual = make_job(template, name, calibrate=scenario=="grid", legacy=scenario=="legacy-budget",
                                  budget=scenario in ("budget", "legacy-budget"), stopped=scenario=="stopped", **factors)
                with self.subTest(run=name):
                    self.assertEqual(actual, expected)
                    self.assertEqual(template, before)


# unittest discovers imported TestCase classes too. Keep only the N0 subclass
# in this module; the original N1 corpus retains its separate acceptance suite.
del _Base
