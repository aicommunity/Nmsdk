"""Independent replay of explicitly pinned published primary bytes only."""
import json
import os
from pathlib import Path
import unittest

from ..collector_provenance import frozen_digest
from ..native_evidence import load, require
from ..recorded_matrix_primary import audit_primary


class DeclaredCompactReplayTest(unittest.TestCase):
    def test_published_primary_rescores_without_original_worker_directories(self):
        primary = Path(os.environ['TIMELEARNER_RECORDED_MATRIX_BUNDLE'])
        declaration = load(Path(os.environ['TIMELEARNER_COMPACT_REPLAY_EXPECTATION'])/'expected.json')
        require(set(declaration) == {'kind', 'schema_version', 'bundle',
                'maximum_member_bytes', 'must_be_absent', 'readback'} and
                declaration['kind'] == 'timelearner_declared_compact_replay' and
                type(declaration['schema_version']) is int and declaration['schema_version'] == 1,
                'declared_compact_replay_schema')
        absent = declaration['must_be_absent']
        require(type(absent) is list and absent and all(type(p) is str and
                Path(p).is_absolute() for p in absent), 'declared_compact_replay_originals')
        for path in absent:
            self.assertFalse(Path(path).exists(), 'Original worker directory is available: '+path)
        bundle = load(primary/'bundle.json')
        expected = declaration['bundle']
        require(set(expected) == {'schema_version', 'archive_bytes', 'archive_sha256',
                'expanded_bytes', 'members'}, 'declared_compact_replay_bundle')
        self.assertEqual({key: bundle[key] for key in expected if key != 'members'},
                         {key: value for key, value in expected.items() if key != 'members'})
        self.assertEqual(len(bundle['members']), expected['members'])
        actual = frozen_digest(primary/'primary.tar.xz', 128*1024**2)
        self.assertEqual(actual['bytes'], expected['archive_bytes'])
        self.assertEqual(actual['sha256'], expected['archive_sha256'])
        root = Path(os.environ['TMPDIR'])
        result = audit_primary(primary/'bundle.json', root/'declared-portable-restored',
                               maximum_member_bytes=declaration['maximum_member_bytes'])
        self.assertEqual(result, declaration['readback'])
        self.assertTrue(result['diagnostic_only'])
        self.assertFalse(result['complete_runtime_directory'])
        self.assertFalse(result['native_execution_attested'])
        self.assertIsNone(result['scientific_verdict'])
        (root/'declared-portable-readback.json').write_text(
            json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
