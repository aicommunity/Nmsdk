"""Archive inclusion contracts only; these bytes attest no native execution."""
import hashlib
import json
import unittest

from ..artifact_bundle import verify_packaged_run_closure, verify_packaged_run_inventory
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError


class FileSourceArchiveInventoryContractTest(unittest.TestCase):
    def files(self, operation='diagnostic-evaluate', **changes):
        files = {'run/input/job.json': b'{"role":"original resolved job retained"}',
                 'run/input/native-job-source.json': b'{"role":"envelope retained"}',
                 'run/input/source/state.json': b'{"history":["all evidence retained"]}'}
        body = dict(kind='timelearner_native_pipeline_run_manifest', schema_version=5,
                    operation=operation, source_package_path='input/source/state.json',
                    process_policy={'role': 'opaque here; production run auditor validates it'},
                    job_source_transport={'transport': 'checked-file-source-v1',
                                          'path': 'input/native-job-source.json'},
                    artifacts=[dict(path=n.removeprefix('run/'), bytes=len(raw),
                                    sha256=hashlib.sha256(raw).hexdigest()) for n, raw in files.items()])
        body.update(changes);body['sha256'] = sha(body)
        files['run/run-manifest.json'] = json.dumps(body).encode()
        return files

    def test_all_source_roles_retain_original_job_envelope_and_complete_source(self):
        for operation in ('export', 'evaluate', 'diagnostic-evaluate', 'physical-model-evaluate'):
            files = self.files(operation)
            result = verify_packaged_run_closure(files)
            records = {n: dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()) for n, raw in files.items()}
            self.assertEqual(result, verify_packaged_run_inventory(records,
                {'run/run-manifest.json': files['run/run-manifest.json']}))
            self.assertEqual(result['artifact_entries_verified'], 3)
            self.assertIsNone(result['scientific_verdict'])
            self.assertNotIn('validity', result)

    def test_dropped_or_changed_envelope_and_source_fail_byte_inclusion(self):
        for operation in ('export', 'evaluate', 'diagnostic-evaluate', 'physical-model-evaluate'):
            for name in ('run/input/job.json', 'run/input/native-job-source.json', 'run/input/source/state.json'):
                for mutation in ('drop', 'change'):
                    files = self.files(operation)
                    if mutation == 'drop':files.pop(name)
                    else:files[name] += b'changed'
                    with self.subTest(operation=operation, name=name, mutation=mutation), self.assertRaises(EvidenceError):
                        verify_packaged_run_closure(files)

    def test_rehashed_cold_or_wrong_transport_roles_cannot_acquire_schema_five(self):
        for changes in (dict(operation='train'), dict(operation='preflight'), dict(operation='probe'),
                        dict(job_source_transport=None),
                        dict(job_source_transport={'transport': 'unknown', 'path': 'input/native-job-source.json'}),
                        dict(job_source_transport={'transport': 'checked-file-source-v1', 'path': '../other'})):
            with self.subTest(changes=changes), self.assertRaisesRegex(EvidenceError, 'file_source_schema'):
                verify_packaged_run_closure(self.files(**changes))

    def test_rehashing_an_inventory_without_either_job_still_rejects(self):
        for missing in ('input/job.json', 'input/native-job-source.json'):
            files = self.files();body = json.loads(files['run/run-manifest.json'])
            files.pop('run/'+missing)
            body['artifacts'] = [r for r in body['artifacts'] if r['path'] != missing]
            body.pop('sha256');body['sha256'] = sha(body)
            files['run/run-manifest.json'] = json.dumps(body).encode()
            with self.subTest(missing=missing), self.assertRaisesRegex(EvidenceError, 'file_source_missing'):
                verify_packaged_run_closure(files)
