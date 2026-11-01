"""Lossless compact archives from actual native runs; no new model calculations."""
import gzip
import hashlib
import io
import json
import os
import shutil
import tarfile
import tempfile
import unittest
from pathlib import Path

from ..artifact_bundle import pack_native_tests, verify_bundle, extract_bundle
from ..native_evidence import EvidenceError, load
from ..native_test_reports import inventory_native_test_run


class ArtifactBundleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = os.environ.get("TIMELEARNER_BUNDLE_ARTIFACTS")
        report = os.environ.get("TIMELEARNER_BUNDLE_SELECTED_REPORT")
        if not source or not report:
            raise unittest.SkipTest("requires actual native A3 data and source-bound selected figures")
        cls.source = Path(source); cls.report = Path(report)
        cls.contract = Path(__file__).parents[1]/"specs/repeat-boundary-native-v1.json"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="tl-primary-bundle-")
        self.addCleanup(self.temp.cleanup); self.root = Path(self.temp.name)

    def pack(self, name="bundle"):
        out = self.root/name
        pack_native_tests(self.contract, self.source, out, self.report)
        return out

    def test_actual_roundtrip_retains_every_primary_byte_and_complete_expected_set(self):
        bundle = self.pack(); restored = self.root/"restored"
        extract_bundle(bundle, restored)
        manifest = verify_bundle(bundle)
        original = inventory_native_test_run(self.contract, self.source)
        replay = inventory_native_test_run(restored/"contract.json", restored)
        self.assertEqual(replay, original)
        self.assertEqual(replay["trials"], 338)
        for path in (self.source/"native").iterdir():
            self.assertEqual(path.read_bytes(), (restored/"native"/path.name).read_bytes(), path.name)
        self.assertEqual(len(manifest["selected_figures"]), 6)
        self.assertEqual(len(list(bundle.rglob("*.png"))), 6)
        self.assertFalse(list(bundle.rglob("*.pdf"))); self.assertFalse(list(bundle.rglob("*.svg")))
        self.assertFalse(list(restored.rglob("*.png")))
        self.assertIsNone(manifest["scientific_verdict"])

    def test_archive_is_deterministic_and_existing_output_is_preserved(self):
        first, second = self.pack("one"), self.pack("two")
        self.assertEqual((first/"primary.tar.gz").read_bytes(), (second/"primary.tar.gz").read_bytes())
        self.assertEqual(load(first/"manifest.json"), load(second/"manifest.json"))
        before = (first/"manifest.json").read_bytes()
        with self.assertRaises(FileExistsError): self.pack("one")
        self.assertEqual((first/"manifest.json").read_bytes(), before)

    def test_damaged_archive_rejects_before_any_extracted_output(self):
        bundle = self.pack(); archive = bundle/"primary.tar.gz"
        data = bytearray(archive.read_bytes()); data[len(data)//2] ^= 1; archive.write_bytes(data)
        with self.assertRaisesRegex(EvidenceError, "archive_checksum"):
            extract_bundle(bundle, self.root/"bad")
        self.assertFalse((self.root/"bad").exists())

    def test_manifest_traversal_and_duplicate_paths_reject_before_extraction(self):
        bundle = self.pack(); original = load(bundle/"manifest.json")
        for name in ("../escape", "/absolute", "native/../escape", "C:/escape", "native\\escape"):
            value = json.loads(json.dumps(original)); value["files"][0]["path"] = name
            (bundle/"manifest.json").write_text(json.dumps(value))
            with self.assertRaises(EvidenceError): extract_bundle(bundle, self.root/"bad")
            self.assertFalse((self.root/"bad").exists())
        value = original; value["files"].append(value["files"][0])
        (bundle/"manifest.json").write_text(json.dumps(value))
        with self.assertRaises(EvidenceError): extract_bundle(bundle, self.root/"bad")
        self.assertFalse((self.root/"bad").exists())

    def test_archive_links_are_rejected_even_with_updated_outer_checksum(self):
        bundle = self.pack(); archive = bundle/"primary.tar.gz"
        changed = self.root/"changed.tar.gz"
        with tarfile.open(archive, "r:gz") as source, tarfile.open(changed, "w:gz") as target:
            for index, member in enumerate(source):
                if index == 0:
                    bad = tarfile.TarInfo(member.name); bad.type = tarfile.SYMTYPE; bad.linkname = "../escape"
                    target.addfile(bad)
                else:
                    with source.extractfile(member) as stream: target.addfile(member, stream)
        shutil.copyfile(changed, archive)
        value = load(bundle/"manifest.json")
        value["archive"].update(bytes=archive.stat().st_size, sha256=hashlib.sha256(archive.read_bytes()).hexdigest())
        (bundle/"manifest.json").write_text(json.dumps(value))
        with self.assertRaisesRegex(EvidenceError, "unexpected_primary_archive_member"):
            extract_bundle(bundle, self.root/"bad")
        self.assertFalse((self.root/"bad").exists())

    def test_selected_image_corruption_is_not_hidden_by_valid_raw_archive(self):
        bundle = self.pack(); path = next((bundle/"selected").glob("*.png"))
        path.write_bytes(b"damaged figure")
        with self.assertRaisesRegex(EvidenceError, "selected_figure_checksum"):
            extract_bundle(bundle, self.root/"bad")
        self.assertFalse((self.root/"bad").exists())

    def test_declared_extraction_budget_rejects_before_output(self):
        bundle = self.pack()
        with self.assertRaisesRegex(EvidenceError, "extraction_budget"):
            extract_bundle(bundle, self.root/"bad", maximum_bytes=1)
        self.assertFalse((self.root/"bad").exists())

    def test_pack_honors_explicit_byte_budget_before_creating_output(self):
        with self.assertRaisesRegex(EvidenceError, "extraction_budget"):
            pack_native_tests(self.contract, self.source, self.root/"bad", self.report, maximum_bytes=1)
        self.assertFalse((self.root/"bad").exists())

    def test_metadata_only_corruption_cannot_hide_behind_unchanged_archive(self):
        bundle = self.pack(); value = load(bundle/"manifest.json")
        value["inventory"]["trials"] += 1
        (bundle/"manifest.json").write_text(json.dumps(value))
        with self.assertRaisesRegex(EvidenceError, "bundle_file_checksum_mismatch"):
            extract_bundle(bundle, self.root/"bad")
        self.assertFalse((self.root/"bad").exists())

    def test_compact_archive_contains_required_model_and_runtime_records(self):
        bundle = self.pack(); manifest = verify_bundle(bundle)
        paths = {item["path"] for item in manifest["files"]}
        self.assertTrue({"contract.json", "native.xml", "runtime-before.json", "runtime-after.json", "source-closure.txt"} <= paths)
        self.assertTrue(any(p.endswith("_learned_state.json") for p in paths))
        self.assertTrue(any(p.endswith("_stopped_state.json") for p in paths))
        self.assertTrue(any(p.endswith("_warm_boundary.json") for p in paths))
        raw = sum(item["bytes"] for item in manifest["files"])
        self.assertLess((bundle/"primary.tar.gz").stat().st_size, raw)
