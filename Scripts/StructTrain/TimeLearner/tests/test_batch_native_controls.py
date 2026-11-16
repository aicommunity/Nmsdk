"""Generate small real controls with an existing immutable production SDK."""
import os
from pathlib import Path
import shutil
import unittest
import xml.etree.ElementTree as ET

from ..contained_process import inspect
from ..contained_runner import execute
from ..native_calibration_worker import _write
from ..native_evidence import load
from ..resource_reservations import Reservations
from ..runtime import applied_loader_environment, file_record


NATIVE_CASES = ([f'NativeRecognitionOwner.{name}' for name in (
    'ClassicFreshDestination', 'BranchFreshDestination',
    'ClassicSpikingFreshDestination', 'BranchSpikingFreshDestination')] +
    [f'NativeThresholdCandidate.{topology}N{n}_{frequency}' for topology in ('Classic','Branch')
     for n in (0,1) for frequency in (2000,20000)] +
    [f'NativeCalibratedState.{topology}N1_2000' for topology in ('Classic','Branch')])


class BatchNativeControlsTest(unittest.TestCase):
    def test_fourteen_real_sdk_controls_and_two_retained_diagnostic_models(self):
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
        self.assertEqual(len(actual),14)
        self.assertFalse(list(xml.iter('failure'))+list(xml.iter('error'))+list(xml.iter('skipped')))
        cases = output/'cases';cases.mkdir();rows=[];records=[]
        def add(package, observations, diagnostic):
            folder=cases/f'case-{len(rows):03d}';folder.mkdir()
            names=[]
            for source in (package,*observations):
                self.assertTrue(source.is_file() and not source.is_symlink())
                target=folder/source.name;shutil.copyfile(source,target)
                source_record=file_record(source);target_record=file_record(target)
                self.assertEqual(source_record['sha256'],target_record['sha256'])
                records.append(dict(source=source_record,target=target.relative_to(cases).as_posix()))
                names.append(target.relative_to(cases).as_posix())
            rows.append(dict(package=names[0],observations=names[1:],diagnostic=diagnostic))
        for suffix, trial_suffix, expected in (
                ('_owner_recognition_state.json','_frozen_trial_',4),
                ('_recognition_candidate.json','_frozen_trial_',32),
                ('_calibrated_state.json','_calibrated_frozen_trial_',2)):
            packages=sorted(native.glob('*'+suffix));self.assertEqual(len(packages),expected)
            for p in packages:
                prefix=p.name.removesuffix(suffix)
                add(p,[p.with_name(prefix+trial_suffix+str(i)+'.json') for i in range(4)],False)
        diagnostics=Path(declaration['diagnostic_native'])
        packages=sorted(diagnostics.glob('*_diagnostic_threshold.json'));self.assertEqual(len(packages),2)
        for p in packages:
            prefix=p.name.removesuffix('_diagnostic_threshold.json')
            add(p,[p.with_name(prefix+f'_frozen_trial_{i}.json') for i in range(4)],True)
        self.assertEqual(len(rows),40)
        _write(cases/'cases.json',dict(kind='actual_native_batch_audit_cases',schema_version=1,
            native_sdk_cases=NATIVE_CASES,cases=rows,source_files=records,
            native_runtime=runtime['runtime_fingerprint'],new_scientific_training=False,
            scientific_verdict=None))
