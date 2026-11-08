"""Publication policy over real Git indexes, commits, children and local remotes."""
from pathlib import Path
import base64
import hashlib
import json
import lzma
import os
import unittest

from . import test_publisher as fixtures
from ..native_evidence import EvidenceError
from ..publisher import (LOOSE_REPORT_SCRIPT_SUFFIXES, publication_plan,
                         publish_closure, stage_artifact_set, verify_artifact_set)


class ReportArtifactPolicyTest(unittest.TestCase):
    def setUp(self):
        # Reuse the existing real three-repository fixture without inheriting or
        # rediscovering its test methods in this module.
        fixtures.PublisherTest.setUp(self)

    def _inventory(self, payloads, *, prefix='Reports/StructTrain/TimeLearner/run',
                   manifest_name='SHA256SUMS.json'):
        folder = self.root/prefix; folder.mkdir(parents=True, exist_ok=True)
        for name, raw in payloads.items():
            path = folder/name; path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        manifest = folder/manifest_name
        manifest.write_text(json.dumps({name: hashlib.sha256(raw).hexdigest()
                                        for name, raw in payloads.items()})+'\n')
        return manifest.relative_to(self.root).as_posix(), hashlib.sha256(manifest.read_bytes()).hexdigest()

    def _remotes(self):
        return {name: fixtures.git(self.base/(name+'.git') if name != 'root' else self.remote,
                                   'for-each-ref', '--format=%(refname) %(objectname)')
                for name in ('root', 'A', 'B')}

    def _stage_refused(self, manifest, digest, reason):
        before = fixtures.git(self.root, 'diff', '--cached', '--raw', '-z')
        remotes = self._remotes()
        with self.assertRaisesRegex(EvidenceError, 'loose_report_script_forbidden:'+reason):
            stage_artifact_set(self.root, manifest, digest)
        self.assertEqual(fixtures.git(self.root, 'diff', '--cached', '--raw', '-z'), before)
        self.assertEqual(self._remotes(), remotes)

    def _commit(self, manifest, digest, *, executable=None, change_child=False):
        if change_child:
            child = self.root/'A'
            fixtures.git(child, 'config', 'user.name', 'Policy test')
            fixtures.git(child, 'config', 'user.email', 'test@localhost')
            (child/'model.txt').write_text('new child model, not yet published')
            fixtures.git(child, 'add', 'model.txt'); fixtures.git(child, 'commit', '-m', 'pending child')
            fixtures.git(self.root, 'add', 'A')
        folder = Path(manifest).parent
        inventory = json.loads((self.root/manifest).read_text())
        fixtures.git(self.root, 'add', '--force', '--', manifest,
                     *((folder/name).as_posix() for name in inventory))
        if executable is not None:
            fixtures.git(self.root, 'update-index', '--chmod=+x', (folder/executable).as_posix())
            if os.name != 'nt':
                path = self.root/folder/executable
                path.chmod(path.stat().st_mode | 0o111)
        fixtures.git(self.root, 'commit', '-m', 'record explicit artifact fixture')
        self.spec['schema_version'] = 2
        self.spec['artifacts'] = [{'repository': '.', 'manifest': manifest, 'manifest_sha256': digest}]
        for record in self.spec['repositories']:
            record['push_url'] = fixtures.git(self.root/record['path'], 'remote', 'get-url', 'origin')
            record['commit'] = fixtures.git(self.root/record['path'], 'rev-parse', 'HEAD')

    def _publish_refused(self, reason):
        before = self._remotes(); index = fixtures.git(self.root, 'diff', '--cached', '--raw', '-z')
        result = publish_closure(self.root, self.spec)
        self.assertEqual(result['publication'], 'failed', result)
        self.assertIn('loose_report_script_forbidden:'+reason, result['reason'])
        self.assertEqual(result['repositories_published_before_failure'], [])
        self.assertEqual(self._remotes(), before)
        self.assertEqual(fixtures.git(self.root, 'diff', '--cached', '--raw', '-z'), index)

    def test_compact_archive_models_metrics_and_selected_figures_publish(self):
        png = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jH0kAAAAASUVORK5CYII=')
        payloads = {'primary.tar.xz': lzma.compress(b'#!/bin/sh\necho archived producer\n'),
                    'model.bin': b'\x00model\x00#!not-a-first-line-shebang',
                    'model.xml': b'<model/>\n', 'metrics.json': b'{"validity":"valid"}\n',
                    'trials.csv': b'trial_id,hit\ntarget,1\n',
                    'selected/trace.PY.png': png,
                    'selected/trace.svg': b'<svg xmlns="http://www.w3.org/2000/svg"/>',
                    'selected/trace.pdf': b'%PDF-1.4\n% policy fixture; not a visual-quality claim\n'}
        manifest, digest = self._inventory(payloads)
        result = stage_artifact_set(self.root, manifest, digest)
        self.assertEqual(result['files_staged'], len(payloads)+1)
        self._commit(manifest, digest)
        result = publish_closure(self.root, self.spec)
        self.assertEqual(result['publication'], 'published', result)
        self.assertEqual(fixtures.git(self.remote, 'rev-parse', 'refs/heads/develop'),
                         fixtures.git(self.root, 'rev-parse', 'HEAD'))

    def test_every_known_script_suffix_is_refused_before_staging(self):
        for suffix in sorted(LOOSE_REPORT_SCRIPT_SUFFIXES):
            with self.subTest(suffix=suffix):
                manifest, digest = self._inventory({'nested/Runner'+suffix.upper(): b'plain source bytes'})
                self._stage_refused(manifest, digest, 'suffix')

    def test_unknown_suffix_shebang_and_utf8_bom_are_refused_before_staging(self):
        for raw in (b'#!/usr/bin/env python3\npass\n', b'\xef\xbb\xbf#!/bin/sh\nexit 0\n'):
            with self.subTest(raw=raw):
                manifest, digest = self._inventory({'nested/snapshot.dat': raw})
                self._stage_refused(manifest, digest, 'shebang')

    def test_casefolded_scope_and_nested_paths_are_refused(self):
        manifest, digest = self._inventory({'controller/deep/Launcher.Py': b'pass\n'},
            prefix='rEpOrTs/sTrUcTtRaIn/tImElEaRnEr/run')
        self._stage_refused(manifest, digest, 'suffix')

    def test_script_named_inventory_is_refused_before_staging(self):
        manifest, digest = self._inventory({'metrics.json': b'{}'}, manifest_name='job.PS1')
        self._stage_refused(manifest, digest, 'suffix')

    def test_committed_script_suffix_blocks_pending_child_and_root_pushes(self):
        manifest, digest = self._inventory({'nested/job.Ps1': b'Write-Output done'})
        self._commit(manifest, digest, change_child=True)
        self._publish_refused('suffix')

    def test_committed_shebang_without_script_suffix_blocks_all_pushes(self):
        manifest, digest = self._inventory({'controller/snapshot.dat': b'#!/bin/sh\nexit 0\n'})
        self._commit(manifest, digest, change_child=True)
        self._publish_refused('shebang')

    def test_git_executable_binary_mode_blocks_all_pushes(self):
        manifest, digest = self._inventory({'model.bin': b'\x00\xffbinary fixture, not a model claim'})
        self._commit(manifest, digest, executable='model.bin', change_child=True)
        self._publish_refused('git_executable_mode')

    def test_tracked_git_executable_mode_is_refused_before_staging(self):
        manifest, digest = self._inventory({'payload.bin': b'\x00payload'})
        self._commit(manifest, digest, executable='payload.bin')
        self._stage_refused(manifest, digest, 'git_executable_mode')

    def test_readonly_historical_verification_preserves_old_script_evidence(self):
        manifest, digest = self._inventory({'producer.py': b'print("historical source")\n'})
        self._commit(manifest, digest)
        record = self.spec['artifacts'][0]
        self.assertEqual(verify_artifact_set(self.root, fixtures.git(self.root, 'rev-parse', 'HEAD'),
                                            record)['files_verified'], 2)
        self.assertEqual(len(publication_plan(self.root, self.spec)), 3)
        self._publish_refused('suffix')

    def test_active_project_build_script_outside_report_scope_is_unchanged(self):
        manifest, digest = self._inventory({'build.py': b'#!/usr/bin/env python3\npass\n'},
                                            prefix='Rdk/Tools')
        self.assertEqual(stage_artifact_set(self.root, manifest, digest)['files_staged'], 2)
        self._commit(manifest, digest)
        self.assertEqual(publish_closure(self.root, self.spec)['publication'], 'published')

    def test_refusal_keeps_callers_existing_staged_changes(self):
        (self.root/'user-note.txt').write_text('preexisting staged change')
        fixtures.git(self.root, 'add', 'user-note.txt')
        manifest, digest = self._inventory({'launcher.sh': b'echo old launcher\n'})
        self._stage_refused(manifest, digest, 'suffix')


if __name__ == '__main__':
    unittest.main()
