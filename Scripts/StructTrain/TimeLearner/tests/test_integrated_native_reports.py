"""CI163 observability debt on real immutable native output, not fake probes."""
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from ..native_evidence import EvidenceError, load
from ..native_test_reports import inventory_native_test_run


class IntegratedNativeReportsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("TIMELEARNER_INTEGRATED_REPORT_DIR")
        if not value:
            raise unittest.SkipTest("requires immutable root07167 CI163 output")
        cls.source = Path(value)
        cls.contract = Path(__file__).parents[1]/"specs/integrated-wall-search-report-v2.json"

    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="tl-integrated-report-")
        self.addCleanup(temp.cleanup)
        self.directory = Path(temp.name)
        self.spec = self.directory/"spec.json"
        shutil.copyfile(self.contract, self.spec)

    def write_spec(self, value):
        self.spec.write_text(json.dumps(value), encoding="utf-8")

    def copied_run(self):
        run = self.directory/"run"
        shutil.copytree(self.source/"native", run/"native")
        shutil.copyfile(self.source/"native.xml", run/"native.xml")
        return run

    def test_all_packets_and_csvs_accounted_with_explicit_debt(self):
        result = inventory_native_test_run(self.spec, self.source)
        self.assertEqual(result["tests"], 163)
        self.assertEqual(result["trials"], 407)
        self.assertEqual(result["primary_packet_count"], 413)
        self.assertEqual(len(result["untraced"]), 6)
        self.assertEqual(len(result["observability_gaps"]), 5)
        self.assertFalse(result["data_complete"])
        self.assertFalse(result["visual_acceptance_complete"])
        self.assertIsNone(result["scientific_verdict"])
        self.assertTrue(all(not r["trace_checked"] and not r["data_complete"] for r in result["untraced"]))

    def test_untraced_packet_cannot_be_silently_omitted(self):
        spec = load(self.spec); spec["untraced"].pop(); self.write_spec(spec)
        with self.assertRaisesRegex(EvidenceError, "unaccounted_or_missing_primary_packet"):
            inventory_native_test_run(self.spec, self.source)

    def test_untraced_requires_a_reason_and_cannot_duplicate_traced_packet(self):
        spec = load(self.spec); spec["untraced"][0]["reason"] = ""; self.write_spec(spec)
        with self.assertRaisesRegex(EvidenceError, "invalid_native_test_untraced"):
            inventory_native_test_run(self.spec, self.source)
        spec = load(self.contract)
        spec["untraced"][0].update(packet=spec["standalone"][0]["packet"], json_pointer="")
        self.write_spec(spec)
        with self.assertRaisesRegex(EvidenceError, "duplicate_native_test_source"):
            inventory_native_test_run(self.spec, self.source)

    def test_missing_untraced_file_is_not_a_documentary_excuse(self):
        run = self.copied_run()
        (run/"native"/load(self.spec)["untraced"][0]["packet"]).unlink()
        with self.assertRaises(FileNotFoundError):
            inventory_native_test_run(self.spec, run)

    def test_gap_must_reference_a_real_expected_case_once(self):
        spec = load(self.spec); spec["observability_gaps"][0]["test_id"] = "Invented/Case"; self.write_spec(spec)
        with self.assertRaisesRegex(EvidenceError, "invalid_native_test_observability_gap"):
            inventory_native_test_run(self.spec, self.source)
        spec = load(self.contract); spec["observability_gaps"].append(spec["observability_gaps"][0]); self.write_spec(spec)
        with self.assertRaisesRegex(EvidenceError, "invalid_native_test_observability_gap"):
            inventory_native_test_run(self.spec, self.source)

    def test_equal_alias_is_not_an_independent_measurement_and_changed_alias_fails(self):
        run = self.copied_run(); spec = load(self.spec)
        original = spec["standalone"][0]["packet"]
        target = run/"native/documented-alias.json"
        shutil.copyfile(run/"native"/original, target)
        spec["packet_aliases"] = [{"packet": target.name, "of_packet": original}]; self.write_spec(spec)
        result = inventory_native_test_run(self.spec, run)
        self.assertEqual(result["trials"], 407)
        self.assertEqual(result["primary_packet_count"], 413)
        self.assertFalse(result["packet_aliases"][0]["independent_measurement"])
        value = load(target); value["reasons"].append("changed_copy"); target.write_text(json.dumps(value))
        with self.assertRaisesRegex(EvidenceError, "native_test_alias_packet_mismatch"):
            inventory_native_test_run(self.spec, run)

    def test_alias_cannot_hide_an_unrelated_packet_or_an_alias_chain(self):
        run = self.copied_run(); spec = load(self.spec)
        original = spec["standalone"][0]["packet"]
        for name in ("alias-a.json", "alias-b.json"):
            shutil.copyfile(run/"native"/original, run/"native"/name)
        spec["packet_aliases"] = [{"packet": "alias-a.json", "of_packet": original},
                                   {"packet": "alias-b.json", "of_packet": "alias-a.json"}]
        self.write_spec(spec)
        with self.assertRaisesRegex(EvidenceError, "native_test_alias_target_not_primary"):
            inventory_native_test_run(self.spec, run)
