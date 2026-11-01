"""Actual Git worktrees: matching HEAD/status must not hide another worktree."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from ..runtime import source_closure


def git(repository, *args):
    return subprocess.check_output(
        ["git", "-c", "submodule.recurse=false", "-C", str(repository), *args],
        stderr=subprocess.PIPE, text=True).strip()


def initialize(repository):
    repository.mkdir()
    git(repository, "init")
    git(repository, "config", "user.name", "TimeLearner fixture")
    git(repository, "config", "user.email", "fixture@example.invalid")


class SourceClosureAliasTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="timelearner-source-alias-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "root"
        initialize(self.root)
        self.child = self.root / "Bin"
        initialize(self.child)
        (self.child / "model.txt").write_text("declared physical model\n")
        git(self.child, "add", "model.txt")
        git(self.child, "commit", "-m", "Physical model fixture")
        self.child_head = git(self.child, "rev-parse", "HEAD")
        git(self.root, "update-index", "--add", "--cacheinfo", "160000", self.child_head, "Bin")
        git(self.root, "commit", "-m", "Exact child closure")

    def test_real_child_is_accepted(self):
        closure = source_closure(self.root)
        self.assertEqual(closure["Bin"]["head"], self.child_head)
        self.assertEqual(closure["Bin"]["recorded_gitlink"], self.child_head)

    def test_same_head_clean_status_wrong_child_worktree_is_rejected(self):
        other = self.base / "other-child"
        shutil.move(str(self.child), str(other))
        git(other, "config", "core.worktree", str(other))
        self.child.mkdir()
        (self.child / ".git").write_text("gitdir: " + str(other / ".git") + "\n")
        (self.child / "model.txt").write_text("different unverified physical model\n")
        self.assertEqual(git(self.child, "rev-parse", "HEAD"), self.child_head)
        self.assertEqual(git(self.child, "status", "--porcelain", "--untracked-files=no"), "")
        with self.assertRaisesRegex(RuntimeError, "source repository alias mismatch: Bin"):
            source_closure(self.root)

    def test_same_head_wrong_root_worktree_is_rejected(self):
        alias = self.base / "root-alias"
        alias.mkdir()
        git(self.root, "config", "core.worktree", str(self.root))
        (alias / ".git").write_text("gitdir: " + str(self.root / ".git") + "\n")
        self.assertEqual(git(alias, "rev-parse", "HEAD"), git(self.root, "rev-parse", "HEAD"))
        with self.assertRaisesRegex(RuntimeError, "source repository alias mismatch: root"):
            source_closure(alias)


if __name__ == "__main__":
    unittest.main()
