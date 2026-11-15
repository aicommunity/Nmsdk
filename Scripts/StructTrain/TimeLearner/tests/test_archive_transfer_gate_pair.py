"""Validate reports against real closed native pairs, then corrupt evidence."""
import json
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

from ..archive_transfer_reports import audit_gate_pair
from ..native_evidence import EvidenceError


class ArchiveTransferGatePair(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(os.environ["TL_NATIVE_ARCHIVE_GATE_PAIR"])

    def test_actual_native_pair(self):
        data, report = audit_gate_pair(self.root)
        self.assertEqual(len(data), 2)
        self.assertEqual({v["summary"]["frequency_hz"] for v in data.values()}, {2000, 20000})
        self.assertEqual(report["case_soma_pairs"], 2)
        self.assertFalse(report["legacy16_admitted"])
        self.assertFalse(report["whole_parent_cohort_admitted"])
        self.assertIsNone(report["scientific_verdict"])
        self.assertIsNone(report["training_certificate"])
        original = json.loads((self.root/"process/result.json").read_text())
        self.assertEqual(report["execution_validation"], original)

    def corrupt(self, change, reason):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            for name in ("result.json", "native.xml", "process/result.json"):
                (p/name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(self.root/name, p/name)
            (p/"native").mkdir()
            for frequency in (2000, 20000):
                for phase in ("fixture", "import-verification"):
                    name = f"native/telemetry-matrix-precise-boundary-{phase}-{frequency}.json"
                    shutil.copyfile(self.root/name, p/name)
            change(p)
            with self.assertRaisesRegex(EvidenceError, reason):audit_gate_pair(p)

    def edit(self, name, change, reason):
        def mutate(p):
            f = p/name;value = json.loads(f.read_text());change(value)
            f.write_text(json.dumps(value))
        self.corrupt(mutate, reason)

    def test_unknown_gate_schema(self):
        self.edit("result.json", lambda x:x.update(schema_version=9), "native_gate_not_passed")

    def test_false_green_after_process_failure(self):
        self.edit("process/result.json", lambda x:x.update(execution="timeout", returncode=-9),
                  "native_process_not_closed_or_unproven")

    def test_unclosed_process(self):
        self.edit("process/result.json", lambda x:x.update(all_processes_closed=False),
                  "native_process_not_closed_or_unproven")

    def test_missing_loaded_runtime_proof(self):
        self.edit("process/result.json", lambda x:x.update(runtime_provenance="missing"),
                  "native_process_not_closed_or_unproven")

    def test_changed_inventory_digest(self):
        self.edit("result.json", lambda x:x["inventory"].update(sha256="0"*64),
                  "native_gate_inventory_changed")

    def test_duplicate_native_condition(self):
        def mutate(p):
            f = p/"native.xml";tree = ET.parse(f);cases = list(tree.getroot().iter("testcase"))
            cases[1].attrib.update(cases[0].attrib);tree.write(f, encoding="utf-8")
        self.corrupt(mutate, "native_gate_junit_expected_set_mismatch")

    def test_skipped_native_condition(self):
        def mutate(p):
            f = p/"native.xml";tree = ET.parse(f)
            next(tree.getroot().iter("testcase")).set("result", "skipped")
            tree.write(f, encoding="utf-8")
        self.corrupt(mutate, "native_gate_skipped_or_unfinished_case")

    def test_missing_actual_probe(self):
        self.corrupt(lambda p:(p/"native/telemetry-matrix-precise-boundary-fixture-20000.json").unlink(),
                     "missing_or_unreadable_artifact")

    def test_censored_window(self):
        self.edit("native/telemetry-matrix-precise-boundary-fixture-2000.json",
                  lambda x:x.update(complete=False), "incomplete_window")


    def test_actual_cli_plots(self):
        # Retain this artifact cache in the owned worker's TMPDIR for visual
        # review. Production inputs remain read-only; no model is rerun.
        parent = Path(tempfile.mkdtemp(prefix="archive-pair-cli-"))
        output = parent/"report"
        run = subprocess.run([sys.executable, "-B", "-m",
            "Scripts.StructTrain.TimeLearner", "report", str(self.root),
            "--format", "native-archive-transfer-pair", "--output", str(output)],
            cwd=Path(__file__).resolve().parents[4],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
        (parent/"cli.stdout.log").write_bytes(run.stdout)
        (parent/"cli.stderr.log").write_bytes(run.stderr)
        self.assertEqual(run.returncode, 0, run.stderr.decode(errors="replace"))
        report = json.loads((output/"validation.json").read_text())
        self.assertEqual(report["case_soma_pairs"], 2)
        self.assertIsNone(report["scientific_verdict"])
        from PIL import Image
        for name, case in report["cases"].items():
            self.assertTrue(case["figures"])
            self.assertEqual(case["observed_soma_paths"], ["$.Soma2"])
            for figure in case["figures"]:
                png = output/name/figure["path"]
                self.assertEqual(hashlib.sha256(png.read_bytes()).hexdigest(), figure["sha256"])
                with Image.open(png) as image:
                    self.assertEqual(image.size, (figure["png_width"], figure["png_height"]))
                    self.assertGreaterEqual(image.width, 1600)
                    self.assertGreaterEqual(image.height, 800)
                self.assertFalse(figure["downsampling"])


if __name__ == "__main__":unittest.main()
