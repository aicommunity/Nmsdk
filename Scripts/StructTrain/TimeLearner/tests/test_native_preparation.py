"""Linux metadata tests using actual cc23/eaa Git objects; no model execution."""
import base64
import copy
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from .. import collector_provenance as collector
from .. import native_preparation as subject
from ..native_evidence import EvidenceError
from ..runtime import digest_json


FIXTURE = Path(os.environ.get("TL_NATIVE_PREPARATION_FIXTURE",
                             Path(__file__).with_name("fixtures")/"native_preparation"))
CPP = "Tests/Integration/Libraries/Test_PulseLib_CompositeTraining.cpp"


@unittest.skipUnless(sys.platform == "linux", "Linux metadata gate required")
class NativePreparationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(gzip.decompress((FIXTURE/"actual-metadata.json.gz").read_bytes()))
        cls.tmp = tempfile.TemporaryDirectory(prefix="native-preparation-git-")
        cls.root = Path(cls.tmp.name)/"source"
        cls.root.mkdir()
        cls.git("init", "--quiet")
        raw = (FIXTURE/"source-git-objects.pack").read_bytes()
        assert len(raw) == cls.fixture["pack"]["bytes"]
        assert hashlib.sha256(raw).hexdigest() == cls.fixture["pack"]["sha256"]
        cls.git("index-pack", "--stdin", "--promisor", data=raw)
        (cls.root/".git/shallow").write_text(cls.fixture["root"]+"\n", encoding="utf-8")
        cls.git("config", "core.repositoryformatversion", "1")
        cls.git("config", "extensions.partialClone", "origin")
        cls.git("config", "remote.origin.promisor", "true")
        cls.git("config", "core.autocrlf", "false")
        cls.git("sparse-checkout", "init", "--no-cone")
        cls.git("sparse-checkout", "set", "--no-cone",
                *["/"+r["path"] for r in cls.fixture["pack"]["blobs"]])
        cls.git("-c", "submodule.recurse=false", "checkout", "--detach", cls.fixture["root"])

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @classmethod
    def git(cls, *args, data=None):
        return subprocess.check_output(["git", "-C", str(cls.root), *args], input=data,
            env={**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_OPTIONAL_LOCKS": "0"},
            stderr=subprocess.PIPE)

    def setUp(self):
        self.worker = b"from pathlib import Path\n# metadata-only fixture, never executed\n"
        self.supervisor = ("WORKER.write_text("+repr(self.worker.decode())+
                           ", encoding='utf-8')\n").encode()
        self.selections = [{"path": "Tests/Integration/Libraries/"+name,
                            "suites": ["NativePreparationCancellation"] if "NativeExecution" in name else None,
                            "dialect": collector.DIALECT}
                           for name in self.fixture["legacy_copied_inventory"]["files"]]
        self.plan = copy.deepcopy(self.fixture["runplan"])
        self.ids = [v for row in self.plan for v in row["expected_ids"]]
        self.partitions = [{"name": "declared-full248", "ids": self.ids, "count": len(self.ids)}]
        self.prior = [copy.deepcopy(v["original"]) for v in self.fixture["prior_binding_faults"]]
        self.originals = {}
        for row in self.fixture["prior_binding_faults"]:
            primary = row["original_primary"]
            raw = base64.b64decode(primary["base64"], validate=True)
            assert len(raw) == primary["bytes"] and hashlib.sha256(raw).hexdigest() == primary["sha256"]
            assert json.loads(raw) == row["original"]["binding"]
            self.originals[row["original"]["binding_path"]] = raw

    def prepare(self, **changes):
        options = dict(selections=self.selections, selected_ids=self.ids, runplan=self.plan,
                       partitions=self.partitions, prior_bindings=self.prior,
                       prior_originals=self.originals, worker_bytes=self.worker,
                       supervisor_bytes=self.supervisor, supervisor_platform="posix")
        options.update(changes)
        # Actual captured closure is retained metadata, not a live component or
        # kernel claim. The Git commits/blobs/worktree are genuinely read.
        with patch.object(collector, "source_closure", return_value=copy.deepcopy(self.fixture["closure"])):
            return subject.prepare_native_checks(self.root, **options)

    def claims(self):
        return copy.deepcopy(self.prepare()["current"])

    def prepare_module(self, **changes):
        options = dict(selections=self.selections, selected_ids=self.ids, runplan=self.plan,
                       partitions=self.partitions, prior_bindings=self.prior,
                       prior_originals=self.originals, module=self.fixture["repo_module_fixture"],
                       arguments=["--job", "/tmp/План.json"])
        options.update(changes)
        with patch.object(collector, "source_closure", return_value=copy.deepcopy(self.fixture["closure"])):
            return subject.prepare_native_module_checks(self.root, **options)

    def test_actual_cc23_positive_derives_one_consistent248_declaration(self):
        spec = self.prepare(historical={"root": "540179d70ddf3764334eb6bb59b7fef691054eee",
                                       "prior_scope": 179})
        self.assertEqual(spec["current"]["root"], self.fixture["root"])
        self.assertEqual(spec["current"]["inventory"]["files"][CPP]["sha256"],
                         self.fixture["new_active_source_sha256"])
        self.assertEqual(spec["current"]["counts"], {"selected_cases": 248, "leaf_gates": 138})
        self.assertEqual(json.loads(subject.serialize_preparation(spec)), spec)
        for field in ["physical_worker_bytes_verified", "compiled_inventory_verified",
                      "kernel_closure_attested", "test_success_attested"]:
            self.assertIs(spec[field], False)
        self.assertIsNone(spec["scientific_verdict"])

    def test_actual_stale_inventory_root540_is_rejected(self):
        claims = self.claims()
        claims["inventory"]["root"] = self.fixture["legacy_copied_inventory"]["root"]
        with self.assertRaisesRegex(EvidenceError, "current_claim_mismatch"):
            self.prepare(claims=claims)

    def test_actual_nested05f_source_claim_cannot_override_a35(self):
        claims = self.claims()
        claims["source_claims"] = [{"label": "archive_contract.source_sha256", "source_path": CPP,
                                   "sha256": self.fixture["historical_nested_source_sha256"]}]
        with self.assertRaisesRegex(EvidenceError, "source_hash_mismatch"):
            self.prepare(claims=claims)

    def test_actual_three_operator_corrupted_binding_claims_are_rejected(self):
        for index, fault in enumerate(self.fixture["prior_binding_faults"]):
            with self.subTest(index=index):
                prior = copy.deepcopy(self.prior)
                prior[index] = fault["corrupted_claim"]
                with self.assertRaisesRegex(EvidenceError, "binding_changed"):
                    self.prepare(prior_bindings=prior)

    def test_original_binding_bytes_and_integrity_digest_are_not_rewritten(self):
        original = copy.deepcopy(self.originals)
        spec = self.prepare()
        self.assertEqual(self.originals, original)
        self.assertEqual([r["binding"] for r in spec["prior_bindings"]],
                         [r["binding"] for r in self.prior])
        self.assertEqual([r["original_sha256"] for r in spec["prior_bindings"]],
                         [hashlib.sha256(original[r["binding_path"]]).hexdigest() for r in self.prior])

    def test_modified_original_without_new_digest_is_rejected(self):
        originals = copy.deepcopy(self.originals)
        path = self.prior[0]["binding_path"]
        value = json.loads(originals[path]);value["initial_main_pid"] += 1
        originals[path] = json.dumps(value).encode()
        with self.assertRaisesRegex(EvidenceError, "digest_changed"):
            self.prepare(prior_originals=originals)

    def test_missing_original_binding_is_rejected(self):
        originals = dict(self.originals);originals.pop(next(iter(originals)))
        with self.assertRaisesRegex(EvidenceError, "original_missing"):
            self.prepare(prior_originals=originals)

    def test_wrong_count_and_incomplete_partition_are_rejected(self):
        partitions = copy.deepcopy(self.partitions);partitions[0]["count"] = 206
        with self.assertRaisesRegex(EvidenceError, "partition_count"):
            self.prepare(partitions=partitions)
        partitions[0]["ids"] = partitions[0]["ids"][:206]
        with self.assertRaisesRegex(EvidenceError, "partition_union"):
            self.prepare(partitions=partitions)

    def test_required_leaf_order_is_not_replaced_by_set_equality(self):
        plan = copy.deepcopy(self.plan);plan[0], plan[1] = plan[1], plan[0]
        with self.assertRaisesRegex(EvidenceError, "leaf_union_or_order"):
            self.prepare(runplan=plan)

    def test_duplicate_leaf_and_duplicate_case_are_rejected(self):
        plan = copy.deepcopy(self.plan);plan[1]["name"] = plan[0]["name"]
        with self.assertRaisesRegex(EvidenceError, "preparation_leaf"):
            self.prepare(runplan=plan)
        plan = copy.deepcopy(self.plan);plan[1]["expected_ids"] = plan[0]["expected_ids"]
        with self.assertRaisesRegex(EvidenceError, "leaf_union_or_order"):
            self.prepare(runplan=plan)

    def test_leaf_name_cannot_escape_the_owned_output_directory(self):
        plan = copy.deepcopy(self.plan);plan[0]["name"] = "../foreign"
        with self.assertRaisesRegex(EvidenceError, "preparation_leaf"):
            self.prepare(runplan=plan)

    def test_embedded_worker_mismatch_is_rejected(self):
        with self.assertRaisesRegex(EvidenceError, "embedded_worker_changed"):
            self.prepare(worker_bytes=self.worker+b"# changed\n")

    def test_multiple_dynamic_or_unknown_worker_writers_are_rejected(self):
        for supervisor in [self.supervisor+self.supervisor,
                           b"WORKER.write_text(make_worker(), encoding='utf-8')\n",
                           b"WORKER.writelines('literal')\n"]:
            with self.subTest(supervisor=supervisor):
                with self.assertRaises(EvidenceError):
                    self.prepare(supervisor_bytes=supervisor)

    def test_posix_newline_and_utf8_policy_are_explicit(self):
        for supervisor in [self.supervisor.replace(b"\n", b"\r\n"),
                           b"WORKER.write_text('x', encoding='utf-16')\n",
                           b"WORKER.write_text('x', encoding='utf-8', newline='\\r\\n')\n"]:
            with self.subTest(supervisor=supervisor):
                with self.assertRaises(EvidenceError):
                    self.prepare(supervisor_bytes=supervisor)
        with self.assertRaisesRegex(EvidenceError, "platform_or_bytes"):
            self.prepare(supervisor_platform="windows")

    def test_literal_bytes_writer_has_exact_byte_consistency(self):
        supervisor = ("WORKER.write_bytes("+repr(self.worker)+")\n").encode()
        self.assertTrue(self.prepare(supervisor_bytes=supervisor)["static_embedded_worker_bytes_equal"])

    def test_boolean_and_nonfinite_active_claims_are_rejected(self):
        claims = self.claims();claims["counts"]["selected_cases"] = True
        with self.assertRaises(EvidenceError):
            self.prepare(claims=claims)
        claims = self.claims();claims["counts"]["selected_cases"] = float("nan")
        with self.assertRaisesRegex(EvidenceError, "invalid_json_data"):
            self.prepare(claims=claims)

    def test_tampering_serialized_spec_fails_integrity_check(self):
        spec = self.prepare();spec["current"]["root"] = "0"*40
        with self.assertRaisesRegex(EvidenceError, "content_changed"):
            subject.serialize_preparation(spec)

    def test_recomputed_content_digest_does_not_authorize_kernel_attestation(self):
        spec = self.prepare();spec["kernel_closure_attested"] = True
        spec["sha256"] = digest_json({k: v for k, v in spec.items() if k != "sha256"})
        with self.assertRaisesRegex(EvidenceError, "attestation_outside_scope"):
            subject.serialize_preparation(spec)

    def test_rehashed_unknown_schema_or_extra_attestation_field_is_rejected(self):
        for key, value in [("schema_version", 2), ("schema_version", True),
                           ("build_success_attested", True)]:
            with self.subTest(key=key, value=value):
                spec = self.prepare();spec[key] = value
                spec["sha256"] = digest_json({k: v for k, v in spec.items() if k != "sha256"})
                with self.assertRaisesRegex(EvidenceError, "serialized_schema"):
                    subject.serialize_preparation(spec)

    def test_rehashed_inventory_promotion_is_rejected(self):
        spec = self.prepare();spec["source_inventory"]["test_success_attested"] = True
        spec["sha256"] = digest_json({k: v for k, v in spec.items() if k != "sha256"})
        with self.assertRaisesRegex(EvidenceError, "serialized_inventory_schema"):
            subject.serialize_preparation(spec)

    def test_rehashed_unknown_nested_active_fields_are_rejected(self):
        for field in ["worker", "supervisor", "current"]:
            with self.subTest(field=field):
                spec = self.prepare();spec[field]["kernel_closure_attested"] = True
                spec["sha256"] = digest_json({k: v for k, v in spec.items() if k != "sha256"})
                with self.assertRaisesRegex(EvidenceError, "serialized_object_schema"):
                    subject.serialize_preparation(spec)

    def test_rehashed_recognized_count_and_source_hash_shape_remain_strict(self):
        for fault in ["count", "source_hash", "dirty_closure", "missing_root", "wrong_root_head",
                      "mismatched_child_gitlink"]:
            with self.subTest(fault=fault):
                spec = self.prepare()
                if fault == "count":
                    spec["source_inventory"]["count"] = True
                elif fault == "source_hash":
                    spec["source_inventory"]["files"][CPP]["sha256"] = "not-a-hash"
                elif fault == "dirty_closure":
                    spec["source_inventory"]["source_closure"]["root"]["status"] = " M changed"
                elif fault == "missing_root":
                    del spec["source_inventory"]["source_closure"]["root"]
                elif fault == "wrong_root_head":
                    spec["source_inventory"]["source_closure"]["root"]["head"] = "0"*40
                else:
                    spec["source_inventory"]["source_closure"]["Libraries/Nmsdk-PulseLib"]["head"] = "0"*40
                spec["sha256"] = digest_json({k: v for k, v in spec.items() if k != "sha256"})
                with self.assertRaisesRegex(EvidenceError, "serialized_inventory_schema"):
                    subject.serialize_preparation(spec)

    def test_mutating_caller_plan_cannot_rewrite_prepared_spec(self):
        spec = self.prepare();original = subject.serialize_preparation(spec)
        self.plan[0]["wall_seconds"] += 1
        self.assertEqual(subject.serialize_preparation(spec), original)

    def test_worktree_not_matching_actual_git_is_rejected(self):
        path = self.root/CPP;original = path.read_bytes()
        try:
            path.write_bytes(original+b"\n// metadata fault\n")
            with self.assertRaisesRegex(EvidenceError, "worktree_git_bytes_changed"):
                self.prepare()
        finally:
            path.write_bytes(original)

    def test_repo_module_binds_real_git_source_without_unused_supervisor(self):
        spec = self.prepare_module()
        self.assertEqual(spec["schema_version"], 2)
        self.assertNotIn("supervisor", spec)
        self.assertNotIn("worker", spec)
        self.assertEqual(spec["execution"]["mode"], "repo_module")
        self.assertEqual(spec["execution"]["arguments"], ["--job", "/tmp/План.json"])
        path = self.fixture["repo_module_fixture"].replace(".", "/")+".py"
        raw = self.git("show", self.fixture["root"]+":"+path)
        self.assertEqual(spec["execution"]["source"]["sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(spec["execution"]["source"]["git_blob"],
                         self.git("rev-parse", self.fixture["root"]+":"+path).decode().strip())
        self.assertTrue(spec["module_source_bytes_verified_at_preparation"])
        self.assertFalse(spec["loaded_module_bytes_verified"])
        self.assertEqual(json.loads(subject.serialize_preparation(spec)), spec)

    def test_repo_module_rejects_changed_physical_source(self):
        path = self.root/(self.fixture["repo_module_fixture"].replace(".", "/")+".py")
        original = path.read_bytes()
        try:
            path.write_bytes(original+b"\n# metadata source fault\n")
            with self.assertRaisesRegex(EvidenceError, "module_source_changed"):
                self.prepare_module()
        finally:
            path.write_bytes(original)

    def test_repo_module_rejects_foreign_module_and_untyped_arguments(self):
        for changes in [{"module": "os"}, {"module": "Scripts.StructTrain.TimeLearner...escape"},
                        {"arguments": [True]}, {"arguments": ["bad\nargument"]}]:
            with self.subTest(changes=changes):
                with self.assertRaisesRegex(EvidenceError, "repo_module_declaration"):
                    self.prepare_module(**changes)

    def test_repo_module_rehashed_source_identity_is_still_structured(self):
        for fault in ["commit", "path", "git_blob"]:
            with self.subTest(fault=fault):
                spec = self.prepare_module()
                spec["execution"]["source"][fault] = {"commit": "0"*40,
                    "path": "../foreign.py", "git_blob": "not-a-blob"}[fault]
                spec["sha256"] = digest_json({k: v for k, v in spec.items() if k != "sha256"})
                with self.assertRaisesRegex(EvidenceError, "repo_module_source"):
                    subject.serialize_preparation(spec)

    def test_repo_module_cannot_rehash_itself_into_loaded_execution_evidence(self):
        spec = self.prepare_module();spec["loaded_module_bytes_verified"] = True
        spec["sha256"] = digest_json({k: v for k, v in spec.items() if k != "sha256"})
        with self.assertRaisesRegex(EvidenceError, "attestation_outside_scope"):
            subject.serialize_preparation(spec)

    def test_repo_module_checks_fresh_closure_after_source_read(self):
        changed = copy.deepcopy(self.fixture["closure"])
        changed["root"]["status"] = " M another-file"
        with patch.object(subject, "_clean_closure", return_value=changed):
            with self.assertRaisesRegex(EvidenceError, "source_changed_during_module_capture"):
                self.prepare_module()
