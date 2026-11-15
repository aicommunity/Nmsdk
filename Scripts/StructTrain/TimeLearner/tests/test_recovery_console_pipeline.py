"""Real cold8 Console lifecycle, with original source7 declarations only.

Neither saved learned parameters nor saved spike responses seed Train. The
source corpus supplies immutable storage images and configuration; each model
must finish a fresh public native Train before export/calibration/frozen Test.
Technical N2/N0/Sync0.2 fixtures do not establish stock N4 classification.
"""
from pathlib import Path
import tempfile
import unittest

from ..candidate_window_package_evidence import audit_candidate_window_recovery_package
from ..composite_primary import filesystem_primary_resolver
from ..native_evidence import load, require
from ..portable_primary import restore_native_bundle
from . import test_candidate_window_console_pipeline as shared


class RecoveryConsolePipelineTest(shared.CompositeConsolePipelineFixture, unittest.TestCase):
    fixture_environment = 'TIMELEARNER_RECOVERY_CONSOLE'
    corpus_environment = 'TIMELEARNER_RECOVERY_CONSOLE_PACKAGE7_BUNDLE'
    configuration_version = 8
    phase = 'cold8'

    @classmethod
    def prepare_corpus(cls, corpus):
        cls.corpus_scratch = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.corpus_scratch.cleanup)
        destination = Path(cls.corpus_scratch.name)/'actual-native-corpus'
        cls.restoration = restore_native_bundle(corpus/'bundle.json', destination)
        require(cls.restoration['source_archive_modified'] is False,
                'cold8_console_original_archive_changed')
        return destination/'case'

    @classmethod
    def read_template(cls, corpus, branch):
        name = ('Branch' if branch else 'Classic')+'CompletedN0FrozenTargetAndFoil'
        leaf = 'native-002' if branch else 'native-001'
        directory = corpus/leaf/'native-composite/package7/NativeRecoveryRecognition7'/name
        raw = (directory/'source-package.json').read_bytes()
        package = load(directory/'source-package.json')
        summary = load(directory/'source-summary.json')
        audit = audit_candidate_window_recovery_package(package, summary,
            external_resolver=filesystem_primary_resolver(directory))
        require(package['schema_version'] == 7 and summary['schema_version'] == 8,
                'cold8_console_original_version_tuple')
        return package, raw, audit

    def test_classic_cold8_public_preflight_train_export_measured_calibration_frozen_test(self):
        self.cold_pipeline_and_calibration('Classic-window-N0')

    def test_branch_cold8_public_preflight_train_export_measured_calibration_frozen_test(self):
        self.cold_pipeline_and_calibration('Branch-window-N0')
