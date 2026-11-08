"""Declaration/transport contracts only: no fake waveform or training proof."""
from copy import deepcopy
import unittest

from ..candidate_recovery import project_recovery_configuration
from ..composite_configuration import (METHOD, project_composite_configuration,
    project_training_configuration, validate_composite_protocol)
from ..model_identity import canonical_model_sha256 as digest
from ..native_evidence import EvidenceError
from ..native_pipeline_worker import validate_job


def configuration(base=1, *, branch=False, n=2):
    """Complete wire declaration; tests do not claim native image availability."""
    model = dict(schema_version=1, branch=branch, frequency_hz=2000,
        neuron_class='DeclaredNeuronProfile', dataset_class='DeclaredDatasetProfile',
        generator_class='NPulseGeneratorTransit', neuron_structure_mode=0, normalization='N0',
        inputs=[dict(attachment=1, synapses=1, resistance=1.) for _ in range(n)],
        initial_isi=[.02]*n, allocated_cable_lengths=[1] if branch else [1]*n,
        maximum_cable_length=8, preserve_allocated_cable=True, maximum_resistance_ratio=100.,
        configured_minimum_resistance=0., inhibition=[], scale_inhibition_with_input=False,
        allow_muted_input_baseline=False)
    search = dict(maximum_probes=16, maximum_edits=8, maximum_candidates_per_input=4,
        maximum_sweeps=2, maximum_invalid_observations=2, resistance_subdivision_depth=1,
        bounds=[dict(minimum_length=1, maximum_length=8, minimum_synapses=1,
                     maximum_synapses=128, minimum_resistance=.01, maximum_resistance=100.) for _ in range(n)],
        tolerances=dict(amplitude_absolute=1e-5, amplitude_relative=0., sync=.02))
    if base >= 2: search['n0_candidate_repeats'] = 2
    result = dict(kind='timelearner_native_cold_configuration', schema_version=6, base_schema_version=base,
        model=model, stimulus_profile=dict(generator_class='NPulseGeneratorTransit', amplitude=1.,
            pulse_length=.001, frequency_hz=2000, frequency_deviation=0., use_transit_signal=True, use_pattern_output=False),
        run_id='declared-run', protocol_revision='declared-protocol', sample_id='target', duration=.1,
        maximum_sample_gap=.0005, minimum_amplitude=1e-6, maximum_samples=201, record_spikes=False,
        peak_selection='isolated_window', windows=[dict(begin=0., end=.1) for _ in range(n)], search=search,
        maximum_reference_probes=8, maximum_invalid_reference_probes=2, maximum_model_seconds=10., maximum_wall_seconds=30.,
        composite_measurement=dict(schema_version=1, method_id=METHOD,
            context_policy=dict(schema_version=1, comparison_radius_ticks=1, maximum_samples=201,
                maximum_total_samples=201*(n+2), maximum_native_probes=n+2, time_comparison_tolerance=0.,
                baseline_absolute=1e-8, repeatability_absolute=1e-8, repeatability_relative=0.,
                influence_absolute=1e-8, influence_relative=0.),
            geometry_policy=dict(schema_version=1, maximum_inputs=max(4,n), maximum_samples=201,
                maximum_total_samples=201*(n+2), repeatability_absolute=1e-8),
            attempt_limits=dict(maximum_groups=32, maximum_native_probes=128, maximum_total_samples=32000),
            maximum_group_model_seconds=.5, maximum_group_wall_seconds=5., maximum_total_primary_bytes=1000000))
    if base >= 3: result['capacitance_history'] = dict(record=True, maximum_relative_change=.1)
    if base == 4:
        result['capacitance_search'] = dict(enumeration='round_robin_absolute_C0_v1', minimum_scale=.9,
            maximum_scale=1.1, subdivision_depth=1, maximum_contexts=4, maximum_membranes=8, maximum_cursor_elements=8)
    return result


def protocol(config):
    c = config['composite_measurement']; n = len(config['model']['inputs'])
    return dict(schema_version=4, routing='branch_solo_burst' if config['model']['branch'] else 'classic_burst',
        revision=config['protocol_revision'], sample_id=config['sample_id'], pattern_hash=digest(config['model']['initial_isi']),
        origin_stimulus_id='pulse0', inputs=[dict(id='input'+str(i), stimulus_id='pulse'+str(i)) for i in range(n)],
        stimulus_ids=['pulse'+str(i) for i in range(n)], maximum_sample_gap=config['maximum_sample_gap'],
        minimum_amplitude=config['minimum_amplitude'], stimulus_profile=deepcopy(config['stimulus_profile']),
        wave_assignment='window_only', peak_selection='isolated_window', composite_measurement={
            **{key:deepcopy(c[key]) for key in ('schema_version','method_id','context_policy','geometry_policy')},
            'input_windows':[dict(begin_offset=w['begin'],end_offset=w['end']) for w in config['windows']]})


class CompositeConfigurationTest(unittest.TestCase):
    def test_each_base_is_a_private_lossless_view_and_original_identity_is_retained(self):
        for base in range(1,5):
            value=configuration(base); before=deepcopy(value); projected=project_composite_configuration(value)
            expected=deepcopy(value);expected.pop('base_schema_version');expected.pop('composite_measurement');expected['schema_version']=base
            self.assertEqual(projected,expected);self.assertEqual(value,before)
            self.assertNotEqual(digest(value),digest(projected))
            projected['model']['initial_isi'][0]=1.;self.assertEqual(value,before)

    def test_job_preflight_keeps_original_opt_in_and_never_claims_effective_execution(self):
        config=configuration(); job=dict(kind='timelearner_native_training_job',schema_version=1,
            owner_class='NNeuronTimeLearner', implementation_id='declared-only',configuration=config,profile_archives=[],
            optional_modes=dict(sync_capacitance_trim=0,post_train_tuning=False,auto_calibrate_threshold=False),
            calculate_mode=0,structure_build_mode=0,maximum_model_ticks=20000)
        job['sha256']=digest(job);before=deepcopy(job);result=validate_job('train',job)
        self.assertEqual(job,before);self.assertEqual(result['job_sha256'],digest({k:v for k,v in job.items() if k!='sha256'}))
        self.assertFalse(result['effective_model_checked']);self.assertTrue(result['native_configuration_validation_required'])
        scope=result['composite_measurement_declaration']
        self.assertFalse(scope['live_measurement_admission_verified']);self.assertFalse(scope['training_certificate_verified'])
        self.assertEqual({key for key,role in scope['context_policy_field_roles'].items() if role=='diagnostic_only'},
                         {'comparison_radius_ticks','influence_absolute','influence_relative'})

    def test_legacy_one_through_five_cannot_silently_ignore_new_selector(self):
        for version in range(1,6):
            value=configuration();value['schema_version']=version
            if version==5:value['invalid_measurement_recovery']='advance_unassigned_burst'
            with self.subTest(version=version),self.assertRaisesRegex(EvidenceError,'composite_measurement_requires_configuration_schema_6'):
                project_training_configuration(value)

    def test_no_schema5_recovery_or_nested_envelope_is_accepted(self):
        for base in (0,5,6,True,'1'):
            value=configuration();value['base_schema_version']=base
            with self.subTest(base=base),self.assertRaises(EvidenceError):project_composite_configuration(value)
        value=configuration();value['invalid_measurement_recovery']='advance_unassigned_burst'
        with self.assertRaises(EvidenceError):project_composite_configuration(value)
        with self.assertRaises(EvidenceError):project_recovery_configuration(configuration())

    def test_integer_valued_json_numbers_are_semantic_counts_not_boolean_flags(self):
        value=configuration();value['schema_version']=6.;value['base_schema_version']=1.
        value['composite_measurement']['schema_version']=1.
        value['composite_measurement']['attempt_limits']['maximum_groups']=32.
        self.assertEqual(project_composite_configuration(value)['schema_version'],1)
        for invalid in (True,False,None,-1,0,.5,float('nan'),float('inf'),2**53,'32'):
            bad=configuration();bad['composite_measurement']['attempt_limits']['maximum_groups']=invalid
            with self.subTest(invalid=invalid),self.assertRaises(EvidenceError):project_composite_configuration(bad)

    def test_unknown_and_missing_fields_never_default_to_a_new_policy(self):
        for container,key in (('top','composite_measurement'),('composite','method_id'),('context','baseline_absolute'),('geometry','maximum_inputs'),('attempt','maximum_native_probes')):
            value=configuration();c=value['composite_measurement'];target={'top':value,'composite':c,'context':c['context_policy'],'geometry':c['geometry_policy'],'attempt':c['attempt_limits']}[container]
            target.pop(key)
            with self.subTest(container=container),self.assertRaises(EvidenceError):project_composite_configuration(value)
        value=configuration();value['new_unused_factor']=1
        with self.assertRaises(EvidenceError):project_composite_configuration(value)

    def test_native_grid_and_half_timestep_tolerance_are_not_automatically_relaxed(self):
        for gap in (.0004,.001,True):
            value=configuration();value['maximum_sample_gap']=gap
            with self.subTest(gap=gap),self.assertRaises(EvidenceError):project_composite_configuration(value)
        for tolerance in (.00025,.001,-1,float('nan')):
            value=configuration();value['composite_measurement']['context_policy']['time_comparison_tolerance']=tolerance
            with self.subTest(tolerance=tolerance),self.assertRaises(EvidenceError):project_composite_configuration(value)

    def test_dimension_windows_and_recorder_are_explicit(self):
        changes=[lambda v:v['model']['inputs'].pop(),lambda v:v['windows'].pop(),
            lambda v:v['windows'][0].update(begin=-.1),lambda v:v['windows'][0].update(end=.2),
            lambda v:v.update(record_spikes=True),lambda v:v.update(peak_selection='assigned_burst_wave')]
        for edit in changes:
            value=configuration();edit(value)
            with self.assertRaises(EvidenceError):project_composite_configuration(value)

    def test_insufficient_group_capacity_is_rejected_but_small_attempt_budget_stays_explicit(self):
        value=configuration();value['composite_measurement']['context_policy']['maximum_native_probes']=3
        with self.assertRaises(EvidenceError):project_composite_configuration(value)
        value=configuration();value['composite_measurement']['attempt_limits']['maximum_native_probes']=1
        self.assertEqual(project_composite_configuration(value)['schema_version'],1)

    def test_protocol_four_binds_topology_source_and_declared_windows(self):
        for branch in (False,True):
            for n in (2,4,5):
                config=configuration(branch=branch,n=n);p=protocol(config);before=deepcopy(p)
                with self.subTest(branch=branch,n=n):
                    validate_composite_protocol(p,config);self.assertEqual(p,before)

    def test_protocol_cannot_move_window_after_observation_or_change_method(self):
        config=configuration()
        for change in ('window','policy','pattern','routing','schema','assignment','bool'):
            p=protocol(config)
            if change=='window':p['composite_measurement']['input_windows'][0]['begin_offset']=.01
            elif change=='policy':p['composite_measurement']['geometry_policy']['repeatability_absolute']=.1
            elif change=='pattern':p['pattern_hash']='0'*64
            elif change=='routing':p['routing']='branch_solo_burst'
            elif change=='schema':p['schema_version']=3
            elif change=='assignment':p['wave_assignment']='ordered_whole_burst'
            else:p['composite_measurement']['context_policy']['comparison_radius_ticks']=True
            with self.subTest(change=change),self.assertRaises(EvidenceError):validate_composite_protocol(p,config)


if __name__=='__main__':unittest.main()
