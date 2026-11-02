"""Full actual cold A/B traces, inputs, readable zooms and unchanged targets."""
import os
from pathlib import Path

from ..native_evidence import load
from .test_live_pipeline_reports import LivePipelineReportsTest as _Base


class LengthProposalReports(_Base):
    def source_run(self, name):
        return self.source/name

    @classmethod
    def setUpClass(cls):
        cls.source = Path(os.environ["TIMELEARNER_LENGTH_CORPUS"])
        cls.reports = Path(os.environ["TIMELEARNER_LENGTH_REPORTS"])
        index = load(cls.source/"index.json")
        if index["kind"] != "native_measured_length_ab" or len(index["records"]) != 8:
            raise RuntimeError("requires every declared cold length A/B run")
        cls.rows = [dict(r, name=r["version"]+"-"+r["name"], operation="train") for r in index["records"]]
        if len({r["name"] for r in cls.rows}) != 8:
            raise RuntimeError("duplicate cold length A/B condition")

    def test_baseline_current_have_identical_initial_physics_and_captured_targets(self):
        for topology in ("Classic", "Branch"):
            for normalization in ("N0", "N1"):
                folders = [self.source/(v+"-"+topology+"-"+normalization) for v in ("baseline", "current")]
                self.assertEqual(load(folders[0]/"input/job.json"), load(folders[1]/"input/job.json"))
                self.assertEqual(load(folders[0]/"native/initial-state.json"), load(folders[1]/"native/initial-state.json"))
                summaries = [load(f/"native/train_learned_summary.json") for f in folders]
                self.assertEqual(summaries[0]["references"], summaries[1]["references"])
                self.assertEqual(summaries[0]["tolerances"], summaries[1]["tolerances"])


del _Base
