"""Join retained native DATA to its own controller, never a neighbouring job."""
from pathlib import Path

from .native_evidence import load, load_json, require
from .native_gate import audit_junit


def audit_roundtrip_controller(native, controller, *, original_job_path):
    native, controller = Path(native), Path(controller)
    original = Path(original_job_path)
    request = load(controller/'request.json')
    require(request.get('kind') == 'timelearner_native_data_checks' and
            request.get('schema_version') == 1 and request.get('job_id') == original.name,
            'roundtrip_foreign_controller_request')
    require(request['cases'] == [
        {'name': 'classic', 'test_id': 'NativeRecordedRecoveryArchive/ClassicFullDomainN4Roundtrip'},
        {'name': 'branch', 'test_id': 'NativeRecordedRecoveryArchive/BranchFullDomainN4Roundtrip'}],
        'roundtrip_controller_cases')
    result = load(controller/'supervisor-result.json')
    require(result['outer_closed'] and result['reason'] is None and result['record_errors'] == [] and
            len(result['children_closed']) == 2, 'roundtrip_controller_closure')
    outer = load(controller/'outer-closure.json')
    require(outer['all_processes_closed'] and outer['binding'] == result['outer_binding'],
            'roundtrip_outer_binding')
    children = {row['directory']: row for row in result['children_closed']}
    require(set(children) == {str(original/role/'process/contained') for role in ('classic', 'branch')},
            'roundtrip_foreign_child_directory')
    for case in request['cases']:
        role = case['name'];directory = native/role
        child = children[str(original/role/'process/contained')]
        binding = load(directory/'process/contained/owned-unit.json')
        require(child['binding'] == binding and child['closure']['binding'] == binding and
                child['closure']['all_processes_closed'], 'roundtrip_foreign_child_binding')
        specification = load(directory/'specification.json')
        require(specification['expected_test_ids'] == [case['test_id']], 'roundtrip_junit_case_binding')
        require(audit_junit(directory/'native.xml', [case['test_id']])['assertion_status'] == 'passed',
                'roundtrip_original_junit_failed')
        require((directory/'data-inputs-before.json').read_bytes() ==
                (directory/'data-inputs-after.json').read_bytes(), 'roundtrip_data_input_changed')
    leases = load_json(controller/'reservation-final.json')
    require(isinstance(leases, list) and len(leases) == 1 and leases[0]['state'] == 'released',
            'roundtrip_controller_lease_not_released')
    require((native/'source-before.json').read_bytes() == (native/'source-after.json').read_bytes(),
            'roundtrip_source_changed')
    return dict(original_job_id=request['job_id'], original_cpp_cases=2, closed_groups=3,
                native_execution_attested=False, scientific_verdict=None)
