"""Lossless whitespace-only transport of an already validated JSON artifact.

This is not a JSON validator or a smaller model schema. It preserves every
non-whitespace token, all string bytes and number spellings. The original
artifact remains authoritative. A subsequent strict reader must still check
the package signature and its original evidence binding.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re


_EVENT = re.compile(rb'["\\]')
_SPACE = b' \t\r\n'
_STAT = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns')


def compact_json_transport(source, destination, *, expected_bytes, expected_sha256,
                           maximum_output_bytes=1024**3, chunk_bytes=1024**2):
    """Create a new carrier; expected bytes/hash must come from source evidence.

    Missing/changed source, existing destinations and oversized output fail.
    A partial .pending is retained on failure and never published as complete.
    The source itself is never rewritten. Numeric tokens are never parsed.
    """
    source, destination = Path(source).absolute(), Path(destination).absolute()
    if (source.is_symlink() or not source.is_file() or source == destination
            or type(expected_bytes) is not int or expected_bytes <= 0
            or type(expected_sha256) is not str
            or re.fullmatch('[0-9a-f]{64}', expected_sha256) is None
            or type(maximum_output_bytes) is not int or maximum_output_bytes <= 0
            or type(chunk_bytes) is not int or not 1 <= chunk_bytes <= 16*1024**2):
        raise ValueError('invalid_json_transport_declaration')
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(str(destination))
    if destination.parent.is_symlink() or not destination.parent.is_dir():
        raise ValueError('json_transport_requires_existing_output_parent')
    pending = destination.with_name(destination.name+'.pending')
    before = source.stat()
    if before.st_size != expected_bytes:
        raise ValueError('json_transport_source_size_changed')
    original, compact = hashlib.sha256(), hashlib.sha256()
    read = written = 0
    inside = escaped = False
    with source.open('rb') as reader, pending.open('xb') as writer:
        initial = os.fstat(reader.fileno())
        while True:
            raw = reader.read(chunk_bytes)
            if not raw:
                break
            original.update(raw);read += len(raw)
            if read > expected_bytes:
                raise ValueError('json_transport_source_size_changed')
            output = bytearray();offset = 0
            for event in _EVENT.finditer(raw):
                position = event.start();span = raw[offset:position]
                output.extend(span if inside else span.translate(None, _SPACE))
                if span:
                    escaped = False
                value = raw[position];output.append(value)
                if inside:
                    if escaped:
                        escaped = False
                    elif value == 92:
                        escaped = True
                    else:
                        inside = False
                elif value == 34:
                    inside = True
                offset = position+1
            span = raw[offset:]
            output.extend(span if inside else span.translate(None, _SPACE))
            if span:
                escaped = False
            written += len(output)
            if written > maximum_output_bytes:
                raise ValueError('json_transport_output_budget_exhausted')
            compact.update(output);writer.write(output)
        after = os.fstat(reader.fileno())
        current = source.stat()
        if (source.is_symlink() or read != expected_bytes or original.hexdigest() != expected_sha256
                or any(getattr(initial, k) != getattr(after, k) for k in _STAT)
                or any(getattr(before, k) != getattr(current, k) for k in _STAT)):
            raise ValueError('json_transport_source_changed')
        if inside or escaped:
            raise ValueError('json_transport_unterminated_string')
        writer.flush();os.fsync(writer.fileno())
    # Atomic, new-only publication on Linux and Windows; no replacement rename.
    os.link(pending, destination)
    pending.unlink()
    return dict(kind='timelearner_lossless_json_transport', schema_version=1,
                source=dict(path=str(source), bytes=read, sha256=original.hexdigest()),
                transport=dict(path=str(destination), bytes=written, sha256=compact.hexdigest()),
                transformation='remove_JSON_whitespace_outside_strings_only',
                number_tokens_parsed=False, model_fields_removed=False,
                source_modified=False, semantic_package_verified=False,
                strict_package_readback_required=True, scientific_verdict=None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path);parser.add_argument('destination', type=Path)
    parser.add_argument('--expected-bytes', required=True, type=int)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--maximum-output-bytes', type=int, default=1024**3)
    parser.add_argument('--manifest', type=Path, required=True)
    args = parser.parse_args()
    result = compact_json_transport(args.source, args.destination,
        expected_bytes=args.expected_bytes, expected_sha256=args.expected_sha256,
        maximum_output_bytes=args.maximum_output_bytes)
    with args.manifest.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, allow_nan=False);stream.write('\n')


if __name__ == '__main__':
    main()
