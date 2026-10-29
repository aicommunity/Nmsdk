"""Audit actual native owner-boundary probes; fixture tolerance is not science."""
import os
from pathlib import Path
import unittest

from Scripts.StructTrain.TimeLearner.native_evidence import audit_probe, load


class OwnerBoundaryEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("TIMELEARNER_OWNER_BOUNDARY_EVIDENCE_DIR")
        if not value:
            raise unittest.SkipTest("requires actual native owner-boundary output")
        cls.directory = Path(value)
        cls.paths = sorted(cls.directory.glob("*_posttune_owner_policy_owner_policy.json"))
        expected = {f"{topology}_{frequency}_N{mode}_posttune_owner_policy_owner_policy.json"
                    for topology in ("Classic", "Branch")
                    for frequency, mode in ((2000, 0), (2000, 1), (20000, 1))}
        if {p.name for p in cls.paths} != expected:
            raise RuntimeError("requires all six native owner-boundary cases")

    def test_primary_training_proofs_and_frozen_waveforms(self):
        for path in self.paths:
            with self.subTest(case=path.name):
                record = load(path)
                self.assertEqual(record["kind"], "native_posttune_owner_policy")
                self.assertEqual(record["schema_version"], 1)
                self.assertEqual(record["source_model"], record["restored_model"])
                self.assertIsNone(record["evaluation_verdict"])
                self.assertEqual(record["fixture_sync_tolerance"], 1)
                self.assertEqual(record["calculate_mode"], 0 if "_20000_" in path.name else 1)
                self.assertEqual(record["certificate_scope"], "learned_solo")
                certificate = record["source_solo_certificate"]
                self.assertEqual(certificate["model_revision"], record["source_model"])
                prefix = path.name.removesuffix("_owner_policy.json")
                proofs = sorted(self.directory.glob(prefix + "_training_proof_*.json"))
                self.assertTrue(proofs)
                packets = {}
                for proof in proofs:
                    packet = load(proof)
                    audit_probe(packet, proof.with_suffix(".csv"))
                    trial = packet["observation"]["specification"]["trial_id"]
                    self.assertNotIn(trial, packets)
                    packets[trial] = packet
                # Prove that the certificate refers to actual recorded final
                # trials. Full convergence re-derivation needs the complete
                # training summary and is outside this boundary fixture.
                residuals = certificate["residuals"]
                self.assertEqual({r["input_id"] for r in residuals}, {"input0", "input1"})
                self.assertEqual(len(residuals), 2)
                for residual in residuals:
                    packet = packets[residual["trial_id"]]
                    self.assertEqual(packet["prepared"]["input_id"], residual["input_id"])
                    self.assertEqual(packet["prepared"]["base_model_revision"], record["source_model"])
                    self.assertEqual(packet["prepared"]["effective_model_revision"], residual["effective_model_revision"])
                waves = sorted(self.directory.glob(prefix + "_probe_*_evidence.json"))
                self.assertEqual(len(waves), 2)
                traces = []
                for wave in waves:
                    trace = wave.with_name(wave.name.replace("_evidence.json", ".csv"))
                    audit = audit_probe(load(wave), trace)
                    self.assertTrue(audit)
                    traces.append(trace.read_bytes())
                self.assertEqual(traces[0], traces[1])

    def test_changed_reference_provenance_is_a_corruption_control(self):
        paths = list(self.directory.glob("*_posttune_owner_provenance_provenance_guard.json"))
        self.assertEqual(len(paths), 1)
        record = load(paths[0])
        self.assertEqual(record["kind"], "native_boundary_reference_provenance_guard")
        self.assertEqual(record["schema_version"], 1)
        self.assertTrue(record["metadata_corruption_control"])
        self.assertNotEqual(record["previous_reference_trial"], record["new_reference_trial"])
        self.assertEqual(record["reason"], "posttune_boundary_training_controller_changed")
        self.assertIsNone(record["evaluation_verdict"])
        proofs = list(self.directory.glob("*_posttune_owner_provenance_training_proof_*.json"))
        self.assertTrue(proofs)
        trials = set()
        for proof in proofs:
            packet = load(proof)
            audit_probe(packet, proof.with_suffix(".csv"))
            trial = packet["observation"]["specification"]["trial_id"]
            self.assertNotIn(trial, trials)
            trials.add(trial)
        self.assertIn(record["previous_reference_trial"], trials)
        self.assertNotIn(record["new_reference_trial"], trials)


if __name__ == "__main__":
    unittest.main()
