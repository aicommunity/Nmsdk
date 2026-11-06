"""Region audit uses all eight native graph/trace fixtures, with corruption controls."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

from ..capacitance_region_evidence import _audit, audit_capacitance_region
from ..native_evidence import EvidenceError, load


class CapacitanceRegionEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get('TIMELEARNER_CAPACITANCE_REGION_DIR')
        if not root:
            raise unittest.SkipTest('requires actual eight native capacitance region graph/trace fixtures')
        cls.records = [(p, load(p)) for p in sorted(Path(root).glob('*_capacitance_region_region.json'))]
        expected = {(b, n, f) for b in (False, True) for n in (0, 1) for f in (2000, 20000)}
        if len(cls.records) != 8 or {(r['branch'], r['normalization'], r['frequency_hz']) for _, r in cls.records} != expected:
            raise RuntimeError('requires all eight actual region fixtures')

    def test_actual_native_physics_and_every_input_primary_trace(self):
        for path, record in self.records:
            with self.subTest(path=path.name):
                result = audit_capacitance_region(path)
                self.assertTrue(result['physical_state_verified'])
                self.assertEqual(result['primary_trials'], 2*len(record['input_parameters']))
                self.assertFalse(result['training_certificate_verified'])
                self.assertIsNone(result['scientific_verdict'])
                child = subprocess.run([sys.executable, '-m', 'Scripts.StructTrain.TimeLearner', 'analyze',
                    str(path), '--format', 'capacitance-region'], capture_output=True, text=True, timeout=120)
                self.assertEqual(child.returncode, 0, child.stderr)
                self.assertEqual(json.loads(child.stdout)['analysis'], result)

    def reject(self, change):
        for path, original in self.records:
            with self.subTest(path=path.name):
                record = copy.deepcopy(original)
                change(record)
                with self.assertRaises(EvidenceError):
                    _audit(record, path.parent)

    def test_unknown_schema(self):
        self.reject(lambda r: r.update(schema_version=99))

    def test_region_cannot_include_the_adjacent_branch_interval(self):
        self.reject(lambda r: r['region'].update(first=r['region']['first']+1))

    def test_input_banks_cannot_be_renamed_or_dropped(self):
        self.reject(lambda r: r['input_parameters'].pop())

    def test_missing_or_duplicate_input_probe(self):
        self.reject(lambda r: r['probes'].pop())
        self.reject(lambda r: r['probes'].__setitem__(-1, copy.deepcopy(r['probes'][0])))

    def test_physics_witness_cannot_be_replaced_by_unchanged_model(self):
        self.reject(lambda r: r.update(after=copy.deepcopy(r['before'])))

    def test_embedded_packet_must_match_original_primary(self):
        self.reject(lambda r: r['probes'][0]['packet'].update(current_base_revision='0'*64))

    def test_primary_paths_cannot_escape_or_alias(self):
        self.reject(lambda r: r['probes'][0].update(trace_file='../outside.csv'))
        self.reject(lambda r: r['probes'][1].update(trace_file=r['probes'][0]['trace_file']))
