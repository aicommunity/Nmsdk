"""Data consistency checks over actual native dataset/generator/neuron runs."""
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..dataset_clock_reports import audit_dataset_clock
from ..native_evidence import EvidenceError


class DatasetClockReportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_DATASET_CLOCK_ARTIFACTS')
        if not value: raise unittest.SkipTest('requires real native dataset clock artifacts')
        cls.root = Path(value)
        name = 'native-dataset-clock-extended-v1.json' if os.environ.get('TIMELEARNER_DATASET_CLOCK_EXTENDED') == '1' else 'native-dataset-clock-v1.json'
        cls.contract = Path(__file__).parents[1]/'specs'/name

    def test_actual_full_primary_matrix_and_cpp_outcome(self):
        result = audit_dataset_clock(self.contract, self.root)
        self.assertEqual(result['observations'], 76 if os.environ.get('TIMELEARNER_DATASET_CLOCK_EXTENDED') == '1' else 36)
        self.assertIsNone(result['scientific_verdict'])

    def reject(self, edit):
        with tempfile.TemporaryDirectory(prefix='tl-dataset-clock-reader-') as temporary:
            root = Path(temporary)/'copy'; shutil.copytree(self.root, root)
            path = sorted((root/'native').glob('dataset_clock_*.json'))[0]
            record = json.loads(path.read_text()); edit(root, path, record)
            path.write_text(json.dumps(record, allow_nan=False)+'\n')
            with self.assertRaises(EvidenceError): audit_dataset_clock(self.contract, root)

    def test_incomplete_window(self):
        self.reject(lambda root, path, record: record.__setitem__('complete', False))

    def test_unknown_schema(self):
        self.reject(lambda root, path, record: record.__setitem__('schema_version', 999))

    def test_boolean_schema(self):
        self.reject(lambda root, path, record: record.__setitem__('schema_version', True))

    def test_wrong_origin(self):
        self.reject(lambda root, path, record: record.__setitem__('origin', record['origin']+.5))

    def test_missing_events(self):
        self.reject(lambda root, path, record: record.__setitem__('rising_edges', []))

    def test_model_digest_changed(self):
        self.reject(lambda root, path, record: record['model'].__setitem__('sha256', '0'*64))

    def test_nonfinite_csv_is_not_silent(self):
        def corrupt(root, path, record):
            trace = path.with_suffix('.csv'); rows = trace.read_text().splitlines()
            cells = rows[1].split(','); cells[-1] = 'nan'; rows[1] = ','.join(cells)
            trace.write_text('\n'.join(rows)+'\n')
        self.reject(corrupt)

    def test_missing_native_tick(self):
        def corrupt(root, path, record):
            trace = path.with_suffix('.csv'); rows = trace.read_text().splitlines(); rows.pop(5)
            trace.write_text('\n'.join(rows)+'\n')
        self.reject(corrupt)


if __name__ == '__main__': unittest.main()
