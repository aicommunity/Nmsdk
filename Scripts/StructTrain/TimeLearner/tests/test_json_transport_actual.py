"""Lossless carriers of genuine closed N4 sources, not semantic model acceptance."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import unittest

from ..json_transport import compact_json_transport


def file_sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024**2), b''):
            digest.update(chunk)
    return digest.hexdigest()


class JsonTransportActualSourceTest(unittest.TestCase):
    def test_original_closed_source_and_all_primary_bytes_are_retained(self):
        source = Path(os.environ['TIMELEARNER_JSON_TRANSPORT_NATIVE_JSON']).resolve(strict=True)
        self.assertEqual(source, Path(os.environ['TIMELEARNER_JSON_TRANSPORT_NATIVE_CSV']).resolve(strict=True))
        execution = json.loads((source/'execution.json').read_bytes())
        self.assertEqual(execution['execution'], 'completed')
        self.assertEqual(execution['training_outcome'], 'budget_exhausted')
        self.assertFalse(execution['completed_boundary'])
        self.assertEqual(execution['package_path'], 'train_stopped_state.json')
        artifacts = {row['path']: row for row in execution['artifacts']}
        self.assertEqual(len(artifacts), len(execution['artifacts']))
        output = Path(os.environ['TMPDIR'])/'compact-native-source';output.mkdir()
        carrier = output/'source';carrier.mkdir();records = []
        for name in ('train_stopped_state.json', 'train_stopped_summary.json'):
            row = artifacts[name];path = source/name
            self.assertEqual(path.stat().st_size, row['bytes'])
            record = compact_json_transport(path, carrier/name,
                expected_bytes=row['bytes'], expected_sha256=row['sha256'])
            self.assertLessEqual(record['transport']['bytes'], 1024**3)
            self.assertEqual(file_sha(carrier/name), record['transport']['sha256'])
            self.assertFalse(record['source_modified']);self.assertFalse(record['semantic_package_verified'])
            self.assertEqual(path.stat().st_size, row['bytes']);records.append(record)
        copied = []
        for path in sorted(source.glob('train_stopped_trial_*')):
            self.assertTrue(path.is_file() and not path.is_symlink())
            row = artifacts[path.name];self.assertEqual(path.stat().st_size, row['bytes'])
            destination = carrier/path.name;shutil.copyfile(path, destination)
            self.assertEqual(file_sha(destination), row['sha256'])
            copied.append(dict(path=path.name,bytes=row['bytes'],sha256=row['sha256']))
        self.assertTrue(copied)
        provenance = output/'provenance';provenance.mkdir()
        shutil.copyfile(source/'execution.json', provenance/'original-execution.json')
        # The original execution hashes pretty source bytes. It must not be
        # installed beside a reformatted source as if those raw bytes matched.
        self.assertFalse((carrier/'execution.json').exists())
        manifest = dict(kind='timelearner_actual_source_transport',schema_version=1,
            original_native=str(source),carrier=str(carrier),records=records,primary=copied,
            original_execution_sha256=file_sha(source/'execution.json'),
            expected_package_sha256=execution['package_sha256'],
            expected_model_revision=execution['model_revision'],
            training_outcome=execution['training_outcome'],semantic_package_verified=False,
            native_roundtrip_verified=False,strict_original_evidence_join_required=True,
            original_files_retained=True,scientific_verdict=None)
        (output/'manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n',encoding='utf-8')


if __name__ == '__main__':
    unittest.main()
