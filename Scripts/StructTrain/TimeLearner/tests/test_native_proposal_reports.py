"""Production temporal checks for actual two-topology proposal controls."""
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from .test_live_pipeline_reports import LivePipelineReportsTest as _Base


class NativeProposalReportsTest(_Base):
    def source_run(self, name):
        return self.source/name

    @classmethod
    def setUpClass(cls):
        if not all(os.environ.get(k) for k in ("TIMELEARNER_NATIVE_PROPOSAL_CORPUS",
                                               "TIMELEARNER_NATIVE_PROPOSAL_REPORTS")):
            raise unittest.SkipTest("requires actual proposal primary data and reports")
        cls.source = Path(os.environ["TIMELEARNER_NATIVE_PROPOSAL_CORPUS"])
        cls.reports = Path(os.environ["TIMELEARNER_NATIVE_PROPOSAL_REPORTS"])
        index = load(cls.source/"index.json")
        if index["kind"] not in ("native_n0_proposal_controls", "native_n1_proposal_controls"):
            raise RuntimeError("unknown proposal control corpus")
        cls.rows = [dict(r, operation="train") for r in index["records"]]
        if len(cls.rows) != 2 or len({r["name"] for r in cls.rows}) != 2:
            raise RuntimeError("incomplete proposal control corpus")


del _Base
