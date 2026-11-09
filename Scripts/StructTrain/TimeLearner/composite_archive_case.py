"""Read an existing composite case and return compact independently audited DATA.

The three JSON documents and every referenced CSV are mandatory originals.
Embedded primary never substitutes for a missing/corrupt filesystem mirror.
"""
import hashlib
from pathlib import Path

from .composite_measurement_evidence import audit_composite_measurement_archive
from .composite_primary import filesystem_primary_resolver
from .native_evidence import EvidenceError, parse_json_bytes, require

INPUTS=('initial-configuration.json','runtime-plan.json','composite-measurements/index.json')


def _read_documents(directory):
    root=Path(directory)
    require(not root.is_symlink() and root.is_dir(),'composite_case_directory_required')
    root=root.resolve(strict=True);documents={};bindings={}
    for name in INPUTS:
        path=root/name
        require(all(not ancestor.is_symlink() for ancestor in (path,*path.parents) if ancestor.is_relative_to(root))
            and path.is_file(),'composite_case_original_document_required')
        raw=path.read_bytes();documents[name]=parse_json_bytes(raw)
        bindings[name]=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    return root,documents,bindings


def audit_composite_archive_case(directory):
    """Read-only shared schema dispatch; no native execution/certification claim."""
    try:
        root,documents,bindings=_read_documents(directory)
        index=documents[INPUTS[2]]
        result=audit_composite_measurement_archive(index,documents[INPUTS[0]],runtime_plan=documents[INPUTS[1]],
            external_resolver=filesystem_primary_resolver(root))
        groups=result['groups'];geometry={};selection={};statuses=[]
        for row,record in zip(groups,index['records']):
            key=row.get('geometry_validity') or 'not_recomputed';geometry[key]=geometry.get(key,0)+1
            key='not_recorded' if record['selection'] is None else record['selection']['status']
            selection[key]=selection.get(key,0)+1
            statuses.append(dict(group_id=record['group_id'],purpose=record['purpose'],group_state=record['group_state'],
                complete_group=record['complete_group'],consumed=record['consumed'],measurement_present=row['measured'],
                recorded_rejection_reason=record['rejection_reason'],recorded_selection=record['selection'],
                native_closure_recomputed=row['native_closure_recomputed'],geometry_recomputed=row['geometry_recomputed'],
                rejection_reason_recomputed=row['rejection_reason_recomputed']))
        measurements=[dict(group_id=record['group_id'],purpose=record['purpose'],input_index=record['logical_request']['input_index'],
            attempt_id=record['attempt_id'],consumed=record['consumed'],**record['measurement'])
            for record in index['records'] if record['measurement'] is not None]
        return dict(kind='timelearner_composite_archive_analysis',schema_version=1,
            archive_schema_version=index['schema_version'],input_documents=bindings,audit=result,
            coverage=dict(groups=len(groups),measured_groups=sum(row['measured'] for row in groups),
                consumed_groups=sum(row['consumed'] for row in groups),
                native_closure_recomputed_groups=sum(row['native_closure_recomputed'] for row in groups),
                partial_groups=sum(not record['complete_group'] for record in index['records']),
                geometry_validities=geometry,selection_statuses=selection),group_statuses=statuses,measurements=measurements,
            native_execution_verified=False,live_authority_restored=False,training_certificate_verified=False,scientific_verdict=None)
    except EvidenceError:raise
    except (OSError,KeyError,TypeError,ValueError,IndexError) as error:
        raise EvidenceError('missing_or_malformed_composite_case') from error
