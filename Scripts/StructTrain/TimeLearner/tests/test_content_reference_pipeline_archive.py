"""Compact archive integrity DATA; no claimed native model or process evidence."""
import copy
import hashlib
from pathlib import Path
import tarfile
import tempfile
import unittest

from ..artifact_bundle import verify_pipeline_archive
from ..native_evidence import EvidenceError
from ..portable_primary import create_native_bundle
from . import test_file_source_archive_inventory as inclusion


class ContentReferencePipelineArchiveTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        files=inclusion.FileSourceArchiveInventoryContractTest().files()
        files['00-mirror/a-job.json']=files['run/input/job.json']
        files['00-mirror/b-job.json']=files['run/input/job.json']
        files['00-mirror/result.json']=files['run/run-manifest.json']
        files['zz-forward-job.json']=files['run/input/job.json']
        sources={}
        for name,raw in files.items():
            path=self.root/'source'/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
            sources[name]=path
        self.bundle=create_native_bundle(sources,self.root/'bundle',dictionary_bytes=8*1024**2,
                                         deduplicate_content=True)
        self.sources=sources
        self.archive=self.root/'bundle/primary.tar.xz'

    def test_original_job_and_manifest_can_both_reference_earlier_verified_regular_bytes(self):
        with tarfile.open(self.archive) as tar:
            self.assertTrue(tar.getmember('run/run-manifest.json').islnk())
            self.assertTrue(tar.getmember('run/input/job.json').islnk())
        result=verify_pipeline_archive(self.archive,self.bundle)
        self.assertEqual(result['run_snapshots_verified'],1)
        self.assertEqual(result['archive_members_verified'],8)
        self.assertEqual(result['artifact_entries_verified'],3)
        self.assertIsNone(result['scientific_verdict'])

    def test_legacy_inventory_cannot_authorize_content_links(self):
        legacy={k:self.bundle[k] for k in ('members','archive_bytes','archive_sha256')}
        with self.assertRaisesRegex(EvidenceError,'unexpected_pipeline_archive_member'):
            verify_pipeline_archive(self.archive,legacy)

    def test_original_regular_archive_and_minimal_inventory_remain_supported(self):
        bundle=create_native_bundle(self.sources,self.root/'regular',dictionary_bytes=8*1024**2)
        legacy={k:bundle[k] for k in ('members','archive_bytes','archive_sha256')}
        result=verify_pipeline_archive(self.root/'regular/primary.tar.xz',legacy)
        self.assertEqual(result['run_snapshots_verified'],1)
        self.assertEqual(result['archive_members_verified'],8)

    def test_rehashed_links_to_missing_forward_chain_or_outside_targets_are_rejected(self):
        for target,symlink in (('../escape',False),('missing',False),('zz-forward-job.json',False),
                               ('00-mirror/b-job.json',False),('00-mirror/a-job.json',True)):
            changed=self.root/('changed-'+str(symlink)+'-'+target.replace('/','_')+'.tar.xz')
            with tarfile.open(self.archive) as source,tarfile.open(changed,'w:xz',preset=0) as output:
                for old in source:
                    item=copy.copy(old)
                    if item.name=='run/input/job.json':
                        item.linkname=target;item.type=tarfile.SYMTYPE if symlink else tarfile.LNKTYPE
                    output.addfile(item,source.extractfile(old) if old.isfile() else None)
            descriptor=copy.deepcopy(self.bundle);descriptor.update(archive_bytes=changed.stat().st_size,
                archive_sha256=hashlib.sha256(changed.read_bytes()).hexdigest())
            with self.subTest(target=target,symlink=symlink),self.assertRaises(EvidenceError):
                verify_pipeline_archive(changed,descriptor)

    def test_declared_compression_scheme_and_logical_byte_totals_are_checked(self):
        for key,value in (('expanded_bytes',1),('unique_content_bytes',True)):
            changed=copy.deepcopy(self.bundle);changed[key]=value
            with self.subTest(key=key),self.assertRaisesRegex(EvidenceError,'content_reference_totals'):
                verify_pipeline_archive(self.archive,changed)
        changed=copy.deepcopy(self.bundle);changed['compression']['content_references']='unrestricted-links'
        with self.assertRaises(EvidenceError):verify_pipeline_archive(self.archive,changed)
