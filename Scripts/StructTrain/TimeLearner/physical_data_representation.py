"""Declared identity of DATA3 encodings from the same retained DATA1 source.

Native XML and its digest remain primary evidence. XML bytes can differ between
platforms while the native-imported graph and canonical class images agree.
This description audits every document first, but does not prove that XML was
actually imported: callers retain the independent native roundtrip evidence.
"""
import argparse
import copy
import json
from pathlib import Path

from Scripts.StructTrain.TimeLearner.capacitance_evidence import _images
from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256 as sha
from Scripts.StructTrain.TimeLearner.native_evidence import require
from Scripts.StructTrain.TimeLearner.physical_model_data_evidence import audit_physical_model_data


def _archive_identity(archive, *, candidate_record=None):
    result = copy.deepcopy({k:v for k,v in archive.items()
                            if k not in ('sha256', 'graph', 'class_definitions')})
    # audit_physical_model_data has checked the retained native XML digest.
    # Its relation to the declared graph is checked by the native importer,
    # never inferred here from a hash or a successful portable JSON audit.
    result['graph'] = {k:v for k,v in archive['graph'].items()
                       if k not in ('native_xml', 'native_xml_sha256')}
    result['class_definitions'] = _images(archive['class_definitions'])
    if candidate_record is not None:
        result['metadata']['calibration']['candidate_record'] = candidate_record
    return result


def describe_candidate_representation(package):
    """Describe DATA3->DATA2->original DATA1, without changing any input.

    This deliberately retains the complete original DATA1 and all non-encoding
    metadata. Different histories, targets, physics or conversion specifications
    cannot silently become the same source. Only derived references to the
    re-encoded recognition archive are replaced by their declared identity.
    """
    audit = audit_physical_model_data(package, frozen=True)
    require(package['schema_version'] == 3 and
            package['source_recognition_data']['schema_version'] == 2,
            'representation_requires_DATA3_from_DATA2')
    recognition = package['source_recognition_data']
    original = recognition['source_model_data']
    recognition_identity = {k:v for k,v in recognition.items() if k not in ('sha256', 'neuron')}
    recognition_identity['neuron'] = _archive_identity(recognition['neuron'])
    record = dict(package['candidate_record'])
    record['source_recognition_sha256'] = sha(recognition_identity)
    identity = {k:v for k,v in package.items()
                if k not in ('sha256', 'neuron', 'source_recognition_data', 'candidate_record')}
    identity.update(source_recognition_data=recognition_identity, candidate_record=record,
                    neuron=_archive_identity(package['neuron'], candidate_record=record))
    return dict(kind='timelearner_DATA3_declared_representation_identity', schema_version=1,
        original_DATA1_sha256=original['sha256'], document_sha256=package['sha256'],
        model_revision=audit['model_revision'], effective_threshold=audit['effective_threshold'],
        frequency_hz=audit['frequency_hz'], declared_identity_sha256=sha(identity),
        native_xml_digests=dict(candidate=package['neuron']['graph']['native_xml_sha256'],
                               recognition=recognition['neuron']['graph']['native_xml_sha256']),
        canonical_class_images_sha256=sha(_images(package['neuron']['class_definitions'])),
        native_import_verified=False, native_execution_verified=False,
        training_certificate_transferred=False, calibration_confirmed=False,
        scientific_verdict=None)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', required=True, type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(describe_candidate_representation(json.loads(args.model.read_bytes())),
                     sort_keys=True, allow_nan=False))


if __name__ == '__main__':
    main()
