"""All calibrated cold8 trials and somas from the genuine Console pilot.

Reports remain diagnostic until visual inspection. Same-matrix N2 calibration
does not establish independent N4 classification. No missing-data skips.
"""
import os
from pathlib import Path

from ..native_evidence import load, require
from . import test_managed_native_pipeline_reports as shared


class RecoveryConsoleReportsTest(shared.ManagedNativePipelineReportsTest):
    case_names = ('Classic-window-N0', 'Branch-window-N0')
    expected_pairs = 12

    def report_bindings(self):
        controls = os.environ.get('TIMELEARNER_RECOVERY_CONSOLE_REPORT_CONTROLS')
        source = os.environ.get('TIMELEARNER_RECOVERY_CONSOLE_REPORT_SOURCE')
        require(controls is not None and source is not None,
                'cold8_report_actual_source_bindings_required')
        specification = load(Path(controls)/'declaration.json')
        require(type(specification) is dict and set(specification) == {'source', 'output'},
                'cold8_report_declaration_fields')
        require(Path(specification['source']).resolve(strict=True) == Path(source).resolve(strict=True),
                'cold8_report_source_binding_changed')
        return specification['source'], specification['output']

    def case_run(self, source, name):
        return source/'calibration'/name/'runs/fresh-frozen'
