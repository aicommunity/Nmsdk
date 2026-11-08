"""Server metadata regressions from actual closed attempts; no neural execution."""
import base64
import copy
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from .. import collector_provenance as subject
from ..native_evidence import EvidenceError
from ..runtime import digest_json
from ..portable_primary import create_native_bundle


FIXTURE = Path(__file__).with_name("fixtures")/"collector_provenance"
ROOT_A2 = "540179d70ddf3764334eb6bb59b7fef691054eee"
ROOT_A3 = "6dacdb3d4fb3245649aba3a5d69ba8f83f611c8e"
CPP = "Tests/Integration/Libraries/Test_PulseLib_CompositeTraining.cpp"
DOC = "Docs/StructTrain/TimeLearner/CompositeTrainingArchiveGateInventory.json"


def signed(value):
    value = {key: item for key, item in value.items() if key != "sha256"}
    return {**value, "sha256": digest_json(value)}


@unittest.skipUnless(sys.platform == "linux", "owned Linux metadata gate required")
class CollectorProvenanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(gzip.decompress((FIXTURE/"actual-metadata.json.gz").read_bytes()))
        cls.contents = {}
        for name, row in cls.fixture["members"].items():
            raw = base64.b64decode(row["base64"], validate=True)
            assert len(raw) == row["bytes"] and hashlib.sha256(raw).hexdigest() == row["sha256"]
            cls.contents[name] = raw
        cls.git_tmp = tempfile.TemporaryDirectory(prefix="collector-source-metadata-")
        cls.gitroot = Path(cls.git_tmp.name)/"source"
        cls.gitroot.mkdir()
        cls.git("init", "--quiet")
        pack = (FIXTURE/"source-git-objects.pack").read_bytes()
        row = cls.fixture["source_git_pack"]
        assert len(pack) == row["bytes"] and hashlib.sha256(pack).hexdigest() == row["sha256"]
        cls.git("index-pack", "--stdin", "--promisor", data=pack)
        (cls.gitroot/".git/shallow").write_text("\n".join(row["roots"])+"\n")
        cls.git("config", "core.repositoryformatversion", "1")
        cls.git("config", "extensions.partialClone", "origin")
        cls.git("config", "remote.origin.promisor", "true")
        cls.git("config", "core.autocrlf", "false")
        cls.git("sparse-checkout", "init", "--no-cone")
        cls.git("sparse-checkout", "set", "--no-cone",
                *sorted({"/"+item["path"] for item in row["blobs"]}))
        cls.git("-c", "submodule.recurse=false", "checkout", "--detach", ROOT_A3)

    @classmethod
    def tearDownClass(cls):
        cls.git_tmp.cleanup()

    @classmethod
    def git(cls, *args, data=None):
        return subprocess.check_output(["git", "-C", str(cls.gitroot), *args], input=data,
            env={**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_OPTIONAL_LOCKS": "0"},
            stderr=subprocess.PIPE)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="collector-bound-inputs-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.container = self.root/"contained"
        self.container.mkdir()
        self.supervisor = self.root/"explicit-arbitrary-name.log"
        self.progress = self.container/"stdout.log"
        self.install("a3")

    def install(self, prefix):
        for path, key in [(self.container/"request.json", prefix+"_request"),
                          (self.container/"owned-unit.json", prefix+"_binding"),
                          (self.supervisor, prefix+"_supervisor"),
                          (self.progress, prefix+"_worker_stdout")]:
            path.write_bytes(self.contents[key])

    def capture(self, **options):
        return subject.capture_owned_supervisor(self.container, supervisor_log=self.supervisor,
                                                worker_stdout=self.progress, **options)

    def inventory(self, *, root=ROOT_A3, selections=None, documents=()):
        closure = json.loads(self.contents["a3_sdk_closure" if root == ROOT_A3 else "a2_sdk_closure"])
        with patch.object(subject, "source_closure", return_value=closure):
            return subject.capture_git_case_inventory(self.gitroot, selections=selections or [
                {"path": CPP, "suites": None, "dialect": subject.DIALECT}],
                inventory_documents=documents)

    def test_actual_A3_binding_and_explicit_arbitrary_log_path(self):
        captured = self.capture()
        self.assertEqual(captured.descriptor["binding"], json.loads(self.contents["a3_binding"]))
        self.assertEqual(captured.descriptor["inputs"]["supervisor_launch"]["source_path"], str(self.supervisor))
        self.assertFalse(captured.descriptor["kernel_closure_attested"])
        self.assertFalse(captured.descriptor["test_success_attested"])
        self.assertIsNone(captured.descriptor["scientific_verdict"])

    def test_actual_90af_wrong_A2_log_is_rejected_for_A3(self):
        self.supervisor.write_bytes(self.contents["wrong_a2_supervisor"])
        with self.assertRaisesRegex(EvidenceError, "collector_supervisor_binding_mismatch"):
            self.capture()

    def test_actual_A3_log_is_rejected_for_A2_binding(self):
        self.install("a2")
        self.supervisor.write_bytes(self.contents["a3_supervisor"])
        with self.assertRaisesRegex(EvidenceError, "collector_supervisor_binding_mismatch"):
            self.capture()

    def test_actual_A3_log_is_not_worker_progress(self):
        captured = self.capture().descriptor
        self.assertNotEqual(captured["inputs"]["supervisor_launch"]["sha256"],
                            captured["inputs"]["worker_progress"]["sha256"])
        self.assertEqual(sum(line.startswith("GATE ") for line in self.progress.read_text().splitlines()), 12)
        self.assertEqual(sum(line.startswith("GATE ") for line in self.supervisor.read_text().splitlines()), 0)
        with self.assertRaisesRegex(EvidenceError, "collector_log_roles_alias"):
            subject.capture_owned_supervisor(self.container, supervisor_log=self.supervisor,
                                              worker_stdout=self.supervisor)

    def test_missing_STARTED_refuses_publication_inputs(self):
        self.supervisor.write_text("CLOSED only\n")
        with self.assertRaisesRegex(EvidenceError, "collector_supervisor_start_missing_or_ambiguous"):
            self.capture()

    def test_progress_stream_must_belong_to_the_bound_container(self):
        foreign = self.root/"foreign-worker-stdout.log"
        foreign.write_bytes(self.contents["a3_worker_stdout"])
        with self.assertRaisesRegex(EvidenceError, "collector_worker_stdout_not_owned_container"):
            subject.capture_owned_supervisor(self.container, supervisor_log=self.supervisor, worker_stdout=foreign)

    def test_duplicate_identical_STARTED_refuses_ambiguity(self):
        started = next(line for line in self.supervisor.read_text().splitlines() if line.startswith("STARTED "))
        self.supervisor.write_text(started+"\n"+started+"\n")
        with self.assertRaisesRegex(EvidenceError, "collector_supervisor_start_missing_or_ambiguous"):
            self.capture()

    def test_mixed_foreign_and_matching_STARTED_refuses_ambiguity(self):
        self.supervisor.write_bytes(self.supervisor.read_bytes()+self.contents["wrong_a2_supervisor"])
        with self.assertRaisesRegex(EvidenceError, "collector_supervisor_start_missing_or_ambiguous"):
            self.capture()

    def test_malformed_STARTED_JSON_is_rejected(self):
        self.supervisor.write_text("STARTED {not JSON}\n")
        with self.assertRaisesRegex(EvidenceError, "collector_json_invalid"):
            self.capture()

    def test_invalid_UTF8_supervisor_has_structured_refusal(self):
        self.supervisor.write_bytes(self.contents["a3_supervisor"]+b"\xff")
        with self.assertRaisesRegex(EvidenceError, "collector_supervisor_log_invalid_utf8"):
            self.capture()

    def test_duplicate_JSON_keys_are_rejected(self):
        binding = json.loads(self.contents["a3_binding"])
        self.supervisor.write_text('STARTED {"kind":"duplicate",'+json.dumps(binding)[1:]+"\n")
        with self.assertRaisesRegex(EvidenceError, "collector_duplicate_json_key"):
            self.capture()

    def test_tampered_request_content_digest_is_rejected(self):
        request = json.loads(self.contents["a3_request"])
        request["maximum_wall_seconds"] += 1
        (self.container/"request.json").write_text(json.dumps(request))
        with self.assertRaisesRegex(EvidenceError, "collector_record_digest_changed"):
            self.capture()

    def test_tampered_binding_content_digest_is_rejected(self):
        binding = json.loads(self.contents["a3_binding"])
        binding["initial_main_pid"] += 1
        (self.container/"owned-unit.json").write_text(json.dumps(binding))
        with self.assertRaisesRegex(EvidenceError, "collector_record_digest_changed"):
            self.capture()

    def test_rehashed_foreign_binding_identity_still_fails(self):
        for field, replacement in [("invocation_id", "a"*32), ("initial_main_pid", 99),
                                   ("initial_start_ticks", "123"), ("control_group", "/elsewhere/"+
                                    json.loads(self.contents["a3_binding"])["unit"])]:
            with self.subTest(field=field):
                binding = json.loads(self.contents["a3_binding"])
                binding[field] = replacement
                (self.container/"owned-unit.json").write_text(json.dumps(signed(binding)))
                with self.assertRaisesRegex(EvidenceError, "collector_supervisor_binding_mismatch"):
                    self.capture()

    def test_missing_request_is_not_inferred_from_log(self):
        (self.container/"request.json").unlink()
        with self.assertRaises(FileNotFoundError):
            self.capture()

    def test_size_budget_rejects_input_before_parsing(self):
        with self.assertRaisesRegex(EvidenceError, "collector_file_type_or_size"):
            self.capture(maximum_input_bytes=8)

    def test_symlink_log_is_not_an_original_capture(self):
        alias = self.root/"alias.log"
        alias.symlink_to(self.supervisor)
        with self.assertRaisesRegex(EvidenceError, "collector_symlink_path"):
            subject.capture_owned_supervisor(self.container, supervisor_log=alias, worker_stdout=self.progress)

    def test_append_during_frozen_read_is_rejected(self):
        original = os.fstat
        calls = 0
        def append(descriptor):
            nonlocal calls
            calls += 1
            if calls == 2:
                with (self.container/"request.json").open("ab") as stream:
                    stream.write(b" ")
            return original(descriptor)
        with patch.object(subject.os, "fstat", side_effect=append):
            with self.assertRaisesRegex(EvidenceError, "collector_file_changed_during_read"):
                self.capture()

    def test_replacement_during_frozen_read_is_rejected(self):
        original = os.fstat
        calls = 0
        def replace(descriptor):
            nonlocal calls
            calls += 1
            if calls == 2:
                path = self.container/"request.json"
                path.rename(self.container/"old-request.json")
                path.write_bytes(self.contents["a3_request"])
            return original(descriptor)
        with patch.object(subject.os, "fstat", side_effect=replace):
            with self.assertRaisesRegex(EvidenceError, "collector_file_changed_during_read"):
                self.capture()

    def test_materialize_uses_captured_bytes_not_reopened_inputs(self):
        captured = self.capture()
        self.supervisor.write_bytes(self.contents["wrong_a2_supervisor"])
        staged = captured.materialize(self.root, self.root/"frozen")
        self.assertEqual(staged["collector-provenance/supervisor.log"].read_bytes(), self.contents["a3_supervisor"])
        self.assertTrue(all(path.parent == self.root/"frozen" for path in staged.values()))
        self.assertNotIn(self.supervisor, staged.values())
        with self.assertRaisesRegex(EvidenceError, "collector_staging_scope_or_exists"):
            captured.materialize(self.root, self.root/"frozen")

    def test_materialize_rejects_outside_owned_root(self):
        with self.assertRaisesRegex(EvidenceError, "collector_staging_scope_or_exists"):
            self.capture().materialize(self.container, self.root/"outside")

    def test_manually_constructed_escape_name_refuses_before_filesystem_write(self):
        captured = self.capture()
        forged = subject.CapturedCollectorInputs(captured._descriptor_json,
            (("../escape.log", captured._files[0][1]), *captured._files[1:]))
        with patch.object(subject.os, "open", side_effect=AssertionError("must not open")), \
                patch.object(Path, "mkdir", side_effect=AssertionError("must not mkdir")):
            with self.assertRaisesRegex(EvidenceError, "collector_captured_files_invalid"):
                forged.materialize(self.root, self.root/"forged")
        self.assertFalse((self.root/"forged").exists())
        self.assertFalse((self.root/"escape.log").exists())

    def test_manually_constructed_duplicate_role_refuses_before_filesystem_write(self):
        captured = self.capture()
        forged = subject.CapturedCollectorInputs(captured._descriptor_json,
            (captured._files[0], captured._files[0], *captured._files[2:]))
        with patch.object(subject.os, "open", side_effect=AssertionError("must not open")), \
                patch.object(Path, "mkdir", side_effect=AssertionError("must not mkdir")):
            with self.assertRaisesRegex(EvidenceError, "collector_captured_files_invalid"):
                forged.materialize(self.root, self.root/"forged")
        self.assertFalse((self.root/"forged").exists())

    def test_manually_constructed_bytes_must_match_descriptor_before_write(self):
        captured = self.capture()
        forged = subject.CapturedCollectorInputs(captured._descriptor_json,
            ((captured._files[0][0], b"changed bytes"), *captured._files[1:]))
        with patch.object(subject.os, "open", side_effect=AssertionError("must not open")), \
                patch.object(Path, "mkdir", side_effect=AssertionError("must not mkdir")):
            with self.assertRaisesRegex(EvidenceError, "collector_captured_descriptor_changed"):
                forged.materialize(self.root, self.root/"forged")
        self.assertFalse((self.root/"forged").exists())

    def test_existing_packager_uses_frozen_staged_log_and_descriptor(self):
        captured = self.capture()
        staged = captured.materialize(self.root, self.root/"frozen")
        self.supervisor.write_bytes(self.contents["wrong_a2_supervisor"])
        bundle = create_native_bundle(staged, self.root/"packed", dictionary_bytes=8*1024**2)
        with tarfile.open(self.root/"packed/primary.tar.xz", "r:xz") as archive:
            self.assertEqual(archive.extractfile("collector-provenance/supervisor.log").read(),
                             self.contents["a3_supervisor"])
            self.assertEqual(json.load(archive.extractfile("collector-provenance/descriptor.json")),
                             captured.descriptor)
        self.assertEqual(set(bundle["members"]), set(staged))

    def test_actual_Git_source_derives_full206_with_explicit_subset(self):
        selections = [{"path": "Tests/Integration/Libraries/Test_PulseLib_"+name+".cpp",
                       "suites": ["NativePreparationCancellation"] if name == "NativeExecution" else None,
                       "dialect": subject.DIALECT}
                      for name in ["BoundedTraining", "FinalVerification", "CompositeTraining", "NativeExecution"]]
        documents = [{"path": "Docs/StructTrain/TimeLearner/CompositeTraining"+name+"GateInventory.json",
                      "source_path": CPP} for name in ["Archive", "Declarations", "Service"]]
        value = self.inventory(selections=selections, documents=documents)
        self.assertEqual([len(row["ids"]) for row in value["files"].values()], [74, 23, 105, 4])
        self.assertEqual(value["count"], 206)
        self.assertNotIn("TrainingInvalidBudget/name", value["ids"])
        self.assertEqual(sum(case.startswith("TrainingInvalidBudget/") for case in value["ids"]), 4)
        self.assertEqual(value["files"][CPP]["sha256"], "44acf89749caa4ff7644ffbba6726a60a8f6b8de91398679e52a61ecd39f1cca")
        self.assertFalse(value["compiled_inventory_verified"])

    def test_actual153_stale_nested_fc9_is_rejected_against_Git05f(self):
        self.git("-c", "submodule.recurse=false", "checkout", "--detach", ROOT_A2)
        try:
            claimed = json.loads(self.contents["a2_stale_nested_inventory"])["archive_contract"]
            self.assertEqual(claimed["source_sha256"], "fc9dfb4869cd0a6f9f6c6548b9ce642049f016320909688ef76bf86a32150601")
            with self.assertRaisesRegex(EvidenceError, "collector_inventory_source_hash_mismatch"):
                self.inventory(root=ROOT_A2, documents=[{"path": DOC, "source_path": CPP, "claimed": claimed}])
            actual = self.inventory(root=ROOT_A2, documents=[{"path": DOC, "source_path": CPP}])
            self.assertEqual(actual["files"][CPP]["sha256"], "05f5cf15b64d6f16950db33ce6724dffd4c3435a5cac7514701dbfefb10ea49a")
        finally:
            self.git("-c", "submodule.recurse=false", "checkout", "--detach", ROOT_A3)

    def test_actual_invalid_budget_macro_cannot_add_a_second_TEST(self):
        original = self.git("show", ROOT_A3+":Tests/Integration/Libraries/Test_PulseLib_BoundedTraining.cpp")
        marker = b"TEST(TrainingInvalidBudget,name)"
        self.assertEqual(original.count(marker), 1)
        changed = original.replace(marker, b"TEST(UnexpectedSecond,name) {} \\\n"+marker, 1)
        with self.assertRaisesRegex(EvidenceError, "collector_invalid_budget_macro_changed"):
            subject._literal_cases(changed)

    def test_changed_document_claim_cannot_replace_Git_cases(self):
        claimed = json.loads(self.git("show", ROOT_A3+":"+DOC))
        claimed["cases"] = claimed["cases"][:-1]
        claimed["count"] -= 1
        with self.assertRaisesRegex(EvidenceError, "collector_inventory_document_claim_changed"):
            self.inventory(documents=[{"path": DOC, "source_path": CPP, "claimed": claimed}])

    def test_changed_source_worktree_cannot_keep_Git_inventory(self):
        path = self.gitroot/CPP
        raw = path.read_bytes()
        try:
            path.write_bytes(raw+b"\n// drift\n")
            with self.assertRaisesRegex(EvidenceError, "collector_worktree_git_bytes_changed"):
                self.inventory()
        finally:
            path.write_bytes(raw)

    def test_dirty_source_closure_is_rejected(self):
        closure = json.loads(self.contents["a3_sdk_closure"])
        closure["root"]["status"] = " M changed"
        with patch.object(subject, "source_closure", return_value=closure):
            with self.assertRaisesRegex(EvidenceError, "collector_actual_source_not_clean"):
                subject.capture_git_case_inventory(self.gitroot, selections=[
                    {"path": CPP, "suites": None, "dialect": subject.DIALECT}])

    def test_source_epoch_change_during_inventory_is_rejected(self):
        first = json.loads(self.contents["a3_sdk_closure"])
        second = copy.deepcopy(first)
        second["root"]["head"] = ROOT_A2
        with patch.object(subject, "source_closure", side_effect=[first, second]):
            with self.assertRaisesRegex(EvidenceError, "collector_source_changed_during_capture"):
                subject.capture_git_case_inventory(self.gitroot, selections=[
                    {"path": CPP, "suites": None, "dialect": subject.DIALECT}])

    def test_unsupported_dialect_cannot_claim_universal_gtest_coverage(self):
        with self.assertRaisesRegex(EvidenceError, "collector_test_dialect_unsupported"):
            self.inventory(selections=[{"path": CPP, "suites": None, "dialect": "all-C++-tests"}])

    def test_missing_git_blob_fails_without_lazy_fetch(self):
        with self.assertRaises(subprocess.CalledProcessError):
            self.inventory(documents=[{"path": "CMakeLists.txt", "source_path": CPP}])

    def test_actual_c19_preflight_keeps_planned540_actual_d920_and_compiled_null(self):
        self.install("preflight")
        observed = json.loads(self.contents["preflight_actual_sdk"])
        self.assertEqual(observed["root"]["head"], "d92022a41d6f448852d2ecfc6f87ca5a719843bc")
        self.assertEqual(json.loads(self.contents["preflight_planned_runtime"])["source_closure"]["tool_root"], ROOT_A2)
        with patch.object(subject, "source_closure", return_value=observed):
            value = subject.describe_collection(self.capture(), collector_tool_root=Path(__file__).resolve().parents[4],
                compilation_state="not_started",
                actual_sdk_source=self.root, planned_source={"root": ROOT_A2})
        self.assertEqual(value["planned_source"]["root"], ROOT_A2)
        self.assertEqual(value["actual_sdk_source_closure"]["root"]["head"], observed["root"]["head"])
        self.assertIsNone(value["actual_compiled_runtime"])
        self.assertIsNone(value["observed_test_inventory"])
        self.assertFalse(value["collector_tool_source"]["SDK_gitlinks_verified"])
        self.assertFalse(value["kernel_closure_attested"])
        self.assertFalse(value["test_success_attested"])

    def test_actual_compiled_manifest_is_distinct_from_plan_and_not_success(self):
        observed = json.loads(self.contents["a3_sdk_closure"])
        runtime = json.loads(self.contents["a3_runtime"])
        with patch.object(subject, "source_closure", return_value=observed):
            value = subject.describe_collection(self.capture(), collector_tool_root=Path(__file__).resolve().parents[4],
                compilation_state="built",
                actual_sdk_source=self.root, compiled_runtime=runtime, planned_source={"root": ROOT_A2})
        self.assertEqual(value["actual_compiled_runtime"]["source_closure"]["root"]["head"], ROOT_A3)
        self.assertEqual(value["planned_source"]["root"], ROOT_A2)
        self.assertFalse(value["compiled_inventory_verified"])
        self.assertIsNone(value["scientific_verdict"])

    def test_compiled_manifest_digest_tamper_is_rejected(self):
        observed = json.loads(self.contents["a3_sdk_closure"])
        runtime = json.loads(self.contents["a3_runtime"])
        runtime["executable"]["sha256"] = "0"*64
        with patch.object(subject, "source_closure", return_value=observed):
            with self.assertRaisesRegex(EvidenceError, "collector_compiled_runtime_source_or_digest_changed"):
                subject.describe_collection(self.capture(), collector_tool_root=Path(__file__).resolve().parents[4],
                    compilation_state="built",
                    actual_sdk_source=self.root, compiled_runtime=runtime)

    def test_not_started_phase_refuses_any_compiled_runtime(self):
        with self.assertRaisesRegex(EvidenceError, "collector_compilation_phase_runtime_mismatch"):
            subject.describe_collection(self.capture(), collector_tool_root=Path(__file__).resolve().parents[4],
                compilation_state="not_started", compiled_runtime=json.loads(self.contents["a3_runtime"]))
