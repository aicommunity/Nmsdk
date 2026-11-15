"""Render every actual cold7 frozen/calibration pattern with native input.

Uses the maintained public report checks, including full-sample zooms, source
hashes and matrix completeness. This is not stock N4 scientific acceptance.
"""
import os
from pathlib import Path

from ..native_evidence import load, require
from . import test_managed_native_pipeline_reports as pipeline
from . import test_managed_native_calibration_reports as calibration


def report_bindings(name):
    root = os.environ.get('TIMELEARNER_COLD7_CONSOLE_REPORT_CONTROLS')
    require(root is not None, 'cold7_report_controls_required')
    value = load(Path(root)/(name+'.json'))
    require(type(value) is dict and set(value) == {'source', 'output'} and
            all(type(p) is str and Path(p).is_absolute() for p in value.values()),
            'cold7_report_bindings_invalid')
    require(Path(value['source']).resolve(strict=True) ==
            Path(os.environ['TIMELEARNER_COLD7_CONSOLE_PRIMARY']).resolve(strict=True)/
            ('calibration' if name == 'calibration' else ''), 'cold7_report_primary_changed')
    return value['source'], value['output']


class CandidateWindowPipelineReportsTest(pipeline.ManagedNativePipelineReportsTest):
    case_names = ('Classic-window-N0', 'Branch-window-N0')
    expected_pairs = 12

    def report_bindings(self):
        return report_bindings('pipeline')


class CandidateWindowCalibrationReportsTest(calibration.ManagedNativeCalibrationReportsTest):
    case_names = ('Classic-window-N0', 'Branch-window-N0')

    def report_bindings(self):
        return report_bindings('calibration')
