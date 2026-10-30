"""Parse BCB Legend strings for property fallback."""

from __future__ import annotations

import re
from typing import Optional, Tuple

# PosPGenerator[OutputPulseTimes:0]
_RE_BRACKET_PROP = re.compile(
    r"^(?P<comp>.+)\[(?P<prop>[A-Za-z_][A-Za-z0-9_]*)(?::(?P<idx>\d+))?\]$"
)
# PGenerator:Output(0,0)  or  PNeuron.LTZone:Output(0,0)
_RE_COLON_CELL = re.compile(
    r"^(?P<comp>.+):(?P<prop>[A-Za-z_][A-Za-z0-9_]*)\((?P<jx>-?\d+)\s*,\s*(?P<jy>-?\d+)\)$"
)
# DCEngine[1:0] — numeric only
_RE_BRACKET_NUM = re.compile(r"^(?P<comp>.+)\[(?P<a>\d+):(?P<b>\d+)\]$")


def parse_legend(legend: str) -> Optional[Tuple[str, str, int, int]]:
    """Return (component_hint, property, jx, jy) or None."""
    s = (legend or "").strip()
    if not s:
        return None

    m = _RE_COLON_CELL.match(s)
    if m:
        return (
            m.group("comp").strip(),
            m.group("prop"),
            int(m.group("jx")),
            int(m.group("jy")),
        )

    m = _RE_BRACKET_PROP.match(s)
    if m:
        idx = int(m.group("idx") or "0")
        return (m.group("comp").strip(), m.group("prop"), idx, 0)

    m = _RE_BRACKET_NUM.match(s)
    if m:
        # no property name
        return (m.group("comp").strip(), "", int(m.group("a")), int(m.group("b")))

    return None
