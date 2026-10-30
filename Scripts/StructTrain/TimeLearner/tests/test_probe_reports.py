import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from ..native_evidence import EvidenceError, load
from ..probe_reports import render_probe_set


class ProbeReportsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=os.environ.get("TIMELEARNER_N0_REPEATS_DIR")
        if not source:
            raise unittest.SkipTest("requires actual native N0 repeated-candidate primary data")
        cls.source=Path(source)

    def setUp(self):
        output=os.environ.get("TIMELEARNER_PROBE_PLOT_DIR")
        if output:
            self.root=Path(output)/self._testMethodName;self.root.mkdir(parents=True,exist_ok=False)
        else:
            temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup);self.root=Path(temporary.name)

    def prepare(self, topology):
        directory=self.root/topology;directory.mkdir()
        paths=sorted(self.source.glob(topology+'_*configured_repeats_service_*.json'))
        if len(paths)<2:raise RuntimeError("missing actual native topology trials")
        trials=[]
        for index,path in enumerate(paths[:2]):
            packet=load(path);shutil.copyfile(path,directory/f'probe-{index}.json')
            shutil.copyfile(path.with_suffix('.csv'),directory/f'probe-{index}.csv')
            trials.append({'trial_id':packet['observation']['specification']['trial_id'],
                           'packet':f'probe-{index}.json','trace':f'probe-{index}.csv'})
        spec={'kind':'timelearner_probe_report_spec','schema_version':1,'trials':trials}
        path=directory/'spec.json';path.write_text(json.dumps(spec))
        return directory,path,spec

    def test_actual_cli_all_recorded_somas_common_axes_and_primary_hashes(self):
        from PIL import Image
        for topology,count in (('Classic',2),('Branch',1)):
            directory,spec,_=self.prepare(topology);output=directory/'report'
            result=subprocess.run([sys.executable,'-m','Scripts.StructTrain.TimeLearner','report',str(spec),
                                   '--format','probe-set','--output',str(output)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            summary=json.loads(result.stdout);self.assertEqual(summary['trial_soma_pairs'],2*count)
            manifest=load(output/'manifest.json');self.assertEqual(len(manifest['reports']),2)
            for entry in manifest['reports']:
                report=output/entry['folder'];item=load(report/'manifest.json')
                self.assertEqual(item['comparison_scope'],'explicit shared probe set')
                self.assertFalse(item['spike_recording_enabled'])
                self.assertEqual(len(item['figures']),count)
                self.assertEqual(hashlib.sha256((report/'primary/trace.csv').read_bytes()).hexdigest(),item['source_trace_sha256'])
                self.assertEqual(hashlib.sha256((report/'primary/probe.json').read_bytes()).hexdigest(),item['source_packet_sha256'])
                for figure in item['figures']:
                    for view in figure['views']:
                        if view['y_scale']=='shared':self.assertEqual(view['y_limits'],manifest['common_y_limits'][figure['channel']])
                        with Image.open(report/view['files'][0]) as image:self.assertEqual(image.size,(1920,960))
            for name,sha in load(output/'SHA256SUMS.json').items():
                self.assertEqual(hashlib.sha256((output/name).read_bytes()).hexdigest(),sha)
            self.assertIn('unknown spike response',(output/'probe-0000/index.html').read_text())

    def test_missing_duplicate_or_wrong_trial_prevents_report(self):
        directory,path,spec=self.prepare('Classic')
        for mode in ('duplicate','wrong','missing'):
            changed=copy.deepcopy(spec)
            if mode=='duplicate':changed['trials'].append(changed['trials'][0])
            elif mode=='wrong':changed['trials'][0]['trial_id']='not-the-recorded-trial'
            else:changed['trials'][0]['trace']='absent.csv'
            path.write_text(json.dumps(changed));output=directory/mode
            with self.assertRaises((EvidenceError,FileNotFoundError)):render_probe_set(path,output)
            self.assertFalse(output.exists())

    def test_damaged_csv_is_not_plotted_as_zero(self):
        directory,path,spec=self.prepare('Branch')
        trace=directory/spec['trials'][0]['trace'];rows=trace.read_text().splitlines()
        tokens=rows[1].split(',');tokens[2]='NaN';rows[1]=','.join(tokens);trace.write_text('\n'.join(rows)+'\n')
        with self.assertRaises(EvidenceError):render_probe_set(path,directory/'report')
        self.assertFalse((directory/'report').exists())

    def test_unsupported_spike_claim_is_not_shown_as_measured_silence(self):
        directory,path,spec=self.prepare('Branch')
        packet_path=directory/spec['trials'][0]['packet'];packet=load(packet_path)
        packet['observation']['specification']['record_spikes']=True
        packet['requested_specification']['record_spikes']=True
        packet['observation']['spike_count']=0
        packet_path.write_text(json.dumps(packet))
        with self.assertRaises(EvidenceError):render_probe_set(path,directory/'report')
        self.assertFalse((directory/'report').exists())
