"""Holdout declarations on an actual frozen DATA job; no model execution."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..frozen_duration_holdout import make_protocol, validate_protocol
from ..frozen_physical_foil_study import declare_job, condition
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load, number
from ..prepared_physical_study import declare
from ..runtime import file_record


class FrozenDurationHoldoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        descriptor = os.environ.get('TIMELEARNER_DURATION_HOLDOUT_FIXTURE')
        if descriptor:
            fixture = load(Path(descriptor))
            if not (set(fixture) == {'kind','schema_version','job','runtime','source_terminal'} and
                    fixture.get('kind') == 'timelearner_duration_holdout_recorded_DATA_fixture' and
                    type(fixture.get('schema_version')) is int and fixture['schema_version'] == 1):
                raise AssertionError('unsupported actual DATA fixture')
            cls.paths = [Path(fixture[k]['path']) for k in ('job','runtime','source_terminal')]
            if any(file_record(p) != fixture[k] for p,k in zip(cls.paths,('job','runtime','source_terminal'))):
                raise AssertionError('actual DATA fixture bytes changed')
            cls.original = load(cls.paths[0]); cls.runtime = load(cls.paths[1]); terminal = load(cls.paths[2])
            model = cls.original['source_model_data']
            if not (terminal['kind'] == 'timelearner_actual_windows_physical_replay' and
                    terminal['execution'] == 'completed' and terminal['validity'] == 'valid' and
                    terminal['transfer_valid'] and terminal['all_eight_waveforms_and_events_preserved'] and
                    len(terminal['rows']) == 8 and all(r['waveform_preserved'] and
                        r['stimulus_and_spike_events_preserved'] for r in terminal['rows']) and
                    terminal['model_revision'] == model['model_revision'] and
                    terminal['source_model_data_sha256'] == model['sha256']):
                raise AssertionError('actual recorded DATA roundtrip is not verified')
            cls.threshold = number(terminal['threshold'])
            cls.paths.append(Path(descriptor))
        else:
            source = Path(os.environ['TIMELEARNER_FOIL_SOURCE'])
            cls.paths = [source/'input/job.json', source/'process/runtime.json', source/'run-manifest.json']
            cls.original = load(cls.paths[0]); cls.runtime = load(cls.paths[1])
            cls.threshold = load(cls.paths[2])['analysis']['metrics']['effective_threshold']
        cls.records = [file_record(p) for p in cls.paths]
        cls.target = next(t for t in cls.original['trials'] if t['label'] == 'target')

    @classmethod
    def tearDownClass(cls):
        if [file_record(p) for p in cls.paths] != cls.records:
            raise AssertionError('original frozen source changed during holdout design checks')

    def protocol(self, **kwargs):
        return make_protocol(self.original, seed=20261123, **kwargs)

    def binding(self, job, design, *, runtime=None, threshold=None):
        return condition(job, design, self.runtime if runtime is None else runtime,
            dict(threshold=self.threshold if threshold is None else threshold,
                 native_memory_bytes=4*1024**3, maximum_native_wall_seconds=7200))

    def test_new_negatives_match_duration_and_repeat_only_the_original_target(self):
        protocol = self.protocol(); before = deepcopy(self.original)
        job, design = declare_job(self.original, 'heldout/a1', holdout_protocol=protocol)
        self.assertEqual(len(job['trials']), 8)
        self.assertEqual([i for i,t in enumerate(job['trials']) if t['label']=='target'], [5])
        self.assertEqual(job['trials'][5]['sample_id'], self.target['sample_id'])
        self.assertEqual(job['trials'][5]['pattern_isi'], self.target['pattern_isi'])
        excluded = set(protocol['excluded_pattern_hashes'])
        self.assertGreater(len(excluded), 8)
        for row in job['trials']:
            self.assertEqual(len(row['pattern_isi']), 4)
            self.assertEqual(row['pattern_isi'][0], self.target['pattern_isi'][0])
            self.assertEqual(sum(round(v*protocol['frequency_hz']) for v in row['pattern_isi'][1:]),
                             protocol['total_interval_ticks'])
            self.assertEqual(row['duration'], self.target['duration'])
            self.assertEqual(row['maximum_samples'], self.target['maximum_samples'])
            if row['label']=='foil':self.assertNotIn(row['pattern_hash'], excluded)
        self.assertEqual(job['source_model_data'], before['source_model_data'])
        self.assertEqual(job['criterion'], before['criterion'])
        self.assertEqual(self.original, before)
        self.assertIn('negative_patterns_only', design['independence_scope'])

    def test_signed_tick_declaration_replays_and_is_independent_of_source_row_order(self):
        protocol = self.protocol(); self.assertEqual(protocol, self.protocol())
        self.assertEqual(validate_protocol(deepcopy(protocol), self.original), protocol)
        changed = deepcopy(self.original); changed['trials'].reverse()
        self.assertEqual(make_protocol(changed, seed=20261123), protocol)

    def test_corrupt_or_rebound_declarations_fail_even_after_resigning(self):
        protocol = self.protocol()
        for change in (
                lambda p:p['foil_interval_ticks'].__setitem__(0, [160,320,480]),
                lambda p:p['excluded_pattern_hashes'].pop(),
                lambda p:p.__setitem__('sampling_seed', 20261124),
                lambda p:p.__setitem__('draws_used', True),
                lambda p:p['foil_interval_ticks'][0].__setitem__(0, float('nan')),
                lambda p:p.__setitem__('schema_version', True),
                lambda p:p.__setitem__('unrecognized', 1)):
            with self.subTest(change=change):
                broken = deepcopy(protocol); change(broken)
                # The first three mutations have valid JSON and a new digest,
                # but cannot replace the predeclared source/sampling protocol.
                try:broken['sha256'] = sha({k:v for k,v in broken.items() if k!='sha256'})
                except ValueError:pass
                with self.assertRaises((EvidenceError, ValueError)):
                    validate_protocol(broken, self.original)

    def test_sampler_exhaustion_is_bounded(self):
        with self.assertRaisesRegex(EvidenceError, 'candidate_budget_exhausted'):
            self.protocol(foil_count=2, target_position=1, minimum_interval_ticks=320,
                          maximum_interval_ticks=320, draw_limit=3)

    def test_attempt_and_executable_location_do_not_change_case_or_matrix_identity(self):
        protocol = self.protocol()
        first, a = declare_job(self.original, 'attempt/a1', holdout_protocol=protocol)
        other, b = declare_job(self.original, 'another-attempt/b2', holdout_protocol=protocol)
        runtime = deepcopy(self.runtime); runtime['executable']['path'] = '/another/path/to/the/same/executable'
        self.assertEqual(self.binding(first,a)['condition_fingerprint'],
                         self.binding(other,b,runtime=runtime)['condition_fingerprint'])
        self.assertEqual({k:v['condition_fingerprint'] for k,v in self.binding(first,a)['case_conditions'].items()},
                         {k:v['condition_fingerprint'] for k,v in self.binding(other,b,runtime=runtime)['case_conditions'].items()})

    def test_an_added_foil_changes_the_matrix_without_changing_existing_cases(self):
        first, a = declare_job(self.original, 'heldout/a1', holdout_protocol=self.protocol())
        other, b = declare_job(self.original, 'heldout/b2', holdout_protocol=self.protocol(foil_count=8))
        left, right = self.binding(first,a), self.binding(other,b)
        self.assertNotEqual(left['condition_fingerprint'], right['condition_fingerprint'])
        self.assertEqual(set(left['case_conditions']) | set(right['case_conditions']), set(right['case_conditions']))
        self.assertEqual(len(right['case_conditions'])-len(left['case_conditions']), 1)
        for sample, value in left['case_conditions'].items():
            self.assertEqual(value['condition_fingerprint'], right['case_conditions'][sample]['condition_fingerprint'])

    def test_own_input_and_threshold_affect_case_identity(self):
        job, design = declare_job(self.original, 'heldout/a1', holdout_protocol=self.protocol())
        before = self.binding(job,design); after = self.binding(job,design,threshold=self.threshold+.001)
        values = [v['condition_fingerprint'] for v in before['case_conditions'].values()]
        self.assertEqual(len(set(values)), len(job['trials']))
        for sample in before['case_conditions']:
            self.assertNotEqual(before['case_conditions'][sample]['condition_fingerprint'],
                                after['case_conditions'][sample]['condition_fingerprint'])

    def test_windows_dispatch_uses_the_same_common_matrix_and_condition(self):
        protocol = self.protocol(); job, design = declare_job(self.original, 'heldout/a1', holdout_protocol=protocol)
        other, other_design, binding = declare(self.original, 'heldout/a1',
            dict(protocol='heldout_matched_duration', protocol_document=protocol), self.runtime,
            threshold=self.threshold, memory_bytes=4*1024**3, wall_seconds=7200)
        self.assertEqual((other,other_design), (job,design))
        self.assertEqual(binding, self.binding(job,design))
        with self.assertRaisesRegex(EvidenceError, 'holdout_protocol_required'):
            declare(self.original, 'bad',dict(protocol='heldout_matched_duration',protocol_document=None),
                self.runtime,threshold=self.threshold,memory_bytes=4*1024**3,wall_seconds=7200)

    def test_other_target_clock_or_dimension_cannot_reuse_a_protocol(self):
        protocol = self.protocol()
        for key,value in (('frequency_hz',2001), ('initial_isi',[.01,.08,.16])):
            changed=deepcopy(self.original);changed['source_model_data']['configuration']['model'][key]=value
            with self.assertRaises(EvidenceError):validate_protocol(protocol,changed)
