"""Corrupt real native transfer artifacts; no fabricated positive fixture."""
import copy
import json
import os
from pathlib import Path
import shutil
import struct
import tempfile
import unittest
import xml.etree.ElementTree as ET

from ..archive_transfer_reports import audit_run, read_case
from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError


class ArchiveTransferReports(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(os.environ["TL_ARCHIVE_TRANSFER_SOURCE"])
        cls.stem = "matrix-precise-boundary"
        cls.source = cls.stem+"-fixture-2000.json"
        cls.child = cls.stem+"-import-verification-2000.json"

    def test_actual_native_corpus(self):
        rows, summary = audit_run(self.root)
        self.assertEqual(len(rows), 12);self.assertEqual(summary["case_soma_pairs"], 12)
        self.assertIsNone(summary["scientific_verdict"]);self.assertIsNone(summary["training_certificate"])
        self.assertEqual(sum(v["summary"]["precise_matrix"] for v in rows.values()), 4)

    def corrupt(self, change, reason):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            for name in (self.source, self.child):shutil.copyfile(self.root/"artifacts"/name, p/name)
            change(p)
            with self.assertRaisesRegex(EvidenceError, reason):read_case(p, self.stem, True, 2000, True, True)

    def edit(self, name, change, reason):
        def mutate(p):
            f = p/name;value = json.loads(f.read_text());change(value);f.write_text(json.dumps(value))
        self.corrupt(mutate, reason)

    def test_unknown_schema(self):
        self.edit(self.source, lambda x:x.update(schema_version=9), "unknown_fixture_schema")

    def test_incomplete_source(self):
        self.edit(self.source, lambda x:x.update(complete=False), "incomplete_window")

    def test_incomplete_child(self):
        self.edit(self.child, lambda x:x.update(complete=False), "incomplete_window")

    def test_short_window(self):
        self.edit(self.source, lambda x:x.update(window_end_s=.05), "incomplete_window")

    def test_nonfinite_soma(self):
        self.edit(self.child, lambda x:x["soma"].__setitem__(30, float("nan")), "nonfinite_json_token")

    def test_duplicate_json_key(self):
        def mutate(p):
            f = p/self.source;f.write_text('{"complete":true,'+f.read_text().lstrip()[1:])
        self.corrupt(mutate, "duplicate_json_key")

    def test_short_grid(self):
        self.edit(self.child, lambda x:x["time_s"].pop(), "incomplete_grid")

    def test_changed_native_clock(self):
        self.edit(self.source, lambda x:x["time_s"].__setitem__(30, .0151), "native_clock")

    def test_changed_actual_input(self):
        self.edit(self.child, lambda x:x["actual_input"].__setitem__(10, 0), "actual_input")

    def test_changed_soma(self):
        self.edit(self.child, lambda x:x["soma"].__setitem__(30, x["soma"][30]+.001), "response_changed")

    def test_changed_channel(self):
        self.edit(self.child, lambda x:x["waveform"].__setitem__(30, x["waveform"][30]+.001), "response_changed")

    def test_forged_error_summary(self):
        self.edit(self.child, lambda x:x.update(max_soma_pairwise_error=.01), "error_summary")

    def test_flat_soma(self):
        def mutate(p):
            for name in (self.source, self.child):
                f = p/name;x = json.loads(f.read_text());x["soma"] = [0.]*200;f.write_text(json.dumps(x))
        self.corrupt(mutate, "flat_soma")

    def test_changed_xml(self):
        self.edit(self.source, lambda x:x["archive"]["graph"].update(native_xml="<bad/>"), "archive_digest")

    def test_changed_import_identity(self):
        self.edit(self.child, lambda x:x["identity"].update(sha256="0"*64), "identity_digest")

    def test_nonfinite_encoded_parameter_even_when_resealed(self):
        def mutate(x):
            archive = x["archive"];identity = archive["graph"]["identity"]
            node = next(n for n in identity["model"]["nodes"] if n["path"] == "$.Dendrite2_3.ExcChannel")
            node["parameters"]["Capacity"]["data"]["value"] = "7ff8000000000000"
            identity["sha256"] = canonical_model_sha256(identity["model"])
            archive["sha256"] = canonical_model_sha256({k:v for k,v in archive.items() if k != "sha256"})
        self.edit(self.source, mutate, "nonfinite_parameter")

    def test_changed_matrix_even_when_both_identities_resealed(self):
        def mutate(p):
            f = p/self.source;x = json.loads(f.read_text());archive = x["archive"]
            identity = archive["graph"]["identity"]
            node = next(n for n in identity["model"]["nodes"] if n["path"] == "$")
            node["parameters"]["TrainingPattern"]["data"]["value"][0][0] = struct.pack(">d", .00123457).hex()
            identity["sha256"] = canonical_model_sha256(identity["model"])
            archive["sha256"] = canonical_model_sha256({k:v for k,v in archive.items() if k != "sha256"})
            f.write_text(json.dumps(x));f = p/self.child;y = json.loads(f.read_text())
            y["identity"] = copy.deepcopy(identity);f.write_text(json.dumps(y))
        self.corrupt(mutate, "reference_matrix_changed")

    def test_missing_primary(self):
        self.corrupt(lambda p:(p/self.child).unlink(), "missing_or_unreadable_artifact")

    def corrupt_run(self, change, reason):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/"run";shutil.copytree(self.root, p);change(p)
            with self.assertRaisesRegex(EvidenceError, reason):audit_run(p)

    def test_failed_execution(self):
        def mutate(p):
            f = p/"validation.json";x = json.loads(f.read_text());x["execution"]["returncode"] = 1
            f.write_text(json.dumps(x))
        self.corrupt_run(mutate, "native_tests_failed")

    def test_duplicate_native_condition(self):
        def mutate(p):
            f = p/"gtest.xml";tree = ET.parse(f);nodes = tree.findall(".//testcase")
            nodes[-1].attrib.update(nodes[-2].attrib);tree.write(f,encoding="utf-8")
        self.corrupt_run(mutate, "test_condition_set")

    def test_missing_expected_case(self):
        self.corrupt_run(lambda p:(p/"artifacts"/self.child).unlink(), "artifact_set")

    def test_unknown_artifact(self):
        self.corrupt_run(lambda p:(p/"artifacts/extra.json").write_text("{}"), "artifact_set")


if __name__ == "__main__":unittest.main()
