"""Byte-level artifact transport; no fabricated neural result or model audit."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest


if os.environ.get('TIMELEARNER_JSON_TRANSPORT_SCRIPT'):
    _spec = importlib.util.spec_from_file_location('actual_json_transport', os.environ['TIMELEARNER_JSON_TRANSPORT_SCRIPT'])
    _module = importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_module)
    compact_json_transport = _module.compact_json_transport
else:
    from ..json_transport import compact_json_transport


class JsonTransportTest(unittest.TestCase):
    def compact(self, root, data, **options):
        source = root/'source.json';source.write_bytes(data)
        return compact_json_transport(source, root/'compact.json', expected_bytes=len(data),
                                      expected_sha256=hashlib.sha256(data).hexdigest(), **options)

    def test_strings_escapes_utf8_and_exact_number_tokens_across_chunks(self):
        data = (' { "xml": "a \\" b\\\\ c\\n d", "ru": "время потенциал", '
                '"values": [ -0.0, 1e+0003, 9007199254740993, 1.2345678901234567 ] } \r\n').encode()
        expected = (b'{"xml":"a \\" b\\\\ c\\n d","ru":'+
                    '"время потенциал"'.encode()+b',"values":[-0.0,1e+0003,9007199254740993,1.2345678901234567]}')
        for chunk in (1, 2, 3, 7, 1024):
            with self.subTest(chunk=chunk), tempfile.TemporaryDirectory() as directory:
                root = Path(directory);result = self.compact(root, data, chunk_bytes=chunk)
                self.assertEqual((root/'compact.json').read_bytes(), expected)
                self.assertEqual(json.loads(data), json.loads(expected))
                self.assertEqual((root/'source.json').read_bytes(), data)
                self.assertFalse(result['semantic_package_verified'])
                self.assertTrue(result['strict_package_readback_required'])

    def test_existing_destination_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);(root/'compact.json').write_bytes(b'unrelated bytes')
            with self.assertRaises(FileExistsError):self.compact(root, b'{"x":1}')
            self.assertEqual((root/'compact.json').read_bytes(), b'unrelated bytes')

    def test_wrong_source_digest_cannot_publish_transport(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);source = root/'source.json';source.write_bytes(b'{"x":1}')
            with self.assertRaisesRegex(ValueError, 'source_changed'):
                compact_json_transport(source, root/'compact.json', expected_bytes=7, expected_sha256='0'*64)
            self.assertFalse((root/'compact.json').exists())

    def test_output_limit_and_unterminated_string_cannot_publish(self):
        for data, options, reason in ((b'{"x":1234}',dict(maximum_output_bytes=3),'output_budget'),
                                      (b'{"x":"unfinished',{},'unterminated_string')):
            with self.subTest(reason=reason), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                with self.assertRaisesRegex(ValueError, reason):self.compact(root, data, **options)
                self.assertFalse((root/'compact.json').exists())


if __name__ == '__main__':
    unittest.main()
