import copy
import os
from pathlib import Path
import tempfile
import unittest

from ..length_proposal_experiment import make_job, _progress
from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import validate_job
from ..native_calibration_worker import _digest


class LengthProposalExperiment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Acceptance must provide the actual published production templates.
        # Absence is a failure instead of a green skipped data dependency.
        cls.templates = Path(os.environ["TIMELEARNER_LENGTH_TEMPLATES"])

    def templates_and_jobs(self):
        for topology in ("Classic", "Branch"):
            for normalization in ("N0", "N1"):
                template = load(self.templates/(topology+"-"+normalization+"-inputs2-f2000.json"))
                yield template, make_job(template, topology, normalization)

    def test_actual_profiles_targets_tolerances_and_initial_parameters_survive(self):
        for template, job in self.templates_and_jobs():
            _digest(template)
            self.assertEqual(job["profile_archives"], template["profile_archives"])
            self.assertEqual(job["optional_modes"], template["optional_modes"])
            self.assertEqual(job["configuration"]["model"]["inputs"], template["configuration"]["model"]["inputs"])
            self.assertEqual(job["configuration"]["search"]["tolerances"], template["configuration"]["search"]["tolerances"])
            self.assertEqual(job["configuration"]["minimum_amplitude"], template["configuration"]["minimum_amplitude"])

    def test_production_job_validator_accepts_all_four_declared_controls(self):
        for template, job in self.templates_and_jobs():
            validate_job("train", job)
            _digest(job)
            self.assertEqual(job["configuration"]["model"]["initial_isi"], [.01, .08])
            self.assertEqual(job["configuration"]["duration"], .5)

    def test_inhibition_frequency_and_mismatched_initial_graph_are_rejected(self):
        original = load(self.templates/"Classic-N0-inputs2-f2000.json")
        for edit in (lambda m: m.update(frequency_hz=20000),
                     lambda m: m.update(inhibition=[{}]),
                     lambda m: m["inputs"][0].update(attachment=3)):
            template = copy.deepcopy(original)
            edit(template["configuration"]["model"])
            with self.assertRaises(EvidenceError):
                make_job(template, "Classic", "N0")
        _digest(original)

    def test_progress_updates_preserve_latest_record_without_exclusive_write_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            _progress(output, [{"execution": "completed", "measured": None}])
            _progress(output, [{"execution": "completed", "measured": [2, 3, 4, 9]}])
            self.assertEqual(load(output/"progress.json")[0]["measured"], [2, 3, 4, 9])
            self.assertFalse((output/"progress.pending.json").exists())


if __name__ == "__main__":
    unittest.main()
