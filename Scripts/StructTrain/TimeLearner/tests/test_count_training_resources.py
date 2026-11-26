"""Explicit Windows memory declarations preserve scientific and time conditions."""
from copy import deepcopy
import unittest

from ..native_evidence import EvidenceError
from ..prepared_count_training import worker_resource_limits


def request(version=1, kind='timelearner_matched_count_training'):
    record = {'path': 'C:/Projects/TimeLearnerWorker/controls/source.json',
              'sha256': 'a'*64, 'size': 123}
    spec = dict(kind=kind, schema_version=version, python_source='tool', python_root='b'*40,
                sdk_source='sdk', original_job=record, job_file=record, factor_job_file=record,
                run_id='resource-declaration', maximum_synapses=128, output='new-output',
                worker_sha256='c'*64, native_memory_bytes=16*1024**3,
                native_wall_seconds=39600, preflight_wall_seconds=900,
                minimum_free_bytes=10*1024**3, maximum_output_bytes=8*1024**3)
    if kind != 'timelearner_matched_count_training': spec['source_initial_state'] = record
    if kind == 'timelearner_count_candidate_limit_training': spec['maximum_candidates_per_input'] = 24
    if kind == 'timelearner_count_two_sweep_training': spec['native_wall_seconds'] *= 2
    if version == 2: spec.update(native_memory_bytes=8*1024**3, preflight_memory_bytes=4*1024**3)
    return spec


class CountTrainingResourceTest(unittest.TestCase):
    def test_legacy_declarations_keep_the_original_phase_limits(self):
        for kind in ('timelearner_matched_count_training', 'timelearner_count_two_sweep_training',
                     'timelearner_count_candidate_limit_training'):
            with self.subTest(kind=kind):
                self.assertEqual(worker_resource_limits(request(kind=kind)),
                                 dict(preflight_memory_bytes=8*1024**3, native_memory_bytes=16*1024**3))

    def test_explicit_phase_limits_do_not_mutate_the_case_or_its_time_limits(self):
        for kind in ('timelearner_matched_count_training', 'timelearner_count_two_sweep_training',
                     'timelearner_count_candidate_limit_training'):
            with self.subTest(kind=kind):
                spec = request(2, kind); before = deepcopy(spec)
                self.assertEqual(worker_resource_limits(spec),
                                 dict(preflight_memory_bytes=4*1024**3, native_memory_bytes=8*1024**3))
                self.assertEqual(spec, before)

    def test_no_missing_limit_or_legacy_ignored_override_is_accepted(self):
        for version, key in ((1, 'preflight_memory_bytes'), (2, 'preflight_memory_bytes'),
                             (2, 'native_memory_bytes')):
            spec = request(version)
            if version == 1: spec[key] = 4*1024**3
            else: spec.pop(key)
            with self.subTest(version=version, key=key), self.assertRaises(EvidenceError):
                worker_resource_limits(spec)
        spec = request(); spec['native_memory_bytes'] = 8*1024**3
        with self.assertRaisesRegex(EvidenceError, 'legacy_memory_limits'):
            worker_resource_limits(spec)

    def test_boolean_fractional_nonfinite_and_backend_out_of_range_limits_fail(self):
        for key in ('preflight_memory_bytes', 'native_memory_bytes'):
            for value in (True, 0, -1, 8.0*1024**3, float('nan'), float('inf'),
                          32*1024**2-1, 64*1024**3+1):
                spec = request(2); spec[key] = value
                with self.subTest(key=key, value=value), self.assertRaises(EvidenceError):
                    worker_resource_limits(spec)

    def test_memory_declaration_cannot_extend_preflight_or_train_time(self):
        for key, value in (('native_wall_seconds', 79200), ('native_wall_seconds', True),
                           ('preflight_wall_seconds', 1800), ('preflight_wall_seconds', float('inf'))):
            spec = request(2); spec[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(EvidenceError, 'finite_budgets'):
                worker_resource_limits(spec)

    def test_unknown_schema_or_unconsumed_factor_is_rejected(self):
        for version in (True, 1.0, 0, 3):
            spec = request(); spec['schema_version'] = version
            with self.subTest(version=version), self.assertRaises(EvidenceError):
                worker_resource_limits(spec)
        spec = request(2); spec['ignore_memory_preflight'] = True
        with self.assertRaises(EvidenceError):
            worker_resource_limits(spec)
