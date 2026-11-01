"""Real local Git repositories and receive hooks, executed on validation workers."""
from pathlib import Path
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest

from ..native_evidence import EvidenceError
from ..publisher import publication_plan, publish_closure, stage_artifact_set


def git(path, *args):
    return subprocess.check_output(["git", "-C", str(path), *args], stderr=subprocess.STDOUT, text=True).strip()


class PublisherTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base/"root";self.root.mkdir()
        git(self.root, "init", "-b", "develop")
        git(self.root, "config", "user.name", "Publication test")
        git(self.root, "config", "user.email", "test@localhost")
        self.remote = self.base/"root.git";self.remote.mkdir();git(self.remote, "init", "--bare")
        git(self.root, "remote", "add", "origin", str(self.remote))
        for name in ("A", "B"):
            source=self.base/(name+"-source");source.mkdir();git(source,"init","-b","develop")
            git(source,"config","user.name","Publication test");git(source,"config","user.email","test@localhost")
            (source/"model.txt").write_text(name)
            git(source,"add","model.txt");git(source,"commit","-m","initial model")
            remote=self.base/(name+".git");remote.mkdir();git(remote,"init","--bare")
            git(source,"push",str(remote),"develop:refs/heads/develop")
            git(remote,"symbolic-ref","HEAD","refs/heads/develop")
            git(self.root,"-c","protocol.file.allow=always","submodule","add",str(remote),name)
        (self.root/"result.json").write_text('{"execution":"completed"}\n')
        git(self.root,"add",".");git(self.root,"commit","-m","record exact child models and result")
        self.spec={"kind":"timelearner_git_publication","schema_version":1,"repositories":[
            {"path":name,"commit":git(self.root/name,"rev-parse","HEAD"),"remote":"origin","branch":"refs/heads/develop"}
            for name in ("A","B",".")]}

    def test_children_first_and_idempotent(self):
        self.assertEqual([r[1]["path"] for r in publication_plan(self.root,self.spec)],["A","B","."])
        for _ in range(2):
            result=publish_closure(self.root,self.spec)
            self.assertEqual(result["publication"],"published",result)
            self.assertEqual([r["path"] for r in result["repositories"]],["A","B","."])
            self.assertIsNone(result["scientific_verdict"])
        self.assertEqual(git(self.remote,"rev-parse","refs/heads/develop"),git(self.root,"rev-parse","HEAD"))

    def _artifact_set(self, *, stage=True, sparse=False):
        (self.root/".gitignore").write_text("*.png\n")
        git(self.root,"add",".gitignore");git(self.root,"commit","-m","ignore derived images")
        if sparse:
            git(self.root,"sparse-checkout","init","--cone")
            git(self.root,"sparse-checkout","set","Docs")
        directory=self.root/"Reports/run";directory.mkdir(parents=True)
        (directory/"selected").mkdir()
        image=directory/"selected/trace[1].png";image.write_bytes(b"opaque selected image bytes")
        manifest=directory/"SHA256SUMS.json"
        manifest.write_text(json.dumps({"selected/trace[1].png":hashlib.sha256(image.read_bytes()).hexdigest()})+"\n")
        digest=hashlib.sha256(manifest.read_bytes()).hexdigest()
        if stage:
            result=stage_artifact_set(self.root,"Reports/run/SHA256SUMS.json",digest)
            self.assertEqual(result["files_staged"],2)
            self.assertFalse(result["committed"])
        else:
            git(self.root,"add","--sparse","Reports/run/SHA256SUMS.json")
        git(self.root,"commit","-m","record artifact inventory")
        self.spec["schema_version"]=2
        self.spec["artifacts"]=[{"repository":".","manifest":"Reports/run/SHA256SUMS.json","manifest_sha256":digest}]
        for record in self.spec["repositories"]:
            record["push_url"]=git(self.root/record["path"],"remote","get-url","origin")
            record["commit"]=git(self.root/record["path"],"rev-parse","HEAD")
        return image,manifest

    def test_sparse_selected_ignored_artifact_is_staged_and_published(self):
        self._artifact_set(sparse=True)
        for _ in range(2):
            result=publish_closure(self.root,self.spec)
            self.assertEqual(result["publication"],"published",result)
            self.assertEqual(result["schema_version"],2)
            self.assertEqual(result["artifact_sets_verified"],self.spec["artifacts"])
        self.assertEqual(git(self.remote,"show","refs/heads/develop:Reports/run/selected/trace[1].png"),
                         "opaque selected image bytes")

    def test_ignored_uncommitted_image_blocks_every_push(self):
        self._artifact_set(stage=False)
        result=publish_closure(self.root,self.spec)
        self.assertEqual(result["publication"],"failed")
        self.assertIn("missing_committed_artifact",result["reason"])
        self.assertEqual(result["repositories_published_before_failure"],[])
        self.assertEqual(git(self.remote,"for-each-ref","--format=%(refname)"),"")

    def test_changed_committed_image_cannot_keep_previous_inventory(self):
        image,_=self._artifact_set();image.write_bytes(b"changed")
        git(self.root,"add","-f",str(image));git(self.root,"commit","-m","changed artifact")
        self.spec["repositories"][-1]["commit"]=git(self.root,"rev-parse","HEAD")
        result=publish_closure(self.root,self.spec)
        self.assertEqual(result["publication"],"failed")
        self.assertIn("committed_artifact_content_changed",result["reason"])

    def test_explicit_same_repository_push_target_does_not_change_remote_config(self):
        self._artifact_set()
        for record in self.spec["repositories"]:
            git(self.root/record["path"],"config","remote.origin.pushurl",str(self.base/"missing.git"))
        result=publish_closure(self.root,self.spec)
        self.assertEqual(result["publication"],"published",result)
        self.assertEqual(git(self.root,"remote","get-url","--push","origin"),str(self.base/"missing.git"))

    def test_wrong_explicit_push_repository_is_rejected_before_push(self):
        self._artifact_set();self.spec["repositories"][-1]["push_url"]=str(self.base/"other.git")
        result=publish_closure(self.root,self.spec)
        self.assertEqual(result["publication"],"failed")
        self.assertIn("explicit_push_repository_mismatch",result["reason"])

    def test_duplicate_and_traversal_manifest_entries_are_rejected(self):
        _,manifest=self._artifact_set()
        for raw in ('{"x":"'+'0'*64+'","x":"'+'0'*64+'"}', '{"../outside":"'+'0'*64+'"}'):
            manifest.write_text(raw)
            before=git(self.root,"diff","--cached")
            with self.assertRaises(EvidenceError):
                stage_artifact_set(self.root,"Reports/run/SHA256SUMS.json",hashlib.sha256(manifest.read_bytes()).hexdigest())
            self.assertEqual(git(self.root,"diff","--cached"),before)

    def test_working_symlink_is_rejected_without_staging(self):
        image,manifest=self._artifact_set();image.unlink();image.symlink_to(self.root/"result.json")
        with self.assertRaisesRegex(EvidenceError,"artifact_missing_or_symlink"):
            stage_artifact_set(self.root,"Reports/run/SHA256SUMS.json",hashlib.sha256(manifest.read_bytes()).hexdigest())

    def test_artifact_verification_uses_original_objects_not_local_replacements(self):
        self._artifact_set()
        original=git(self.root,"rev-parse","HEAD:Reports/run/selected/trace[1].png")
        fake=subprocess.check_output(["git","-C",str(self.root),"hash-object","-w","--stdin"],input=b"replacement").decode().strip()
        git(self.root,"replace",original,fake)
        result=publish_closure(self.root,self.spec)
        self.assertEqual(result["publication"],"published",result)
        self.assertEqual(git(self.remote,"show","refs/heads/develop:Reports/run/selected/trace[1].png"),
                         "opaque selected image bytes")

    def _reject(self, remote):
        hook=remote/"hooks/pre-receive";hook.write_text('#!/bin/sh\necho deliberate_test_rejection >&2\nexit 1\n')
        hook.chmod(0o755)

    def test_child_push_failure_prevents_root_push(self):
        # Make A actually change: an up-to-date push never invokes receive hooks.
        child=self.root/"A"
        git(child,"config","user.name","Publication test");git(child,"config","user.email","test@localhost")
        (child/"model.txt").write_text("changed model")
        git(child,"add",".");git(child,"commit","-m","changed child")
        git(self.root,"add","A");git(self.root,"commit","-m","record changed child")
        self.spec["repositories"][0]["commit"]=git(child,"rev-parse","HEAD")
        self.spec["repositories"][2]["commit"]=git(self.root,"rev-parse","HEAD")
        self._reject(self.base/"A.git")
        result=publish_closure(self.root,self.spec)
        self.assertEqual(result["publication"],"failed")
        self.assertEqual(result["repositories_published_before_failure"],[])
        self.assertEqual(git(self.remote,"for-each-ref","--format=%(refname)"),"")

    def test_root_rejection_is_not_published_success(self):
        self._reject(self.remote)
        result=publish_closure(self.root,self.spec)
        self.assertEqual(result["publication"],"failed")
        self.assertEqual([r["path"] for r in result["repositories_published_before_failure"]],["A","B"])
        self.assertEqual(git(self.remote,"for-each-ref","--format=%(refname)"),"")

    def test_missing_or_wrong_child_commit_is_preflight_failure(self):
        for mutation in ("missing","wrong"):
            spec=copy.deepcopy(self.spec)
            if mutation=="missing":spec["repositories"].pop(0)
            else:spec["repositories"][0]["commit"]="0"*40
            result=publish_closure(self.root,spec)
            self.assertEqual(result["publication"],"failed")
            self.assertEqual(result["repositories_published_before_failure"],[])

    def test_dirty_source_is_rejected(self):
        (self.root/"unpublished.txt").write_text("not in commit")
        result=publish_closure(self.root,self.spec)
        self.assertEqual(result["publication"],"failed")
        self.assertIn("dirty_publication",result["reason"])

    def test_wrong_child_remote_does_not_claim_checkout_reproducibility(self):
        git(self.root/"A","remote","set-url","origin",str(self.base/"B.git"))
        result=publish_closure(self.root,self.spec)
        self.assertEqual(result["publication"],"failed")
        self.assertIn("child_remote_differs",result["reason"])
        self.assertEqual(result["repositories_published_before_failure"],[])

    def test_real_cli_receipt_and_existing_receipt_guard(self):
        spec=self.base/"publication.json";spec.write_text(json.dumps(self.spec))
        receipt=self.base/"receipt.json"
        command=[sys.executable,"-m","Scripts.StructTrain.TimeLearner","publish",str(spec),
                 "--root",str(self.root),"--output",str(receipt)]
        result=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(receipt.read_text())["publication"],"published")
        before=receipt.read_bytes()
        result=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertEqual(receipt.read_bytes(),before)

    def test_existing_lock_requires_explicit_recovery(self):
        lock=self.root/".git/timelearner-publication.lock";lock.mkdir()
        with self.assertRaises(EvidenceError):publish_closure(self.root,self.spec)
        self.assertTrue(lock.exists())
