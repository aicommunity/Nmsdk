"""Compile the production strict parser; this is not native model admission."""
import os
from pathlib import Path
import unittest

from ..controller_ab import run_controller_kernel
from ..native_evidence import load, require


class NativeJsonKernelTest(unittest.TestCase):
    def test_owned_bytes_framing_and_duplicate_keys_in_production_parser(self):
        controls = Path(os.environ['TIMELEARNER_NATIVE_JSON_CONTROLS']).resolve(strict=True)
        declaration = load(controls/'declaration.json')
        require(set(declaration) == {'root_repository', 'pulse_repository', 'compiler', 'gtest_source'},
                'native_json_kernel_controls_schema')
        specification = load(controls/'specification.json')
        self.assertEqual(specification['production_paths'], [
            'Core/TimeLearner/StrictNativeJson.cpp', 'Core/TimeLearner/StrictNativeJson.h'])
        self.assertEqual(specification['test_paths'], [
            'Tests/Integration/Libraries/Test_PulseLib_NativeJson.cpp'])
        self.assertEqual(specification['schema_version'], 2)
        self.assertIn(specification['qt_core_package'], ('Qt5Core', 'Qt6Core'))
        self.assertCountEqual(specification['expected_test_ids'], [
            'NativeJsonByteInput/OwnedResultAndStringCompatibility',
            'NativeJsonByteInput/DuplicateKeysRemainRejectedInNestedAndEscapedForms',
            'NativeJsonByteInput/Utf8BomDoesNotBypassDuplicateChecks',
            'NativeJsonByteInput/ByteLimitsAndInvalidFramingAreRejected'])
        output = Path(os.environ['TMPDIR']).resolve(strict=True)/'native-json-kernel'
        result = run_controller_kernel(controls/'specification.json',
            declaration['root_repository'], declaration['pulse_repository'],
            declaration['compiler'], declaration['gtest_source'],
            output)
        self.assertEqual(load(output/'toolchain.json')['qt_core']['package'],
                         specification['qt_core_package'])
        case = result['cases']['candidate']
        self.assertEqual(case['compile']['execution'], 'completed')
        self.assertEqual((case['execution'], case['validity'], case['assertion_status']),
                         ('completed', 'valid', 'passed'))
        self.assertEqual(case['inventory']['observed'], 4)
        self.assertEqual(case['inventory']['failed_test_ids'], [])
        self.assertFalse(result['native_rdk_integration_verified'])
        self.assertFalse(result['comparison_performed'])
        self.assertIsNone(result['scientific_verdict'])
