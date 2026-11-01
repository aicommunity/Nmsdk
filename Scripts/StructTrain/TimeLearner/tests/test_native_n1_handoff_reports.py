"""Shared production report checks for actual positive N1 frozen evaluations."""
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from .test_live_pipeline_reports import LivePipelineReportsTest as _Base


class NativeN1HandoffReportsTest(_Base):
    @classmethod
    def setUpClass(cls):
        if not all(os.environ.get(k) for k in ("TIMELEARNER_NATIVE_N1_HANDOFF_CORPUS",
                                               "TIMELEARNER_NATIVE_N1_HANDOFF_REPORTS")):
            raise unittest.SkipTest("requires actual positive N1 frozen primary data and reports")
        cls.source = Path(os.environ["TIMELEARNER_NATIVE_N1_HANDOFF_CORPUS"])
        cls.reports = Path(os.environ["TIMELEARNER_NATIVE_N1_HANDOFF_REPORTS"])
        index = load(cls.source/"index.json")
        if index["kind"] != "native_n1_exact_handoff_controls":
            raise RuntimeError("unknown N1 handoff corpus")
        cls.rows = index["records"]
        if len(cls.rows) != 2 or any(r["operation"] != "evaluate" for r in cls.rows):
            raise RuntimeError("incomplete N1 frozen evaluation corpus")


del _Base
