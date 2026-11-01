"""N0 production acceptance uses real Console results, including repeat schema2.

Inherits the complete fourteen-operation closure and corruption checks. Merely
changing the declaration is insufficient: persisted Train summaries and exported
models must confirm the selected normalization and physical candidate domain.
"""
from copy import deepcopy

from ..native_evidence import EvidenceError, load
from .live_pipeline_corpus import make_job
from .test_live_pipeline_worker import LivePipelineWorkerTest as _Base


class N0LivePipelineWorkerTest(_Base):
    corpus_environment = "TIMELEARNER_N0_LIVE_PIPELINE_CORPUS"

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


# unittest discovers imported TestCase classes too. Keep only the N0 subclass
# in this module; the original N1 corpus retains its separate acceptance suite.
del _Base
