"""Native stage-boundary rollback controls consume complete production probe data."""
import csv
import json
import os
from pathlib import Path
import unittest

from Scripts.StructTrain.TimeLearner.native_evidence import audit_probe, load


class BoundaryEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("TIMELEARNER_BOUNDARY_EVIDENCE_DIR")
        if not value:
            raise unittest.SkipTest("requires actual native graph-boundary controls")
        cls.directory = Path(value)
        cls.paths = sorted(cls.directory.glob("*_posttune_boundary*_boundary.json"))
        if len(cls.paths) != 10:
            raise RuntimeError("requires eight topology/mode/rate cases and both attachment failures")

    def test_complete_probe_evidence_and_exact_replay(self):
        total = 0
        for path in self.paths:
            with self.subTest(case=path.name):
                record = load(path)
                self.assertEqual(record["kind"], "native_posttune_graph_boundary")
                self.assertEqual(record["schema_version"], 1)
                self.assertEqual(record["source_identity"], record["restored_identity"])
                self.assertTrue(record["source_identity"]["valid"])
                self.assertFalse(record["controller_checkpoint"])
                self.assertIsNone(record["scientific_verdict"])
                prefix = path.name.removesuffix("_boundary.json")
                files = sorted(self.directory.glob(prefix + "_probe_*_evidence.json"))
                self.assertEqual(len(files), 2)
                traces = []
                for packet_path in files:
                    trace = packet_path.with_name(packet_path.name.replace("_evidence.json", ".csv"))
                    audit_probe(load(packet_path), trace)
                    with trace.open(newline="", encoding="utf-8") as stream:
                        rows = list(csv.DictReader(stream))
                    self.assertEqual(len(rows), record["sample_pairs"])
                    traces.append(trace.read_bytes())
                self.assertEqual(traces[0], traces[1])
                total += record["sample_pairs"]
        self.assertGreater(total, 0)

    def test_declared_matrix_and_failure_controls_are_present(self):
        records = [load(path) for path in self.paths]
        normal = {(r["branch"], r["normalization"], r["frequency_hz"])
                  for r in records if not r["injected_attach_failure"]}
        self.assertEqual(normal, {(branch, mode, frequency) for branch in (False, True)
                                  for mode in (0, 1) for frequency in (2000, 20000)})
        self.assertEqual({r["branch"] for r in records if r["injected_attach_failure"]}, {False, True})
