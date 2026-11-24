"""Check scientific case coverage and extraction rather than XML formatting."""
import importlib.util
import json
import contextlib
import io
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("classic_prepare", ROOT / "prepare.py")
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)
evaluation_spec = importlib.util.spec_from_file_location("classic_evaluate", ROOT / "evaluate.py")
evaluation = importlib.util.module_from_spec(evaluation_spec)
evaluation_spec.loader.exec_module(evaluation)


class ArchiveEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = prepare.extract_evidence()
        cls.manifest = json.loads((prepare.CONFIGS / "Prepared/manifest.json").read_text(encoding="utf-8"))

    def test_dataset_order_and_class_sizes(self):
        data = self.evidence["dataset"]
        self.assertEqual([s["id"] for s in data], list(range(1, 151)))
        self.assertEqual([sum(s["class"] == c for s in data) for c in (1, 2, 3)], [50]*3)
        self.assertTrue(all(len(s["pattern"]) == 5 and s["pattern"][4] == .2 for s in data))

    def test_each_directed_transition_occurs_once(self):
        ids = self.manifest["selected_ids"]
        sequence = self.manifest["warm_sequence"]
        pairs = [(a["id"], b["id"]) for a, b in zip(sequence, sequence[1:])]
        self.assertEqual(len(pairs), 90)
        self.assertEqual(set(pairs), {(a, b) for a in ids for b in ids if a != b})

    def test_training_references_are_complete(self):
        self.assertEqual(len(self.evidence["cold"]), 60)
        self.assertEqual(len(self.evidence["warm"]), 270)
        for repeat in (1, 2, 3):
            self.assertEqual(sum(x["repeat"] == repeat for x in self.evidence["cold"]), 20)
            self.assertEqual(sum(x["repeat"] == repeat for x in self.evidence["warm"]), 90)

    def test_recognition_has_exactly_150_binary_answers(self):
        self.assertEqual(len(self.evidence["recognition"]), 22)
        for model in self.evidence["recognition"]:
            self.assertEqual(len(model["answers"]), 150)
            self.assertTrue(all(a in (0, 1) for a in model["answers"]))

    def test_missing_baselines_are_not_filled(self):
        self.assertTrue(any(x["synapses"] is None for x in self.evidence["structural"]))
        self.assertTrue(any(any(isinstance(v, str) for v in x["raw_synapses"]) for x in self.evidence["structural"]))

    def test_verbatim_configuration_hashes(self):
        self.assertEqual(len(self.manifest["verbatim_configs"]), 22)
        for item in self.manifest["verbatim_configs"]:
            self.assertEqual(prepare.sha(prepare.CONFIGS / item["path"]), item["sha256"])

    def test_imbalanced_accuracy_is_distinct_from_balanced_accuracy(self):
        m = evaluation.metrics([1, 0, 0, 0, 0, 1], [1, 1, 2, 2, 2, 2], 1)
        self.assertEqual([m[k] for k in ["TP", "FP", "FN", "TN"]], [1, 1, 1, 3])
        self.assertAlmostEqual(m["accuracy"], 4/6)
        self.assertAlmostEqual(m["balanced_accuracy"], .625)
        self.assertAlmostEqual(m["empirical_risk"], 2/6)

    def test_missing_or_extra_recognition_answers_are_rejected(self):
        with self.assertRaises(ValueError):
            evaluation.metrics([1, 0, 1], [1, 2], 1)

    def test_frozen_variants_are_traceable_to_measurements(self):
        variants = self.manifest["recognition_frozen"]
        self.assertEqual(len(variants), 4)
        self.assertEqual({(v["kind"], v["id"]) for v in variants}, {("trainer", 64), ("learner", 129)})

    def test_all_recognition_variants_have_their_own_structure_reference(self):
        models = self.manifest["recognition_models"]
        self.assertEqual(len(models), 22)
        for index, model in enumerate(models):
            reference = self.evidence["recognition"][index]
            self.assertEqual(model["variant_index"], index)
            self.assertEqual((model["kind"], model["id"], model["recognition_variant"]),
                             (reference["kind"], reference["id"], reference["variant"]))
            self.assertIn(model["dendrites"], [r["dendrites"] for r in self.evidence["cold"]
                                             if r["id"] == model["id"] and r["kind"] == model["kind"]])

    def test_accounted_failures_are_distinct_from_success(self):
        with tempfile.TemporaryDirectory(prefix="classic-evidence-test-") as temp:
            run = Path(temp)
            job = run / "warm-r1"
            job.mkdir()
            process = {"suite": "warm", "repeat": 1, "status": "completed", "command": []}
            (job / "process.json").write_text(json.dumps(process), encoding="utf-8")
            (run / "run.json").write_text(json.dumps({"jobs": [process]}), encoding="utf-8")
            records = [{"suite": "warm", "repeat": 1, "case": f"transition-{i}", "status": "not_run_precondition",
                        "reason": "Previous model did not finish training"} for i in range(91)]
            results = job / "results.jsonl"
            results.write_text("\n".join(map(json.dumps, records))+"\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                complete = evaluation.evaluate(run)
            self.assertTrue(complete["all_expected_cases_recorded"])
            self.assertFalse(complete["all_experiments_completed"])
            results.write_text("\n".join(map(json.dumps, records[:-1]))+"\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                missing = evaluation.evaluate(run)
            self.assertFalse(missing["all_expected_cases_recorded"])
            self.assertTrue(any("transition-90" in error for error in missing["coverage_errors"]))

    def test_answer_diagnostics_are_variant_specific_and_secondary(self):
        reference = {"id": 64, "kind": "trainer", "variant": "NT(8)", "answers": [0]*150}
        alternative = {**reference, "variant": "NT(9)", "answers": [1]+[0]*149}
        record = {"suite": "recognition", "id": 64, "kind": "trainer", "status": "completed",
                  "frozen_archive_structure": True, "reference": {"recognition_variant": "NT(8)"},
                  "answers": alternative["answers"]}
        classification, _ = evaluation.compare(record, {"recognition": [reference, alternative]})
        diagnostic = evaluation.recognition_diagnostics(record, {"recognition": [reference, alternative]})
        self.assertEqual(classification, "recorded")
        self.assertEqual(diagnostic["answer_mismatches_min"], 1)
        self.assertFalse(diagnostic["answer_exact_match"])

    def test_iteration_difference_does_not_change_structure_acceptance(self):
        reference = {"id": 22, "kind": "learner", "dendrites": [17, 7, 19, 19, 1], "synapses": [28, 15, 30, 30, 1], "iterations": 33}
        record = {**reference, "suite": "cold", "repeat": 1, "status": "completed", "iterations": 34}
        classification, _ = evaluation.compare(record, {"cold": [reference]})
        details = evaluation.structure_details(record, {"cold": [reference]})
        self.assertEqual(classification, "match")
        self.assertTrue(details["final_structure_match"])
        self.assertEqual(details["structure_stage"], "final_trained")
        record["status"] = "uninitialized_dynamic_structure"
        partial = evaluation.structure_details(record, {"cold": [reference]})
        self.assertEqual(partial["structure_stage"], "intermediate_at_stop")
        self.assertIsNone(partial["final_structure_match"])


if __name__ == "__main__":
    unittest.main()
