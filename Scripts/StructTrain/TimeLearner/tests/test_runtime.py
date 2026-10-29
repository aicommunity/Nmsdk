import copy
import tempfile
import unittest
from pathlib import Path

from Scripts.StructTrain.TimeLearner.runtime import build_flags, digest_file, parse_ldd, digest_json, runtime_content_identity


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



class RuntimeContentIdentityTest(unittest.TestCase):
    def manifest(self):
        return {"schema_version": 2, "executable": {"path": "/a/console", "sha256": "a"*64},
                "app_ini": {"path": "/a/app.ini", "sha256": "b"*64},
                "compiler": {"path": "/a/g++", "sha256": "c"*64},
                "build_flags": {"CMAKE_CXX_COMPILER": "/a/g++", "NMSDK_DEPLOY_ROOT": "/a/runtime",
                                "NMSDK_RESOURCE_ROOT": "/a/resources", "CMAKE_CXX_FLAGS": "-O2"},
                "resolved_libraries": [{"path": "/a/lib.so", "sha256": "d"*64}],
                "loaded_process_files": None}

    def test_relocation_suffix_and_compiler_path_do_not_change_identity(self):
        original = self.manifest(); moved = copy.deepcopy(original)
        for name in ("executable", "app_ini", "compiler"):
            moved[name]["path"] = "/b/" + name + ".rs2"
        for key in ("CMAKE_CXX_COMPILER", "NMSDK_DEPLOY_ROOT", "NMSDK_RESOURCE_ROOT"):
            moved["build_flags"][key] = "/b/" + key
        moved["resolved_libraries"][0]["path"] = "/b/lib.so"
        self.assertEqual(runtime_content_identity(original), runtime_content_identity(moved))
        self.assertEqual(original["build_flags"]["NMSDK_DEPLOY_ROOT"], "/a/runtime")

    def test_content_and_semantic_flags_remain_significant(self):
        original = self.manifest(); before = digest_json(runtime_content_identity(original))
        for field in ("executable", "app_ini", "compiler"):
            changed = copy.deepcopy(original); changed[field]["sha256"] = "f"*64
            self.assertNotEqual(before, digest_json(runtime_content_identity(changed)))
        changed = copy.deepcopy(original); changed["build_flags"]["CMAKE_CXX_FLAGS"] = "-O3"
        self.assertNotEqual(before, digest_json(runtime_content_identity(changed)))

    def test_mapping_snapshot_is_not_equated_with_unknown_mappings(self):
        original = self.manifest(); known = copy.deepcopy(original)
        known["loaded_process_files"] = [{"path": "/a/plugin", "sha256": "e"*64}]
        self.assertNotEqual(runtime_content_identity(original), runtime_content_identity(known))
        moved = copy.deepcopy(known); moved["loaded_process_files"][0]["path"] = "/b/plugin"
        self.assertEqual(runtime_content_identity(known), runtime_content_identity(moved))


if __name__ == "__main__":
    unittest.main()
