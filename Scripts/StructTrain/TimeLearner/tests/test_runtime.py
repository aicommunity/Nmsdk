import tempfile
import unittest
from pathlib import Path

from Scripts.StructTrain.TimeLearner.runtime import build_flags, digest_file, parse_ldd


class RuntimeProvenanceTest(unittest.TestCase):
    def test_resolved_loader_paths_and_missing_dependency(self):
        self.assertEqual(parse_ldd("libglog.so => /lib/libglog.so (0x123)\n/lib64/ld-linux.so (0x234)\n"),
                         [Path("/lib/libglog.so"), Path("/lib64/ld-linux.so")])
        with self.assertRaises(RuntimeError):
            parse_ldd("libglog.so => not found")

    def test_hash_is_content_based(self):
        with tempfile.TemporaryDirectory() as name:
            a = Path(name) / "console"
            b = Path(name) / "console.rs2"
            a.write_bytes(b"binary")
            b.write_bytes(b"binary")
            self.assertEqual(digest_file(a), digest_file(b))
            b.write_bytes(b"different")
            self.assertNotEqual(digest_file(a), digest_file(b))

    def test_cache_allowlist_does_not_collect_credentials(self):
        with tempfile.TemporaryDirectory() as name:
            path = Path(name) / "CMakeCache.txt"
            path.write_text("CMAKE_BUILD_TYPE:STRING=Release\nAPI_PASSWORD:STRING=secret\n", encoding="utf-8")
            self.assertEqual(build_flags(path), {"CMAKE_BUILD_TYPE": "Release"})


if __name__ == "__main__":
    unittest.main()
