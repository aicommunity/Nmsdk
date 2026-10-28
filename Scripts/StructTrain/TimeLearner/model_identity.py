"""Portable semantic JSON hash used by PulseLib ModelIdentity.cpp.

Keys follow QString UTF-16 order. Numbers use finite binary64 bits, with zero
canonicalized; JSON spelling, indentation and Qt version do not affect identity.
"""
from __future__ import annotations

import hashlib
import math
import struct
from typing import Any

from .native_evidence import require


def canonical_model_sha256(value: Any) -> str:
    digest = hashlib.sha256()

    def frame(payload: bytes) -> None:
        digest.update(str(len(payload)).encode("ascii") + b":" + payload)

    def visit(item: Any) -> None:
        if item is None:
            digest.update(b"n")
        elif type(item) is bool:
            digest.update(b"t" if item else b"f")
        elif isinstance(item, (int, float)):
            number = float(item)
            require(math.isfinite(number), "nonfinite_identity_number")
            if number == 0:
                number = 0.
            digest.update(b"d")
            frame(struct.pack(">d", number).hex().encode("ascii"))
        elif isinstance(item, str):
            digest.update(b"s")
            frame(item.encode("utf-8"))
        elif isinstance(item, list):
            digest.update(b"a")
            frame(str(len(item)).encode("ascii"))
            for child in item:
                visit(child)
        elif isinstance(item, dict):
            require(all(isinstance(key, str) for key in item), "nonstring_identity_key")
            digest.update(b"o")
            frame(str(len(item)).encode("ascii"))
            for key in sorted(item, key=lambda key: key.encode("utf-16-be")):
                frame(key.encode("utf-8"))
                visit(item[key])
        else:
            raise ValueError("unsupported_identity_type")

    visit(value)
    return digest.hexdigest()
