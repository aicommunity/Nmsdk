"""Controller declarations cannot change frozen physics or hide phase budgets."""
from copy import deepcopy
import unittest

from ..native_evidence import EvidenceError
from ..windows_frozen_physical_followups import validate_request


def request():
    record = lambda name: dict(path='C:/Projects/TimeLearnerWorker/controls/'+name,
                               sha256='a'*64, size=1024)
    return dict(kind='timelearner_windows_frozen_physical_followups', schema_version=1,
        job_id='classic-cap8-frozen-followups', python_root='b'*40,
        source_repeat_request=record('source/request.json'),
        source_repeat_owner=dict(pid=123, executable='C:/Tools/python.exe', creation_filetime='134401019930872925'),
        preparation_gate=record('gate.json'), preparation_source_inventory=record('projection.json'),
        native_wall_seconds=dict(third_pulse=5400, new_foils=18000), native_memory_bytes=8*1024**3,
        maximum_wait_seconds=60000, maximum_whole_seconds=108000)


class WindowsFrozenFollowupRequest(unittest.TestCase):
    def test_declared_two_phases_and_exact_owner_are_preserved(self):
        q = request(); before = deepcopy(q)
        self.assertEqual(validate_request(q), before)
        self.assertEqual(q, before)

    def test_unrequested_physics_or_threshold_factors_are_rejected(self):
        for key in ('threshold', 'normalization', 'new_Train', 'third_pulse_ticks'):
            with self.subTest(key=key), self.assertRaises(EvidenceError):
                validate_request(dict(request(), **{key: 1}))

    def test_boolean_and_insufficient_whole_budgets_are_rejected(self):
        for key,value in [('native_memory_bytes', True), ('maximum_wait_seconds', True),
                          ('maximum_whole_seconds', 86400)]:
            with self.subTest(key=key), self.assertRaises(EvidenceError):
                validate_request(dict(request(), **{key:value}))
        for key in ('third_pulse', 'new_foils'):
            q = request(); q['native_wall_seconds'][key] = True
            with self.subTest(key=key), self.assertRaises(EvidenceError):
                validate_request(q)

    def test_identity_ambiguity_or_foreign_paths_are_rejected(self):
        for key,value in [('pid', True), ('creation_filetime', 134401019930872925), ('executable', 'python.exe')]:
            q = request(); q['source_repeat_owner'][key] = value
            with self.subTest(key=key), self.assertRaises(EvidenceError):
                validate_request(q)
        for name in ('../request.json', '/tmp/request.json'):
            q = request(); q['source_repeat_request']['path'] = name
            with self.subTest(name=name), self.assertRaises(EvidenceError):
                validate_request(q)
