"""Actual censored/unprepared native probes and explicit corrupted-copy controls."""
import copy
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

from ..native_evidence import EvidenceError, load
from ..probe_reports import render_probe, render_probe_set


class ProbeDiagnosticsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        names=("TIMELEARNER_PARTIAL_PROBE_DIR", "TIMELEARNER_STOPPED_EVIDENCE_DIR", "TIMELEARNER_N0_REPEATS_DIR", "TIMELEARNER_SIX_SOMA_DIR")
        if not all(os.environ.get(n) for n in names):
            raise unittest.SkipTest("requires actual partial, unprepared and complete native probes")
        cls.partial,cls.stopped,cls.complete,cls.six=(Path(os.environ[n]) for n in names)

    def setUp(self):
        output=os.environ.get("TIMELEARNER_DIAGNOSTIC_PLOT_DIR")
        if output:
            self.root=Path(output)/self._testMethodName;self.root.mkdir(parents=True,exist_ok=False)
        else:
            temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup);self.root=Path(temporary.name)

    def copy_case(self, topology="Branch", kind="partial", name="probe"):
        if kind=="partial":
            source=next(iter(sorted(self.partial.glob(topology+"_*stopped_N0RepeatedEarly_stopped_trial_*.json"))))
        elif kind in ("empty", "no_context"):
            source=next(iter(sorted(self.stopped.glob(topology+"_*stopped_InvalidProbe_stopped_trial_*.json"))))
        else:
            source=next(iter(sorted(self.complete.glob(topology+"_*configured_repeats_service_*.json"))))
        packet=self.root/(name+".json");trace=self.root/(name+".csv")
        shutil.copyfile(source,packet);shutil.copyfile(source.with_suffix('.csv'),trace)
        if kind=="no_context":
            # Declared wire mutation of a real zero-sample record, not a new
            # native observation or a scientific no-response result.
            value=load(packet);value.update(observation=None,prepared=None,native_status="rejected",
                                            reasons=["synthetic_no_context_wire_control"])
            packet.write_text(json.dumps(value))
        return packet,trace

    def test_actual_censored_trace_cli_retains_samples_and_unknown_tail(self):
        from PIL import Image
        for topology,count in (("Classic",2),("Branch",1)):
            packet,trace=self.copy_case(topology,name=topology)
            source=load(packet);self.assertIs(source["observation"]["complete"],False)
            strict=self.root/(topology+"-strict")
            with self.assertRaises(EvidenceError):render_probe(packet,trace,strict)
            self.assertFalse(strict.exists())
            output=self.root/(topology+"-diagnostic")
            child=subprocess.run([sys.executable,"-m","Scripts.StructTrain.TimeLearner","report",str(packet),
                                  "--format","probe-diagnostic","--trace",str(trace),"--output",str(output)],capture_output=True,text=True)
            self.assertEqual(child.returncode,0,child.stderr)
            manifest=load(output/"manifest.json");quality=manifest["trace_quality"]
            self.assertEqual(manifest["schema_version"],2);self.assertFalse(quality["recorded_window_complete"])
            self.assertEqual(quality["sample_count"],source["observation"]["sample_count"])
            self.assertLess(quality["last_sample_time"],source["observation"]["specification"]["end"])
            self.assertFalse(manifest["primary_audit"]["valid_observation"])
            self.assertIsNone(manifest["scientific_verdict"])
            self.assertEqual((output/"primary/trace.csv").read_bytes(),trace.read_bytes())
            self.assertEqual(len(manifest["figures"]),count)
            figure=manifest["figures"][0];overview=next(v for v in figure["views"] if v["view"]=="overview")
            with Image.open(output/overview["files"][0]) as image:self.assertEqual(image.size,(1920,960))
            svg=(output/overview["files"][1]).read_text()
            self.assertIn("Unobserved / censored",svg)

    def test_actual_six_soma_trace_has_six_individual_full_size_figures(self):
        from PIL import Image
        stem="Classic_2000_N0_learned_boundary_explicit_tolerance_inputs6_frozen_test"
        packet,trace=self.six/(stem+"_evidence.json"),self.six/(stem+".csv")
        self.assertEqual(len(load(packet)["observation"]["specification"]["baseline"]),6)
        output=self.root/"report";result=render_probe(packet,trace,output)
        manifest=load(output/"manifest.json")
        self.assertEqual(result["soma_count"],6)
        self.assertEqual({f["channel"] for f in manifest["figures"]},set(range(6)))
        for figure in manifest["figures"]:
            overview=next(v for v in figure["views"] if v["view"]=="overview")
            with Image.open(output/overview["files"][0]) as image:self.assertEqual(image.size,(1920,960))
        self.assertEqual((output/"primary/trace.csv").read_bytes(),trace.read_bytes())

    def test_no_context_wire_record_has_no_invented_soma_or_clock(self):
        packet,trace=self.copy_case(kind="no_context")
        source=load(packet);self.assertIsNone(source["observation"])
        output=self.root/"report";result=render_probe(packet,trace,output,allow_incomplete=True)
        manifest=load(output/"manifest.json")
        self.assertEqual(result["plotted_soma_count"],0)
        self.assertIsNone(manifest["observed_soma_count"]);self.assertIsNone(manifest["frequency_hz"])
        self.assertEqual(manifest["figures"],[]);self.assertFalse(manifest["trace_quality"]["context_observed"])
        self.assertEqual((output/"primary/trace.csv").read_bytes(),trace.read_bytes())

    def test_actual_zero_sample_rejection_keeps_known_channels_without_curves(self):
        packet,trace=self.copy_case(kind="empty")
        source=load(packet);self.assertEqual(source["observation"]["sample_count"],0)
        output=self.root/"report";result=render_probe(packet,trace,output,allow_incomplete=True)
        manifest=load(output/"manifest.json")
        self.assertEqual(result["plotted_soma_count"],0)
        self.assertEqual(manifest["observed_soma_count"],1)
        self.assertTrue(manifest["trace_quality"]["context_observed"])
        self.assertFalse(manifest["trace_quality"]["recorded_window_complete"])
        self.assertTrue(all(not f["views"] for f in manifest["figures"]))

    def test_empty_trace_wire_record_remains_explicitly_unobserved(self):
        packet,trace=self.copy_case(kind="no_context");trace.write_bytes(b'')
        output=self.root/"report";render_probe(packet,trace,output,allow_incomplete=True)
        manifest=load(output/"manifest.json")
        self.assertFalse(manifest["trace_quality"]["trace_header_present"])
        self.assertIsNone(manifest["trace_quality"]["recorded_header_channels"])
        self.assertEqual((output/"primary/trace.csv").read_bytes(),b'')
        self.assertEqual(manifest["figures"],[])

    def test_nonfinite_ordinate_is_preserved_as_a_gap_never_zero(self):
        packet,trace=self.copy_case()
        with trace.open(newline='') as stream:rows=list(csv.reader(stream))
        rows[4][2]='NaN'
        with trace.open('w',newline='') as stream:csv.writer(stream).writerows(rows)
        original=trace.read_bytes();output=self.root/"report"
        render_probe(packet,trace,output,allow_incomplete=True)
        manifest=load(output/"manifest.json")
        self.assertEqual(manifest["trace_quality"]["nonfinite_cells"],[{"csv_row":5,"column":"soma0"}])
        self.assertEqual((output/"primary/trace.csv").read_bytes(),original)
        self.assertEqual(manifest["source_trace_sha256"],hashlib.sha256(original).hexdigest())
        self.assertFalse(manifest["trace_quality"]["recorded_window_complete"])

    def test_one_recorded_sample_remains_visible_in_both_actual_series(self):
        packet,trace=self.copy_case();value=load(packet)
        with trace.open(newline='') as stream:rows=list(csv.reader(stream))
        with trace.open('w',newline='') as stream:csv.writer(stream).writerows(rows[:2])
        value["observation"]["sample_count"]=1
        value["reasons"].append("synthetic_one_sample_censoring_control")
        packet.write_text(json.dumps(value));output=self.root/"report"
        render_probe(packet,trace,output,allow_incomplete=True)
        manifest=load(output/"manifest.json");self.assertEqual(manifest["trace_quality"]["sample_count"],1)
        view=next(v for v in manifest["figures"][0]["views"] if v["view"]=="overview")
        svg=ET.parse(output/view["files"][1]).getroot()
        parents={child:parent for parent in svg.iter() for child in parent}
        def under(node,identity):
            while node is not None:
                if node.get('id')==identity:return True
                node=parents.get(node)
            return False
        for identity,color in (("axes_1","#154c9a"),("axes_2","#d46200")):
            markers=[n for n in svg.iter() if n.tag.endswith('use') and color in n.get('style','') and under(n,identity)]
            self.assertEqual(len(markers),1,(identity,markers))
            node=markers[0]
            while node is not None:
                self.assertIsNone(node.get('clip-path'), (identity,node.attrib))
                node=parents.get(node)
            waveforms=[n for n in svg.iter() if n.tag.endswith('path') and color in n.get('style','')
                       and under(n,identity) and n.get('clip-path')]
            self.assertTrue(waveforms, "waveform must remain clipped to the plotted time window")
        self.assertTrue(view["sample_markers"])

    def test_invalid_schema_clock_and_counts_still_reject_diagnostic(self):
        packet,trace=self.copy_case();source=load(packet);original=trace.read_text()
        for index,mutation in enumerate(("schema","count","clock","token","ragged")):
            value=copy.deepcopy(source);trace.write_text(original)
            if mutation=="schema":value["observation"]["specification"]["schema_version"]=999
            elif mutation=="count":value["observation"]["sample_count"]+=1
            else:
                rows=list(csv.reader(original.splitlines()))
                if mutation=="clock":rows[2][0]='NaN'
                elif mutation=="token":rows[2][2]='damaged-token'
                else:rows[2].pop()
                with trace.open('w',newline='') as stream:csv.writer(stream).writerows(rows)
            packet.write_text(json.dumps(value));output=self.root/f'bad-{index}'
            with self.assertRaises(EvidenceError):render_probe(packet,trace,output,allow_incomplete=True)
            self.assertFalse(output.exists())

    def test_mixed_set_keeps_partial_policy_and_explicit_unknown_trial(self):
        trials=[]
        for kind in ("complete","partial","no_context"):
            packet,trace=self.copy_case(kind=kind,name=kind)
            trials.append({"trial_id":load(packet)["requested_specification"]["trial_id"],"packet":packet.name,"trace":trace.name})
        spec={"kind":"timelearner_probe_report_spec","schema_version":2,"observation_policy":"complete_or_partial","trials":trials}
        path=self.root/"spec.json";path.write_text(json.dumps(spec));output=self.root/"report"
        result=render_probe_set(path,output);manifest=load(output/"manifest.json")
        self.assertEqual(result["trials"],3);self.assertEqual(result["trial_soma_pairs"],2)
        self.assertFalse(manifest["data_complete"])
        self.assertEqual(manifest["unknown_soma_trials"],[trials[-1]["trial_id"]])
        portable=load(output/"report-spec.json")
        self.assertEqual(portable["schema_version"],2);self.assertEqual(portable["observation_policy"],"complete_or_partial")
        again=self.root/"rerender";second=render_probe_set(output/"report-spec.json",again)
        self.assertEqual(second["trial_soma_pairs"],2)
