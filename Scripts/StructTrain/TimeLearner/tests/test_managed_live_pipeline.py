"""Actual managed live Train must hand its final recognition state to Test."""
import contextlib
from copy import deepcopy
import hashlib
import io
import json
import os
from pathlib import Path
import unittest

from . import test_managed_native_pipeline as fixtures
from ..__main__ import main
from ..contained_process import inspect as inspect_contained
from ..managed_pipeline import audit_pipeline
from ..native_evidence import load
from ..native_process_policy import policy_for_reservation
from ..resource_reservations import Reservations


class ManagedLivePipelineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.ManagedNativePipelineTest.setUpClass.__func__(cls)
        calibration = os.environ.get('TIMELEARNER_COORDINATOR_CALIBRATION_TEMPLATES')
        if not calibration:
            raise unittest.SkipTest('requires measured calibration job declarations')
        cls.calibration_templates = Path(calibration)

    def case(self, topology, *, calibrate=False, stopped=False):
        name = topology+'-'+('stopped' if stopped else 'grid' if calibrate else 'fixed')
        root = self.output/name;root.mkdir()
        source_name = topology+'-v2'
        train = load(self.positive_templates/(source_name+'-train/input/job.json'))
        train['schema_version'] = 2
        train['configuration']['run_id'] += '/managed-live/'+name
        train['optional_modes']['post_train_tuning'] = True
        train['calculate_mode'] = int(calibrate)
        train['maximum_model_ticks'] = 1 if stopped else 200000
        calibration = load(self.calibration_templates/source_name/'measured-grid-job.json')
        conversion = load(self.positive_templates/(source_name+'-export/input/job.json'))['conversion_spec']
        trials = deepcopy(calibration['trials'])
        for i, trial in enumerate(trials):
            trial['run_id'] = train['configuration']['run_id']+'/inline-probes'
            trial['trial_id'] = trial['run_id']+'/'+str(i)
        confirmation = deepcopy(calibration['specification'])
        confirmation['attempt_id'] = train['configuration']['run_id']+'/inline-finalization'
        train['finalization_plan'] = fixtures.signed({
            'kind': 'native_live_finalization_plan', 'schema_version': 1,
            'implementation_id': train['implementation_id'], 'conversion': conversion,
            'post_tune': {'schema_version': 3, 'mode': 'keep_done', 'metric': 'auto',
                'canonical_floor': 0., 'canonical_last': 0., 'resistance_bounds': [],
                'search_passes': 1, 'maximum_candidates': 1, 'maximum_recorded_samples': 2000000,
                'minimum_positive_gap': 0., 'finalization': 'calibrate' if calibrate else 'keep_fixed_threshold',
                'weight_probe_threshold': 2.},
            'trials': trials, 'thresholds': calibration['thresholds'] if calibrate else [],
            'maximum_calibration_candidates': calibration['maximum_candidates'] if calibrate else 0,
            'confirmation': confirmation})
        train = fixtures.signed(train)
        evaluation = load(self.positive_templates/(source_name+'-frozen/input/job.json'))
        evaluation.pop('sha256');evaluation['source_recognition'] = None
        evaluation['run_id'] = train['configuration']['run_id']+'/managed-frozen'
        for i, trial in enumerate(evaluation['trials']):
            trial['run_id'] = evaluation['run_id'];trial['trial_id'] = evaluation['run_id']+'/'+str(i)
        specification = {'kind': 'timelearner_managed_pipeline_job', 'schema_version': 1,
            'attempt_id': train['configuration']['run_id'], 'phases': [
                {'operation': 'train', 'job': train, 'wall_seconds': 1200},
                {'operation': 'evaluate', 'job': evaluation, 'wall_seconds': 600}]}
        declaration = root/'pipeline-job.json';declaration.write_text(json.dumps(specification, allow_nan=False))
        registry = Reservations(root/'leases.sqlite3', managed_units=True,
            capacity={'slots': 1, 'memory_bytes': 6*1024**3, 'disk_bytes': 1024**3, 'tasks': 512})
        lease = registry.reserve('managed-live-'+name, [{'path': str(root/'runs'), 'access': 'write'}],
            demands={'slots': 1, 'memory_bytes': 4*1024**3+512*1024**2,
                     'disk_bytes': 512*1024**2, 'tasks': 256},
            controller_directory=self.spec['controller'], ttl_seconds=3600)
        policy = root/'policy.json'
        policy.write_text(json.dumps(policy_for_reservation(registry, lease['token'],
                                                          memory_bytes=4*1024**3, tasks=64)))
        output = root/'runs/pipeline'

        def invoke(action, *, stop_after=None):
            args = ['pipeline', action, str(output), '--specification', str(declaration),
                '--runtime-manifest', self.spec['runtime'], '--process-policy', str(policy)]
            if stop_after:
                args += ['--stop-after', stop_after]
            text = io.StringIO()
            with contextlib.redirect_stdout(text), contextlib.redirect_stderr(text):
                result = main(args)
            (root/(action+('-'+stop_after if stop_after else '')+'-cli.log')).write_text(text.getvalue())
            self.assertEqual(result, 2 if stopped else 0, text.getvalue())
            return audit_pipeline(output)

        paused = invoke('run', stop_after='train')
        self.assertFalse(paused['pipeline_complete']);self.assertIsNone(paused['pending_phase'])
        units = [output/'phases/train/process/contained']
        if stopped:
            self.assertEqual(paused['halted_phase'], 'train')
            self.assertFalse((output/'phases/evaluate').exists())
            self.assertFalse((output/'phases/train/native/recognition-model.json').exists())
        else:
            self.assertEqual(paused['completed_phases'], ['train'])
            native = output/'phases/train/native';package = native/'recognition-model.json'
            final = load(package);before = hashlib.sha256(package.read_bytes()).hexdigest()
            manifest = load(output/'phases/train/run-manifest.json')
            self.assertTrue(manifest['analysis']['recognition_available'])
            self.assertEqual(final['sha256'], load(native/'execution.json')['recognition_package_sha256'])
            complete = invoke('continue')
            self.assertTrue(complete['pipeline_complete'])
            self.assertEqual(complete['completed_phases'], ['train', 'evaluate'])
            actual = load(output/'phases/evaluate/input/job.json')
            self.assertEqual(actual['source_recognition'], final)
            self.assertEqual(actual['source_recognition']['source_candidate']['source_recognition']['source_solo']
                             if final['kind'] == 'timelearner_calibrated_recognition_state'
                             else actual['source_recognition']['source_solo'],
                             load(native/'train_learned_state.json'))
            self.assertEqual(hashlib.sha256(package.read_bytes()).hexdigest(), before)
            self.assertFalse((output/'phases/export').exists())
            self.assertFalse((output/'phases/calibrate').exists())
            units.append(output/'phases/evaluate/process/contained')
            before_units = [load(p/'owned-unit.json') for p in units]
            self.assertEqual(invoke('continue'), complete)
            self.assertEqual([load(p/'owned-unit.json') for p in units], before_units)
        for unit in units:
            self.assertTrue(inspect_contained(unit)['all_processes_closed'])
            context = load(unit.parent/'reservation-context.json')
            self.assertEqual(context['lease']['token'], lease['token'])
        registry.release(lease['token'], note='All live Train/frozen units freshly closed; final recognition was routed without re-export.')
        self.assertEqual(registry.inspect()['leases'][0]['state'], 'released')
        (root/'result.json').write_text(json.dumps({'final_audit': audit_pipeline(output),
            'native_units': len(units), 'inline_calibration_declared': calibrate,
            'scientific_verdict': None}, indent=2))

    def test_classic_fixed_live_state_to_frozen_test(self):
        self.case('Classic')

    def test_branch_fixed_live_state_to_frozen_test(self):
        self.case('Branch')

    def test_classic_grid_live_state_to_frozen_test(self):
        self.case('Classic', calibrate=True)

    def test_branch_grid_live_state_to_frozen_test(self):
        self.case('Branch', calibrate=True)

    def test_classic_unfinished_live_train_has_no_test(self):
        self.case('Classic', stopped=True)

    def test_branch_unfinished_live_train_has_no_test(self):
        self.case('Branch', stopped=True)
