"""Archive inclusion checks on original complete production run snapshots."""
import copy
import json
import os
from pathlib import Path
import unittest

from ..artifact_bundle import verify_packaged_run_closure
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, parse_json_bytes


class PackagedRunClosureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("TIMELEARNER_ARCHIVE_RUN_SOURCE")
        if not value:
            raise unittest.SkipTest("requires both actual owned production run directories")
        root = Path(value)
        cls.files = {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}
        cls.manifests = [p for p in cls.files if p.endswith("/run-manifest.json")]
        if len(cls.manifests) != 2:
            raise RuntimeError("requires both actual Classic and Branch snapshots")

    def test_complete_snapshots_preserve_both_internal_run_closures(self):
        result = verify_packaged_run_closure(self.files)
        self.assertEqual(result["run_snapshots_verified"], 2)
        self.assertEqual(result["artifact_entries_verified"], len(self.files)-2)
        self.assertIsNone(result["scientific_verdict"])

    def test_code_cache_filter_cannot_remove_primary_source_directories(self):
        missing = {p: raw for p, raw in self.files.items() if "/input/source/" not in p}
        self.assertLess(len(missing), len(self.files))
        with self.assertRaisesRegex(EvidenceError, "packaged_run_missing_artifact"):
            verify_packaged_run_closure(missing)

    def test_corrupted_and_unrecorded_files_reject(self):
        path = next(p for p in self.files if p.endswith(".csv"))
        damaged = dict(self.files);damaged[path] += b"damaged"
        with self.assertRaisesRegex(EvidenceError, "packaged_run_artifact_bytes_changed"):
            verify_packaged_run_closure(damaged)
        extra = dict(self.files);extra[self.manifests[0].removesuffix("run-manifest.json")+"unregistered.txt"] = b"extra"
        with self.assertRaisesRegex(EvidenceError, "packaged_run_has_unrecorded_artifacts"):
            verify_packaged_run_closure(extra)

    def test_duplicate_traversal_and_unknown_manifest_schema_reject(self):
        name = self.manifests[0];original = parse_json_bytes(self.files[name])
        for change in ("duplicate", "traversal", "schema"):
            value = copy.deepcopy(original)
            if change == "duplicate":value["artifacts"].append(value["artifacts"][0])
            elif change == "traversal":value["artifacts"][0]["path"] = "../escape"
            else:value["schema_version"] = 999
            value["sha256"] = sha({k: v for k, v in value.items() if k != "sha256"})
            files = dict(self.files);files[name] = json.dumps(value).encode()
            with self.subTest(change=change), self.assertRaises(EvidenceError):
                verify_packaged_run_closure(files)
        with self.assertRaisesRegex(EvidenceError, "duplicate_json_key"):
            parse_json_bytes(b'{"source":1,"source":2}')
        with self.assertRaisesRegex(EvidenceError, "nonfinite_json_token"):
            parse_json_bytes(b'{"value":NaN}')
