"""Owned native controller DATA/path/immutability regressions; server only.

These tests make no model, native-build, physical or kernel-success claims.
Real ownership tests are in test_owned_native_job_kernel.py.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from .. import owned_native_job as subject


def request():
    return {'kind':'timelearner_owned_native_job','schema_version':1,'job_id':'native-case',
            'worker_host':'worker','execution_root':'/media/user/Data/TimeLearnerRefactor',
            'tool_commit':'a'*40,'job':{'path':'/input/job.json','sha256':'b'*64},
            'preparation':{'path':'/input/preparation.json','sha256':'c'*64}}


class OwnedNativeMetadataTest(unittest.TestCase):
    def test_request_has_no_user_command_or_worker_module_extension(self):
        source=request();self.assertEqual(subject.validate_request(source),source)
        for key in ('arguments','module','worker','limits','operation'):
            with self.subTest(key=key):
                changed=copy.deepcopy(source);changed[key]='injected'
                with self.assertRaisesRegex(ValueError,'owned_native_request_schema'):
                    subject.validate_request(changed)

    def test_boolean_and_unknown_schema_are_not_v1(self):
        for version in (True,1.0,2,'1'):
            changed=request();changed['schema_version']=version
            with self.subTest(version=version),self.assertRaisesRegex(ValueError,'owned_native_request_schema'):
                subject.validate_request(changed)

    def test_short_commit_and_bad_bound_digest_fail_before_launch(self):
        changed=request();changed['tool_commit']='a'*8
        with self.assertRaisesRegex(ValueError,'owned_native_tool_commit'):
            subject.validate_request(changed)
        changed=request();changed['job']['sha256']='not-a-hash'
        with self.assertRaisesRegex(ValueError,'owned_native_file_binding'):
            subject.validate_request(changed)

    def test_relative_or_extra_input_binding_is_rejected(self):
        for mutate in (lambda x:x['job'].update(path='relative.json'),
                       lambda x:x['preparation'].update(bytes=123)):
            changed=request();mutate(changed)
            with self.assertRaisesRegex(ValueError,'owned_native_file_binding'):
                subject.validate_request(changed)

    def test_bound_input_real_bytes_and_symlink_alias(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();path=root/'input.json';path.write_bytes(b'{"value":1}')
            binding={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
            self.assertEqual(subject._file_record(binding)[0],{'value':1})
            external={k:{'path':str(path),'identity':subject._control_identity(path),
                'sha256':binding['sha256']} for k in ('job','preparation')}
            subject._control_guard(root,{},external)

            path.write_bytes(b'{"value":2}')
            with self.assertRaisesRegex(ValueError,'owned_native_external_control_identity_changed'):
                subject._control_guard(root,{},external)

            with self.assertRaisesRegex(ValueError,'owned_native_input_changed'):
                subject._file_record(binding)
            link=root/'alias.json';link.symlink_to(path)
            with self.assertRaisesRegex(ValueError,'collector_symlink_path'):
                subject._file_record({'path':str(link),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})

    def test_replaced_identical_control_bytes_are_not_the_original_consumption_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();(root/'inputs').mkdir();path=root/'inputs/job.json';path.write_bytes(b'{}')
            expected={'job.json':{'identity':subject._control_identity(path),'sha256':hashlib.sha256(b'{}').hexdigest()}}
            subject._control_guard(root,expected)
            replacement=root/'replacement';replacement.write_bytes(b'{}');os.replace(replacement,path)
            with self.assertRaisesRegex(ValueError,'owned_native_consumed_control_identity_changed'):
                subject._control_guard(root,expected)

    def test_same_inode_rewrite_and_restore_is_still_a_consumption_change(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();(root/'inputs').mkdir();path=root/'inputs/job.json';path.write_bytes(b'{}')
            expected={'job.json':{'identity':subject._control_identity(path),'sha256':hashlib.sha256(b'{}').hexdigest()}}
            time.sleep(.01);path.write_bytes(b'[]');path.write_bytes(b'{}')
            with self.assertRaisesRegex(ValueError,'owned_native_consumed_control_identity_changed'):
                subject._control_guard(root,expected)

    def test_malformed_launch_does_not_create_controller_or_other_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();path=root/'request.json';bad=request();bad['module']='arbitrary'
            path.write_text(json.dumps(bad),encoding='utf-8')
            before={p.name for p in root.iterdir()}
            with self.assertRaisesRegex(ValueError,'owned_native_request_schema'):
                subject.launch(path)
            self.assertEqual({p.name for p in root.iterdir()},before)

    def test_process_identity_cannot_turn_unknown_or_boolean_pid_into_closed(self):
        valid={'pid':os.getpid(),'start_ticks':'1','boot_id':'a'*36,'uid':os.getuid()}
        for key,value in [('pid',True),('pid',0),('start_ticks','01'),('uid',False),('boot_id','short')]:
            bad={**valid,key:value}
            with self.subTest(key=key,value=value),self.assertRaisesRegex(ValueError,'owned_native_process_identity_invalid'):
                subject._same_process(bad)

    def test_recover_cannot_treat_absent_supervisor_identity_as_dead(self):
        with patch.object(subject,'_context',return_value=(Path('/unused'),request(),{})), \
             patch.object(subject,'status',return_value={'supervisor_identity_known':False,'supervisor_live':False}):
            with self.assertRaisesRegex(ValueError,'owned_native_supervisor_not_proven_closed'):
                subject.recover('/unused')


if __name__=='__main__':
    unittest.main()
