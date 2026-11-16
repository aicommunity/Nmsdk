"""Replay a declared real threshold experiment away from its original worker."""
import os
from pathlib import Path, PurePosixPath
import unittest

from ..native_evidence import load
from ..native_pipeline_worker import audit_run_manifest
from ..recognition_metrics import load_diagnostic_evaluation
from ..runtime import file_record
from ..portable_primary import ALIAS_ADAPTER, restore_native_bundle


class RestoredThresholdPrimaryTest(unittest.TestCase):
    def test_both_actual_series_keep_complete_metrics_after_independent_restore(self):
        controls = Path(os.environ["TIMELEARNER_RESTORED_THRESHOLD_CONTROLS"])
        expected = load(controls/"expected.json")
        for path in expected["original_worker_directories"]:
            self.assertFalse(Path(path).exists(), path)
        output = Path(os.environ["TMPDIR"])/"restored-threshold-primary"
        restored = restore_native_bundle(controls/"bundle.json", output,
                                         compatibility=ALIAS_ADAPTER)
        self.assertEqual(restored["archive_members_verified"], expected["members"])
        self.assertEqual(restored["retained_regular_files"], expected["retained_files"])
        self.assertEqual(len(restored["omitted_redundant_aliases"]), expected["aliases"])
        self.assertFalse(restored["native_execution_attested"])
        study = output/"threshold/worker/tmp/threshold-study"
        original = load(study/"result.json")
        self.assertTrue(original["baseline_waveforms_equal"])
        self.assertFalse(original["training_completed"])
        self.assertFalse(original["independent_evaluation"])
        rows = []
        for actual in original["actual_results"]:
            name = actual["name"]
            manifest_path = study/"runs"/name/"run-manifest.json"
            audit = audit_run_manifest(manifest_path)
            self.assertTrue(audit["run_evidence_consistent"])
            metrics = load(manifest_path)["analysis"]["metrics"]
            self.assertEqual(metrics, actual["metrics"])
            self.assertEqual(metrics["validity"], "valid")
            self.assertEqual(len(metrics["trials"]), 8)
            self.assertEqual(metrics["pooled_counts"], expected["counts"][name])
            self.assertTrue(metrics["diagnostic_only"])
            self.assertFalse(metrics["training_completed"])
            self.assertIsNone(metrics["evaluation_verdict"])
            rows.append(dict(name=name, model_revision=metrics["model_revision"],
                             threshold=metrics["effective_threshold"],
                             counts=metrics["pooled_counts"]))
        self.assertEqual([r["name"] for r in rows], ["baseline100", "candidate"])
        self.assertEqual(rows[0]["threshold"], 100.)
        self.assertEqual(rows[1]["threshold"], expected["threshold"])
        original_baseline_checked = False
        if expected.get('original_baseline_prefix') is not None:
            relative = PurePosixPath(expected['original_baseline_prefix'])
            self.assertFalse(relative.is_absolute())
            self.assertNotIn('..', relative.parts)
            original_run = output.joinpath(*relative.parts)
            source_manifest = file_record(original_run/'run-manifest.json')
            for field in ('size', 'sha256'):
                self.assertEqual(source_manifest[field], original['proposal']['source_manifest'][field])
            self.assertTrue(audit_run_manifest(original_run/'run-manifest.json')['run_evidence_consistent'])
            _, old = load_diagnostic_evaluation(original_run/'native/evaluation.json')
            _, replay = load_diagnostic_evaluation(study/'runs/baseline100/native/evaluation.json')
            by_id = {o['trial_id']: o for o in old}
            self.assertEqual(len(old), len(by_id))
            self.assertEqual(len(replay), len(by_id))
            self.assertEqual({o['trial_id'] for o in replay}, set(by_id))
            for observation in replay:
                previous = by_id[observation['trial_id']]
                for field in ('samples', 'model_before', 'model_after', 'pattern_hash', 'label',
                              'reset_policy', 'stimulus_times', 'relative_stimulus_times',
                              'frequency_hz', 'complete', 'valid', 'censored'):
                    self.assertEqual(observation[field], previous[field],
                                     (observation['trial_id'], field))
            original_baseline_checked = True
        from ..native_calibration_worker import _write
        _write(Path(os.environ["TMPDIR"])/"restored-threshold-readback.json",
               dict(restoration=restored, actual_series=rows,
                    independent_data_restore=True, new_native_execution=False,
                    original_baseline_waveforms_checked=original_baseline_checked,
                    training_completed=False, scientific_verdict=None))
