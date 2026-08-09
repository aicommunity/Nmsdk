#!/usr/bin/env python3
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from watch_formats.bcb_watch import parse_bcb_watch
from watch_formats.common import parse_xml_file
from watch_formats.composition import default_composition, expand_presets_for_class
from watch_formats.legend_parse import parse_legend
from watch_formats.model_map import load_class_map_from_xml
from watch_formats.path_roles import normalize_role_path, template_role_path
from watch_formats.qt_watch import parse_qt_mdi, parse_qt_tabs

FIX = Path(__file__).parent / "fixtures"


class TestLegend(unittest.TestCase):
    def test_bracket_prop(self):
        r = parse_legend("PosPGenerator[OutputPulseTimes:0]")
        self.assertEqual(r[1], "OutputPulseTimes")

    def test_colon_cell(self):
        r = parse_legend("PNeuronBio.LTZone:Output(0,0)")
        self.assertEqual(r[0], "PNeuronBio.LTZone")
        self.assertEqual(r[1], "Output")
        self.assertEqual(r[2:], (0, 0))

    def test_numeric(self):
        r = parse_legend("DCEngine[1:0]")
        self.assertEqual(r[1], "")


class TestPathRoles(unittest.TestCase):
    def test_ltzone(self):
        self.assertEqual(normalize_role_path("LTZone"), "LTZone")
        self.assertEqual(normalize_role_path("Motoneuron1.LTZone"), "LTZone")
        self.assertEqual(normalize_role_path("NeuronTrainer1.Neuron.LTZone"), "LTZone")

    def test_dendrite_channel(self):
        self.assertEqual(
            normalize_role_path("Dendrite3_1.ExcChannel"), "Dendrite1_1.ExcChannel"
        )
        self.assertEqual(
            template_role_path("Dendrite1_1.ExcChannel"), "Dendrite*.ExcChannel"
        )

    def test_soma_synapse(self):
        self.assertEqual(
            normalize_role_path("Soma2.ExcSynapse3"), "Soma1.ExcSynapse1"
        )


class TestCompositionExpand(unittest.TestCase):
    def test_parent_inherits_ltzone(self):
        by_class = {
            "NPLTZone": [
                {
                    "id": "output",
                    "title": "LTZone output",
                    "series": [{"path": "", "property": "Output", "jx": 0, "jy": 0}],
                }
            ],
            "NPNeuron": [],
        }
        expanded = expand_presets_for_class("NPNeuron", by_class, default_composition())
        ids = [p["id"] for p in expanded]
        self.assertIn("inherited:LTZone:output", ids)
        inh = next(p for p in expanded if p["id"] == "inherited:LTZone:output")
        self.assertEqual(inh["series"][0]["path"], "LTZone")
        self.assertEqual(inh["series"][0]["property"], "Output")


class TestParsers(unittest.TestCase):
    def test_bcb_y_only(self):
        root = parse_xml_file(FIX / "bcb_y_only.xml")
        graphs = parse_bcb_watch(root, "test/bcb_y")
        self.assertTrue(graphs)
        s = graphs[0].series[0]
        self.assertEqual(s.y.long_name, "PGenerator")
        self.assertEqual(s.y.property, "Output")

    def test_bcb_x_pulse(self):
        root = parse_xml_file(FIX / "bcb_x_pulse.xml")
        graphs = parse_bcb_watch(root, "test/bcb_x")
        s = graphs[0].series[0]
        self.assertEqual(s.y.property, "OutputPulseTimes")

    def test_bcb_frame_no_underscore(self):
        root = parse_xml_file(FIX / "bcb_frame1.xml")
        graphs = parse_bcb_watch(root, "test/frame1")
        self.assertEqual(len(graphs), 1)

    def test_bcb_numeric_y_unmatched_property(self):
        root = parse_xml_file(FIX / "bcb_numeric_y.xml")
        graphs = parse_bcb_watch(root, "test/bcb_numeric")
        self.assertTrue(graphs)
        s = graphs[0].series[0]
        self.assertEqual(s.y.long_name, "DCEngine")
        self.assertTrue(s.unmatched_property)
        self.assertEqual(s.y.property, "")

    def test_qt_v1(self):
        root = parse_xml_file(FIX / "qt_v1.xml")
        graphs = parse_qt_tabs(root, "test/qt")
        self.assertEqual(len(graphs[0].series), 2)
        self.assertEqual(graphs[0].series[1].y.long_name, "IaFNeuron.LTZone")

    def test_qt_v2(self):
        root = parse_xml_file(FIX / "qt_v2.xml")
        graphs = parse_qt_tabs(root, "test/v2")
        self.assertEqual(graphs[0].series[0].format, "qt_v2")
        self.assertEqual(graphs[0].series[0].y.property, "Output")

    def test_mdi(self):
        root = parse_xml_file(FIX / "qt_mdi.xml")
        graphs = parse_qt_mdi(root, "test/mdi")
        self.assertEqual(graphs[0].series[0].y.property, "SomaNeuronAmplitude")

    def test_model_map_legacy(self):
        m = load_class_map_from_xml(FIX / "model_legacy.xml")
        self.assertEqual(m.get("PosPGenerator"), "NPGenerator")
        self.assertEqual(m.get("PNeuron.LTZone"), "NPLTZone")

    def test_model_map_modern(self):
        m = load_class_map_from_xml(FIX / "model_modern.xml")
        self.assertEqual(m.get("IaFNeuron"), "NPulseNeuronIaF")
        self.assertEqual(m.get("IaFNeuron.LTZone"), "NPulseLTZoneIaF")


if __name__ == "__main__":
    unittest.main()
