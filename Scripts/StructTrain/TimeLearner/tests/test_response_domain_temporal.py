"""Production diagnostic plotting controls; execute on designated workers only."""
import csv
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ..native_evidence import EvidenceError, load
from ..response_domain_temporal import render
from .test_response_domain_evidence import fixture


def _case(root, name, *, scale=False):
    packet, raw = fixture()
    if scale:
        temporal = {'begin','end','maximum_sample_gap','pulse_length','time','plateau_end',
                    'delay_from_stimulus','relative_to_trial_start','actual_stimulus_time',
                    'maximum_offset_low','maximum_offset_high','first_stimulus_time'}
        def change(value):
            if type(value) is list:
                for item in value: change(item)
            elif type(value) is dict:
                for key, item in value.items():
                    if type(item) in (int,float):
                        if key in temporal:value[key]=item/2
                        elif key=='frequency_hz':value[key]=item*2
                        elif key=='amplitude':value[key]=item*2
                        elif key in ('raw','raw_potential'):value[key]=2+(item-2)*2
                    elif key in ('run_id','trial_id'):value[key]=name+'/'+item
                    else:change(item)
        change(packet)
        rows=list(csv.reader(io.StringIO(raw.decode())))
        raw=(','.join(rows[0])+'\n'+''.join(','.join(format(v,'.17g') for v in
            [float(row[0])/2,float(row[1])*2,*[2+(float(v)-2)*2 for v in row[2:]]])+'\n' for row in rows[1:])).encode()
        packet['trace'].update(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    folder=root/name;folder.mkdir(parents=True)
    (folder/'trace.csv').write_bytes(raw);path=folder/(name+'.domains.json')
    path.write_text(json.dumps(packet,allow_nan=False),encoding='utf-8')
    return path


class ResponseDomainTemporalTest(unittest.TestCase):
    def setUp(self):
        temporary=tempfile.TemporaryDirectory(prefix='timelearner-domain-temporal-')
        self.addCleanup(temporary.cleanup);self.root=Path(temporary.name)
        self.corpus=self.root/'primary';self.corpus.mkdir();self.output=self.root/'report'

    def test_actual_render_all_somas_two_frequencies_and_full_tick_views(self):
        from PIL import Image
        first=_case(self.corpus,'first');second=_case(self.corpus,'second',scale=True)
        source_hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in self.corpus.rglob('*') if p.is_file()}
        result=render(self.corpus,self.output,'a'*40)
        self.assertEqual(result['case_count'],2);self.assertEqual(result['trial_soma_pairs'],4)
        self.assertEqual(len(result['selected_overviews']),4)
        self.assertEqual(len(result['figures']),16)
        self.assertEqual(result['schema_version'],2)
        self.assertTrue(result['anchored_to_actual_events'])
        centered=[f for f in result['figures'] if f['view'].startswith('input-')]
        self.assertEqual(len(centered),8)
        for figure in centered:
            self.assertTrue(figure['anchored_to_actual_event'])
            self.assertEqual(figure['purpose'],'actual_stimulus_context')
            source=load(self.corpus/figure['packet'])
            spec=source['native_evidence']['observation']['specification']
            events=source['native_evidence']['observation']['stimuli']
            event=next(e for e in events if e['id']==figure['actual_event_id'])
            self.assertEqual(figure['actual_event_time'],event['time'])
            self.assertEqual(figure['x_bounds_s'],[
                max(spec['begin'],event['time']-20/figure['frequency_hz']),
                min(spec['end'],event['time']+80/figure['frequency_hz'])])
            left,right=figure['x_bounds_s']
            if spec['begin']<event['time']<spec['end']:
                self.assertLess(left,event['time']);self.assertLess(event['time'],right)
            # The literal fixture contains a complete one-tick digital pulse;
            # both its actual leading edge and end fit the anchored context.
            self.assertLess(left,event['time'])
            self.assertGreaterEqual(right,event['time']+spec['stimulus_profile']['pulse_length'])
        self.assertEqual({c['frequency_hz'] for c in result['cases']},{10.,20.})
        self.assertFalse(result['training_certificate_eligible']);self.assertFalse(result['causal_origin_verified'])
        self.assertFalse(result['physical_paths_independently_verified']);self.assertIsNone(result['scientific_verdict'])
        self.assertFalse(result['downsampling'])
        common={}
        for figure in result['figures']:
            self.assertTrue(figure['actual_input_overlay']);self.assertFalse(figure['downsampling'])
            self.assertFalse(figure['matplotlib_path_simplification'])
            self.assertEqual(figure['full_sample_count'],figure['plotted_sample_count'])
            key=tuple(figure['shared_y_group'])
            if key in common:self.assertEqual(figure['y_bounds_native'],common[key])
            common[key]=figure['y_bounds_native']
            # The second corpus has larger potential. The first must share it.
            self.assertGreater(figure['y_bounds_native'][1],10.)
            if figure['view']!='overview':self.assertGreaterEqual(figure['minimum_native_tick_pixels_on_zoom'],8.)
            with Image.open(self.output/figure['files'][0]) as image:self.assertEqual(list(image.size),figure['pixels'])
        for filename,record in result['figure_files'].items():
            raw=(self.output/filename).read_bytes();self.assertEqual(len(raw),record['bytes'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(),record['sha256'])
        for relative,record in result['primary_file_bindings'].items():
            self.assertEqual(hashlib.sha256((self.corpus/relative).read_bytes()).hexdigest(),record['sha256'])
        self.assertEqual(source_hashes,{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in self.corpus.rglob('*') if p.is_file()})
        page=(self.output/'index.html').read_text(encoding='utf-8')
        self.assertIn('max-width:none',page);self.assertIn('no downsampling',page)
        self.assertIn('no proven peak origin',page)
        self.assertEqual(load(self.output/'manifest.json')['declared_source_evidence'],'a'*40)

    def test_all_packets_audited_before_any_output_or_backend(self):
        _case(self.corpus,'a-valid');bad=_case(self.corpus,'z-invalid',scale=True)
        packet=load(bad);packet['training_certificate_eligible']=True
        bad.write_text(json.dumps(packet),encoding='utf-8')
        with patch('Scripts.StructTrain.TimeLearner.response_domain_temporal.plotting_runtime') as backend:
            with self.assertRaises(EvidenceError):render(self.corpus,self.output,'a'*40)
            backend.assert_not_called()
        self.assertFalse(self.output.exists())

    def test_changed_csv_is_rejected_before_report_creation(self):
        path=_case(self.corpus,'damaged');trace=path.parent/'trace.csv'
        trace.write_bytes(trace.read_bytes()+b'\n')
        with self.assertRaises(EvidenceError):render(self.corpus,self.output,'a'*40)
        self.assertFalse(self.output.exists())

    def test_duplicate_trial_is_not_silently_rendered_twice(self):
        _case(self.corpus,'one');_case(self.corpus,'two')
        with self.assertRaisesRegex(EvidenceError,'duplicate_trial'):render(self.corpus,self.output,'a'*40)
        self.assertFalse(self.output.exists())

    def test_empty_corpus_bad_revision_and_primary_overlap_are_rejected(self):
        with self.assertRaises(EvidenceError):render(self.corpus,self.output,'a'*40)
        _case(self.corpus,'one')
        with self.assertRaises(EvidenceError):render(self.corpus,self.output,'not-a-commit')
        with self.assertRaises(EvidenceError):render(self.corpus,self.corpus/'plots','a'*40)
        self.assertFalse((self.corpus/'plots').exists())
