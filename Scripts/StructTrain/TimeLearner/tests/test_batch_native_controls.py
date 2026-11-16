"""Generate small real controls with an existing immutable production SDK."""
import os
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from ..contained_process import inspect
from ..contained_runner import execute
from ..native_evidence import load
from ..resource_reservations import Reservations
from ..runtime import applied_loader_environment
from .batch_native_cases import SELECTED_CASES, prepare


NATIVE_CASES = SELECTED_CASES


class BatchNativeControlsTest(unittest.TestCase):
    def test_six_real_sdk_controls_and_two_retained_diagnostic_models(self):
        controls = Path(os.environ['TIMELEARNER_BATCH_GENERATOR_CONTROLS'])
        declaration = load(controls/'declaration.json')
        live = inspect(declaration['controller'])
        self.assertEqual(live['binding']['initial_main_pid'], os.getpid())
        self.assertFalse(live['all_processes_closed'])
        runtime = load(controls/'runtime.json')
        output = Path(os.environ['TMPDIR'])/'batch-native-controls';output.mkdir()
        native = output/'native';native.mkdir()
        memory = 4*1024**3;tasks = 64
        registry = Reservations(output/'leases.sqlite3', managed_units=True,
            capacity=dict(slots=1,memory_bytes=live['memory_max']+2*memory,
                          disk_bytes=4*1024**3,tasks=live['tasks_max']+2*tasks))
        lease = registry.reserve('batch-scoring-native-controls',
            [dict(path=str(output),access='write'),
             dict(path=str(Path(runtime['executable']['path']).parent),access='read')],ttl_seconds=3600,
            demands=dict(slots=1,memory_bytes=live['memory_max']+memory,
                         disk_bytes=2*1024**3,tasks=live['tasks_max']+tasks),
            controller_directory=declaration['controller'])
        previous = os.environ.get('TIMELEARNER_EXECUTION_OUTPUT')
        try:
            os.environ['TIMELEARNER_EXECUTION_OUTPUT'] = str(native)
            with applied_loader_environment(runtime):
                result = execute(runtime, ['--gtest_filter='+':'.join(NATIVE_CASES),
                    '--gtest_output=xml:'+str(output/'native.xml')],
                    Path(runtime['executable']['path']).parent, output/'process', 1800.,
                    memory_bytes=memory,tasks=tasks,cooperative_capture=False,
                    managed_reservation=(registry,lease['token']))
            self.assertEqual(result['execution'], 'completed')
            self.assertTrue(inspect(output/'process/contained')['all_processes_closed'])
        finally:
            if previous is None:os.environ.pop('TIMELEARNER_EXECUTION_OUTPUT',None)
            else:os.environ['TIMELEARNER_EXECUTION_OUTPUT'] = previous
            registry.release(lease['token'],note='Small native fixture generation closed; not a scientific classifier study.')
        xml = ET.parse(output/'native.xml').getroot()
        actual = [f"{c.attrib['classname']}.{c.attrib['name']}" for c in xml.iter('testcase')]
        self.assertEqual(sorted(actual), sorted(NATIVE_CASES))
        self.assertEqual(len(actual),6)
        self.assertFalse(list(xml.iter('failure'))+list(xml.iter('error'))+list(xml.iter('skipped')))
        diagnostics=Path(os.environ['TIMELEARNER_BATCH_DIAGNOSTIC_NATIVE'])
        self.assertEqual(str(diagnostics),declaration['diagnostic_native'])
        prepare(native,output/'native.xml',diagnostics,output/'cases')
