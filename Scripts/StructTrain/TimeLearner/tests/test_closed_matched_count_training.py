"""Audit an actual finished N0 Train once, without a second package JSON tree."""
from pathlib import Path
import json
import os
from unittest.mock import patch
import unittest

from .. import learned_evidence, native_pipeline_worker, stopped_evidence
from ..native_evidence import load, require
from ..runtime import file_record


class ClosedMatchedCountTrainingTest(unittest.TestCase):
    def test_actual_complete_primary_and_single_package_decode(self):
        native=Path(os.environ['TIMELEARNER_MATCHED_COUNT_NATIVE']).resolve(strict=True)
        outer=native.parent.parent
        process=load(native.parent/'process/result.json')
        terminal=load(outer/'terminal.json')
        require(process['execution']=='completed' and process['all_processes_closed'] is True and
                process['runtime_provenance']=='loaded_files_captured' and
                terminal['full_primary_audit_complete'] is False,
                'closed_count_requires_original_closed_pending_audit_attempt')
        job=load(native/'job.json');execution=load(native/'execution.json')
        self.assertEqual(job['configuration']['model']['normalization'],'N0')
        self.assertEqual(len(job['configuration']['model']['inputs']),4)
        self.assertEqual(job['sha256'],terminal['job_sha256'])
        self.assertEqual(execution['job_sha256'],job['sha256'])
        self.assertEqual(terminal['native_execution_sha256'],execution['sha256'])
        self.assertIs(type(execution['completed_boundary']),bool)
        name='train_learned_state.json' if execution['completed_boundary'] else 'train_stopped_state.json'
        self.assertEqual(execution['package_path'],name)
        package=native/name;before=file_record(package);reads=[]
        def traced_load(path):
            if Path(path).resolve(strict=True)==package:
                reads.append(str(path))
            return load(path)
        # Only instrument file loading; the complete production validator,
        # simulator output, model, history, raw packets and traces are real.
        with patch.object(native_pipeline_worker,'load',traced_load), \
             patch.object(learned_evidence,'load',traced_load), \
             patch.object(stopped_evidence,'load',traced_load):
            audit=native_pipeline_worker.audit_execution('train',native,job)
        self.assertEqual(len(reads),1)
        self.assertEqual(file_record(package),before)
        self.assertEqual(audit['training_outcome'],execution['training_outcome'])
        self.assertEqual(audit['completed_boundary'],execution['completed_boundary'])
        self.assertFalse(audit['native_execution_verified'])
        self.assertIsNone(audit['evaluation_verdict'])
        result=dict(kind='timelearner_closed_matched_count_training_audit',schema_version=1,
            native=str(native),consumed_job_sha256=job['sha256'],
            consumed_job_file=file_record(native/'job.json'),execution_file=file_record(native/'execution.json'),
            original_pending_terminal=file_record(outer/'terminal.json'),source_package=before,
            process_record=file_record(native.parent/'process/result.json'),
            source_package_full_decodes=len(reads),full_primary_audit=audit,
            next_operation='export_completed_solo' if audit['completed_boundary'] else 'diagnostic_evaluation_of_actual_stopped_model',
            original_outcome_unchanged=True,native_execution_attested_by_portable_reader=False,
            classification_performed=False,scientific_verdict=None)
        path=Path(os.environ['TMPDIR'])/'matched-count-training-audit.json'
        require(not path.exists(),'closed_count_audit_fresh_output_required')
        path.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
