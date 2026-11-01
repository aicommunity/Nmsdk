"""Apply the production temporal report checks to the dimension corpus."""
import os
import unittest
from pathlib import Path

from ..native_evidence import load
from .test_live_pipeline_reports import LivePipelineReportsTest as _Base


class NativeDimensionReportsTest(_Base):
    @classmethod
    def setUpClass(cls):
        if not all(os.environ.get(k) for k in ("TIMELEARNER_NATIVE_DIMENSION_CORPUS",
                                               "TIMELEARNER_NATIVE_DIMENSION_REPORTS")):
            raise unittest.SkipTest("requires actual dimension primary data and reports")
        cls.source = Path(os.environ["TIMELEARNER_NATIVE_DIMENSION_CORPUS"])
        cls.reports = Path(os.environ["TIMELEARNER_NATIVE_DIMENSION_REPORTS"])
        index = load(cls.source/"index.json")
        cls.rows = [dict(r, operation="train") for r in index["records"]]
        expected = {(n, top, norm) for n in index["dimensions"]
                    for top in ("Classic", "Branch") for norm in ("N0", "N1")}
        if len(cls.rows) != len(expected) or {(r["inputs"], r["topology"], r["normalization"])
                                             for r in cls.rows} != expected:
            raise RuntimeError("incomplete dimension report corpus")


del _Base
