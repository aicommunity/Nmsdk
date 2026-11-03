"""Real N1 protocol matrices, native sample binding and readable all-trial plots."""
from copy import deepcopy
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..n1_protocol_reports import render_study
from ..n1_protocol_robustness import _signed, _write
from ..native_evidence import EvidenceError, load
from ..recognition_metrics import load_evaluation, score_threshold_candidate
from .test_native_calibration_worker_reports import NativeCalibrationWorkerReportTest as _Shared


class N1ProtocolReportsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        paths = [os.environ.get(k) for k in ('TIMELEARNER_N1_PROTOCOL_STUDY_DIR', 'TIMELEARNER_N1_PROTOCOL_REPORTS_DIR')]
        if not all(paths):
            raise unittest.SkipTest('requires actual fixed N1 study and all temporal reports')
        cls.source, cls.root = map(Path, paths)
        cls.rows = load(cls.source/'design.json')['rows']
        cls.paths = [cls.root/r['name'] for r in cls.rows]

    test_all_native_input_overlays_are_readable_and_every_file_hash_matches = (
        _Shared.test_all_native_input_overlays_are_readable_and_every_file_hash_matches)

    def test_all_conditions_and_original_samples_are_bound_to_the_report(self):
        combined = load(self.root/'manifest.json')
        self.assertEqual(combined['operations'], 10)
        self.assertEqual(combined['analysis']['search_trials'], 528)
        self.assertEqual({r['name'] for r in combined['rows']}, {r['name'] for r in self.rows})
        self.assertFalse(combined['threshold_retuning'])
        self.assertFalse(combined['independent_patterns'])
        self.assertFalse(combined['visual_acceptance_complete'])
        pairs = 0
        for row in self.rows:
            original = load(self.source/'runs'/row['name']/'native/transaction.json')
            root = self.root/row['name']
            self.assertEqual(load(root/'primary/transaction.json.gz'), original)
            matrices = [('candidate-0000', original['candidates'][0]['matrix'])]
            if original['status'] in {'calibrated', 'confirmation_failed'}:
                matrices.append(('fresh-confirmation', original['confirmation']))
            self.assertEqual([r['name'] for r in load(root/'manifest.json')['matrices']], [n for n, _ in matrices])
            for name, matrix in matrices:
                spec, observations = load_evaluation(root/name/'primary/evaluation.json')
                candidate = load(root/name/'primary/model.json')
                self.assertEqual({o['trial_id']: o for o in observations},
                                 {o['trial_id']: o for o in matrix['observations']})
                self.assertEqual(load(root/name/'analysis.json'), score_threshold_candidate(spec, observations, candidate))
                figures = load(root/name/'manifest.json')['figures']
                channels = 1 if row['topology'] == 'Branch' else 2
                self.assertEqual({(f['presentation_index'], f['descriptor']['index']) for f in figures},
                                 {(i, c) for i in range(len(observations)) for c in range(channels)})
                pairs += len(figures)
        self.assertEqual(combined['trial_soma_pairs'], pairs)

    def test_missing_condition_is_rejected_before_any_figure_output(self):
        with tempfile.TemporaryDirectory(dir=self.root.parent) as directory:
            root = Path(directory);source = root/'source';source.mkdir()
            design = deepcopy(load(self.source/'design.json'));design['rows'].pop()
            _write(source/'design.json', _signed(design))
            shutil.copyfile(self.source/'index.json', source/'index.json')
            with self.assertRaisesRegex(EvidenceError, 'n1_study_incomplete_conditions'):
                render_study(source, root/'report')
            self.assertFalse((root/'report').exists())


del _Shared
