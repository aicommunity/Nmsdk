"""Server-only metadata/API regressions; synthetic text, never neural physics."""
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from .. import collector_provenance as subject
from ..native_evidence import EvidenceError


MODULE = "Scripts.StructTrain.TimeLearner.tests.test_metadata_fixture"
PATH = MODULE.replace(".", "/")+".py"
SOURCE = b"""import unittest
class First(unittest.TestCase):
    def test_alpha(self): pass
    def test_beta(self): pass
class Second(unittest.TestCase):
    def test_gamma(self): pass
"""
IDS = [MODULE+".First.test_alpha", MODULE+".First.test_beta", MODULE+".Second.test_gamma"]


@unittest.skipUnless(sys.platform == "linux", "owned Linux metadata gate required")
class CollectorInputCapabilitiesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="collector-input-capabilities-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()

    def git(self, repository, *arguments):
        return subprocess.check_output(["git", "-C", str(repository), *arguments],
            env={**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_OPTIONAL_LOCKS": "0"}, stderr=subprocess.PIPE)

    def repo(self, name="source", raw=SOURCE):
        root = self.root/name
        root.mkdir()
        self.git(root, "init", "--quiet")
        self.git(root, "config", "core.autocrlf", "false")
        path = root/PATH
        path.parent.mkdir(parents=True)
        path.write_bytes(raw)
        self.git(root, "add", "--", PATH)
        self.git(root, "-c", "user.name=MetadataFixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "--quiet", "-m", "metadata fixture "+name)
        return root, self.git(root, "rev-parse", "HEAD").decode().strip()

    def file_role(self, name="request", raw=b"original metadata", staged="request.json"):
        path = self.root/(name+".json")
        path.write_bytes(raw)
        return subject.RequiredFileRole(name, self.root, path.name, len(raw), hashlib.sha256(raw).hexdigest(),
                                        max(1, len(raw)), staged)

    def git_role(self, root, commit, raw=SOURCE, role="source"):
        oid = self.git(root, "rev-parse", commit+":"+PATH).decode().strip()
        return subject.GitInputRole(role, root, commit, commit, PATH, oid, len(raw),
                                    hashlib.sha256(raw).hexdigest(), len(raw)+1)

    def test_required_files_stage_captured_bytes_after_original_changes(self):
        role = self.file_role()
        captured = subject.capture_required_file_roles([role])
        (self.root/role.relative_path).write_bytes(b"later source is not the snapshot")
        staged = captured.materialize(self.root, self.root/"staged")
        self.assertEqual(staged["collector-file-inputs/request.json"].read_bytes(), b"original metadata")
        self.assertFalse(captured.descriptor["kernel_closure_attested"])
        self.assertFalse(captured.descriptor["test_success_attested"])

    def test_entire_manifest_is_validated_before_any_file_is_read(self):
        first = self.file_role()
        malformed = replace(first, role="other", expected_sha256="not-a-sha256")
        with patch.object(subject, "_frozen", side_effect=AssertionError("unexpected read")) as reader:
            with self.assertRaises(EvidenceError):
                subject.capture_required_file_roles([first, malformed])
            reader.assert_not_called()

    def test_missing_required_input_never_creates_a_staging_directory(self):
        role = self.file_role()
        (self.root/role.relative_path).unlink()
        with self.assertRaisesRegex(EvidenceError, "collector_required_input_unavailable"):
            subject.capture_required_file_roles([role])
        self.assertFalse((self.root/"staged").exists())

    def test_duplicate_roles_staged_aliases_and_source_aliases_fail(self):
        first = self.file_role()
        second = self.file_role("second", staged="other.json")
        for requirements in ([first, replace(second, role=first.role)],
                             [first, replace(second, staged_name="REQUEST.JSON")],
                             [first, replace(first, role="other", staged_name="other.json")]):
            with self.subTest(requirements=requirements), self.assertRaises(EvidenceError):
                subject.capture_required_file_roles(requirements)

    def test_total_size_budget_is_checked_before_partial_capture(self):
        first = self.file_role()
        second = self.file_role("second", staged="other.json")
        with patch.object(subject, "_frozen", side_effect=AssertionError("unexpected read")) as reader:
            with self.assertRaisesRegex(EvidenceError, "collector_input_total_size_budget"):
                subject.capture_required_file_roles([first, second], maximum_total_bytes=first.expected_bytes)
            reader.assert_not_called()

    def test_control_paths_and_boolean_budgets_fail_before_filesystem_reads(self):
        role = self.file_role()
        with patch.object(subject, "_frozen", side_effect=AssertionError("unexpected read")) as reader:
            for value in (replace(role, root="/tmp/\0invalid"), replace(role, relative_path="bad\nname"),
                          replace(role, expected_bytes=True), replace(role, maximum_bytes=False)):
                with self.subTest(value=value), self.assertRaises(EvidenceError):
                    subject.capture_required_file_roles([value])
            reader.assert_not_called()

    def test_wrong_frozen_content_and_symlink_are_rejected(self):
        role = self.file_role()
        with self.assertRaisesRegex(EvidenceError, "collector_required_input_changed"):
            subject.capture_required_file_roles([replace(role, expected_sha256="0"*64)])
        (self.root/"alias.json").symlink_to(self.root/role.relative_path)
        with self.assertRaises(EvidenceError):
            subject.capture_required_file_roles([replace(role, relative_path="alias.json")])

    def test_file_declared_size_mismatch_rejects_before_body_capture(self):
        role = replace(self.file_role(), expected_bytes=1, maximum_bytes=1024*1024)
        with patch.object(subject, "_frozen", side_effect=AssertionError("unexpected body read")) as reader:
            with self.assertRaisesRegex(EvidenceError, "collector_required_input_size_changed"):
                subject.capture_required_file_roles([role])
            reader.assert_not_called()

    def test_constructed_unsafe_capture_is_rejected_before_any_write(self):
        role = self.file_role()
        malformed = subject.CapturedFileRoles((replace(role, staged_name="../escape"),), (("../escape", b"original metadata"),))
        with self.assertRaises(EvidenceError):
            malformed.materialize(self.root, self.root/"staged")
        self.assertFalse((self.root/"staged").exists())
        self.assertFalse((self.root/"escape").exists())

    def test_captured_descriptor_cannot_hide_changed_bytes_or_malformed_requirements(self):
        role = self.file_role()
        for value in (subject.CapturedFileRoles((role,), ((role.staged_name, b"wrong"),)),
                      subject.CapturedFileRoles([role], ((role.staged_name, b"original metadata"),))):
            with self.subTest(value=value), self.assertRaises(EvidenceError):
                value.materialize(self.root, self.root/"staged")
        self.assertFalse((self.root/"staged").exists())

    def test_git_role_binds_head_commit_path_blob_and_bytes_without_retaining_primary(self):
        root, commit = self.repo()
        role = self.git_role(root, commit)
        before = self.git(root, "status", "--porcelain")
        result = subject.verify_git_input_roles([role])
        self.assertEqual(result["roles"][role.role]["git_blob"], role.git_blob)
        self.assertFalse(result["roles"][role.role]["payload_retained"])
        self.assertNotIn("raw", result["roles"][role.role])
        self.assertEqual(self.git(root, "status", "--porcelain"), before)

    def test_same_blob_in_wrong_repository_does_not_supply_the_declared_role(self):
        root, commit = self.repo()
        other, other_commit = self.repo("other")
        self.assertNotEqual(commit, other_commit)
        role = self.git_role(root, commit)
        with self.assertRaisesRegex(EvidenceError, "collector_git_role_head_changed"):
            subject.verify_git_input_roles([replace(role, repository=other)])

    def test_wrong_git_path_oid_and_content_digest_fail_without_fallback(self):
        root, commit = self.repo()
        role = self.git_role(root, commit)
        for changed in (replace(role, path="missing.json"), replace(role, git_blob="0"*40),
                        replace(role, expected_sha256="0"*64)):
            with self.subTest(changed=changed), self.assertRaises(EvidenceError):
                subject.verify_git_input_roles([changed])

    def test_git_size_is_checked_before_object_body_read(self):
        root, commit = self.repo()
        role = replace(self.git_role(root, commit), expected_bytes=1, maximum_bytes=1)
        original = subject._git
        calls = []
        def observe(repository, *arguments):
            calls.append(arguments)
            self.assertFalse(len(arguments) > 1 and arguments[:2] == ("cat-file", "blob"))
            return original(repository, *arguments)
        with patch.object(subject, "_git", side_effect=observe):
            with self.assertRaisesRegex(EvidenceError, "collector_git_blob_size_budget"):
                subject.verify_git_input_roles([role])
        self.assertTrue(any(arguments[:2] == ("cat-file", "-t") for arguments in calls))
        self.assertTrue(any(arguments[:2] == ("cat-file", "-s") for arguments in calls))

    def test_git_tree_is_not_a_regular_blob_role(self):
        root, commit = self.repo()
        path = "Scripts"
        oid = self.git(root, "rev-parse", commit+":"+path).decode().strip()
        role = replace(self.git_role(root, commit), path=path, git_blob=oid)
        with self.assertRaisesRegex(EvidenceError, "collector_git_regular_blob_required"):
            subject.verify_git_input_roles([role])

    def test_git_declared_byte_count_is_checked_before_body_even_with_large_limit(self):
        root, commit = self.repo()
        role = replace(self.git_role(root, commit), expected_bytes=1, maximum_bytes=1024*1024)
        original = subject._git
        def observe(repository, *arguments):
            self.assertFalse(len(arguments) > 1 and arguments[:2] == ("cat-file", "blob"))
            return original(repository, *arguments)
        with patch.object(subject, "_git", side_effect=observe):
            with self.assertRaisesRegex(EvidenceError, "collector_git_blob_declared_size_changed"):
                subject.verify_git_input_roles([role])

    def test_module_selection_captures_both_literal_classes_without_import(self):
        raw = b"raise RuntimeError('this source MUST NOT be executed')\n"+SOURCE
        root, commit = self.repo(raw=raw)
        result = subject.capture_python_selection_inventory(root, commit, [MODULE], IDS)
        self.assertEqual(result["literal_test_ids"], sorted(IDS))
        self.assertFalse(result["tests_executed"])
        self.assertFalse(result["runtime_inventory_verified"])

    def test_class_selection_does_not_count_other_class_in_same_module(self):
        root, commit = self.repo()
        result = subject.capture_python_selection_inventory(root, commit, [MODULE+".First"], IDS[:2])
        self.assertEqual(result["literal_test_ids"], sorted(IDS[:2]))
        self.assertEqual(result["selections"][0]["outside_declared_scope"], ["Second"])

    def test_two_class_selectors_reuse_one_source_and_match_exact_union(self):
        root, commit = self.repo()
        result = subject.capture_python_selection_inventory(root, commit, [MODULE+".First", MODULE+".Second"], IDS)
        self.assertEqual(len(result["sources"]), 1)
        self.assertEqual(result["literal_test_ids"], sorted(IDS))

    def test_method_unknown_class_and_duplicate_selection_are_explicitly_rejected(self):
        root, commit = self.repo()
        for selectors in ([MODULE+".First.test_alpha"], [MODULE+".Unknown"], [MODULE, MODULE+".First"]):
            with self.subTest(selectors=selectors), self.assertRaises(EvidenceError):
                subject.capture_python_selection_inventory(root, commit, selectors, IDS)

    def test_dynamic_class_member_and_load_tests_hooks_are_unsupported(self):
        extras = (b"First.test_added = lambda self: None\n",
                  b"def load_tests(loader, tests, pattern): return tests\n", b"Alias = First\n",
                  b"First, other = Second, 0\n", b"unittest, other = None, 0\n",
                  b"class Extra(unittest.TestCase):\n    def test_plain(self): pass\n    test_added, other = (lambda self: None), 0\n",
                  b"class Extra(unittest.TestCase):\n    def test_plain(self): pass\n    [test_added, other] = (lambda self: None), 0\n",
                  b"class Extra(unittest.TestCase):\n    def test_plain(self): pass\n    *test_added, other = [(lambda self: None), 0]\n")
        for index, extra in enumerate(extras):
            root, commit = self.repo("dynamic"+str(index), SOURCE+extra)
            expected = IDS+([MODULE+".Extra.test_plain"] if b"class Extra" in extra else [])
            with self.subTest(extra=extra), self.assertRaisesRegex(EvidenceError, "collector_python_dynamic_inventory_unsupported"):
                subject.capture_python_selection_inventory(root, commit, [MODULE], expected)

    def test_inherited_and_conditional_cases_are_not_silently_undercounted(self):
        variants = [SOURCE+b"class Derived(First):\n    pass\n",
                    SOURCE+b"if True:\n    class Conditional(unittest.TestCase):\n        def test_added(self): pass\n"]
        for index, raw in enumerate(variants):
            root, commit = self.repo("unsupported"+str(index), raw)
            with self.subTest(index=index), self.assertRaises(EvidenceError):
                subject.capture_python_selection_inventory(root, commit, [MODULE], IDS)

    def test_source_physical_edit_head_change_and_size_limit_are_checked(self):
        root, commit = self.repo()
        (root/PATH).write_bytes(SOURCE+b"# later edit\n")
        with self.assertRaisesRegex(EvidenceError, "collector_python_physical_source_changed"):
            subject.capture_python_selection_inventory(root, commit, [MODULE], IDS)
        (root/PATH).write_bytes(SOURCE)
        with self.assertRaisesRegex(EvidenceError, "collector_python_source_head_changed"):
            subject.capture_python_selection_inventory(root, "0"*40, [MODULE], IDS)
        with self.assertRaisesRegex(EvidenceError, "collector_git_blob_size_budget"):
            subject.capture_python_selection_inventory(root, commit, [MODULE], IDS, maximum_source_bytes=1)

    def test_malformed_selector_manifest_is_rejected_before_git_or_file_reads(self):
        with patch.object(subject, "_git", side_effect=AssertionError("unexpected Git read")) as reader:
            with self.assertRaises(EvidenceError):
                subject.capture_python_selection_inventory(self.root, "0"*40, [["bad"]], IDS)
            reader.assert_not_called()

    def test_class_scope_allows_local_test_named_variables_without_dynamic_members(self):
        raw = SOURCE.replace(b"def test_alpha(self): pass", b"def test_alpha(self):\n        test_value = 1\n        return test_value")
        root, commit = self.repo(raw=raw)
        result = subject.capture_python_selection_inventory(root, commit, [MODULE+".First"], IDS[:2])
        self.assertEqual(result["literal_test_ids"], sorted(IDS[:2]))

    def test_required_files_keep_both_observer_snapshots_without_normalizing_bytes(self):
        before = json.dumps({"token": "same", "state": "released", "heartbeat_expired": False}).encode()
        after = json.dumps({"token": "same", "state": "released", "heartbeat_expired": True}).encode()
        first = self.file_role("original", before, "original.json")
        second = self.file_role("fresh", after, "fresh.json")
        captured = subject.capture_required_file_roles([first, second])
        staged = captured.materialize(self.root, self.root/"staged")
        self.assertEqual(staged["collector-file-inputs/original.json"].read_bytes(), before)
        self.assertEqual(staged["collector-file-inputs/fresh.json"].read_bytes(), after)
        self.assertNotEqual(captured.descriptor["roles"]["original"]["sha256"], captured.descriptor["roles"]["fresh"]["sha256"])


if __name__ == "__main__":
    unittest.main()
