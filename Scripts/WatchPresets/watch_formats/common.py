"""Shared types for Watch Interface.xml mining."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PropRef:
    long_name: str = ""
    property: str = ""
    jx: int = 0
    jy: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "longName": self.long_name,
            "property": self.property,
            "jx": self.jx,
            "jy": self.jy,
        }


@dataclass
class NormalizedSerie:
    project: str
    format: str
    container: str
    graph_id: str
    serie_index: int
    viz_kind: str = "TimeSeries"
    y: Optional[PropRef] = None
    x: Optional[PropRef] = None
    legend: str = ""
    y_shift: float = 0.0
    unmatched_property: bool = False
    # filled after class map
    y_class: str = ""
    anchor_class: str = ""
    anchor_long_name: str = ""
    rel_path: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "project": self.project,
            "format": self.format,
            "container": self.container,
            "graphId": self.graph_id,
            "serieIndex": self.serie_index,
            "vizKind": self.viz_kind,
            "y": self.y.to_dict() if self.y else None,
            "x": self.x.to_dict() if self.x else None,
            "visual": {"legend": self.legend, "yShift": self.y_shift},
            "unmatchedProperty": self.unmatched_property,
            "yClass": self.y_class,
            "anchorClass": self.anchor_class,
            "anchorLongName": self.anchor_long_name,
            "relPath": self.rel_path,
        }
        return d


@dataclass
class NormalizedGraph:
    project: str
    format: str
    container: str
    graph_id: str
    series: List[NormalizedSerie] = field(default_factory=list)


SKIP_SERIES_TAGS = {
    "WatchInterval",
    "AutoMinYValue",
    "AutoMaxYValue",
    "UpdateInterval",
    "ComponentControlName",
    "AlwaysUpdateFlag",
    "ShowLegendCheckBox",
    "Visible",
}

# BCB series nodes are <0>, <1>, … — invalid XML 1.0 names for ElementTree.
import re
from xml.etree import ElementTree as ET

_RE_NUMERIC_TAG = re.compile(r"</?(\d+)(/?)>")


def sanitize_numeric_tags(xml_text: str) -> str:
    """Rewrite <0>…</0> as <n0>…</n0> so ElementTree can parse."""

    def repl(m: re.Match) -> str:
        num = m.group(1)
        slash = m.group(2)
        if m.group(0).startswith("</"):
            return f"</n{num}>"
        if slash:
            return f"<n{num}/>"
        return f"<n{num}>"

    return _RE_NUMERIC_TAG.sub(repl, xml_text)


def parse_xml_file(path) -> ET.Element:
    raw = path.read_text(encoding="utf-8", errors="replace")
    return ET.fromstring(sanitize_numeric_tags(raw))


def parse_xml_string(xml_text: str) -> ET.Element:
    return ET.fromstring(sanitize_numeric_tags(xml_text))


def is_series_tag(tag: str) -> bool:
    if tag.isdigit():
        return True
    if len(tag) > 1 and tag[0] == "n" and tag[1:].isdigit():
        return True
    return False


def text(el, tag: str, default: str = "") -> str:
    child = el.find(tag)
    if child is None or child.text is None:
        return default
    return child.text.strip()


def text_int(el, tag: str, default: int = 0) -> int:
    s = text(el, tag, "")
    if s == "":
        return default
    try:
        return int(float(s))
    except ValueError:
        return default


def text_float(el, tag: str, default: float = 0.0) -> float:
    s = text(el, tag, "")
    if s == "":
        return default
    try:
        return float(s)
    except ValueError:
        return default
