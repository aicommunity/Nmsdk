"""Read the actual closed four-cell native corpus after independent recovery."""
from copy import deepcopy
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from ..external_archive import locate, resolve
from ..native_continuity_reports import analyze_fixture, read_fixture
from ..native_evidence import EvidenceError, load
from ..portable_primary import RETAIN_ALIASES, restore_native_bundle
from ..runtime import file_record


class NativeContinuityPrimaryRestorationTest(unittest.TestCase):
    def test_all_original_bytes_four_measured_controls_and_rejections(self):
        package = Path(os.environ['TIMELEARNER_NATIVE_CONTINUITY_PACKAGE'])
        metadata = locate(package/'bundle.json');bundle = load(metadata)
        reference = load(package/'primary.tar.xz.archive.json');archive = resolve(reference)
        self.assertEqual(reference['sha256'], 'ab7f007152e9ee041c28f1de7a7721e8945ffc2fd8abdcdeea3198bbabef585d')
        self.assertEqual(bundle['archive_sha256'], reference['sha256'])
        self.assertEqual(len(bundle['members']), 114)
        self.assertEqual(bundle['expanded_bytes'], 37366223)
        before = file_record(archive);rows=[];figures=[]
        with tempfile.TemporaryDirectory(prefix='native-continuity-restore-',dir=os.environ['TMPDIR']) as temporary:
            local = Path(temporary)/'package';local.mkdir()
            (local/'bundle.json').write_bytes(metadata.read_bytes())
            (local/'primary.tar.xz.archive.json').write_text(json.dumps(reference),encoding='utf-8')
            restored = Path(temporary)/'restored'
            recovery = restore_native_bundle(local/'bundle.json',restored,compatibility=RETAIN_ALIASES)
            self.assertEqual(recovery['archive_members_verified'],114)
            self.assertEqual(recovery['retained_regular_files'],114)
            self.assertFalse(recovery['native_execution_attested'])
            run = restored/'s11-native-dynamics-continuity-m40-a1/physical-model-and-measured-continuity'
            xml = ET.parse(run/'native.xml').getroot()
            tests = list(xml.iter('testcase'))
            self.assertEqual(len(tests),11)
            self.assertFalse(list(xml.iter('failure')) or list(xml.iter('error')) or list(xml.iter('skipped')))
            process = load(run/'process/result.json')
            self.assertEqual(process['execution'],'completed')
            self.assertTrue(process['all_processes_closed'])
            for topology in ('Classic','Branch'):
                for frequency in (2000,20000):
                    path = run/'native'/f'physical-continuity-{topology}-{frequency}.json'
                    value,result = read_fixture(path)
                    self.assertEqual(result['complete_observations'],4)
                    self.assertFalse(result['effective_model_audited'])
                    self.assertGreater(result['preserved_first_sample_difference'],1e-6)
                    mutations=[]
                    changed=deepcopy(value);changed['schema_version']=True;mutations.append(changed)
                    changed=deepcopy(value);changed['unknown_field']=0;mutations.append(changed)
                    changed=deepcopy(value);changed['model_revision']='0'*64;mutations.append(changed)
                    changed=deepcopy(value);changed['observations'][1]['preserve']['reset_policy']='reset_per_trial';mutations.append(changed)
                    changed=deepcopy(value);changed['observations'][1]['reset']['samples'][0]['soma'][0]+=1e-3;mutations.append(changed)
                    changed=deepcopy(value);changed['observations'][0]['reset']['spike_count']+=1;mutations.append(changed)
                    changed=deepcopy(value);changed['observations'][0]['reset']['samples'].pop();mutations.append(changed)
                    changed=deepcopy(value);changed['observations'][1]['preserve']['samples'][0]['soma'][0]=float('nan');mutations.append(changed)
                    for index,changed in enumerate(mutations):
                        with self.subTest(topology=topology,frequency=frequency,mutation=index):
                            with self.assertRaises(EvidenceError):
                                analyze_fixture(changed,branch=topology=='Branch',frequency=frequency)
                    output=Path(os.environ['TMPDIR'])/'continuity-figures'/path.stem
                    from ..__main__ import main
                    text=io.StringIO()
                    with redirect_stdout(text):
                        status=main(['report',str(path),'--format','native-continuity','--output',str(output)])
                    self.assertEqual(status,0)
                    manifest=load(output/'manifest.json')
                    self.assertTrue(manifest['full_samples_rendered'])
                    self.assertTrue((output/'continuity.png').is_file())
                    figures.append(dict(manifest=str(output/'manifest.json'),source_member=path.relative_to(restored).as_posix()))
                    rows.append(dict(result,source_archive_member=path.relative_to(restored).as_posix(),negative_checks=len(mutations)))
        self.assertEqual(file_record(archive),before)
        proof=dict(kind='timelearner_native_continuity_primary_restoration',schema_version=1,
            archive_reference=reference,restoration=recovery,recorded_native_tests=11,
            controls=rows,figure_sets=figures,negative_checks=32,
            original_archive_unchanged=True,temporary_recovery_removed=True,
            new_native_execution=False,production_continuous_wrapper_verified=False,scientific_verdict=None)
        (Path(os.environ['TMPDIR'])/'native-continuity-primary-restoration-proof.json').write_text(
            json.dumps(proof,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
