"""Read-only comparison of two actual frozen-profile cold N1 executions.

Selection is declared before outcomes: anchor reference, best joint-residual
candidate per measured input, first rejected search group, last recorded group.
Complete histories and negative/setup outcomes remain in comparison metadata.
"""
from copy import deepcopy
import hashlib
import html
import math
import re
import os
from pathlib import Path
import unittest
from ..composite_training_temporal import render
from ..native_calibration_worker import _write
from ..native_evidence import load,require
from ..uniform_profile_physics import audit_uniform_profile


def comparable_configuration(configuration):
    c=deepcopy(configuration);c.pop('run_id');c['model'].pop('neuron_class')
    for p in c['composite_measurement']['candidate_window_policy']['inputs']:
        require(p['hard_first_frame']==0 and p['hard_last_frame']==3600 and
                p['maximum_window_frames']==3601,'uniform_report_not_full_window_domain')
        p.pop('base_left_guard_frames');p.pop('base_right_guard_frames')
    return c


class UniformProfileTrainingReportTest(unittest.TestCase):
    def test_actual_pair_keeps_full_history_and_readable_assigned_peak_traces(self):
        controls=Path(os.environ['TIMELEARNER_PROFILE_PAIR_REPORT_CONTROLS']).resolve(strict=True)
        declaration=load(controls/'declaration.json')
        legacy=set(declaration)=={'stock','fast'}
        if legacy:
            cases=declaration
            factor='C and DissociationTC together; no separate C causal claim'
            walls=None
        else:
            self.assertEqual(set(declaration),{'cases','comparison_factor','wall_seconds'})
            cases=declaration['cases'];factor=declaration['comparison_factor'];walls=declaration['wall_seconds']
            self.assertIsInstance(factor,str);self.assertTrue(factor.strip())
            self.assertIsInstance(cases,dict);self.assertIsInstance(walls,dict)
            self.assertTrue(all(type(w) in (int,float) and math.isfinite(w) and w>0 for w in walls.values()))
            self.assertGreaterEqual(len(cases),2);self.assertLessEqual(len(cases),8)
            self.assertEqual(set(walls),set(cases))
            self.assertTrue(all(re.fullmatch(r'[A-Za-z0-9_-]+',role) for role in cases))
        output=Path(os.environ['TMPDIR'])/'uniform-profile-N1-training-gallery'
        output.mkdir(exist_ok=False)
        rows={};configurations={}
        for role,path in cases.items():
            native=Path(path).resolve(strict=True)
            paths=[native/n for n in ('train_learned_state.json','train_stopped_state.json') if (native/n).is_file()]
            self.assertEqual(len(paths),1)
            state_path=paths[0];summary_path=state_path.with_name(state_path.name.replace('_state.','_summary.'))
            summary=load(summary_path);package=load(state_path)
            checked=comparable_configuration(package['configuration'])
            if legacy:
                configurations[role]=checked
            else:
                # New comparisons keep class and guard coordinates exact.
                # The only removed factor is explicitly declared for every case.
                checked=deepcopy(package['configuration']);checked.pop('run_id')
                self.assertEqual(checked.pop('maximum_wall_seconds'),walls[role])
                configurations[role]=checked
            records=package['measurement_archive']['records']
            ordinals={r['group_id']:i for i,r in enumerate(records,1)}
            selected=[ordinals[g] for g in summary['reference_group_ids'][-1:]]
            candidates=summary['candidates'];tol=summary['tolerances']
            def rank(c):
                timing=max(abs(c['timing_low']),abs(c['timing_high']))/tol['sync']
                amplitude=abs(c['amplitude_residual'])/tol['amplitude_absolute']
                return (not c['within_timing'],not c['within_amplitude'],timing+amplitude)
            best={}
            for i in sorted({c['input_index'] for c in candidates}):
                c=min((c for c in candidates if c['input_index']==i),key=rank)
                best[str(i)]=c;selected.append(ordinals[c['measurement_group_id']])
            rejected=[r for r in records if r['purpose']!='reference' and r['measurement'] is None]
            if rejected:selected.append(ordinals[rejected[0]['group_id']])
            if records:selected.append(len(records))
            selected=list(dict.fromkeys(selected));self.assertTrue(selected)
            frames=[r['method_specification']['candidate_frame'] for r in records
                    if r['purpose']!='reference' and r['method_specification'] is not None]
            self.assertTrue(all(f==dict(first_frame=0,last_frame=3600) for f in frames))
            facts=dict(outcome=summary['outcome'],reason=summary['reason'],certificate=summary['certificate'],
                reference_complete=summary['reference_complete'],references=summary['references'],
                actual_parameters=summary['actual_parameters'],accepted_parameters=summary['accepted_parameters'],
                search_probes=summary['search_probes'],applied_edits=summary['applied_edits'],
                composite_counters=summary['composite_counters'],selected_measured_by_input=best,
                report_selection_rank='outside timing, outside amplitude, normalized sum, first observed tie; controller edit cost not replayed',
                all_scalar_candidates=candidates,rejections=summary['rejections'],
                resistance_domains=summary['resistance_domains'],selected_groups=selected,
                terminal_has_consumed_scalar=any(c['full_parameters']==summary['actual_parameters'] for c in candidates),
                classification_assessed=False,scientific_verdict=None)
            bindings=dict(package_sha256=hashlib.sha256(state_path.read_bytes()).hexdigest(),
                          summary_sha256=hashlib.sha256(summary_path.read_bytes()).hexdigest())
            initial=package['measurement_archive']['source_binding']['initial_model']
            facts['fixed_physics_recheck']=audit_uniform_profile(initial,package['neuron']['graph']['identity'])
            del package,records
            report=render(native,output/role,selected,native_window_zooms=True,allow_incomplete_groups=True)
            self.assertFalse(report['downsampling']);self.assertFalse(report['visual_acceptance_complete'])
            for figure in report['figures']:
                if figure['view'].endswith('-native'):
                    self.assertGreaterEqual(figure['minimum_native_tick_pixels'],8.)
            rows[role]=dict(facts=facts,bindings=bindings,report=report)
        common=next(iter(configurations.values()))
        self.assertTrue(all(value==common for value in configurations.values()))
        _write(output/'comparison.json',dict(kind='timelearner_uniform_profile_cold_N1_comparison',
            schema_version=1 if legacy else 2,common_configuration=common,rows=rows,
            profile_factor=factor,**({} if legacy else dict(declared_wall_seconds=walls)),
            full_observation_domain=[0,3600],classification_assessed=False,scientific_verdict=None))
        links=''.join('<li><a href="'+html.escape(role,quote=True)+'/index.html">'+html.escape(role)+'</a></li>' for role in cases)
        (output/'index.html').write_text('<!doctype html><meta charset="utf-8"><h1>Cold Branch N1: actual immutable profiles</h1><p>'+html.escape(factor)+'</p><p>Full histories in comparison.json. Training diagnostics, no classifier verdict.</p><ul>'+links+'</ul>')
