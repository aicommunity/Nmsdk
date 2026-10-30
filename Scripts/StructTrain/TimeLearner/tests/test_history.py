"""Actual filtered history aliases; no model calculations."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from ..history import resolve_revision
from ..native_evidence import EvidenceError

class RootHistoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p=os.environ.get("NMSDK_FILTERED_HISTORY_ROOT")
        if not p:raise unittest.SkipTest("requires actual validated filtered root history")
        cls.root=Path(p)

    def test_actual_rewritten_root_resolves_to_available_commit(self):
        r=resolve_revision(self.root,"243778a0b51c77e4014459f7e8d7feac4ee5601c")
        self.assertEqual(r["resolved_revision"],"12c1192b89fe4af4f6d356114e61316489e43b71")
        self.assertTrue(r["rewritten"]);self.assertIsNone(r["scientific_verdict"])

    def test_original_august_anchor_is_unchanged(self):
        old="de02a3809395dd0bbd11e2ba792bfc04a51c89f3"
        r=resolve_revision(self.root,old)
        self.assertEqual(r["resolved_revision"],old);self.assertFalse(r["rewritten"])

    def test_short_or_shell_like_revision_is_rejected(self):
        for old in ("243778a","HEAD","../other","0"*40+";cmd"):
            with self.assertRaisesRegex(EvidenceError,"full_commit_sha_required"):
                resolve_revision(self.root,old)

    def test_unknown_revision_is_explicitly_unavailable(self):
        with self.assertRaisesRegex(EvidenceError,"mapped_revision_not_available"):
            resolve_revision(self.root,"f"*40)

    def test_corrupt_map_schema_and_target_are_not_used(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"map.json"
            for value in ({"kind":"nmsdk_root_revision_aliases","schema_version":True,"mapping":{}},
                          {"kind":"nmsdk_root_revision_aliases","schema_version":1,"mapping":{"0"*40:"HEAD"}}):
                path.write_text(json.dumps(value))
                with self.assertRaises(EvidenceError):resolve_revision(self.root,"0"*40,path)
