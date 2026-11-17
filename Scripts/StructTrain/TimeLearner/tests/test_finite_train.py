"""The finite owner admits real signed Train input, not arbitrary commands."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from ..finite_train import preflight_jobs
from ..native_data_checks import validate_request
from ..native_evidence import EvidenceError
from .test_native_data_checks import declaration
from .test_candidate_window_training_job import cold7, job


def request():
    value = declaration();value.update(schema_version=3, operation='train')
    value['cases'] = [dict(name='candidate', job_name='train.json')]
    value['inputs'][0]['name'] = 'train.json'
    return value


class FiniteTrainTest(unittest.TestCase):
    def test_only_explicit_train_and_exact_input_roles_are_admitted(self):
        value = request();self.assertEqual(validate_request(value), value)
        for operation in ('evaluate', 'diagnostic-evaluate', 'calibrate', 'export', 'command', None):
            changed = deepcopy(value);changed['operation'] = operation
            with self.subTest(operation=operation), self.assertRaisesRegex(EvidenceError, 'finite_train_operation'):
                validate_request(changed)
        for cases in ([], value['cases']*2, [dict(name='candidate', job_name='foreign.json')],
                      [dict(name='candidate', job_name='train.json', command='extra')]):
            changed = deepcopy(value);changed['cases'] = cases
            with self.subTest(cases=cases), self.assertRaises(EvidenceError):validate_request(changed)

    def test_aggregate_reservation_cannot_omit_the_native_sibling_or_overflow(self):
        for memory in (True, 1024**3, 2**63):
            value = request();value['limits']['reservation_memory_bytes'] = memory
            with self.subTest(memory=memory), self.assertRaises(EvidenceError):validate_request(value)

    def test_actual_job_bytes_and_training_semantics_are_checked_before_launch(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'train.json'
            value = request()
            def bind(payload):
                raw=json.dumps(payload).encode();path.write_bytes(raw)
                value['inputs']=[dict(name='train.json', path=str(path), bytes=len(raw),
                                     sha256=hashlib.sha256(raw).hexdigest())]
            for branch in (False, True):
                bind(job(cold7(branch=branch, n=4)))
                result=preflight_jobs(value)
                self.assertEqual(result['candidate']['job_sha256'], json.loads(path.read_bytes())['sha256'])
                self.assertFalse(result['candidate']['effective_model_checked'])
            path.write_bytes(path.read_bytes()+b' ')
            with self.assertRaisesRegex(EvidenceError, 'finite_train_job_changed'):preflight_jobs(value)
            bind(dict(kind='unsupported-template'))
            with self.assertRaises(EvidenceError):preflight_jobs(value)

    def test_signed_but_invalid_factor_is_not_accepted_as_a_train_job(self):
        from ..model_identity import canonical_model_sha256
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'train.json';value=request();payload=job(cold7())
            payload['configuration']['search']['tolerances']['amplitude_absolute'] = -1.
            payload.pop('sha256');payload['sha256'] = canonical_model_sha256(payload)
            raw=json.dumps(payload).encode();path.write_bytes(raw)
            value['inputs']=[dict(name='train.json', path=str(path), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())]
            with self.assertRaises(EvidenceError):preflight_jobs(value)
