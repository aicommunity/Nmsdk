"""Strict repeated-candidate proof against native primary JSON and CSV files."""
import copy
import os
from pathlib import Path
import unittest

from ..native_evidence import EvidenceError, audit_probe, audit_training_summary, load


class N0RepeatEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory=os.environ.get("TIMELEARNER_N0_REPEATS_DIR")
        if not directory:
            raise unittest.SkipTest("requires actual configured Classic/Branch N0 repeat trials")
        root=Path(directory);cls.cases=[]
        summaries=sorted(root.glob('*configured_repeats*_training_summary.json'))
        if len(summaries)!=2:
            raise RuntimeError("requires both native topology summaries")
        for path in summaries:
            summary=load(path);prefix=path.name.removesuffix('_training_summary.json')
            packets={}
            for packet_path in sorted(root.glob(prefix+'_service_*.json')):
                packet=load(packet_path);audit_probe(packet,packet_path.with_suffix('.csv'))
                trial=packet['observation']['specification']['trial_id']
                if trial in packets:raise RuntimeError("duplicate native primary trial")
                packets[trial]=packet
            cls.cases.append((summary,packets))

    def test_every_amplitude_group_has_actual_primary_support(self):
        for summary,packets in self.cases:
            result=audit_training_summary(summary,packets,'pulse0')
            self.assertTrue(result['certificate_consistent'])
            self.assertFalse(result['exact'])
            self.assertEqual(result['training_summary_schema'],2)
            self.assertGreater(result['candidate_repeat_groups_checked'],0)

    def test_changed_amplitude_range_and_reused_ids_are_rejected(self):
        summary,packets=self.cases[0]
        for mutation in ('raw','range','id','revision','missing'):
            value=copy.deepcopy(summary);group=value['candidate_repeat_groups'][0]
            if mutation=='raw':group['raw_potentials'][0]+=.001
            elif mutation=='range':group['maximum_raw_potential']+=.001
            elif mutation=='id':group['trial_ids'][1]=group['trial_ids'][0]
            elif mutation=='revision':group['model_revision']='wrong-revision'
            else:value['candidate_repeat_groups'].pop(0)
            with self.assertRaises(EvidenceError,msg=mutation):audit_training_summary(value,packets,'pulse0')

    def test_one_trial_or_downgraded_schema_cannot_claim_repeats(self):
        summary,packets=self.cases[0]
        value=copy.deepcopy(summary);group=value['candidate_repeat_groups'][0]
        for field in ('trial_ids','anchor_trial_ids','raw_potentials'):group[field]=group[field][:1]
        with self.assertRaises(EvidenceError):audit_training_summary(value,packets,'pulse0')
        value=copy.deepcopy(summary);value['schema_version']=1
        with self.assertRaises(EvidenceError):audit_training_summary(value,packets,'pulse0')
