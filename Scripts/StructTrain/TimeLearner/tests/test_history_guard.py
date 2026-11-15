"""Real Git histories, including payloads deleted before the proposed HEAD."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from ..history_guard import check_history


class ExperimentHistoryGuardTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.repo=Path(self.temp.name)/'source';self.repo.mkdir()
        self.git('init','-b','develop');self.git('config','user.name','History guard test')
        self.git('config','user.email','test@invalid.local')
        (self.repo/'code.cpp').write_text('int n = 1;\n')
        self.git('add','.');self.git('commit','-m','code baseline')
        self.baseline=self.git('rev-parse','HEAD')

    def git(self,*args):
        return subprocess.check_output(['git','-C',str(self.repo),*args],stderr=subprocess.STDOUT).decode().strip()

    def payload(self,name,raw):
        path=self.repo/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        self.git('add',name);self.git('commit','-m','record candidate')
        return self.git('rev-parse','HEAD')

    def test_legacy_non_utf8_source_filename_is_preserved(self):
        blob = subprocess.check_output(['git', '-C', str(self.repo), 'hash-object', '-w', '--stdin'],
            input=b'preserved source code').strip()
        tree = subprocess.check_output(['git', '-C', str(self.repo), 'mktree', '-z'],
            input=b'100644 blob '+blob+b'\tlegacy-\xc8.cpp\0').strip()
        commit = subprocess.check_output(['git', '-C', str(self.repo), 'commit-tree', tree.decode(),
            '-p', self.baseline, '-m', 'legacy byte filename']).decode().strip()
        self.assertEqual(check_history(self.repo, commit)['commit'], commit)

    def test_clean_code_and_small_metrics_pass(self):
        head=self.payload('Reports/StructTrain/TimeLearner/run/metrics.json',b'{"validity":"valid"}')
        self.assertEqual(check_history(self.repo,head)['commit'],head)

    def test_deleted_archive_still_blocks_history_reintroduction(self):
        path='Reports/StructTrain/TimeLearner/run/primary.tar.xz'
        self.payload(path,b'compressed fixture')
        self.git('rm',path);self.git('commit','-m','remove payload at tip')
        with self.assertRaisesRegex(ValueError,'binary_experiment_artifact_requires_archive'):
            check_history(self.repo,self.git('rev-parse','HEAD'),old=self.baseline)

    def test_large_text_with_spaces_and_quoted_filename_is_detected(self):
        head=self.payload('Docs/StructTrain/TimeLearner/run/raw "data".json',b'x'*(1024**2+1))
        with self.assertRaisesRegex(ValueError,'large_experiment_artifact_requires_archive'):
            check_history(self.repo,head)

    def test_commit_message_cannot_spoof_a_file_record(self):
        self.git('commit','--allow-empty','-m','data\nM 100644 '+'0'*40+' Reports/StructTrain/TimeLearner/spoof.tar.xz')
        check_history(self.repo,self.git('rev-parse','HEAD'))

    def test_same_blob_at_an_allowed_path_does_not_hide_a_forbidden_path(self):
        raw=b'not real archive; tests the shared-blob path selection'
        self.payload('source.txt',raw)
        head=self.payload('Reports/StructTrain/TimeLearner/run/primary.tar.xz',raw)
        with self.assertRaisesRegex(ValueError,'binary_experiment_artifact_requires_archive'):
            check_history(self.repo,head)

    def test_pre_push_protocol_fails_before_remote_changes(self):
        head=self.payload('Reports/StructTrain/TimeLearner/run/primary.tar.xz',b'archive')
        guard=Path(__file__).parents[1]/'history_guard.py'
        result=subprocess.run([sys.executable,str(guard),'--repository',str(self.repo),'--pre-push'],
            input=('refs/heads/develop '+head+' refs/heads/develop '+'0'*40+'\n').encode(),capture_output=True)
        self.assertEqual(result.returncode,1)
        self.assertIn(b'binary_experiment_artifact_requires_archive',result.stderr)

    def test_shallow_boundary_cannot_hide_old_artifact_ancestry(self):
        self.payload('note.txt',b'next commit')
        partial=Path(self.temp.name)/'partial'
        subprocess.check_output(['git','clone','--depth=1',self.repo.as_uri(),str(partial)],stderr=subprocess.STDOUT)
        with self.assertRaisesRegex(ValueError,'archive_history_guard_full_history_required'):
            check_history(partial,self.git('rev-parse','HEAD'))


if __name__=='__main__':unittest.main()
