"""Restore actual closed six-run bytes before production primary audits."""
import os
from pathlib import Path
import tempfile
import unittest

from ..native_characterization import audit_execution
from ..native_calibration_worker import _write
from ..native_evidence import EvidenceError, load
from ..portable_primary import ALIAS_ADAPTER, restore_native_bundle
from ..source_envelope_bundle import create


class SourceEnvelopeBundleRecordedTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(os.environ['TIMELEARNER_SOURCE_ENVELOPE_RECORDED']).resolve(strict=True)
        cls.sources={p.relative_to(cls.root).as_posix():p for p in cls.root.rglob('*') if p.is_file()}
        cls.folders=sorted(cls.root.iterdir())
        if len(cls.folders)!=6:raise AssertionError('requires all six actual closed run directories')
        cls.rows=[dict(target=folder.name+'/'+suffix,source=folder.name+'/input/source/train_stopped_state.json')
                  for folder in cls.folders for suffix in ('input/job.json','native/job.json')]

    def test_full_actual_corpus_restores_before_all_six_production_audits(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            packed=create(self.sources,self.rows,root/'packed',maximum_total_bytes=1024**3)
            self.assertEqual(packed['factored_files'],12)
            self.assertEqual(packed['literal_fallbacks'],{})
            restored=restore_native_bundle(root/'packed/bundle.json',root/'restored',compatibility=ALIAS_ADAPTER)
            self.assertTrue(restored['all_primary_bytes_verified'])
            self.assertEqual(restored['reconstructed_job_files'],12)
            self.assertFalse(restored['run_manifests_rewritten'])
            self.assertFalse(restored['native_execution_attested'])
            for folder in self.folders:
                result=audit_execution(root/'restored'/folder.name/'native')
                self.assertTrue(result['primary_evidence_checked'])
                self.assertEqual(result['execution'],'completed')

    def test_changed_recipe_is_refused_before_restore_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);row=self.rows[0]
            sources={n:self.sources[n] for n in (row['target'],row['source'])}
            create(sources,[row],root/'packed',maximum_total_bytes=128*1024**2)
            index=load(root/'packed/bundle.json');path=root/'packed'/index['recipes'][row['target']]['path']
            path.write_bytes(path.read_bytes()+b' ')
            with self.assertRaises(EvidenceError):
                restore_native_bundle(root/'packed/bundle.json',root/'restored')
            self.assertFalse((root/'restored').exists())

    def test_unsupported_job_stays_literal_without_losing_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);row=self.rows[0]
            original=self.sources[row['target']].read_bytes().replace(b'"source_stopped":',b'"different_source":',1)
            path=root/'literal-job.json';path.write_bytes(original)
            sources={row['target']:path,row['source']:self.sources[row['source']]}
            packed=create(sources,[row],root/'packed',maximum_total_bytes=128*1024**2)
            self.assertEqual(packed['factored_files'],0)
            self.assertEqual(packed['literal_fallbacks'],{row['target']:'unsupported_encoding'})
            restored=restore_native_bundle(root/'packed/bundle.json',root/'restored')
            self.assertTrue(restored['all_primary_bytes_verified'])
            self.assertEqual((root/'restored'/row['target']).read_bytes(),original)

    def test_reference_to_another_recipe_target_is_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);a,b=self.rows[:2]
            rows=[dict(target=a['target'],source=b['target']),dict(target=b['target'],source=a['target'])]
            with self.assertRaises(EvidenceError):
                create(self.sources,rows,root/'packed',maximum_total_bytes=1024**3)
            self.assertFalse((root/'packed').exists())

    def test_manifest3_roles_and_legacy_manifest1_are_validated(self):
        from ..archive_retirement import snapshot
        from ..closed_primary_bundle import validate_manifest
        from ..contained_process import inspect
        snap=snapshot(self.root.parent,[self.root.name])
        files={n:dict(bytes=r['bytes'],sha256=r['sha256']) for n,r in snap['regular'][self.root.name].items()}
        units=[]
        for path in self.root.rglob('owned-unit.json'):
            state=inspect(path.parent)
            self.assertTrue(state['all_processes_closed'])
            units.append(dict(directory=str(path.parent),binding=state['binding']))
        self.assertEqual(len(units),6)
        manifest=dict(kind='timelearner_closed_primary_bundle',schema_version=3,
            base='/media/user/Data/TimeLearnerRefactor',roots=[dict(directory=str(self.root),prefix='runs',
                files=files,links=snap['links'][self.root.name])],closed_units=units,
            bounds=dict(maximum_file_bytes=64*1024**2,maximum_total_bytes=1024**3,
                        maximum_archive_bytes=128*1024**2),scientific_verdict=None,
            source_envelopes=[dict(target='runs/'+r['target'],source='runs/'+r['source']) for r in self.rows])
        self.assertEqual(validate_manifest(manifest),[self.root])
        legacy={k:v for k,v in manifest.items() if k!='source_envelopes'};legacy['schema_version']=1
        self.assertEqual(validate_manifest(legacy),[self.root])
        bad=dict(manifest,source_envelopes=[dict(target='runs/missing.json',source='runs/missing-source.json')])
        with self.assertRaises(EvidenceError):validate_manifest(bad)


class SourceEnvelopeProducedTest(unittest.TestCase):
    def test_actual_manifest3_collector_package_restores_before_primary_audits(self):
        package=Path(os.environ['TIMELEARNER_SOURCE_ENVELOPE_PRODUCED']).resolve(strict=True)
        previous=Path(os.environ['TIMELEARNER_SOURCE_ENVELOPE_LEGACY_PACKAGE']).resolve(strict=True)
        index=load(package/'bundle.json')
        self.assertEqual(len(index['recipes']),18)
        self.assertEqual(index['literal_fallbacks'],{})
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            result=restore_native_bundle(package/'bundle.json',root/'restored',compatibility=ALIAS_ADAPTER)
            self.assertTrue(result['all_primary_bytes_verified'])
            self.assertEqual(result['reconstructed_job_files'],18)
            runs=root/'restored/console-six-a4/worker/tmp/native-burst-readback-small/runs'
            cases=[]
            for topology in ('Classic','Branch'):
                for variant in ('replay','matched','changed'):
                    audit=audit_execution(runs/(topology+'-'+variant)/'native')
                    self.assertEqual(audit['execution'],'completed')
                    self.assertTrue(audit['primary_evidence_checked'])
                    cases.append(topology+'-'+variant)
            _write(Path(os.environ['TMPDIR'])/'source-envelope-produced-proof.json',
                dict(kind='source_envelope_produced_package_restore',schema_version=1,
                    restored=result,primary_audits=cases,original_members=len(index['members']),
                    schema3_package_bytes=sum(p.stat().st_size for p in package.rglob('*') if p.is_file()),
                    legacy_package_bytes=sum(p.stat().st_size for p in previous.rglob('*') if p.is_file()),
                    original_manifests_rewritten=False,native_execution_attested=False,scientific_verdict=None))
