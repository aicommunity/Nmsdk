"""Illustrate recorded N0 residuals, without replaying or certifying training.

The input is the compact, provenance-bound search projection. Equal command
vectors are presentation groups, not a claim of equal complete physical state.
No native calculation, interpolation, extrapolation or scoring is performed.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path


def project(profile):
    if (profile.get('kind') != 'timelearner_actual_N0_recorded_search_profile' or
            profile.get('schema_version') != 1 or profile.get('normalization') != 'N0'):
        raise ValueError('recorded_count_profile_schema')
    flag = profile.get('terminal_fresh_all_input_verification')
    if flag is not None and type(flag) is not bool:
        raise ValueError('recorded_count_terminal_flag_type')
    rows = profile['candidate_rows']
    if not isinstance(rows, list) or len(rows) != profile['recorded_candidates']:
        raise ValueError('recorded_count_candidate_inventory')
    dimension = len(profile['actual_terminal_parameters'])
    seen = set()
    groups = {}
    for row in rows:
        identity = row['trial_id']
        i, parameters = row['input_index'], row['full_parameters']
        if (type(identity) is not str or not identity or identity in seen or
                type(i) is not int or not 0 <= i < dimension or
                len(parameters) != dimension or parameters[i] != row['parameters'] or
                type(row['within_timing']) is not bool or
                type(row['within_amplitude']) is not bool):
            raise ValueError('recorded_count_candidate_identity')
        seen.add(identity)
        for value in parameters:
            if (set(value) != {'length', 'resistance', 'synapses'} or
                    any(type(value[k]) is not int or value[k] < 1 for k in ('length', 'synapses')) or
                    type(value['resistance']) not in (int, float) or
                    not math.isfinite(value['resistance']) or value['resistance'] <= 0):
                raise ValueError('recorded_count_command_vector')
        for key in ('amplitude_residual', 'timing_low', 'timing_high'):
            if type(row[key]) not in (int, float) or not math.isfinite(row[key]):
                raise ValueError('recorded_count_nonfinite_residual')
        if row['timing_low'] > row['timing_high']:
            raise ValueError('recorded_count_timing_interval')
        if not row['within_timing']:
            continue
        # Include ALL commanded lengths, all resistances and all other counts.
        # Branch preparation can move an earlier attachment when Ns changes.
        key = (i, tuple((p['length'], p['resistance'], None if k == i else p['synapses'])
                        for k, p in enumerate(parameters)))
        groups.setdefault(key, []).append(row)
    contexts = []
    for (i, vector), observations in groups.items():
        contexts.append(dict(input_index=i,
            commanded_lengths=[v[0] for v in vector],
            commanded_resistances=[v[1] for v in vector],
            other_commanded_counts=[v[2] for v in vector],
            rows=observations,
            distinct_measured_counts=sorted({r['parameters']['synapses'] for r in observations})))
    selected = []
    for i in range(dimension):
        options = [c for c in contexts if c['input_index'] == i]
        if options:
            selected.append(max(options, key=lambda c: (
                max(c['distinct_measured_counts']), len(c['distinct_measured_counts']))))
    return dict(kind='timelearner_recorded_count_plot_projection', schema_version=1,
        source_model_revision=profile['actual_terminal_model_revision'],
        original_outcome=profile['outcome'], original_reason=profile['reason'],
        all_timing_ready_command_contexts=contexts, selected_contexts=selected,
        selection='highest measured count, then number of distinct measured counts',
        command_vectors_only=True, full_physical_context_equivalence_attested=False,
        terminal_selection_fresh_all_input_verification=flag,
        terminal_flag_scope='terminal selection; not completeness of historical final measurements',
        historical_final_pass_completeness_assessed=False,
        training_decisions_replayed=False, convergence_reassessed=False,
        interpolation_performed=False, unmeasured_points_invented=False,
        scientific_verdict=None)


def render(source, output):
    source = Path(source).resolve(strict=True)
    raw = source.read_bytes()
    projection = project(json.loads(raw))
    output = Path(output).absolute()
    if output.exists():
        raise ValueError('fresh_recorded_count_figure_directory_required')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    output.mkdir(parents=True)
    files = []
    style = {'font.family': 'DejaVu Sans', 'font.size': 11, 'svg.fonttype': 'none'}
    with plt.rc_context(style):
        for context in projection['selected_contexts']:
            i = context['input_index']
            fig, axis = plt.subplots(figsize=(6.35, 3.6))
            fig.subplots_adjust(left=.16, right=.98, bottom=.19, top=.79)
            rows = context['rows']
            axis.scatter([r['parameters']['synapses'] for r in rows],
                         [r['amplitude_residual'] for r in rows],
                         color='#1756a9', s=35, zorder=3)
            axis.axhline(0, color='#52606d', linewidth=.8)
            axis.grid(alpha=.25)
            axis.set_xlabel('Число синапсов Nₛ')
            axis.set_ylabel('Амплитудная ошибка, усл. ед.')
            axis.set_title('Вход '+str(i)+' · L='+str(context['commanded_lengths'][i])+
                           '\nВременной допуск выполнен', y=1., pad=5)
            axis.set_xticks(context['distinct_measured_counts'])
            axis.ticklabel_format(axis='y', style='sci', scilimits=(-3, 3), useMathText=True)
            for suffix in ('png', 'svg'):
                path = output/('input-'+str(i)+'.'+suffix)
                fig.savefig(path, dpi=220)
                files.append(dict(name=path.name, bytes=path.stat().st_size,
                                  sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
            plt.close(fig)
    projection.update(matplotlib_version=matplotlib.__version__,
        renderer_source=dict(path=str(Path(__file__).resolve()),
            sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),
        source=dict(path=str(source), bytes=len(raw),
                      sha256=hashlib.sha256(raw).hexdigest()), files=files,
                      visual_review_complete=False)
    (output/'projection.json').write_bytes((json.dumps(projection, ensure_ascii=False,
        indent=2, allow_nan=False)+'\n').encode('utf-8'))
    if source.read_bytes() != raw:
        raise ValueError('recorded_count_source_changed')
    return projection


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    result = render(args.source, args.output)
    print(json.dumps(dict(figures=len(result['selected_contexts']),
        source=result['source'], scientific_verdict=None)))


if __name__ == '__main__':
    main()
