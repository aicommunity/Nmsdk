"""BCB UWatchForm / UWatchFrame_* parser."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import List, Optional, Tuple

from .common import (
    SKIP_SERIES_TAGS,
    NormalizedGraph,
    NormalizedSerie,
    PropRef,
    is_series_tag,
    text,
    text_float,
    text_int,
)
from .legend_parse import parse_legend

_FRAME_RE = re.compile(r"^UWatchFrame_?(\d+)$")


def _local(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


def _prop_from_series(el, side: str, legend: str):
    """Return (PropRef|None, unmatched_property). side is 'X' or 'Y'."""
    src = text(el, f"{side}DataSourceName")
    prop_new = text(el, f"{side}OutputIndexNew")
    mrow = text_int(el, "MRow", 0)
    mcol = text_int(el, "MCol", 0)
    if not src:
        return None, False
    prop = prop_new
    unmatched = False
    jx, jy = mcol, mrow
    if not prop:
        parsed = parse_legend(legend)
        if parsed:
            _hint, prop, ljx, ljy = parsed
            if prop:
                jx, jy = ljx, ljy
            else:
                unmatched = True
                jx, jy = ljx, ljy
        else:
            unmatched = True
    return PropRef(long_name=src, property=prop, jx=jx, jy=jy), unmatched


def _parse_series_el(
    el,
    project: str,
    container: str,
    graph_id: str,
    serie_index: int,
) -> Optional[NormalizedSerie]:
    legend = text(el, "Legend")
    y_ref, y_unmatched = _prop_from_series(el, "Y", legend)
    x_ref, x_unmatched = _prop_from_series(el, "X", legend)

    if y_ref and x_ref and y_ref.long_name and x_ref.long_name:
        viz = "XYLine"
        y, x = y_ref, x_ref
        unmatched = y_unmatched or x_unmatched
    elif y_ref and y_ref.long_name:
        viz = "TimeSeries"
        y, x = y_ref, None
        unmatched = y_unmatched
    elif x_ref and x_ref.long_name:
        # BCB pulse-style: signal on X side
        viz = "TimeSeries"
        y, x = x_ref, None
        unmatched = x_unmatched
    else:
        return None

    return NormalizedSerie(
        project=project,
        format="bcb",
        container=container,
        graph_id=graph_id,
        serie_index=serie_index,
        viz_kind=viz,
        y=y,
        x=x,
        legend=legend,
        y_shift=text_float(el, "YShift", 0.0),
        unmatched_property=unmatched,
    )


def parse_bcb_watch(root: ET.Element, project: str) -> List[NormalizedGraph]:
    graphs: List[NormalizedGraph] = []
    for el in root.iter():
        tag = _local(el.tag)
        if tag != "UWatchForm":
            continue
        for frame in list(el):
            ftag = _local(frame.tag)
            m = _FRAME_RE.match(ftag)
            if not m:
                continue
            frame_id = ftag
            series: List[NormalizedSerie] = []
            idx = 0
            for child in list(frame):
                ctag = _local(child.tag)
                if ctag in SKIP_SERIES_TAGS:
                    continue
                if not is_series_tag(ctag):
                    continue
                ser = _parse_series_el(
                    child, project, f"UWatchForm/{frame_id}", frame_id, idx
                )
                if ser:
                    series.append(ser)
                    idx += 1
            if series:
                graphs.append(
                    NormalizedGraph(
                        project=project,
                        format="bcb",
                        container=f"UWatchForm/{frame_id}",
                        graph_id=frame_id,
                        series=series,
                    )
                )
    return graphs
