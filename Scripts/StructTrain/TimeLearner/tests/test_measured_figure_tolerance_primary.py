"""Render real saved probes; mutations are rejection fixtures, never new science.

Run on a declared server with the verified five-file primary fixture directory.
Every successful PNG/SVG and its exact input bytes remain in the owned output.
"""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import unittest

from ..native_evidence import EvidenceError
from ..publications.plot_algorithm_measurements import render


class MeasuredFigureTolerancePrimary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.primary = Path(os.environ['TIMELEARNER_MEASURED_TOLERANCE_PRIMARY']).resolve(strict=True)
        cls.output = Path(os.environ['TIMELEARNER_MEASURED_TOLERANCE_OUTPUT']).resolve(strict=True)
        cls.original = json.loads((cls.primary/'history.json').read_bytes())
        cls.packet = json.loads((cls.primary/'reference-0.json').read_bytes())
        refs = cls.original['summary']['references']
        if len(refs) != 2 or refs[0]['raw_potential'] == refs[1]['raw_potential']:
            raise RuntimeError('fixture_requires_distinct_actual_per_input_references')
        if refs[0]['trial_id'] != cls.packet['observation']['specification']['trial_id']:
            raise RuntimeError('fixture_reference_packet_does_not_belong_to_history')

    def case(self, suffix=''):
        path = self.output/(self._testMethodName+suffix)
        path.mkdir(exist_ok=False)
        for name in ('history.json', 'reference-0.json', 'reference-0.csv',
                     'reference-1.json', 'reference-1.csv'):
            (path/name).write_bytes((self.primary/name).read_bytes())
        return path

    @staticmethod
    def record(path, name):
        raw = (path/name).read_bytes()
        return dict(path=name, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())

    def specification(self, path, *, version=2, proof=0):
        row = dict(id='measured-search', title='Измеренные кандидаты и исходный допуск',
                   history=self.record(path, 'history.json'), input_index=0)
        if proof is not None:
            row['reference_probe'] = dict(packet=self.record(path, f'reference-{proof}.json'),
                                          trace=self.record(path, f'reference-{proof}.csv'))
        return dict(kind='timelearner_scientific_measurement_figure_sources',
                    schema_version=version, searches=[row])

    def run_render(self, path, specification=None):
        source = path/'sources.json'
        source.write_text(json.dumps(specification or self.specification(path),
                                    ensure_ascii=False, allow_nan=False)+'\n', encoding='utf-8')
        return render(source, path/'figures')['figures'][0]['details']

    def change_history(self, path, change):
        data = deepcopy(self.original)
        change(data['summary'])
        (path/'history.json').write_text(json.dumps(data, allow_nan=True)+'\n', encoding='utf-8')

    def test_legacy_absolute_only_retains_unknown_binding_and_original_tolerance(self):
        path = self.case()
        details = self.run_render(path, self.specification(path, version=1, proof=None))
        self.assertEqual(details['amplitude_tolerance'], 1e-5)
        self.assertEqual(details['tolerance']['reference_binding'], 'unknown_legacy_absolute_only')
        self.assertIsNone(details['tolerance']['reference_raw_potential'])

    def test_actual_reference_supplies_relative_term_in_its_own_units(self):
        path = self.case()
        self.change_history(path, lambda h: h['tolerances'].update(amplitude_relative=.1))
        details = self.run_render(path)
        expected = 1e-5+.1*abs(self.original['summary']['references'][0]['raw_potential'])
        wrong = 1e-5+.1*abs(self.original['summary']['references'][1]['raw_potential'])
        self.assertEqual(details['amplitude_tolerance'], expected)
        self.assertNotEqual(details['amplitude_tolerance'], wrong)
        self.assertEqual(details['tolerance']['reference_binding'], 'audited_native_probe')
        self.assertTrue(details['tolerance']['reference_audit']['valid_observation'])

    def test_reordered_arbitrarily_named_references_preserve_physical_index_binding(self):
        path = self.case()
        def rename(value):
            if isinstance(value, dict):
                return {k: rename(v) for k, v in value.items()}
            if isinstance(value, list):
                return [rename(v) for v in value]
            return {'input0': 'recorded-path-A', 'input1': 'recorded-path-B'}.get(value, value) if isinstance(value, str) else value
        data = rename(deepcopy(self.original))
        data['summary']['references'].reverse()
        data['summary']['tolerances']['amplitude_relative'] = .1
        (path/'history.json').write_text(json.dumps(data)+'\n', encoding='utf-8')
        (path/'reference-0.json').write_text(json.dumps(rename(self.packet))+'\n', encoding='utf-8')
        details = self.run_render(path)
        self.assertEqual(details['tolerance']['reference_input_id'], 'recorded-path-A')
        self.assertEqual(details['amplitude_tolerance'],
                         1e-5+.1*abs(self.original['summary']['references'][0]['raw_potential']))

    def test_foreign_physical_reference_cannot_supply_the_selected_input_tolerance(self):
        path = self.case()
        with self.assertRaisesRegex(EvidenceError, 'measured_search_reference_input_mismatch'):
            self.run_render(path, self.specification(path, proof=1))

    def test_missing_and_duplicate_reference_ids_are_rejected(self):
        for defect in ('missing', 'duplicate'):
            with self.subTest(defect=defect):
                path = self.case('-'+defect)
                def change(history):
                    refs = history['references']
                    if defect == 'missing':
                        refs.pop()
                    else:
                        refs[1]['input_id'] = refs[0]['input_id']
                self.change_history(path, change)
                with self.assertRaises(EvidenceError):
                    self.run_render(path)

    def test_schema2_requires_bound_primary_even_with_absolute_only_tolerance(self):
        path = self.case()
        with self.assertRaisesRegex(EvidenceError, 'measured_search_reference_probe_required'):
            self.run_render(path, self.specification(path, proof=None))

    def test_legacy_unbound_relative_tolerance_is_rejected(self):
        path = self.case()
        self.change_history(path, lambda h: h['tolerances'].update(amplitude_relative=.1))
        with self.assertRaisesRegex(EvidenceError, 'measured_search_reference_probe_required'):
            self.run_render(path, self.specification(path, version=1, proof=None))

    def test_reference_amplitude_must_equal_the_actually_measured_peak(self):
        path = self.case()
        self.change_history(path, lambda h: h['references'][0].update(raw_potential=.1))
        with self.assertRaisesRegex(EvidenceError, 'measured_search_reference_amplitude_mismatch'):
            self.run_render(path)

    def test_trial_revision_and_epoch_cannot_be_borrowed_from_another_reference(self):
        for defect in ('trial_id', 'effective_model_revision', 'reference_model_epoch'):
            with self.subTest(defect=defect):
                path = self.case('-'+defect)
                def change(h):
                    if defect == 'reference_model_epoch':
                        h[defect] += 1
                    else:
                        h['references'][0][defect] = 'foreign'
                self.change_history(path, change)
                with self.assertRaisesRegex(EvidenceError, 'measured_search_reference_context_mismatch'):
                    self.run_render(path)

    def test_nonfinite_and_negative_tolerances_or_reference_levels_are_rejected(self):
        for field, value in (('amplitude_relative', float('nan')),
                             ('amplitude_absolute', float('inf')),
                             ('amplitude_relative', -.1),
                             ('reference', float('nan')),
                             ('reference', float('inf'))):
            with self.subTest(field=field, value=value):
                path = self.case('-'+field+'-'+str(value))
                def change(h):
                    if field == 'reference':
                        h['references'][0]['raw_potential'] = value
                    else:
                        h['tolerances'][field] = value
                self.change_history(path, change)
                with self.assertRaises(EvidenceError):
                    self.run_render(path)

    def test_zero_tolerance_is_exactly_zero_despite_nonzero_display_scale(self):
        path = self.case()
        self.change_history(path, lambda h: h['tolerances'].update(
            amplitude_absolute=0, amplitude_relative=0))
        details = self.run_render(path)
        self.assertEqual(details['amplitude_tolerance'], 0)
        self.assertTrue(details['zero_tolerance_display_scale_only'])
        self.assertLess(details['amplitude_zoom_limits'][0], details['amplitude_zoom_limits'][1])

    def test_primary_trace_hash_change_is_not_silently_accepted(self):
        path = self.case()
        spec = self.specification(path)
        with (path/'reference-0.csv').open('ab') as stream:
            stream.write(b'\n')
        with self.assertRaisesRegex(EvidenceError, 'measured_figure_source_changed'):
            self.run_render(path, spec)

    def test_rebinding_a_corrupted_trace_does_not_bypass_the_actual_probe_auditor(self):
        path = self.case()
        rows = (path/'reference-0.csv').read_text().splitlines()
        cells = rows[1].split(',')
        cells[0] = 'NaN'
        rows[1] = ','.join(cells)
        (path/'reference-0.csv').write_text('\n'.join(rows)+'\n', encoding='utf-8')
        with self.assertRaises(EvidenceError):
            self.run_render(path)


if __name__ == '__main__':
    unittest.main()
