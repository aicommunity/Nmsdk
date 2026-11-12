"""Bounded, strict reader for retained Qt qCompress JSON model artifacts."""
import hashlib
from pathlib import Path
import struct
import zlib

from .native_evidence import EvidenceError, parse_json_bytes, require


def read_qcompress_bytes(path, *, expected_bytes, expected_sha256):
    path = Path(path)
    require(not path.is_symlink() and 4 < path.stat().st_size <= 64*1024**2,
            'recorded_qz_packed_size')
    require(type(expected_bytes) is int and 0 < expected_bytes <= 256*1024**2,
            'recorded_qz_declared_size')
    packed = path.read_bytes()
    declared = struct.unpack('>I', packed[:4])[0]
    require(declared == expected_bytes, 'recorded_qz_declared_size')
    decoder = zlib.decompressobj()
    try:
        raw = decoder.decompress(packed[4:], declared+1)
    except zlib.error as error:
        raise EvidenceError('recorded_qz_invalid_stream') from error
    require(decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail
            and len(raw) == declared, 'recorded_qz_incomplete_or_trailing')
    require(hashlib.sha256(raw).hexdigest() == expected_sha256, 'recorded_qz_raw_sha256')
    return raw


def read_qcompress_json(path, *, expected_bytes, expected_sha256):
    document = parse_json_bytes(read_qcompress_bytes(path, expected_bytes=expected_bytes,
                                                   expected_sha256=expected_sha256))
    require(isinstance(document, dict), 'recorded_qz_json_object')
    return document
