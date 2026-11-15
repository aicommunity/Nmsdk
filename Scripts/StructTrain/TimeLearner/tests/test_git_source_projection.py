"""Real Git pack/checkout/status, including policy files outside selection."""
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest

from ..git_source_projection import build_projection


class GitSourceProjectionTest(unittest.TestCase):
    def fixture(self, root):
        source = root/'source'; source.mkdir()
        def git(*args, **kwargs):
            return subprocess.check_output(['git', '-C', str(source), *args], **kwargs)
        git('init', '--quiet'); git('config', 'user.name', 'Projection Fixture')
        git('config', 'user.email', 'projection@localhost'); git('config', 'core.autocrlf', 'false')
        files = {'.gitignore': b'*.cache\n', '.gitattributes': b'* -text\n',
                 '.gitmodules': b'[submodule "unused"]\n path = unused\n url = ../unused\n',
                 'Scripts/Code/.gitignore': b'*.generated\n',
                 'Scripts/Code/проверка.py': b'VALUE = 1\n', 'Other/hidden.txt': b'not selected\n',
                 'Other/.gitattributes': b'*.txt -text\n'}
        for name, raw in files.items():
            path = source/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
        git('add', '.'); git('commit', '--quiet', '-m', 'fixture')
        return source, git('rev-parse', 'HEAD').decode().strip(), files

    def test_checkout_and_strict_status_work_without_promisor_remote(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); source, commit, files = self.fixture(root); pack = root/'projection.pack'
            result = build_projection(source, commit, ['Scripts/Code/'], pack)
            destination = root/'destination'
            subprocess.check_call(['git', 'init', '--quiet', str(destination)])
            def git(*args, **kwargs):
                return subprocess.check_output(['git', '-C', str(destination), *args], **kwargs)
            with pack.open('rb') as stream:
                git('index-pack', '--stdin', '--promisor', stdin=stream)
            (destination/'.git/shallow').write_bytes((commit+'\n').encode())
            git('config', 'core.autocrlf', 'false'); git('config', 'core.repositoryformatversion', '1')
            git('config', 'extensions.partialClone', 'origin'); git('config', 'remote.origin.promisor', 'true')
            git('sparse-checkout', 'init', '--no-cone')
            git('sparse-checkout', 'set', '--no-cone', '!/*', '/Scripts/Code/')
            git('-c', 'submodule.recurse=false', 'checkout', '--detach', commit)
            self.assertEqual(git('status', '--porcelain', '--untracked-files=all', '--ignore-submodules=all'), b'')
            self.assertEqual((destination/'Scripts/Code/проверка.py').read_bytes(), files['Scripts/Code/проверка.py'])
            self.assertFalse((destination/'Other/hidden.txt').exists())
            for name in ('.gitignore', '.gitattributes', '.gitmodules', 'Other/.gitattributes'):
                self.assertEqual(git('show', commit+':'+name), files[name])
                self.assertIn(name, result['git_policy_files'])
            self.assertEqual(result['pack']['sha256'], hashlib.sha256(pack.read_bytes()).hexdigest())
            self.assertFalse(result['full_SDK_verified']); self.assertIsNone(result['scientific_verdict'])

    def test_pack_output_is_new_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); source, commit, _ = self.fixture(root); output = root/'existing'
            output.write_bytes(b'preserve')
            with self.assertRaises(FileExistsError):
                build_projection(source, commit, ['Scripts/Code/'], output)
            self.assertEqual(output.read_bytes(), b'preserve')

    def test_invalid_revision_and_unsafe_selection_fail_before_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); source, commit, _ = self.fixture(root)
            for revision, prefixes in [('HEAD', ['Scripts/Code/']), (commit, ['../outside/']),
                                       (commit, ['missing/'])]:
                with self.subTest(revision=revision, prefixes=prefixes):
                    output = root/'absent'
                    with self.assertRaises(ValueError):
                        build_projection(source, revision, prefixes, output)
                    self.assertFalse(output.exists())
