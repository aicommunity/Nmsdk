"""Real local Git repositories and receive hooks, executed on validation workers."""
from pathlib import Path
import copy
import subprocess
import tempfile
import unittest

from ..native_evidence import EvidenceError
from ..publisher import publication_plan, publish_closure


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

    def test_dirty_source_and_extra_repository_are_rejected(self):
        (self.root/"unpublished.txt").write_text("not in commit")
        result=publish_closure(self.root,self.spec)
        self.assertEqual(result["publication"],"failed")
        self.assertIn("dirty_publication",result["reason"])

    def test_existing_lock_requires_explicit_recovery(self):
        lock=self.root/".git/timelearner-publication.lock";lock.mkdir()
        with self.assertRaises(EvidenceError):publish_closure(self.root,self.spec)
        self.assertTrue(lock.exists())
