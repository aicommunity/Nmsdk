"""Report the four preregistered N0 terminal-state evaluations without rerunning them."""
import os
from pathlib import Path
import unittest

from ..native_evidence import load, require
from ..contained_process import inspect
from ..n1_protocol_robustness import _write
from ..recognition_metrics import load_diagnostic_evaluation
from ..reports import render_diagnostic_evaluation_case
from ..stopped_evidence import load_case


class N0LengthFrozenReportTest(unittest.TestCase):
    def test_actual_preset_conditions_all_eight_patterns_and_native_zooms(self):
        from PIL import Image

        controls = Path(os.environ['TIMELEARNER_N0_LENGTH_FROZEN_REPORT_CONTROLS']).resolve(strict=True)
        declaration = load(controls/'declaration.json')
        require(set(declaration) == {'runs'} and set(declaration['runs']) == {'baseline', 'candidate'},
                'n0_length_report_declaration')
        output = Path(os.environ['TMPDIR']).resolve(strict=True)/'n0-length-frozen-gallery'
        output.mkdir(exist_ok=False)
        rows = []
        for role, paths in declaration['runs'].items():
            self.assertEqual(len(paths), 2)
            case = None
            thresholds = []
            for raw in paths:
                source = Path(raw).resolve(strict=True)
                run = load(source/'run-manifest.json')
                require(run['operation'] == 'diagnostic-evaluate' and
                        (run['execution'], run['validity']) == ('completed', 'valid'),
                        'n0_length_report_requires_completed_diagnostic')
                self.assertTrue(inspect(source/'process/contained')['all_processes_closed'])
                actual = run['analysis']['metrics']
                self.assertEqual(actual['validity'], 'valid')
                thresholds.append(actual['effective_threshold'])
                self.assertEqual(len(actual['trials']), 8)
                self.assertTrue(actual['diagnostic_only'])
                self.assertFalse(actual['training_completed'])
                self.assertFalse(actual['training_certificate_present'])
                self.assertIsNone(actual['evaluation_verdict'])
                self.assertEqual(actual['criterion']['anchor'], 'last_stimulus')
                self.assertTrue(actual['criterion']['reject_target_outside_window'])
                stopped = source/'input/source/train_stopped_state.json'
                package = load(stopped)
                if case is None:
                    case = load_case(stopped)
                self.assertEqual(package, case[0])
                model = load(source/'native/model.json')
                self.assertEqual(model, load(source/'native/model-after.json'))
                recognition = (model['source_recognition']
                    if model['kind'] == 'timelearner_diagnostic_threshold_candidate' else model)
                self.assertEqual(recognition['source_solo'], case[0])
                self.assertIsNone(case[0]['certificate'])
                self.assertEqual(case[0]['training_outcome'], 'budget_exhausted')
                _, observations = load_diagnostic_evaluation(source/'native/evaluation.json')
                pairs = sum(len(o['samples'][0]['soma']) for o in observations)
                self.assertGreater(pairs, 0)
                folder = output/source.name
                result = render_diagnostic_evaluation_case(source/'native/evaluation.json',
                    source/'native/model.json', case, folder)
                manifest = load(folder/'manifest.json')
                self.assertEqual(load(folder/'analysis.json'), actual)
                self.assertEqual(manifest['missing_observation_ids'], [])
                self.assertEqual(len(manifest['declared_trials']), 8)
                self.assertTrue(all(t['complete'] and t['sample_count'] > 0
                                    for t in manifest['declared_trials']))
                self.assertEqual(result['trial_soma_pairs'], pairs)
                self.assertEqual(manifest['expected_trial_soma_pairs'], pairs)
                self.assertEqual(len(manifest['figures']), pairs)
                self.assertEqual({f['sample_id'] for f in manifest['figures']},
                                 {t['sample_id'] for t in actual['trials']})
                self.assertFalse(manifest['visual_acceptance_complete'])
                for figure in manifest['figures']:
                    self.assertTrue(any(v['time_view'] == 'overview' for v in figure['views']))
                    self.assertTrue(any(v['time_view'] != 'overview' and
                        v['minimum_native_tick_pixels_on_zoom'] >= 8 for v in figure['views']))
                    for view in figure['views']:
                        self.assertFalse(view['downsampling'])
                        with Image.open(folder/view['files'][0]) as image:
                            self.assertEqual(image.size, (1920, 960))
                        self.assertTrue((folder/view['files'][1]).is_file())
                        self.assertTrue((folder/view['files'][2]).read_bytes().startswith(b'%PDF-'))
                extrema = []
                if actual['effective_threshold'] == 100.:
                    for observation in observations:
                        self.assertTrue(observation['complete'])
                        self.assertEqual(observation['spike_count'], 0)
                        last = max(observation['stimulus_times'])
                        for soma in range(len(observation['samples'][0]['soma'])):
                            selections = dict(global_peak=observation['samples'],
                                before_last=[s for s in observation['samples'] if s['time'] < last],
                                after_last=[s for s in observation['samples'] if s['time'] >= last])
                            peaks = {}
                            for name, samples in selections.items():
                                self.assertTrue(samples)
                                peak = max(samples, key=lambda s: s['soma'][soma])
                                peaks[name] = dict(value=peak['soma'][soma],
                                    time_from_trial_begin=peak['time']-observation['begin'])
                            extrema.append(dict(sample_id=observation['sample_id'], label=observation['label'],
                                soma_index=soma, peaks=peaks,
                                scope='high-threshold waveform only; no spike-threshold certificate'))
                rows.append(dict(role=role, run=source.name, threshold=actual['effective_threshold'],
                    counts=actual['pooled_counts'], trials=8, trial_soma_pairs=pairs,
                    waveform_extrema=extrema,
                    source_stopped_sha256=package['sha256'], scientific_verdict=None))
                _write(output/'progress.json', dict(rows=rows, scientific_verdict=None))
            self.assertEqual(thresholds, [100., .0117])
        _write(output/'index.json', dict(kind='n0_length_frozen_temporal_report', schema_version=1,
            rows=rows, trials=32, native_model_executed=False, scientific_verdict=None,
            visual_acceptance_complete=False))
