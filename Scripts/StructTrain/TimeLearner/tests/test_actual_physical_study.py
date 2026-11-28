"""Real closed Windows DATA source; preparation/negative guards, no native run."""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..model_identity import canonical_model_sha256 as sha
from ..prepared_physical_study import declare, prepare, run
from ..runtime import file_record


class ActualPhysicalStudyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads((Path(os.environ['TIMELEARNER_ACTUAL_PHYSICAL_STUDY'])/'fixture.json').read_bytes())
        cls.base = Path('C:/Projects/TimeLearnerWorker').resolve(strict=True)
        cls.actor = Path(__file__).resolve().parents[4]
        cls.source = Path(cls.fixture['source_controls']).resolve(strict=True)
        cls.source_spec = json.loads((cls.source/'specification.json').read_bytes())
        cls.original = json.loads((Path(cls.source_spec['inputs'])/'job.json').read_bytes())
        cls.runtime = json.loads((cls.source/'runtime.json').read_bytes())
        cls.threshold = json.loads((Path(cls.source_spec['output'])/'terminal.json').read_bytes())['threshold']
        if os.name != 'nt': raise ValueError('actual_windows_physical_study_fixture_required')

    def setUp(self):
        self.controls = tempfile.TemporaryDirectory(prefix='physical-study-check-', dir=self.base/'controls')
        self.jobs = tempfile.TemporaryDirectory(prefix='physical-study-check-', dir=self.base/'jobs')
        self.control, self.job = Path(self.controls.name).resolve(strict=True), Path(self.jobs.name).resolve(strict=True)
        self.before = {str(p): file_record(p) for p in (self.source/'specification.json',
            Path(self.source_spec['inputs'])/'job.json', Path(self.source_spec['output'])/'terminal.json')}

    def tearDown(self):
        self.assertEqual({p:file_record(Path(p)) for p in self.before}, self.before)
        self.assertEqual(self.control.parent, self.base/'controls'); self.assertEqual(self.job.parent, self.base/'jobs')
        self.controls.cleanup(); self.jobs.cleanup()

    def declaration(self):
        destination = self.control/'destination'; destination.mkdir()
        return dict(kind='timelearner_physical_study_preparation', schema_version=1,
            source_controls=str(self.source), destination=str(destination), inputs=str(self.job/'inputs'),
            output=str(self.job/'output'), run_id='actual-physical-study-validation', study={'protocol':'new_foils'},
            python_source=str(self.actor), python_root=self.fixture['python_root'])

    def copied_source(self):
        controls = self.control/'copied-source'; controls.mkdir()
        output = self.job/'copied-source-output'
        shutil.copytree(self.source_spec['output'], output, copy_function=shutil.copyfile)
        spec = {**self.source_spec, 'output':str(output)}
        (controls/'specification.json').write_text(json.dumps(spec), encoding='utf-8')
        shutil.copyfile(self.source/'runtime.json', controls/'runtime.json')
        return controls, output

    def test_new_foils_keep_model_threshold_and_only_repeat_original_target(self):
        d = self.declaration(); result = prepare(d)
        job = json.loads((Path(d['inputs'])/'job.json').read_bytes())
        spec = json.loads((Path(d['destination'])/'specification.json').read_bytes())
        self.assertEqual(len(job['trials']), 27); self.assertEqual(result['expected_trials'], 27)
        self.assertEqual(job['source_model_data'], self.original['source_model_data'])
        self.assertEqual(spec['threshold'], self.threshold)
        old = {t['pattern_hash'] for t in self.original['trials']}
        targets = [t for t in job['trials'] if t['label'] == 'target']
        self.assertEqual(len(targets), 1)
        self.assertEqual({t['pattern_hash'] for t in job['trials']} & old, {targets[0]['pattern_hash']})
        self.assertFalse(result['native_execution_started']); self.assertFalse(Path(d['output']).exists())

    def test_condition_identity_survives_new_attempt_ids(self):
        first = declare(self.original, 'first-attempt', {'protocol':'new_foils'}, self.runtime,
            threshold=self.threshold, memory_bytes=4*1024**3, wall_seconds=7200)
        second = declare(self.original, 'another-attempt', {'protocol':'new_foils'}, self.runtime,
            threshold=self.threshold, memory_bytes=4*1024**3, wall_seconds=7200)
        self.assertEqual(first[2]['condition_fingerprint'], second[2]['condition_fingerprint'])

    def test_cadence_uses_shared_tick_grid_and_distinct_reset_factor(self):
        for rotation in (0, 7):
            jobs = []
            for policy in ('reset_per_trial','preserve_neuron_dynamics'):
                job, design, identity = declare(self.original, 'cadence-check', dict(protocol='cadence',
                    rotation=rotation, cadence='short', reset_policy=policy), self.runtime,
                    threshold=self.threshold, memory_bytes=4*1024**3, wall_seconds=7200)
                self.assertEqual(job['trials'][0]['duration'], .69)
                self.assertEqual(job['coverage_policy'], 'continuous_native_stream')
                self.assertEqual(job['trials'][0]['reset_policy'], 'reset_per_trial')
                self.assertTrue(all(t['reset_policy']==policy for t in job['trials'][1:]))
                self.assertEqual(job['source_model_data'], self.original['source_model_data'])
                self.assertGreaterEqual(job['trials'][-1]['duration']-sum(job['trials'][-1]['pattern_isi']), 2.)
                jobs.append((job, identity))
            self.assertEqual([{k:v for k,v in t.items() if k!='reset_policy'} for t in jobs[0][0]['trials']],
                [{k:v for k,v in t.items() if k!='reset_policy'} for t in jobs[1][0]['trials']])
            self.assertNotEqual(jobs[0][1]['condition_fingerprint'], jobs[1][1]['condition_fingerprint'])

    def test_rejects_unverified_source_before_creating_inputs(self):
        d = self.declaration(); source, output = self.copied_source()
        terminal = json.loads((output/'terminal.json').read_bytes()); terminal['transfer_valid'] = False
        (output/'terminal.json').write_text(json.dumps(terminal), encoding='utf-8'); d['source_controls'] = str(source)
        with self.assertRaisesRegex(ValueError, 'physical_study_source_replay_not_verified'): prepare(d)
        self.assertFalse(Path(d['inputs']).exists())

    def test_rejects_corrupt_observation_even_if_old_terminal_claims_success(self):
        d = self.declaration(); source, output = self.copied_source()
        p = output/'native/trial-0.json'; trial = json.loads(p.read_bytes()); trial['spike_count'] += 1
        p.write_text(json.dumps(trial), encoding='utf-8'); d['source_controls'] = str(source)
        with self.assertRaises(ValueError): prepare(d)
        self.assertFalse(Path(d['inputs']).exists())

    def test_rebound_trial_job_cannot_replace_predeclared_matrix(self):
        d = self.declaration(); prepare(d); inputs = Path(d['inputs']); controls = Path(d['destination'])
        job = json.loads((inputs/'job.json').read_bytes()); job['trials'].pop()
        job['sha256'] = sha({k:v for k,v in job.items() if k!='sha256'})
        (inputs/'job.json').write_text(json.dumps(job), encoding='utf-8')
        spec = json.loads((controls/'specification.json').read_bytes())
        spec['input_inventory'] = {p.name:file_record(p) for p in inputs.iterdir()}; spec['job_sha256'] = job['sha256']
        (controls/'specification.json').write_text(json.dumps(spec), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'physical_study_predeclared_job_changed'): run(controls)
        self.assertFalse(Path(d['output']).exists())
