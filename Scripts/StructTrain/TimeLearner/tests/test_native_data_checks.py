"""Server-only DATA controller metadata; no native/kernel success is inferred."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from .. import native_data_checks as subject
from ..resource_reservations import ReservationError


def declaration():
    base = '/media/user/Data/TimeLearnerRefactor'
    return dict(kind='timelearner_native_data_checks', schema_version=1, job_id='recorded-cases',
        worker_host='M40', execution_root=base, tool_commit='a'*40,
        source=dict(path=base+'/SDK', commit='b'*40),
        runtime_manifest=dict(path=base+'/runtime-manifest.json', sha256='c'*64),
        inputs=[dict(name='recorded.qz', path=base+'/inputs/recorded.qz', bytes=7, sha256='d'*64)],
        cases=[dict(name='classic', test_id='Recorded/Classic'), dict(name='branch', test_id='Recorded/Branch')],
        limits=dict(memory_bytes=512*1024**2, tasks=32, maximum_wall_seconds=660,
            leaf_memory_bytes=1024**3, leaf_tasks=64, leaf_wall_seconds=300,
            reservation_memory_bytes=1536*1024**2),
        disk=dict(minimum_free_bytes=1024**3, maximum_output_bytes=1024**3))


class NativeDataChecksTest(unittest.TestCase):
    def test_exact_closed_request_has_no_command_or_build_extension(self):
        source = declaration();self.assertEqual(subject.validate_request(source), source)
        for key in ('command', 'module', 'build', 'environment', 'arguments'):
            changed = copy.deepcopy(source);changed[key] = 'extra'
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'request_schema'):
                subject.validate_request(changed)

    def test_schema_bool_unknown_and_extra_fields_refuse(self):
        for version in (True, 2, '1', None):
            changed = declaration();changed['schema_version'] = version
            with self.subTest(version=version), self.assertRaisesRegex(ValueError, 'request_schema'):
                subject.validate_request(changed)

    def test_id_and_workspace_cannot_escape_layout(self):
        for field, value in [('job_id', '../escape'), ('job_id', 'a/b'), ('tool_commit', 'short'),
                             ('execution_root', '/tmp'), ('worker_host', '')]:
            changed = declaration();changed[field] = value
            with self.subTest(field=field, value=value), self.assertRaisesRegex(ValueError, 'job_identity'):
                subject.validate_request(changed)

    def test_source_and_runtime_binding_are_exact(self):
        for field in ('source', 'runtime_manifest'):
            for change in (dict(path='relative'), dict(extra=True)):
                changed = declaration();changed[field].update(change)
                with self.subTest(field=field, change=change), self.assertRaisesRegex(ValueError, 'binding'):
                    subject.validate_request(changed)

    def test_inputs_keep_production_staging_name_size_and_digest_guards(self):
        for change in (dict(name='../x'), dict(bytes=True), dict(sha256='bad'), dict(path='relative')):
            changed = declaration();changed['inputs'][0].update(change)
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, 'inputs'):
                subject.validate_request(changed)

    def test_empty_or_unbounded_case_inventory_refuses(self):
        for cases in ([], declaration()['cases']*17, [dict(name='x', test_id='invalid')],
                      [dict(name='../x', test_id='Recorded/Classic')]):
            changed = declaration();changed['cases'] = cases
            with self.subTest(cases=len(cases)), self.assertRaisesRegex(ValueError, 'cases'):
                subject.validate_request(changed)

    def test_duplicate_case_name_casefold_and_test_id_refuse(self):
        for change in (dict(name='CLASSIC'), dict(test_id='Recorded/Classic')):
            changed = declaration();changed['cases'][1].update(change)
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, 'duplicate_case'):
                subject.validate_request(changed)

    def test_bool_zero_and_aggregate_limits_refuse(self):
        for field, value in [('leaf_tasks', True), ('tasks', 0), ('maximum_wall_seconds', 600),
                             ('reservation_memory_bytes', 1024**3)]:
            changed = declaration();changed['limits'][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                subject.validate_request(changed)

    def test_disk_budget_bool_or_missing_field_is_not_a_budget(self):
        for disk in ({}, dict(minimum_free_bytes=True, maximum_output_bytes=100)):
            changed = declaration();changed['disk'] = disk
            with self.subTest(disk=disk), self.assertRaisesRegex(ValueError, 'disk'):
                subject.validate_request(changed)

    def test_layout_has_one_finite_sibling_controller(self):
        value = declaration();base, output, controller = subject.layout(value)
        self.assertEqual(output, base/'readbacks/recorded-cases')
        self.assertEqual(controller, output.with_name(output.name+'-controller'))
        self.assertEqual([output/r['name']/'process/contained' for r in value['cases']],
            [output/'classic/process/contained', output/'branch/process/contained'])

    def fixture(self, root):
        value = declaration();value['execution_root'] = str(root)
        for name in ('tool', 'SDK', 'runtime', 'inputs', 'controls'):
            (root/name).mkdir()
        (root/'readbacks').mkdir()
        source = root/'inputs/recorded.qz';source.write_bytes(b'fixture')
        manifest = root/'controls/runtime.json';manifest.write_bytes(b'{}')
        spec = root/'controls/request.json';spec.write_bytes(b'{}')
        value['source']['path'] = str(root/'SDK');value['runtime_manifest']['path'] = str(manifest)
        value['inputs'][0]['path'] = str(source)
        return value, dict(executable=dict(path=str(root/'runtime/test'))), spec

    def test_resources_reserve_inputs_runtime_source_and_owned_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve();value, runtime, spec = self.fixture(root)
            with patch.object(subject, 'ROOT', root/'tool'):
                rows = subject.resources(value, runtime, spec)
            writes = [r for r in rows if r['access'] == 'write']
            self.assertEqual(writes, [dict(path=str(root/'readbacks/recorded-cases'), access='write')])
            reads = {r['path'] for r in rows if r['access'] == 'read'}
            for path in (root/'tool', root/'SDK', root/'runtime', spec.parent, root/'inputs'):
                self.assertIn(str(path), reads)
            # The actual registry contract, not a parallel test-only schema.
            subject.validate_resource_trees(rows)

    def test_read_resource_outside_workspace_and_alias_refuse(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory).resolve();value, runtime, spec = self.fixture(root)
            with patch.object(subject, 'ROOT', root/'tool'):
                with self.assertRaisesRegex(ValueError, 'outside_workspace'):
                    subject.resources(value, runtime, Path(outside).resolve())
                alias = root/'alias';alias.symlink_to(root/'inputs/recorded.qz')
                value['inputs'][0]['path'] = str(alias)
                with self.assertRaises(ValueError): subject.resources(value, runtime, spec)

    def test_input_cannot_be_inside_owned_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve();value, runtime, spec = self.fixture(root)
            _, output, _ = subject.layout(value);output.mkdir()
            source = output/'input.qz';source.write_bytes(b'fixture')
            value['inputs'][0]['path'] = str(source)
            with patch.object(subject, 'ROOT', root/'tool'):
                with self.assertRaisesRegex(ValueError, 'input_output_overlap'):
                    subject.resources(value, runtime, spec)

    def test_parent_tree_is_deduplicated_and_registry_rejects_file_lease(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve();value, runtime, spec = self.fixture(root)
            second = root/'inputs/second.qz';second.write_bytes(b'fixture')
            value['inputs'].append(dict(value['inputs'][0], name='second.qz', path=str(second)))
            with patch.object(subject, 'ROOT', root/'tool'):
                rows = subject.resources(value, runtime, spec)
            self.assertEqual(sum(r['path'] == str(root/'inputs') for r in rows), 1)
            with self.assertRaisesRegex(ReservationError, 'requires_directory_tree'):
                subject.validate_resource_trees([dict(path=value['inputs'][0]['path'], access='read')])

    def test_control_bytes_and_replaced_identity_refuse(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve();original = root/'original';copied = root/'copied'
            original.write_bytes(b'input');copied.write_bytes(b'input')
            identity = subject._control_identity(original)
            subject._controls(original, copied, identity, b'input')
            copied.write_bytes(b'other')
            with self.assertRaisesRegex(ValueError, 'control_changed'):
                subject._controls(original, copied, identity, b'input')
            copied.write_bytes(b'input');replacement = root/'replacement';replacement.write_bytes(b'input')
            replacement.replace(original)
            with self.assertRaisesRegex(ValueError, 'control_changed'):
                subject._controls(original, copied, identity, b'input')

    def test_runtime_hash_refuses_before_runtime_execution_api(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve();path = root/'runtime.json';path.write_bytes(b'{}')
            value = declaration();value['runtime_manifest']['path'] = str(path)
            with patch.object(subject, 'verify_runtime') as verifier:
                with self.assertRaisesRegex(ValueError, 'manifest_changed'): subject._bound_runtime(value)
                verifier.assert_not_called()

    def test_context_changed_copy_refuses_before_process_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve();(root/'readbacks').mkdir()
            value = declaration();value['execution_root'] = str(root);value['worker_host'] = subject.socket.gethostname()
            _, _, controller = subject.layout(value);controller.mkdir()
            raw = json.dumps(value).encode();(controller/'request.json').write_bytes(raw)
            subject._write(controller/'launch-intent.json', dict(supervisor={}, request_sha256='0'*64,
                request_path=str(root/'source.json'), external_identity={}))
            with patch.object(subject, 'BASES', {root}):
                with self.assertRaisesRegex(ValueError, 'request_copy_changed'): subject._context(controller)

    def test_context_cannot_borrow_other_supervisor_request(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve();(root/'readbacks').mkdir()
            value = declaration();value['execution_root'] = str(root);value['worker_host'] = subject.socket.gethostname()
            _, _, controller = subject.layout(value);controller.mkdir()
            raw = json.dumps(value).encode();(controller/'request.json').write_bytes(raw)
            identity = dict(pid=123, start_ticks='456', boot_id='boot', uid=1000)
            subject._write(controller/'launch-intent.json', dict(supervisor=identity,
                request_sha256=subject._hash(raw), request_path=str(root/'source.json'), external_identity={}))
            outer = controller/'process/contained';outer.mkdir(parents=True)
            request = dict(controller=dict(pid=999, start_ticks='456'), boot_id='boot', uid=1000)
            subject._write(outer/'request.json', request)
            with patch.object(subject, 'BASES', {root}):
                with self.assertRaisesRegex(ValueError, 'supervisor_binding_changed'): subject._context(controller)


if __name__ == '__main__':
    unittest.main()
