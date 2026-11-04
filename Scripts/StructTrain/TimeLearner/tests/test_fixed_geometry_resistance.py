"""Actual stock cold-preflight mismatch and the mandatory model graph gate."""
from pathlib import Path
import os
import shutil
import tempfile
import unittest

from ..fixed_geometry_resistance import graph_difference, physical_bank_owners, validate_prepared
from ..native_calibration_worker import _signed, _write
from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import audit_run_manifest


class FixedGeometryResistanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value, prepared = os.environ.get('TIMELEARNER_FIXED_GEOMETRY_CORPUS'), os.environ.get('TIMELEARNER_FIXED_GEOMETRY_PREPARED')
        if not value or not prepared:
            raise unittest.SkipTest('requires actual stock preflights and version2 prepared inputs')
        cls.root, cls.prepared = Path(value), Path(prepared)

    def test_actual_graph_gate_blocks_both_interventions_despite_equal_lengths_counts_and_resistances(self):
        result = load(self.root/'runs/result.json')
        self.assertFalse(result['all_source_graphs_reproduced'])
        for row in result['rows']:
            name = row['name']
            self.assertFalse(row['source_graph_reproduced']);self.assertFalse(row['probes_executed'])
            self.assertEqual(row['actual_parameters'], row['expected_parameters'])
            self.assertTrue(row['baseline_difference'])
            preflight = self.root/'runs'/(name+'-preflight')
            self.assertTrue(audit_run_manifest(preflight/'run-manifest.json')['run_evidence_consistent'])
            self.assertEqual(load(preflight/'native/execution.json')['model_ticks'], 0)
            for suffix in ('baseline', 'resistance'):
                self.assertFalse((self.root/'runs'/(name+'-'+suffix)).exists())
            expected = load(self.root/'prepared/expected'/(name+'.json'))['identity']['model']
            actual = load(preflight/'native/initial-state.json')['identity']['model']
            missing = {n['path'] for n in actual['nodes']}-{n['path'] for n in expected['nodes']}
            self.assertEqual(len(missing), 13 if row['branch'] else 3)
            self.assertTrue(all(p.endswith('.ExcSynapse1') for p in missing))

    def test_branch_control_changes_the_shared_physical_bank_and_classic_only_one_bank(self):
        plan = validate_prepared(self.prepared)
        for row in plan['rows']:
            name = row['name'];baseline = load(self.prepared/'jobs'/(name+'-baseline.json'))
            changed = load(self.prepared/'jobs'/(name+'-resistance.json'))
            owners = physical_bank_owners(baseline['model'], row['input_index'])
            self.assertEqual(owners, [0, 1, 2] if row['branch'] else [0])
            for i, (a, b) in enumerate(zip(baseline['model']['inputs'], changed['model']['inputs'])):
                self.assertEqual(a['attachment'], b['attachment']);self.assertEqual(a['synapses'], b['synapses'])
                self.assertEqual(b['resistance'], row['intervention_resistance'] if i in owners else a['resistance'])

    def test_rehashed_job_change_cannot_bypass_the_prepared_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)/'prepared';shutil.copytree(self.prepared, folder)
            p = folder/'jobs/Classic-threshold-training100-resistance.json'
            job = load(p);job.pop('sha256');job['model']['inputs'][0]['resistance'] *= 1.1
            p.unlink();_write(p, _signed(job))
            with self.assertRaisesRegex(EvidenceError, 'fixed_geometry_prepared_file_changed'):
                validate_prepared(folder)

    def test_graph_diagnostics_retain_actual_node_order_changes(self):
        row = load(self.root/'runs/result.json')['rows'][0]
        model = load(self.root/'prepared/expected'/(row['name']+'.json'))['identity']['model']
        changed = {**model, 'nodes': list(reversed(model['nodes']))}
        delta = graph_difference(model, changed)
        self.assertTrue(any(d['path'] == ['nodes', 'node_order'] for d in delta))
