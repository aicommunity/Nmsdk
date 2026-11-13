"""Lossless storage of a job around an already retained source document.

Only byte-exact known producer encodings are factored. Unsupported inputs stay
literal. This codec proves neither JSON validity nor model/native execution.
"""
import base64
import binascii
import hashlib
import json
import re

from .native_evidence import parse_json_bytes, require

MAX_DOCUMENT_BYTES = 512*1024**2
MAX_ENVELOPE_BYTES = 16*1024**2
_FIELD = re.compile(rb'(?m)^( {2}| {4})"source_stopped": ')


def record(raw):
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def _raw(raw):
    require(type(raw) is bytes and 0 < len(raw) <= MAX_DOCUMENT_BYTES,
            'source_envelope_document_budget')


def _record(value):
    require(type(value) is dict and set(value) == {'bytes', 'sha256'} and
        type(value['bytes']) is int and 0 < value['bytes'] <= MAX_DOCUMENT_BYTES and
        type(value['sha256']) is str and re.fullmatch('[0-9a-f]{64}', value['sha256']),
        'source_envelope_record')


def _indent(raw, spaces):
    require(raw.startswith(b'{\n') and raw.endswith(b'}\n'), 'source_envelope_object_layout')
    return raw[:-1].replace(b'\n', b'\n'+b' '*spaces)


def reference_encodings(reference):
    """Reusable for many envelopes referring to the same immutable bytes."""
    _raw(reference)
    source = parse_json_bytes(reference)
    require(type(source) is dict, 'source_envelope_object_reference_required')
    python = (json.dumps(source, ensure_ascii=False, indent=2, allow_nan=False)+'\n').encode('utf-8')
    encodings = {'python-indent2': _indent(python, 2)}
    if reference.startswith(b'{\n') and reference.endswith(b'}\n'):
        encodings['qt-indent4'] = _indent(reference, 4)
    return dict(source=record(reference), payloads=encodings)


def factor(original, reference, *, prepared_reference=None):
    """Return a verified recipe or None, requiring the original to stay literal."""
    _raw(original);_raw(reference)
    if not original.startswith(b'{\n') or not original.endswith(b'}\n'):
        return None
    matches = list(_FIELD.finditer(original))
    if len(matches) != 1:
        return None
    match = matches[0]
    codec = 'python-indent2' if len(match[1]) == 2 else 'qt-indent4'
    prepared = prepared_reference if prepared_reference is not None else reference_encodings(reference)
    require(prepared['source'] == record(reference), 'source_envelope_prepared_reference_changed')
    payload = prepared['payloads'].get(codec)
    if payload is None or not original.startswith(payload, match.end()):
        return None
    prefix, suffix = original[:match.end()], original[match.end()+len(payload):]
    if len(prefix)+len(suffix) > MAX_ENVELOPE_BYTES or suffix[:1] not in (b',', b'\n'):
        return None
    result = dict(kind='timelearner_source_job_envelope', schema_version=1, codec=codec,
        source=record(reference), original=record(original),
        prefix_base64=base64.b64encode(prefix).decode('ascii'),
        suffix_base64=base64.b64encode(suffix).decode('ascii'))
    require(restore(result, reference, prepared_reference=prepared) == original,
            'source_envelope_factor_roundtrip_failed')
    return result


def restore(recipe, reference, *, prepared_reference=None):
    """Return exact original bytes; callers write a new file only on success."""
    _raw(reference)
    require(type(recipe) is dict and set(recipe) == {'kind', 'schema_version', 'codec',
        'source', 'original', 'prefix_base64', 'suffix_base64'} and
        recipe['kind'] == 'timelearner_source_job_envelope' and
        type(recipe['schema_version']) is int and recipe['schema_version'] == 1 and
        recipe['codec'] in ('python-indent2', 'qt-indent4'), 'source_envelope_schema')
    _record(recipe['source']);_record(recipe['original'])
    require(record(reference) == recipe['source'], 'source_envelope_reference_changed')
    decoded=[]
    for key in ('prefix_base64', 'suffix_base64'):
        value=recipe[key]
        require(type(value) is str and len(value) <= 2*MAX_ENVELOPE_BYTES,
                'source_envelope_literal_budget')
        try:raw=base64.b64decode(value, validate=True)
        except (ValueError, binascii.Error) as error:
            raise ValueError('source_envelope_invalid_base64') from error
        require(base64.b64encode(raw).decode('ascii') == value, 'source_envelope_noncanonical_base64')
        decoded.append(raw)
    require(sum(len(v) for v in decoded) <= MAX_ENVELOPE_BYTES, 'source_envelope_literal_budget')
    prepared=prepared_reference if prepared_reference is not None else reference_encodings(reference)
    require(prepared['source'] == recipe['source'], 'source_envelope_prepared_reference_changed')
    require(recipe['codec'] in prepared['payloads'], 'source_envelope_encoding_unavailable')
    original=decoded[0]+prepared['payloads'][recipe['codec']]+decoded[1]
    require(record(original) == recipe['original'], 'source_envelope_restored_bytes_changed')
    return original
