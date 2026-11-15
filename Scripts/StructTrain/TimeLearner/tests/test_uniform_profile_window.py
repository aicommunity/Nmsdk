"""Reproduce and fix a real profile-dependent full-window declaration error."""
from copy import deepcopy
import os
from pathlib import Path
import unittest
from ..candidate_window_binding_evidence import reference_seed
from ..candidate_window_contract import calculate_window
from ..native_evidence import EvidenceError,load
from ..uniform_profile_study import declare_case,reference_window_frames


class UniformProfileWindowTest(unittest.TestCase):
    def test_audited_fast_reference_coordinates_restore_the_same_full_domain(self):
        root=Path(os.environ['TIMELEARNER_UNIFORM_REFERENCE_SOURCE']).resolve(strict=True)
        controls=Path(os.environ['TIMELEARNER_UNIFORM_WINDOW_CONTROLS']).resolve(strict=True)
        characterization=reference_window_frames(root)
        self.assertFalse(characterization['references_imported_into_train'])
        original=load(controls/'original.json');archive=load(controls/'profile.json')
        old=declare_case(original,archive,3)
        new=declare_case(original,archive,3,characterization['frames'])
        p=load(root/'train_stopped_state.json');source=p['measurement_archive']['source_binding']
        refs=[r for r in p['measurement_archive']['records'] if r['purpose']=='reference']
        self.assertEqual(len(refs),4)
        for r in refs:
            seed=reference_seed(r,source,p['protocol'])
            facts=dict(grid=seed['grid'],declared_maximum_samples=3605,
                       parameters=seed['initial_parameters'],capacitance=seed['initial_capacitance'])
            with self.assertRaises(EvidenceError):
                calculate_window(old['configuration']['composite_measurement']['candidate_window_policy'],seed,facts)
            for length in (1,28,100,256):
                changed=deepcopy(facts)
                changed['parameters'][0]['length']=length
                result=calculate_window(new['configuration']['composite_measurement']['candidate_window_policy'],seed,changed)
                self.assertEqual((result['first_frame'],result['last_frame']),(0,3600))
        self.assertEqual(old['configuration']['search'],new['configuration']['search'])
        self.assertEqual(old['configuration']['maximum_wall_seconds'],new['configuration']['maximum_wall_seconds'])
