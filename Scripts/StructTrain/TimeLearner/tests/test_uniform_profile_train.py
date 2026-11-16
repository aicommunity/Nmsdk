"""A declared real cold Train; valid negative outcomes do not become PASS science."""
from copy import deepcopy
import os
from pathlib import Path
import unittest
from unittest.mock import patch
from ..n1_protocol_robustness import _signed
from ..native_evidence import load
from ..uniform_profile_study import declare_case,run,reference_window_frames


class UniformProfileTrainTest(unittest.TestCase):
    def test_actual_cold_branch_N1_preserves_declared_profile_and_honest_outcome(self):
        controls=Path(os.environ['TIMELEARNER_UNIFORM_TRAIN_CONTROLS']).resolve(strict=True)
        spec=load(controls/'declaration.json');job=load(controls/'job.json')
        frames=spec.get('reference_frames')
        if frames is not None:
            source=Path(os.environ['TIMELEARNER_UNIFORM_REFERENCE_SOURCE']).resolve(strict=True)
            self.assertEqual(frames,reference_window_frames(source)['frames'])
        original=load(controls/'original.json')
        if spec.get('budget_change') is not None:
            change=spec['budget_change']
            owners={'maximum_wall_seconds':None,'maximum_group_wall_seconds':'composite_measurement'}
            self.assertTrue(change);self.assertTrue(set(change)<=set(owners))
            before=load(controls/'original-before-budget.json')
            expected_sha=spec.get('before_job_sha256',
                '9c7b2c662d04a8fb32db0e80fc50d0e4b534ab21e8d01c717c0a46ea042ea056')
            self.assertEqual(before['sha256'],expected_sha)
            changed=deepcopy(before)
            for key,delta in change.items():
                self.assertEqual(set(delta),{'before','after'})
                old=before['configuration'];new=original['configuration'];target=changed['configuration']
                if owners[key] is not None:
                    old=old[owners[key]];new=new[owners[key]];target=target[owners[key]]
                self.assertEqual(delta,dict(before=old[key],after=new[key]))
                target[key]=delta['after']
            self.assertEqual(original,_signed({k:v for k,v in changed.items() if k!='sha256'}))
        expected=declare_case(original,load(controls/'profile.json'),spec['variant'],frames,
                              run_label=spec.get('run_label'))
        self.assertEqual(job,expected)
        runtime=load(controls/'runtime.json')
        with patch.dict(os.environ,runtime['loader_environment']):
            result=run(controls/'job.json',controls/'runtime.json',spec['controller'],
                       controls/'initial-state.json',spec['output'],finalization_seconds=300.)
        self.assertEqual(result['execution'],'completed')
        self.assertEqual(result['validity'],'valid')
        self.assertIsNotNone(result['package_audit']);self.assertIsNotNone(result['physical_audit'])
        self.assertFalse(result['classification_assessed']);self.assertIsNone(result['scientific_verdict'])
