"""Controls over real native ownership snapshots, including dormant C0."""
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..capacitance_ownership_evidence import audit_ownership
from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError, load


def resign(value):
    value['sha256'] = canonical_model_sha256({k: v for k, v in value.items() if k != 'sha256'})


class CapacitanceOwnershipEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_CAPACITANCE_OWNER_ARTIFACTS')
        if not value: raise unittest.SkipTest('requires real native C0 owner artifacts')
        cls.root = Path(value)
        cls.contract = Path(__file__).parents[1]/'specs/native-capacitance-ownership-v1.json'

    def test_actual_full_native_matrix(self):
        result = audit_ownership(self.contract, self.root)
        self.assertEqual((result['cases'], result['snapshots']), (8, 48))
        self.assertTrue(result['consistent'])
        self.assertFalse(result['native_import_verified'])
        self.assertIsNone(result['scientific_verdict'])

    def reject(self, edit, phase='ordinary_shrink'):
        with tempfile.TemporaryDirectory(prefix='tl-c0-owner-reader-') as temporary:
            root = Path(temporary)/'copy'; shutil.copytree(self.root, root)
            paths = [p for p in sorted((root/'native').glob('*_ownership_*.json')) if load(p)['phase'] == phase]
            self.assertEqual(len(paths), 8)
            path = paths[0]; record = load(path); edit(path, record)
            if path.exists(): path.write_text(json.dumps(record)+'\n', encoding='utf-8')
            with self.assertRaises(EvidenceError): audit_ownership(self.contract, root)

    def test_missing_phase(self):
        self.reject(lambda path, record: path.unlink())

    def test_duplicate_identity(self):
        def duplicate(path, record):
            path.with_name('extra_ownership_duplicate.json').write_text(json.dumps(record), encoding='utf-8')
        self.reject(duplicate)

    def test_boolean_schema(self):
        self.reject(lambda path, record: record.__setitem__('schema_version', True))

    def test_unknown_state_schema(self):
        def corrupt(path, record):
            record['state']['schema_version'] = 999; resign(record['state'])
        self.reject(corrupt)

    def test_changed_owned_input_readback(self):
        def corrupt(path, record):
            record['input_parameters'][0]['synapses'] += 1
        self.reject(corrupt, 'ordinary_regrowth_without_correction_argument')

    def test_overlapping_active_dormant_maps(self):
        def corrupt(path, record):
            state = record['state']; key = next(iter(state['dormant_membrane_scales']))
            state['membrane_scales'][key] = state['dormant_membrane_scales'][key]; resign(state)
        self.reject(corrupt)

    def test_unknown_dormant_path(self):
        def corrupt(path, record):
            state = record['state']; state['dormant_membrane_scales']['Dendrite1_999'] = 1.; resign(state)
        self.reject(corrupt)

    def test_history_cannot_be_discarded_as_a_legacy_current_state(self):
        def corrupt(path, record):
            state = record['state']; state['schema_version'] = 1; state.pop('dormant_membrane_scales'); resign(state)
        self.reject(corrupt)

    def test_reset_does_not_change_declared_correction_limit(self):
        def corrupt(path, record):
            state = record['state']; state['maximum_relative_change'] = .25; resign(state)
        self.reject(corrupt, 'native_reset')

    def test_wrong_effective_model_revision(self):
        def corrupt(path, record):
            state = record['state']; state['applied_model_revision'] = '0'*64; resign(state)
        self.reject(corrupt)


if __name__ == '__main__': unittest.main()
