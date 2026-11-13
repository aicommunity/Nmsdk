"""Production CLI retrieval357 and last-record restored-path rejection; Git only."""
import contextlib
import hashlib
import io
import os
from pathlib import Path
import unittest

from ..__main__ import main
from ..native_evidence import load, parse_json_bytes
from ..native_calibration_worker import _write


def git_metadata_snapshot(root):
    root=Path(root)
    result={}
    for p in sorted((root/'.git').rglob('*')):
        if p.is_file():
            if p.is_symlink():
                raise AssertionError('metadata fixture must not use symlinks')
            raw=p.read_bytes()
            result[p.relative_to(root).as_posix()]=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    return result


class CurrentScriptMigrationCliTest(unittest.TestCase):
    def test_all357_exact_history_records_and_restored_last_path_negative(self):
        controls=Path(os.environ['TIMELEARNER_MIGRATION357_CONTROLS'])
        spec=load(controls/'declaration.json')
        repositories={name:Path(os.environ[env]) for name,env in spec['repository_fixtures'].items()}
        before={k:git_metadata_snapshot(p) for k,p in repositories.items()}
        output=Path(os.environ['TMPDIR'])/'migration357-cli'
        output.mkdir()
        common=['--root',str(repositories['root']),'--map',str(controls/'revision-map.json'),
                '--bin-repository',str(repositories['Bin']),
                '--pulselib-repository',str(repositories['PulseLib'])]
        def invoke(revision,path):
            stdout=io.StringIO();stderr=io.StringIO()
            with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
                code=main(['history','verify-migration',revision,*common,'--output',str(path)])
            return code,stdout.getvalue(),stderr.getvalue()
        positive=output/'positive.json'
        code,stdout,stderr=invoke(spec['target_root'],positive)
        self.assertEqual(code,0,stderr)
        proof=load(positive)
        self.assertEqual(proof,parse_json_bytes(stdout.encode()))
        self.assertEqual(proof['source_records_verified'],357)
        self.assertEqual(len(proof['checks']),357)
        self.assertFalse(proof['manifest_declares_complete'])
        self.assertFalse(proof['whole_migration_attested'])
        self.assertFalse(proof['runtime_equivalence_attested'])
        self.assertTrue(all(r['old_path_absent'] for r in proof['checks']))
        last=[r for r in proof['checks'] if r['repository']=='root' and r['old_path']==spec['last_retired_path']]
        self.assertEqual(len(last),1)
        self.assertEqual(last[0]['blob_sha1'],spec['last_blob_sha1'])
        negative=output/'negative-must-not-exist.json'
        code,stdout,stderr=invoke(spec['restored_path_negative_revision'],negative)
        self.assertEqual(code,2,stderr)
        self.assertEqual(stdout,'')
        self.assertFalse(negative.exists())
        reason=parse_json_bytes(stderr.encode())
        self.assertEqual(reason['status'],'invalid')
        self.assertEqual(reason['reason'],'migration_old_path_still_present:'+spec['last_retired_path'])
        self.assertIsNone(reason['scientific_verdict'])
        self.assertEqual(before,{k:git_metadata_snapshot(p) for k,p in repositories.items()})
        _write(output/'restored-path-negative.json',reason)
        _write(output/'result.json',dict(kind='production_migration357_cli_result',schema_version=1,
            target_root=spec['target_root'],source_records_verified=357,last_record_verified=True,
            restored_last_path_rejected=True,git_metadata_unchanged=True,
            archived_scripts_materialized_or_executed=False,new_model_execution=False,
            whole_migration_attested=False,scientific_verdict=None))
