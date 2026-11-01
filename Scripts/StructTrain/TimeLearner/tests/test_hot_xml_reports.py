"""Failures injected into actual schema3 native warm XML/model/replay exports."""
import csv
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET

from ..hot_xml_reports import audit_run, read_case
from ..native_evidence import EvidenceError


class HotXmlReports(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(os.environ["TL_HOT_XML_SOURCE"]);cls.case=cls.root/"artifacts/Classic-N4-f2000-state1"

    def test_actual_native_corpus(self):
        data, summary=audit_run(self.root)
        self.assertEqual(len(data),32);self.assertEqual(summary["case_soma_pairs"],68)
        self.assertIsNone(summary["scientific_verdict"]);self.assertIsNone(summary["training_certificate"])
        self.assertTrue(any(v["summary"]["warm_time_constants"] != v["summary"]["rest_time_constants"] for v in data.values()))

    def corrupt(self, change, reason):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"case";shutil.copytree(self.case,p);change(p)
            with self.assertRaisesRegex(EvidenceError,reason):read_case(p,False,4,2000,True)

    def json_corrupt(self, name, change, reason):
        def mutate(p):
            f=p/name;value=json.loads(f.read_text());change(value);f.write_text(json.dumps(value))
        self.corrupt(mutate,reason)

    def csv_corrupt(self, change, reason):
        def mutate(p):
            f=p/"replay.csv"
            with f.open(newline="") as stream:rows=list(csv.reader(stream))
            change(rows)
            with f.open("w",newline="") as stream:csv.writer(stream).writerows(rows)
        self.corrupt(mutate,reason)

    def xml_corrupt(self, change, reason):
        def mutate(p):
            f=p/"hot-model.xml";tree=ET.parse(f);change(tree.getroot());tree.write(f,encoding="utf-8")
        self.corrupt(mutate,reason)

    def test_unknown_schema(self):self.json_corrupt("observation.json",lambda o:o.update(schema_version=2),"hot_unknown_observation_schema")
    def test_wrong_state_protocol(self):self.json_corrupt("observation.json",lambda o:o.update(include_state=False),"hot_xml_wrong_protocol")
    def test_short_declared_window(self):self.json_corrupt("observation.json",lambda o:o.update(warm_duration_s=.05),"hot_xml_wrong_protocol")
    def test_missing_saved_state(self):
        self.xml_corrupt(lambda r:r.find("./Model/Components/Learner").remove(r.find("./Model/Components/Learner/State")),"hot_xml_state_flag_mismatch")
    def test_saved_state_not_warm(self):
        self.xml_corrupt(lambda r:setattr(r.find("./Model/Components/Learner/State/SomaNeuronAmplitude"),"text","0 0 0 0 0"),"hot_xml_saved_state_not_warm")
    def test_saved_matrix_dimension(self):
        self.xml_corrupt(lambda r:r.find("./Model/Components/Learner/State/SomaNeuronAmplitude").set("Rows","2"),"hot_xml_saved_readout_dimension")
    def test_missing_rest_link(self):self.json_corrupt("source-rest-model.json",lambda o:o["links"].pop(),"hot_xml_rest_graph_changed")
    def test_rest_physics_changed(self):
        def change(o):next(n for n in o["nodes"] if "capacity_f" in n["physics"])["physics"]["capacity_f"] *= 2
        self.json_corrupt("loaded-model.json",change,"hot_xml_rest_graph_changed")
    def test_warm_physics_changed(self):
        def change(o):next(n for n in o["nodes"] if "capacity_f" in n["physics"])["physics"]["capacity_f"] *= 2
        self.json_corrupt("source-model.json",change,"hot_xml_warm_parameters_changed")
    def test_native_load_error(self):self.corrupt(lambda p:(p/"load-errors.txt").write_text("broken native link"),"hot_xml_native_load_errors")
    def test_replay_truncated(self):self.csv_corrupt(lambda r:r.pop(),"hot_xml_incomplete_replay")
    def test_replay_clock(self):self.csv_corrupt(lambda r:r[2].__setitem__(0,r[1][0]),"hot_xml_replay_clock")
    def test_replay_nonfinite(self):self.csv_corrupt(lambda r:r[2].__setitem__(4,"nan"),"hot_xml_invalid_replay_number")
    def test_replay_stimulus(self):self.csv_corrupt(lambda r:r[40].__setitem__(2,"1"),"hot_xml_replay_stimulus_changed")
    def test_replay_waveform(self):self.csv_corrupt(lambda r:r[40].__setitem__(4,"1"),"hot_xml_replay_waveform_changed")
    def test_original_waveform(self):self.csv_corrupt(lambda r:r[40].__setitem__(3,"1"),"hot_xml_source_waveform_changed")
    def test_invalid_replay_token(self):self.csv_corrupt(lambda r:r[2].__setitem__(4,"broken"),"hot_xml_invalid_replay_number")


if __name__=="__main__":unittest.main()
