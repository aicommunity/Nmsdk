"""Readable actual input/soma traces for the four baseline equivalence probes."""
import os
from pathlib import Path
import unittest
from ..native_calibration_worker import _write
from ..native_evidence import load
from ..plotting import padded_limits
from ..probe_reports import _read_probe_data,render_probe


class FastProfileBaselineReportTest(unittest.TestCase):
    def test_four_actual_bursts_have_common_scale_temporal_reports(self):
        root=Path(os.environ['TIMELEARNER_FAST_BASELINE_READBACK']).resolve(strict=True)
        output=Path(os.environ['TMPDIR'])/'fast-profile-baseline-gallery'
        output.mkdir(exist_ok=False)
        prepared=[];values=[]
        for graph in ('cold','grown'):
            for profile in ('original','storage-baseline'):
                name=graph+'-'+profile;native=root/name/'native'
                packet=native/'probe_trial_1.json';trace=native/'probe_trial_1.csv'
                data=_read_probe_data(packet,trace,True)
                self.assertEqual(data[6],1)
                self.assertTrue(data[7]['recorded_window_complete'])
                values.extend(s['soma'][0] for s in data[5])
                prepared.append((name,packet,trace))
        limits=[padded_limits(values)];entries=[]
        from PIL import Image
        for name,packet,trace in prepared:
            result=render_probe(packet,trace,output/name,limits,True)
            self.assertEqual(result['plotted_soma_count'],1)
            manifest=load(output/name/'manifest.json')
            self.assertFalse(manifest['spike_recording_enabled'])
            self.assertFalse(manifest['visual_acceptance_complete'])
            views=manifest['figures'][0]['views'];self.assertTrue(views)
            for view in views:
                with Image.open(output/name/view['files'][0]) as im:
                    self.assertGreaterEqual(im.width,1600);self.assertGreaterEqual(im.height,600)
            entries.append(dict(name=name,report=result,source_trace_sha256=manifest['source_trace_sha256']))
        _write(output/'comparison.json',dict(kind='timelearner_fast_profile_baseline_visual_report',schema_version=1,
            common_y_limits=limits,entries=entries,classification_assessed=False,scientific_verdict=None))
        links=''.join('<li><a href="'+e['name']+'/index.html">'+e['name']+'</a></li>' for e in entries)
        (output/'index.html').write_text('<!doctype html><meta charset="utf-8"><h1>Stock / storage baseline: actual input and soma</h1><p>Cold and grown graphs; common Y scale. Diagnostic probes, no classification claim.</p><ul>'+links+'</ul>')
