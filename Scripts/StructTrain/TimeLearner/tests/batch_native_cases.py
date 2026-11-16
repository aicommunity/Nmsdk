"""Select real exports only from explicitly passed native fixture cases."""
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

from ..native_calibration_worker import _write
from ..native_evidence import load, require
from ..runtime import file_record

SELECTED_CASES = ([f'NativeRecognitionOwner.{name}' for name in (
    'ClassicFreshDestination', 'BranchFreshDestination',
    'ClassicSpikingFreshDestination', 'BranchSpikingFreshDestination')] +
    [f'NativeCalibratedState.{topology}N1_2000' for topology in ('Classic','Branch')])


def prepare(native, xml_path, diagnostics, output, *, excluded_tests=()):
    native, diagnostics, output = map(Path, (native, diagnostics, output))
    require(len(set(excluded_tests))==len(excluded_tests) and
            not set(excluded_tests)&set(SELECTED_CASES),'invalid_excluded_native_fixture_cases')
    xml = ET.parse(xml_path).getroot();results={}
    for c in xml.iter('testcase'):
        name=c.attrib['classname']+'.'+c.attrib['name']
        require(name not in results,'duplicate_native_fixture_case')
        results[name]=(c.attrib.get('status')=='run' and c.attrib.get('result')=='completed' and
                       not any(c.find(tag) is not None for tag in ('failure','error','skipped')))
    require(set(results)==set(SELECTED_CASES)|set(excluded_tests) and
            all(results.get(name) is True for name in SELECTED_CASES),
            'selected_native_fixture_case_missing_or_failed')
    output.mkdir(exist_ok=False);rows=[];records=[]
    def add(package, observations, diagnostic, embedded=None):
        folder=output/f'case-{len(rows):03d}';folder.mkdir();names=[]
        target=folder/package.name
        if embedded is None:
            require(package.is_file() and not package.is_symlink(),'native_fixture_source_not_regular')
            shutil.copyfile(package,target)
        else:
            # This is the exact candidate exported inside a native calibrated
            # model. No threshold/graph/field edit or re-signing is performed.
            _write(target,embedded)
        record=dict(source=file_record(package),target=target.relative_to(output).as_posix())
        if embedded is not None:
            record.update(json_pointer='/source_candidate',semantic_sha256=embedded['sha256'])
        else:require(file_record(target)['sha256']==record['source']['sha256'],'native_fixture_copy_changed')
        records.append(record);names.append(record['target'])
        for source in observations:
            require(source.is_file() and not source.is_symlink(),'native_fixture_source_not_regular')
            target=folder/source.name;shutil.copyfile(source,target)
            require(file_record(source)['sha256']==file_record(target)['sha256'],'native_fixture_copy_changed')
            records.append(dict(source=file_record(source),target=target.relative_to(output).as_posix()))
            names.append(target.relative_to(output).as_posix())
        rows.append(dict(package=names[0],observations=names[1:],diagnostic=diagnostic))
    owners=sorted(native.glob('*_owner_recognition_state.json'))
    calibrated=sorted(native.glob('*_calibrated_state.json'))
    require(len(owners)==4 and len(calibrated)==2,'native_fixture_export_family_incomplete')
    for p in owners:
        prefix=p.name.removesuffix('_owner_recognition_state.json')
        add(p,[p.with_name(prefix+f'_frozen_trial_{i}.json') for i in range(4)],False)
    for p in calibrated:
        prefix=p.name.removesuffix('_calibrated_state.json')
        observations=[p.with_name(prefix+f'_calibrated_frozen_trial_{i}.json') for i in range(4)]
        add(p,observations,False)
        package=load(p);add(p,observations,False,package['source_candidate'])
    packages=sorted(diagnostics.glob('*_diagnostic_threshold.json'))
    require(len(packages)==2,'native_fixture_diagnostic_pair_missing')
    for p in packages:
        prefix=p.name.removesuffix('_diagnostic_threshold.json')
        add(p,[p.with_name(prefix+f'_frozen_trial_{i}.json') for i in range(4)],True)
    require(len(rows)==10,'native_fixture_case_inventory_incomplete')
    declaration=dict(kind='actual_native_batch_audit_cases',schema_version=1,cases=rows,
        source_files=records,source_xml=file_record(xml_path),selected_cpp_cases=SELECTED_CASES,
        source_suite_passed=all(results.values()),excluded_cpp_results={n:results[n] for n in excluded_tests},
        selection_scope='ordinary4 calibrated2 native-embedded-threshold2 diagnostic2; 2000Hz',
        new_scientific_training=False,scientific_verdict=None)
    _write(output/'cases.json',declaration)
    return declaration
