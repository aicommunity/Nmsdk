"""Read real archived preserve-dynamics results without admitting new jobs."""
from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..external_archive import locate, resolve
from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import (audit_run_manifest, validate_job, _load_source_case,
                                      _validate_job, _historical_reset_analysis)
from ..recognition_evidence import audit_recognition_images
from ..portable_primary import ALIAS_ADAPTER, restore_native_bundle
from ..runtime import file_record


class HistoricalEvaluationResetAnalysisTest(unittest.TestCase):
    def test_actual_preserve_results_are_readable_but_cannot_admit_a_new_execution(self):
        package = Path(os.environ['TIMELEARNER_HISTORICAL_RESET_PACKAGE'])
        metadata = locate(package/'bundle.json');bundle = load(metadata)
        reference = load(package/'primary.tar.xz.archive.json');archive = resolve(reference)
        self.assertEqual(bundle['archive_sha256'],
            '67499f58763f2d0188c4d09d4258a63802a84989ca68eee79ed5ba852c0c5b2d')
        self.assertEqual(len(bundle['members']), 3078)
        before = file_record(archive);rows = []
        with tempfile.TemporaryDirectory(prefix='historical-reset-reader-',dir=os.environ['TMPDIR']) as temporary:
            local = Path(temporary)/'package';local.mkdir()
            (local/'bundle.json').write_bytes(metadata.read_bytes())
            (local/'primary.tar.xz.archive.json').write_text(json.dumps(reference),encoding='utf-8')
            restored = Path(temporary)/'restored'
            recovery = restore_native_bundle(local/'bundle.json',restored,compatibility=ALIAS_ADAPTER)
            self.assertEqual(recovery['archive_members_verified'],3078)
            self.assertFalse(recovery['source_archive_modified'])
            for name in ('continuous','long-continuous'):
                run = restored/'study24'/name;manifest = run/'run-manifest.json'
                recorded = file_record(manifest)
                job = load(run/'input/job.json')
                self.assertEqual(job['coverage_policy'],'per_trial_windows')
                self.assertTrue(all(t['reset_policy']=='preserve_neuron_dynamics' for t in job['trials']))
                with self.assertRaisesRegex(EvidenceError,'pipeline_reset_policy_not_yet_verified'):
                    audit_run_manifest(manifest)
                audit = audit_run_manifest(manifest,historical_analysis='evaluation-v1-native-reset-policy')
                self.assertTrue(audit['run_evidence_consistent'])
                self.assertFalse(audit['new_execution_permitted'])
                self.assertFalse(audit['continuous_production_runner_verified'])
                self.assertFalse(audit['native_execution_verified'])
                self.assertEqual(audit['historical_analysis_adapter'],'evaluation-v1-native-reset-policy')
                metrics = load(manifest)['analysis']['metrics']
                self.assertEqual(tuple(metrics['pooled_counts'][k] for k in ('TP','FP','FN','TN')),(1,1,0,6))
                source = _load_source_case('diagnostic-evaluate',run/load(manifest)['source_package_path'])
                with self.assertRaisesRegex(EvidenceError,'pipeline_reset_policy_not_yet_verified'):
                    validate_job('diagnostic-evaluate',job,source)
                changed = {**job,'trials':[dict(t) for t in job['trials']]}
                changed['trials'][-1]['reset_policy']='unknown_reset_policy';changed.pop('sha256')
                changed['sha256']=canonical_model_sha256(changed)
                with self.assertRaisesRegex(EvidenceError,'unsupported_pipeline_historical_reset_scope'):
                    _validate_job('diagnostic-evaluate',changed,source,historical_evaluation_reset=True)
                # Exercise the exact metadata transition using this real old
                # analysis and its validated image definitions. No expensive
                # native source audit is bypassed by the positive check above.
                previous = load(manifest)['analysis'];current = deepcopy(previous)
                definitions = source[0]['neuron']['class_definitions']
                for proof in (current['source_diagnostic_audit'],current['metrics']['source_diagnostic_audit']):
                    leaf = proof['source_audit'] if job['schema_version']==2 else proof
                    self.assertEqual(leaf['auditor_version'],2)
                    leaf['auditor_version']=3
                    leaf['storage_images']=audit_recognition_images(definitions,definitions)
                self.assertEqual(_historical_reset_analysis(previous,current,'diagnostic-evaluate',job),previous)
                for mutation in ('count','bool_count','auditor','source','unknown','image_scope','image_field'):
                    saved,measured=deepcopy(previous),deepcopy(current)
                    if mutation in ('count','bool_count'):
                        saved['metrics']['pooled_counts']['TP']=2 if mutation=='count' else True
                    else:
                        proof=saved['source_diagnostic_audit']
                        leaf=proof['source_audit'] if job['schema_version']==2 else proof
                        if mutation=='auditor':leaf['auditor_version']=99
                        elif mutation=='source':leaf['source_audit']['model_revision']='0'*64
                        elif mutation=='unknown':leaf['unknown_field']=None
                        else:
                            proof=measured['source_diagnostic_audit']
                            leaf=proof['source_audit'] if job['schema_version']==2 else proof
                            if mutation=='image_scope':leaf['storage_images']['xml_documents_byte_equal']=False
                            else:leaf['storage_images']['unknown_field']=None
                    with self.subTest(run=name,mutation=mutation),self.assertRaises(EvidenceError):
                        _historical_reset_analysis(saved,measured,'diagnostic-evaluate',job)
                self.assertEqual(file_record(manifest),recorded)
                rows.append(dict(name=name,audit=audit,counts=metrics['pooled_counts'],source_manifest=recorded,
                                 new_job_rejected=True,unknown_historical_reset_rejected=True,
                                 recognition_metadata_transition_negative_checks=7))
        self.assertEqual(file_record(archive),before)
        proof = dict(kind='timelearner_historical_evaluation_reset_readback',schema_version=1,
            archive_reference=reference,restoration=recovery,rows=rows,original_artifacts_changed=False,
            temporary_cache_removed=True,new_model_execution=False,scientific_verdict=None)
        (Path(os.environ['TMPDIR'])/'historical-evaluation-reset-reader-proof.json').write_text(
            json.dumps(proof,indent=2,allow_nan=False)+'\n',encoding='utf-8')
