"""Project complete physical DATA from retained source bytes.

This checks document/physics consistency, not the source's measurement history,
native execution, training certificate or calibration proof. Those remain in
the separately retained original package and primary audit. A subsequent native
DATA import must verify the actual graph before any scientific evaluation.
"""
from copy import deepcopy
import argparse
import json
import os
from pathlib import Path

from .model_identity import canonical_model_sha256 as sha
from .native_evidence import load, require
from .physical_model_data_evidence import SOLO, RECOGNITION, audit_physical_model_data
from .runtime import file_record


_PARENT = {
    'timelearner_recognition_state': 'source_solo',
    'timelearner_diagnostic_recognition_state': 'source_solo',
    'timelearner_recognition_threshold_candidate': 'source_recognition',
    'timelearner_diagnostic_threshold_candidate': 'source_recognition',
    'timelearner_calibrated_recognition_state': 'source_candidate',
}


def project_physical_model_data(source):
    """Preserve graph, images, target and input values; discard no source bytes.

    The output is a new DATA document, never a shortened/resigned learned state.
    Its source boundary names the unchanged original. Omitted history grants no
    authority; every physical field is still checked by the production auditor.
    """
    chain = []
    current = source
    for _ in range(4):
        require(type(current) is dict and current.get('kind') in SOLO | RECOGNITION,
                'physical_projection_source_kind')
        require(current.get('dynamic_checkpoint') is False and
                current.get('state_kind') == (SOLO | RECOGNITION)[current['kind']] and
                current.get('sha256') == sha({k:v for k,v in current.items() if k != 'sha256'}),
                'physical_projection_source_digest_or_role')
        require(type(current.get('implementation_id')) is str and
                current['implementation_id'] == source['implementation_id'],
                'physical_projection_implementation_changed')
        chain.append(current)
        if current['kind'] in SOLO:
            break
        current = current.get(_PARENT[current['kind']])
    else:
        require(False, 'physical_projection_source_nesting')
    solo = chain[-1]
    recognition = next((p for p in chain if p['kind'] in (
        'timelearner_recognition_state', 'timelearner_diagnostic_recognition_state')), None)
    require((recognition is None) == (source['kind'] in SOLO),
            'physical_projection_missing_recognition_boundary')
    require(all(k in solo for k in ('configuration','protocol','controller_version',
            'calculate_mode','structure_build_mode','trained_inputs','model_revision')) and
            all(k in source for k in ('dataset','neuron','model_revision','schema_version')) and
            type(solo['configuration']) is dict and type(solo['configuration'].get('model')) is dict and
            (recognition is None or all(k in recognition for k in ('recognition_inputs','conversion_record'))),
            'physical_projection_missing_physical_fields')
    configuration = deepcopy(solo['configuration'])
    # This text is a semantically equivalent declaration, not a native export
    # signature. Recognition's effective all-input policy is set separately,
    # exactly as PrepareRecognitionPackage does after importing the solo state.
    configuration_text = json.dumps(configuration, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':'), allow_nan=False)
    if recognition is not None:
        configuration['model']['allow_muted_input_baseline'] = False
    result = dict(kind='timelearner_physical_model_data', schema_version=1,
        data_only=True, dynamic_checkpoint=False, certificate=None,
        implementation_id=source['implementation_id'],
        source_boundary={k:source[k] for k in ('kind','schema_version','state_kind','sha256','model_revision')},
        configuration=configuration, configuration_text=configuration_text,
        protocol=deepcopy(solo['protocol']),
        controls={k:solo[k] for k in ('controller_version','calculate_mode','structure_build_mode')},
        parameters=deepcopy(solo['trained_inputs'] if recognition is None else recognition['recognition_inputs']),
        model_revision=source['model_revision'], source_solo_revision=solo['model_revision'],
        conversion_record=None if recognition is None else deepcopy(recognition['conversion_record']),
        dataset=deepcopy(source['dataset']), neuron=deepcopy(source['neuron']))
    result['sha256'] = sha(result)
    audit_physical_model_data(result, frozen=recognition is not None)
    return result


def project_file(source, destination, *, expected_bytes, expected_sha256,
                 maximum_source_bytes=1024**3, maximum_output_bytes=32*1024**2):
    """One explicitly bounded preparation; does not execute or import a model."""
    source, destination = Path(source).absolute(), Path(destination).absolute()
    require(type(expected_bytes) is int and type(maximum_source_bytes) is int and
            0 < expected_bytes <= maximum_source_bytes <= 4*1024**3 and
            type(maximum_output_bytes) is int and 0 < maximum_output_bytes <= 128*1024**2,
            'physical_projection_byte_limits')
    require(not source.is_symlink() and not getattr(source, 'is_junction', lambda:False)() and
            source.is_file() and source != destination and not destination.exists() and
            not destination.is_symlink() and destination.parent.is_dir() and
            not destination.parent.is_symlink(), 'physical_projection_paths')
    before = file_record(source)
    require(before['size'] == expected_bytes and before['sha256'] == expected_sha256,
            'physical_projection_source_bytes_changed')
    package = load(source)
    projected = project_physical_model_data(package)
    encoded = (json.dumps(projected, ensure_ascii=False, indent=2, allow_nan=False)+'\n').encode('utf-8')
    require(len(encoded) <= maximum_output_bytes, 'physical_projection_output_budget')
    require(file_record(source) == before, 'physical_projection_source_changed_during_read')
    pending = destination.with_name(destination.name+'.pending')
    with pending.open('xb') as stream:
        stream.write(encoded);stream.flush();os.fsync(stream.fileno())
    # New-only publication on both workers; an existing result is never replaced.
    audit_physical_model_data(load(pending), frozen=package['kind'] not in SOLO)
    os.link(pending, destination);pending.unlink()
    return dict(kind='timelearner_physical_DATA_projection', schema_version=1,
        source=before, output=file_record(destination), source_boundary=projected['source_boundary'],
        model_revision=projected['model_revision'], physical_model_data_sha256=projected['sha256'],
        source_unchanged=True, source_history_retained_separately=True,
        source_training_evidence_checked=False, native_import_verified=False,
        training_certificate_transferred=False, calibration_confirmed=False,
        scientific_verdict=None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path);parser.add_argument('destination', type=Path)
    parser.add_argument('--expected-bytes', type=int, required=True)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--maximum-source-bytes', type=int, default=1024**3)
    parser.add_argument('--maximum-output-bytes', type=int, default=32*1024**2)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    require(not args.receipt.exists(), 'physical_projection_receipt_exists')
    result = project_file(args.source, args.destination, expected_bytes=args.expected_bytes,
                          expected_sha256=args.expected_sha256,
                          maximum_source_bytes=args.maximum_source_bytes,
                          maximum_output_bytes=args.maximum_output_bytes)
    with args.receipt.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(result, stream, indent=2, allow_nan=False);stream.write('\n')


if __name__ == '__main__':
    main()
