"""Validate index generation against complete worker-rendered native reports."""
import os
from pathlib import Path
import unittest

from ..historical_report_index import index_bytes
from ..native_evidence import EvidenceError


class HistoricalReportIndex(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(os.environ["TL_HISTORICAL_REPORT_CACHE"]).resolve(strict=True)
        cls.cases = ["original-order-gap1.5", "original-order-gap3",
                     "rotated-order-gap1.5", "rotated-order-gap3"]

    def test_actual_all_pattern_index_has_complete_links_and_lazy_native_images(self):
        raw, bindings = index_bytes(self.root, self.cases)
        text = raw.decode("utf-8")
        self.assertEqual(len(bindings), 4)
        self.assertTrue(all(r["figures_verified"] == 32 for r in bindings))
        self.assertEqual(text.count("<details>"), 32)
        self.assertEqual(text.count('loading="lazy"'), 32)
        for case in self.cases:
            for sample in range(8):
                for mode in ("full", "response", "positive_full", "positive_response"):
                    self.assertIn(f'{case}/phasea-{sample}-{mode}.png', text)

    def test_duplicate_cases_cannot_inflate_report_coverage(self):
        with self.assertRaisesRegex(EvidenceError, "report_index_invalid_case_set"):
            index_bytes(self.root, [self.cases[0], self.cases[0]])

    def test_case_path_escape_is_rejected_before_reading_it(self):
        with self.assertRaisesRegex(EvidenceError, "report_index_unsafe_name"):
            index_bytes(self.root, ["../outside"])


if __name__ == "__main__":
    unittest.main()
