"""Qt Watch tab / MDI parsers (v1 + v2)."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import List, Optional

from .common import NormalizedGraph, NormalizedSerie, PropRef, text, text_float, text_int

_TAB_RE = re.compile(r"^UGEngineControllWidget\.UWatch\.tab_(\d+)$")
_MDI_RE = re.compile(r"^UGEngineControllWidget\.Watches_(\d+)$")


def _local(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


def _read_role(serie_el: ET.Element, prefix: str) -> Optional[PropRef]:
    kind = text(serie_el, f"{prefix}Kind", "")
    if kind == "" and text(serie_el, f"{prefix}Component", "") == "":
        return None
    # Kind 0 = Time → no property ref for axis
    try:
        kind_i = int(kind) if kind != "" else -1
    except ValueError:
        kind_i = -1
    if kind_i == 0:
        return None
    return PropRef(
        long_name=text(serie_el, f"{prefix}Component"),
        property=text(serie_el, f"{prefix}Property"),
        jx=text_int(serie_el, f"{prefix}Jx", 0),
        jy=text_int(serie_el, f"{prefix}Jy", 0),
    )


def _parse_serie_v2(
    serie_el: ET.Element,
    project: str,
    fmt: str,
    container: str,
    graph_id: str,
    serie_index: int,
    viz_kind: str,
) -> Optional[NormalizedSerie]:
    y = _read_role(serie_el, "SerieY")
    x = _read_role(serie_el, "SerieX")
    if y is None or not y.long_name:
        # fallback v1 fields inside v2-ish node
        return _parse_serie_v1(
            serie_el, project, fmt, container, graph_id, serie_index, viz_kind
        )
    return NormalizedSerie(
        project=project,
        format=fmt,
        container=container,
        graph_id=graph_id,
        serie_index=serie_index,
        viz_kind=viz_kind if not x else viz_kind,
        y=y,
        x=x,
        legend=text(serie_el, "SerieName"),
        y_shift=text_float(serie_el, "SerieYShift", 0.0),
    )


def _parse_serie_v1(
    serie_el: ET.Element,
    project: str,
    fmt: str,
    container: str,
    graph_id: str,
    serie_index: int,
    viz_kind: str,
) -> Optional[NormalizedSerie]:
    comp = text(serie_el, "SerieNameComponent")
    prop = text(serie_el, "SerieNameProperty")
    if not comp:
        return None
    y = PropRef(
        long_name=comp,
        property=prop,
        jx=text_int(serie_el, "SerieJx", 0),
        jy=text_int(serie_el, "SerieJy", 0),
    )
    return NormalizedSerie(
        project=project,
        format=fmt,
        container=container,
        graph_id=graph_id,
        serie_index=serie_index,
        viz_kind=viz_kind,
        y=y,
        x=None,
        legend=text(serie_el, "SerieName"),
        y_shift=text_float(serie_el, "SerieYShift", 0.0),
        unmatched_property=not bool(prop),
    )


def _parse_container(
    cont_el: ET.Element, project: str, container: str, fmt_base: str
) -> List[NormalizedGraph]:
    graphs: List[NormalizedGraph] = []
    graph_count = text_int(cont_el, "GraphCount", 0)
    # Also discover graph_* children even if count wrong
    graph_els = []
    for child in list(cont_el):
        ctag = _local(child.tag)
        if ctag.startswith("graph_"):
            graph_els.append((ctag, child))
    if not graph_els and graph_count > 0:
        for i in range(graph_count):
            ge = cont_el.find(f"graph_{i}")
            if ge is not None:
                graph_els.append((f"graph_{i}", ge))

    for graph_id, gel in graph_els:
        viz = text(gel, "VizKind", "TimeSeries") or "TimeSeries"
        series: List[NormalizedSerie] = []
        serie_els = []
        for child in list(gel):
            ctag = _local(child.tag)
            if ctag.startswith("serie_"):
                serie_els.append((ctag, child))
        sc = text_int(gel, "SeriesCount", 0)
        if not serie_els:
            for i in range(sc):
                se = gel.find(f"serie_{i}")
                if se is not None:
                    serie_els.append((f"serie_{i}", se))

        for idx, (_sid, sel) in enumerate(serie_els):
            has_v2 = text(sel, "SerieYKind", "") != "" or text(
                sel, "SerieYComponent", ""
            ) != ""
            fmt = "qt_v2" if has_v2 else fmt_base
            if has_v2:
                ser = _parse_serie_v2(
                    sel, project, fmt, container, graph_id, idx, viz
                )
            else:
                ser = _parse_serie_v1(
                    sel, project, fmt, container, graph_id, idx, viz
                )
            if ser:
                series.append(ser)
        if series:
            graphs.append(
                NormalizedGraph(
                    project=project,
                    format=fmt_base,
                    container=container,
                    graph_id=graph_id,
                    series=series,
                )
            )
    return graphs


def parse_qt_tabs(root: ET.Element, project: str) -> List[NormalizedGraph]:
    graphs: List[NormalizedGraph] = []
    for el in root.iter():
        tag = _local(el.tag)
        m = _TAB_RE.match(tag)
        if not m:
            continue
        graphs.extend(_parse_container(el, project, tag, "qt_v1"))
    return graphs


def parse_qt_mdi(root: ET.Element, project: str) -> List[NormalizedGraph]:
    graphs: List[NormalizedGraph] = []
    for el in root.iter():
        tag = _local(el.tag)
        m = _MDI_RE.match(tag)
        if not m:
            continue
        graphs.extend(_parse_container(el, project, tag, "qt_mdi"))
    return graphs
