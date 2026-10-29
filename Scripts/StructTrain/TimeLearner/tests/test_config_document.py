import os
from pathlib import Path
import unittest

from Scripts.StructTrain.TimeLearner.config_document import ConfigDocument, ConfigDocumentError, TextEdit


class ConfigDocumentTest(unittest.TestCase):
    def setUp(self):
        self.raw = b'\xef\xbb\xbf<?xml version="1.0" encoding="UTF-8"?>\r\n<Project Version="2.1">\r\n<!-- <00>fake</00> -->\r\n<Channels><00><GlobalTimeStep>2000</GlobalTimeStep></00></Channels>\r\n<Note key="a&gt;b">old &amp; value</Note><Empty/>\r\n</Project>\r\n'
        self.path = ("Project", "Channels", "00", "GlobalTimeStep")

    def test_numeric_tags_roundtrip_exact_bytes(self):
        doc = ConfigDocument(self.raw)
        self.assertEqual(doc.edited([]), self.raw)
        self.assertEqual(doc.text(self.path), "2000")

    def test_only_selected_text_changes(self):
        result = ConfigDocument(self.raw).edited([TextEdit(self.path, "2000", "20000")])
        self.assertEqual(result, self.raw.replace(b'>2000<', b'>20000<'))
        self.assertTrue(result.startswith(b'\xef\xbb\xbf'))

    def test_multiple_changes_use_original_offsets_and_escape_once(self):
        doc = ConfigDocument(self.raw)
        result = doc.edited([TextEdit(self.path, "2000", "20"),
                             TextEdit(("Project", "Note"), "old & value", '<new> & "text"')])
        self.assertEqual(ConfigDocument(result).text(("Project", "Note")), '<new> & "text"')
        self.assertIn(b'&lt;new&gt; &amp; "text"', result)
        self.assertEqual(doc.raw, self.raw)

    def test_stale_missing_duplicate_and_nonleaf_fail(self):
        doc = ConfigDocument(self.raw)
        for edits in [[TextEdit(self.path, "wrong", "20")],
                      [TextEdit(("Project", "Missing"), "", "x")],
                      [TextEdit(self.path, "2000", "20")]*2,
                      [TextEdit(("Project", "Channels"), "", "x")],
                      [TextEdit(("Project", "Empty"), "", "x")]]:
            with self.subTest(edits=edits), self.assertRaises(ConfigDocumentError):
                doc.edited(edits)
        with self.assertRaises(ConfigDocumentError):
            ConfigDocument(b'<Root><A>1</A><A>2</A></Root>').text(("Root", "A"))

    def test_structure_and_external_declarations_fail_closed(self):
        for raw in [b'<A><B></A>', b'<A/>trailing', b'<A/><B/>', b'<!DOCTYPE A><A/>',
                    b'<A x="1" x="2"/>', b'<A x="unterminated/>', b'<A>\x00</A>',
                    b'<?xml version="1.0"?><?xml version="1.0"?><A/>',
                    b'<A>&unknown;</A>', b'<A>&amp</A>', b'<A>&#x+41;</A>',
                    b'<A>&#1_0;</A>', b'<A>&#0;</A>', b'<A>\xff</A>',
                    b'<?xml version="1.0" encoding="windows-1251"?><A/>']:
            with self.subTest(raw=raw), self.assertRaises(ConfigDocumentError):
                ConfigDocument(raw)

    def test_numeric_entities_and_preserved_unsupported_leaf_markup(self):
        doc = ConfigDocument(b'<Root><A>&#65;&#x42;</A><B><![CDATA[x<y]]></B></Root>')
        self.assertEqual(doc.text(("Root", "A")), "AB")
        self.assertEqual(doc.edited([]), doc.raw)
        with self.assertRaises(ConfigDocumentError):
            doc.edited([TextEdit(("Root", "B"), "x<y", "z")])

    def test_existing_project_corpus_roundtrips_without_edits(self):
        # Parsing real configuration bytes is required, not silently skipped.
        root = Path(os.environ.get("TIMELEARNER_CONFIG_CORPUS", Path(__file__).resolve().parents[4] / "Bin/Configs/SpikeSamples/StructTrain"))
        paths = sorted(root.rglob("Project.ini"))
        self.assertGreaterEqual(len(paths), 10)
        for path in paths:
            with self.subTest(path=str(path)):
                raw = path.read_bytes()
                self.assertEqual(ConfigDocument(raw).edited([]), raw)


if __name__ == "__main__":
    unittest.main()
