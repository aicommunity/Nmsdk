"""Independent DATA replay of both large recorded N4 roundtrips.

Uses production archive/model auditors. No new native execution or successful
training is inferred from the saved stopped states or matching responses.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

from ..candidate_window_package_evidence import audit_candidate_window_recovery_package
from ..native_evidence import EvidenceError, load, require
from ..qt_json import read_qcompress_json as read_qcompress
from ..portable_primary import restore_native_bundle
from ..recorded_roundtrip_evidence import audit_roundtrip_controller
from ..closed_primary_bundle import verify_controller_join


class RecordedN4RoundtripPrimaryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = Path(os.environ['TIMELEARNER_RECORDED_N4_ROUNDTRIP_BUNDLE'])
        manifest = load(cls.bundle/'bundle.json')
        require(manifest['archive_sha256'] ==
                'f00fd600e1ca5341e4cdd1e8216085a8fea2dc3719f0b624b98ea71fdadb4f25'
                and manifest['archive_bytes'] == 91914992
                and len(manifest['members']) == 189 and manifest['expanded_bytes'] == 151482797,
                'recorded_n4_original_corpus')
        cls.temporary = tempfile.TemporaryDirectory(prefix='recorded-n4-data-')
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.restored = Path(cls.temporary.name)/'restored'
        cls.restoration = restore_native_bundle(cls.bundle/'bundle.json', cls.restored)

    def test_original_two_junit_cases_and_three_closed_groups(self):
        self.assertEqual(self.restoration['archive_members_verified'], 189)
        self.assertFalse(self.restoration['native_execution_attested'])
        self.assertFalse(self.restoration['source_archive_modified'])
        original = load(self.bundle/'ORIGIN.json')['source_job']
        # The original 189-member collector selected a neighbouring SDK36
        # controller. Keep it as failed evidence; never use it as authority.
        with self.assertRaisesRegex(EvidenceError, 'roundtrip_foreign_controller_request'):
            audit_roundtrip_controller(self.restored/'native', self.restored/'controller',
                                       original_job_path=original)
        # Explicit, separately pinned Git fixture: original native2 proofs.
        corrected = Path(os.environ['TIMELEARNER_RECORDED_N4_EXECUTION_PROOF'])
        result = audit_roundtrip_controller(self.restored/'native', corrected/'controller',
                                            original_job_path=original)
        self.assertEqual(result['closed_groups'], 3)
        self.assertFalse(result['native_execution_attested'])
        # Exercise the production collector's pre-archive semantic gate too.
        manifest = dict(schema_version=2, roots=[
            dict(prefix='native', directory=str(self.restored/'native')),
            dict(prefix='controller', directory=str(corrected/'controller'))],
            controller_join=dict(kind='recorded-n4-roundtrip', native_prefix='native',
                                 controller_prefix='controller', original_job_path=original))
        self.assertEqual(verify_controller_join(manifest), result)
        manifest['roots'][1]['directory'] = str(self.restored/'controller')
        with self.assertRaisesRegex(EvidenceError, 'roundtrip_foreign_controller_request'):
            verify_controller_join(manifest)

    def audit_case(self, role, outcome, revision, groups, raw_bytes, raw_sha):
        name = role.title()+'FullDomainN4Roundtrip'
        base = self.restored/f'native/{role}/native-composite/package7/NativeRecordedRecoveryArchive/{name}'
        phase = load(base/'phase-times.json')
        package = read_qcompress(base/'roundtrip-package.json.qz',
            expected_bytes=raw_bytes, expected_sha256=raw_sha)
        summary = load(base/'roundtrip-summary.json')
        audit = audit_candidate_window_recovery_package(package, summary)
        self.assertEqual(audit['model_revision'], revision)
        self.assertEqual(audit['logical_groups'], groups)
        self.assertEqual(audit['training_outcome'], outcome)
        self.assertFalse(audit['certificate_consistent']);self.assertIsNone(audit['exact'])
        self.assertFalse(audit['native_execution_verified']);self.assertFalse(audit['live_authority_restored'])
        self.assertIsNone(package['certificate']);self.assertEqual(len(package['trained_inputs']), 4)
        self.assertEqual(phase['source_package_sha256'], package['sha256'])
        self.assertEqual(phase['exported_package_sha256'], package['sha256'])
        self.assertEqual(phase['exported_raw_bytes'], raw_bytes)
        self.assertEqual(phase['exported_raw_sha256'], raw_sha)
        self.assertFalse(phase['cold_training_replayed']);self.assertFalse(phase['controller_checkpoint_restored'])
        self.assertIsNone(phase['scientific_verdict'])
        self.assertEqual(summary['recovery_ledger'], package['recovery_ledger'])
        self.assertFalse(summary['search_history_retained']);self.assertFalse(summary['contains_controller_checkpoint'])
        before, after = load(base/'response-before.json'), load(base/'response-after.json')
        for response in (before, after):
            self.assertEqual(response['kind'], 'native_boundary_response_fixture')
            self.assertEqual(response['routing'], 'native_burst_active_input0')
            self.assertIsNone(response['scientific_verdict'])
        left, right = (r['relative_time_stimulus_potentials'] for r in (before, after))
        self.assertTrue(left);self.assertEqual(len(left), len(right))
        dimension = len(left[0]);self.assertGreaterEqual(dimension, 3)
        self.assertEqual(left[0][0], 0.)
        self.assertTrue(all(a[0] < b[0] for a, b in zip(left, left[1:])))
        edges, previous, excursion = 0, False, 0.
        for a, b in zip(left, right):
            self.assertEqual(len(a), dimension);self.assertEqual(len(b), dimension)
            self.assertTrue(all(type(v) in (int, float) and math.isfinite(v) for v in a+b))
            self.assertLessEqual(abs(a[0]-b[0]), 5e-10);self.assertEqual(a[1], b[1])
            active = a[1] > 0
            edges += int(active and not previous);previous = active
            for index in range(2, dimension):
                self.assertLessEqual(abs(a[index]-b[index]), 1e-12)
                excursion = max(excursion, abs(a[index]-left[0][index]))
        self.assertEqual(edges, 4);self.assertEqual(phase['actual_stimulus_edges'], edges)
        self.assertGreater(excursion, 1e-6)
        self.assertAlmostEqual(phase['maximum_soma_excursion'], excursion, delta=1e-12)
        # Audit the retained producer input too. Phase metadata alone cannot
        # prove that the exported model corresponds to the original model.
        del package, summary, audit
        original_bytes, original_sha = {
            'classic': (175521654, '6107b4b0762ae2d5247bc2356a8fb533d872af2f0aafeb972783aeb85555a078'),
            'branch': (192607805, 'd10368eb17016819387daf4ee614bddffda46dbe774c440109fa741e222308d9'),
        }[role]
        source = read_qcompress(self.restored/f'native/{role}/native-inputs/{role}-recorded-model.qz',
            expected_bytes=original_bytes, expected_sha256=original_sha)
        original_audit = audit_candidate_window_recovery_package(source)
        self.assertEqual(original_audit['model_revision'], revision)
        self.assertEqual(original_audit['training_outcome'], outcome)
        self.assertEqual(source['sha256'], phase['exported_package_sha256'])

    def test_classic_full_model_archive_summary_and_response(self):
        self.audit_case('classic', 'invalid_observation',
            '35d849faa2aaea5d2620f0fd59d9934c77760b7fde0dd49d3284539f69f68263', 42,
            142851310, 'e4060577f2c9d99f9b23898ee00e9c1c028379c2abda4912c2a23b48d11529a2')

    def test_branch_full_model_archive_summary_and_response(self):
        self.audit_case('branch', 'budget_exhausted',
            'efc6bacd25770cb3ccde41b952b2e09638296e401be88e2b6f5f7bd3548e9ecd', 105,
            143716360, 'bfdc7d54eec4ef7ec27f21c631a19066582fe8981cbce459616779c96b0d24f8')


class RecordedQcompressFramingTest(unittest.TestCase):
    def test_corrupted_size_stream_hash_and_trailing_bytes_rejected(self):
        raw = b'{"schema_version":7}'
        correct = struct.pack('>I', len(raw))+zlib.compress(raw)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'model.qz'
            path.write_bytes(correct)
            expected = dict(expected_bytes=len(raw), expected_sha256=hashlib.sha256(raw).hexdigest())
            self.assertEqual(read_qcompress(path, **expected), {'schema_version': 7})
            for broken in (b'bad', struct.pack('>I', len(raw)+1)+correct[4:],
                           correct[:-1], correct+b'extra', correct+zlib.compress(raw)):
                with self.subTest(bytes=len(broken)):
                    path.write_bytes(broken)
                    with self.assertRaises(EvidenceError):read_qcompress(path, **expected)
            path.write_bytes(correct)
            with self.assertRaises(EvidenceError):
                read_qcompress(path, expected_bytes=len(raw), expected_sha256='0'*64)


class RecordedN4RoundtripVisualTest(unittest.TestCase):
    setUpClass = classmethod(RecordedN4RoundtripPrimaryTest.setUpClass.__func__)

    def test_actual_two_models_all_somas_with_input_and_difference(self):
        from PIL import Image
        from ..plotting import render_boundary_roundtrip
        output = Path(os.environ['TMPDIR'])/'recorded-n4-roundtrip-gallery'
        output.mkdir()
        reports = {}
        for role in ('classic', 'branch'):
            name = role.title()+'FullDomainN4Roundtrip'
            base = self.restored/f'native/{role}/native-composite/package7/NativeRecordedRecoveryArchive/{name}'
            before, after = load(base/'response-before.json'), load(base/'response-after.json')
            phase = load(base/'phase-times.json')
            context = role.title()+' | stopped: '+phase['training_outcome']+' | '+phase['model_revision'][:16]
            report = render_boundary_roundtrip(before, after, output/role, context=context)
            self.assertEqual(len(report['figures']), 2*(len(before['relative_time_stimulus_potentials'][0])-2))
            for figure in report['figures']:
                with Image.open(output/role/figure['file']) as image:
                    self.assertEqual(image.size, (1920, 1200))
                    self.assertGreater(len(image.getcolors(maxcolors=1000000)), 100)
                self.assertTrue(figure['actual_input_overlay']);self.assertFalse(figure['downsampling'])
            report['source_response_sha256'] = {
                name: hashlib.sha256((base/name).read_bytes()).hexdigest()
                for name in ('response-before.json', 'response-after.json')}
            reports[role] = report
        with (output/'manifest.json').open('x', encoding='utf-8') as stream:
            json.dump(reports, stream, indent=2, allow_nan=False);stream.write('\n')
