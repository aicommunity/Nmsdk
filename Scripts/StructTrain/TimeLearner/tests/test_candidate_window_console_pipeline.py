"""Real cold7 Console preflight/Train/export/calibration/frozen Test.

Saved packages provide declarations and immutable profile images only. Every
learned/evaluated state must come from a new public Train. N2/N0 engineering
fixtures, explicit SyncTolerance0.2 and historical same-matrix calibration do
not establish stock N4 selectivity or default0.02 convergence. Workers only.
"""
from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from ..candidate_window_package_evidence import audit_candidate_window_package
from ..composite_primary import filesystem_primary_resolver
from ..model_identity import canonical_model_sha256 as digest
from ..native_evidence import load, require
from ..process_runner import verify_runtime
from . import test_managed_native_pipeline as pipeline_checks
from . import test_managed_native_calibration as calibration_checks


class CandidateWindowConsolePipelineTest(unittest.TestCase):
    # Actual package6 measured-grid auditing exceeded the former 256 MiB
    # controller cap. This is separate from each native model's 4 GiB cap.
    controller_reserve_bytes = 2*1024**3

    @classmethod
    def setUpClass(cls):
        binding = os.environ.get('TIMELEARNER_CANDIDATE_WINDOW_CONSOLE')
        require(binding is not None, 'cold7_console_fixture_binding_required')
        control = Path(binding).resolve(strict=True)
        require(control.is_dir(), 'cold7_console_control_directory_required')
        cls.spec = load(control/'declaration.json')
        require(type(cls.spec) is dict and set(cls.spec) == {'runtime', 'corpus', 'controller', 'output'},
                'cold7_console_fixture_declaration')
        corpus_binding = os.environ.get('TIMELEARNER_NATIVE_PACKAGE6_FIXTURES')
        runtime_binding = os.environ.get('TIMELEARNER_CONSOLE_RUNTIME_FILES')
        require(corpus_binding is not None and runtime_binding is not None, 'cold7_console_all_fixture_bindings_required')
        require(Path(cls.spec['corpus']).resolve(strict=True) == Path(corpus_binding).resolve(strict=True),
                'cold7_console_corpus_binding_changed')
        runtime_path = Path(cls.spec['runtime']).resolve(strict=True)
        require(runtime_path.parent == control, 'cold7_console_runtime_metadata_not_in_controls')
        runtime = load(runtime_path);verify_runtime(runtime)
        require(Path(runtime['executable']['path']).parent.resolve(strict=True) == Path(runtime_binding).resolve(strict=True),
                'cold7_console_actual_runtime_binding_changed')
        cls.output = Path(cls.spec['output'])
        cls.output.mkdir(parents=True, exist_ok=False)
        cls.templates = cls.positive_templates = cls.output/'declarations'
        cls.templates.mkdir()
        for name, branch in (('Classic-window-N0', False), ('Branch-window-N0', True)):
            directory = Path(cls.spec['corpus'])/('package6-branch' if branch else 'package6-classic')/'source-0'
            raw = (directory/'train_learned_state.json').read_bytes()
            package = load(directory/'train_learned_state.json')
            audit = audit_candidate_window_package(package, external_resolver=filesystem_primary_resolver(directory))
            require(audit['exact'] is True and audit['certificate_consistent'] is True,
                    'cold7_console_requires_complete_actual_source_fixture')
            config = deepcopy(package['configuration'])
            require(config['schema_version'] == 7 and config['model']['branch'] is branch and
                    config['model']['normalization'] == 'N0' and len(config['model']['inputs']) == 2 and
                    config['search']['tolerances'] == dict(amplitude_absolute=1e-5, amplitude_relative=0., sync=.2),
                    'cold7_console_engineering_fixture_changed')
            config['run_id'] += '/fresh-public-cold7-console'
            implementation = package['implementation_id']
            owner = 'NNeuronTimeLearner'+('Branch' if branch else '')
            train = pipeline_checks.signed(dict(kind='timelearner_native_training_job', schema_version=1,
                owner_class=owner, implementation_id=implementation, configuration=config,
                profile_archives=[package['neuron']], optional_modes=dict(sync_capacitance_trim=0,
                post_train_tuning=False, auto_calibrate_threshold=False), calculate_mode=1,
                structure_build_mode=1, maximum_model_ticks=240000))
            export = dict(kind='timelearner_native_recognition_export_job', schema_version=1,
                implementation_id=implementation, source_solo=None,
                conversion_spec=dict(schema_version=1, mode='identity', resistance_bounds=[]))
            target = config['model']['initial_isi']
            foil = deepcopy(target);foil[-1] *= 1.5
            duration = max(2., sum(foil)+.5)
            frequency = config['model']['frequency_hz']
            run = name+'/initial-fixed-frozen-calibration-matrix'
            trials = []
            for i, (label, pattern) in enumerate((('target', target), ('foil', foil), ('foil', foil), ('target', target))):
                trials.append(dict(run_id=run, trial_id=run+'/'+str(i), sample_id=label+'-pattern', label=label,
                    pattern_hash=digest(pattern), pattern_isi=deepcopy(pattern), duration=duration,
                    maximum_samples=math.ceil(duration*frequency)+1, reset_policy='reset_per_trial',
                    record_threshold_potential=True))
            evaluate = dict(kind='timelearner_native_evaluation_job', schema_version=1,
                owner_class=owner, implementation_id=implementation, source_recognition=None,
                maximum_model_ticks=200000, run_id=run, coverage_policy='per_trial_windows',
                criterion=dict(id='post_anchor_target_whole_window_foil_v1', anchor='onset',
                    begin_offset=0., end_offset=None, reject_target_outside_window=True), trials=trials)
            for suffix, job in (('train', train), ('export', export), ('frozen', evaluate)):
                destination = cls.templates/(name+'-'+suffix)/'input'
                destination.mkdir(parents=True)
                (destination/'job.json').write_text(json.dumps(job, indent=2, allow_nan=False)+'\n', encoding='utf-8')
            (cls.templates/(name+'-scope.json')).write_text(json.dumps(dict(
                source_package_sha256=hashlib.sha256(raw).hexdigest(), source_model_revision=package['model_revision'],
                original_learned_state_used_as_seed=False, profile_images_imported=True,
                mathematical_sync_tolerance=.2, calibration_protocol='historical_same_matrix',
                training_normalization='N0', physical_inputs=2, scientific_verdict=None), indent=2)+'\n', encoding='utf-8')

    def cold_pipeline_and_calibration(self, name):
        # The Python controller has no Qt loader environment of its own. Public
        # native operations must run with the immutable Console declaration,
        # including offscreen Qt, rather than silently changing that manifest.
        runtime = load(Path(self.spec['runtime']))
        with patch.dict(os.environ, runtime['loader_environment']):
            self._cold_pipeline_and_calibration(name)

    def _cold_pipeline_and_calibration(self, name):
        # These maintained helpers execute public CLI commands, audit the real
        # manifests and native graph, check whole cgroup closure and match
        # durable reservation intents. They never fabricate simulator outputs.
        pipeline_checks.ManagedNativePipelineTest.case(self, name, positive=True, preflight=True)
        initial_spec, initial_output = self.spec, self.output
        calibration_output = initial_output/'calibration'
        calibration_output.mkdir(exist_ok=True)
        self.spec = dict(runtime=initial_spec['runtime'], source=str(initial_output),
                         controller=initial_spec['controller'], output=str(calibration_output))
        self.output = calibration_output
        try:
            # Real measured-grid candidates, threshold confirmation, frozen
            # evaluation and silent-candidate rollback/replay are all exercised.
            # Nonseparable is retained as a valid result; no 8/8 is required.
            calibration_checks.ManagedNativeCalibrationTest.case(self, name)
        finally:
            self.spec, self.output = initial_spec, initial_output

    def test_classic_cold7_public_preflight_train_export_measured_calibration_frozen_test(self):
        self.cold_pipeline_and_calibration('Classic-window-N0')

    def test_branch_cold7_public_preflight_train_export_measured_calibration_frozen_test(self):
        self.cold_pipeline_and_calibration('Branch-window-N0')
