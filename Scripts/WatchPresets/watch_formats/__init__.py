"""Watch Interface.xml format parsers."""

from .aggregate import aggregate_drafts, annotate_with_classes
from .bcb_watch import parse_bcb_watch
from .cldesc_libs import build_class_to_library
from .legend_parse import parse_legend
from .model_map import load_project_class_map
from .qt_watch import parse_qt_mdi, parse_qt_tabs

__all__ = [
    "parse_bcb_watch",
    "parse_qt_tabs",
    "parse_qt_mdi",
    "load_project_class_map",
    "annotate_with_classes",
    "aggregate_drafts",
    "build_class_to_library",
    "parse_legend",
]
