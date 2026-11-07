"""Read real fresh-owner installation fixtures; no training or waveform claim."""
import os
from pathlib import Path
import unittest

from ..feedback_intervention import audit_profile_delta
from ..native_evidence import load


class PreparedModelEvidenceTest(unittest.TestCase):
    def audit_topology(self, topology):
        root = Path(os.environ['TIMELEARNER_PREPARED_MODEL_CORPUS'])
        paths = sorted(root.glob('prepared-model-'+topology+'-*.json'))
        self.assertEqual({p.name for p in paths}, {f'prepared-model-{topology}-{f}.json' for f in (2000,20000)})
        for path in paths:
            row = load(path)
            self.assertEqual(row['kind'],'native_prepared_model_fixture')
            self.assertEqual(row['schema_version'],1)
            self.assertEqual(row['source_identity'],row['source_after'])
            self.assertEqual(row['preview_identity'],row['candidate_identity'])
            audit_profile_delta(row['source_identity'],row['candidate_identity'],row['class_renames'],feedback_gain=0.)
            self.assertEqual(row['parameters'],[{'length':2,'synapses':1,'resistance':86e6},
                                               {'length':1,'synapses':1,'resistance':91e6}])
            self.assertTrue(row['control_idle'])
            self.assertEqual(row['observed_packet_count'],0)
            for name in ('references_present','search_present','certificate_present','need_to_train','candidate_waveform_evaluated'):
                self.assertIs(row[name],False)
            self.assertEqual(row['request'],{})
            self.assertTrue(row['source_refused']);self.assertTrue(row['repeat_refused'])

    def test_classic_fresh_state_and_unchanged_graph(self):self.audit_topology('Classic')
    def test_branch_fresh_state_and_unchanged_graph(self):self.audit_topology('Branch')
