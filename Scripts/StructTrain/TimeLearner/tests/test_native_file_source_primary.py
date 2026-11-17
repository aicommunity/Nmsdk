"""Verify the actual compact four-case native archive, not a model surrogate."""
import json
import os
from pathlib import Path, PurePosixPath
import unittest

from ..artifact_bundle import verify_pipeline_archive
from ..collector_provenance import frozen_digest
from ..contained_process import inspect
from ..native_evidence import load


class NativeFileSourcePrimaryTest(unittest.TestCase):
    def test_full_actual_archive_retains_four_pipeline_snapshots_including_file_transport(self):
        root=Path(os.environ['TIMELEARNER_NATIVE_AB_PRIMARY'])
        self.assertTrue(inspect(root/'process/contained')['all_processes_closed'])
        self.assertTrue(load(root/'worker/terminal.json')['operation_passed'])
        packed=root/'worker/packed-primary';bundle=load(packed/'bundle.json')
        before=frozen_digest(packed/'primary.tar.xz',512*1024**2)
        proof=load(root/'worker/primary-bundle-proof.json')
        self.assertEqual(proof['collection_status'],'completed')
        expected={}
        for source in proof['manifest']['roots']:
            for name,record in source['files'].items():
                expected[(PurePosixPath(source['prefix'])/name).as_posix()]=record
            for name,link in source['links'].items():
                target=(PurePosixPath(name).parent/link['link_text']).as_posix()
                expected[(PurePosixPath(source['prefix'])/name).as_posix()]=source['files'][target]
        self.assertEqual(bundle['members'],expected)
        result=verify_pipeline_archive(packed/'primary.tar.xz',bundle,maximum_bytes=2*1024**3)
        self.assertEqual(result['run_snapshots_verified'],4)
        self.assertEqual(result['archive_members_verified'],len(expected))
        self.assertGreaterEqual(len(expected),809)
        self.assertIsNone(result['scientific_verdict'])
        self.assertEqual(before,frozen_digest(packed/'primary.tar.xz',512*1024**2))
        target=Path(os.environ['TMPDIR'])/'actual-native-ab-archive-verification.json'
        with target.open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(result,stream,indent=2);stream.write('\n')
