"""Descriptive event timing and aligned figures from bound recorded responses.

Source scorer classifications are retained, never manufactured here. This
reader does not attest execution, convergence, causation or a new threshold.
"""
import argparse
import hashlib
import json
from pathlib import Path

from ..native_evidence import equal, number, require
from ..plotting import plotting_runtime, padded_limits


def _read(record, root):
    requested = Path(record['path'])
    if not requested.is_absolute():
        require('..' not in requested.parts, 'response_comparison_relative_source_escape')
        requested = root / requested
    path = requested.resolve(strict=True)
    before = path.stat()
    raw = path.read_bytes()
    after = path.stat()
    require((before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
            and len(raw) == record['bytes']
            and hashlib.sha256(raw).hexdigest() == record['sha256'],
            'response_comparison_source_changed')
    return json.loads(raw)


def read_sources(path):
    path = Path(path).resolve(strict=True)
    specification = json.loads(path.read_bytes())
    require(specification['kind'] == 'timelearner_recorded_response_comparison_sources'
            and specification['schema_version'] == 1
            and 1 <= len(specification['cohorts']) <= 16, 'response_comparison_schema')
    prepared, summaries, names = [], [], set()
    for cohort in specification['cohorts']:
        name = cohort['id']
        require(type(name) is str and name not in names and name
                and all(c.isascii() and (c.isalnum() or c == '-') for c in name),
                'response_comparison_cohort_id')
        names.add(name)
        score_rows = _read(cohort['source_audit'], path.parent)
        for key in cohort['score_rows_path']:
            score_rows = score_rows[key]
        require(type(score_rows) is list, 'response_comparison_source_score_rows')
        source_by_sample = {row['sample_id']: row for row in score_rows}
        require(len(source_by_sample) == len(score_rows), 'response_comparison_source_sample_collision')
        require(2 <= len(cohort['observations']) <= 512, 'response_comparison_inventory')
        threshold = number(cohort['threshold'])
        ids, rows, observations = set(), [], []
        for declared in cohort['observations']:
            o = _read(declared['file'], path.parent)
            require(o['trial_id'] == declared['trial_id'] and o['trial_id'] not in ids,
                    'response_comparison_trial_identity')
            ids.add(o['trial_id'])
            require(o['schema_version'] == 2 and o['kind'] == 'native_recognition_trial'
                    and o['complete'] is True and o['valid'] is True and o['censored'] is False
                    and o['model_before'] == o['model_after'] == cohort['model_revision'],
                    'response_comparison_incomplete_or_changed_model')
            require(o['reset_policy'] == 'reset_per_trial', 'response_comparison_reset_scope')
            response = declared['classification']
            require(o['sample_id'] in source_by_sample and
                    all(source_by_sample[o['sample_id']][k] == o[k]
                        for k in ('sample_id', 'label')) and
                    source_by_sample[o['sample_id']]['classification'] == response,
                    'response_comparison_source_classification_mismatch')
            require(response in ('TP', 'FP', 'FN', 'TN') and o['label'] ==
                    ('target' if response in ('TP', 'FN') else 'foil'),
                    'response_comparison_label')
            samples = o['samples']
            begin, end, frequency = (number(o[k]) for k in ('begin', 'end', 'frequency_hz'))
            require(samples and frequency > 0 and end > begin and equal(o['closed_at'], end),
                    'response_comparison_window')
            channels = len(samples[0]['soma'])
            require(0 < channels <= 256 and len(samples) <= 1000000,
                    'response_comparison_sample_shape')
            for index, sample in enumerate(samples):
                require(equal(number(sample['time']), begin + index / frequency)
                        and len(sample['soma']) == channels, 'response_comparison_sample_grid')
                for value in sample['soma'] + [sample['lt_potential'], sample['lt_output'], sample['stimulus']]:
                    number(value)
            require(equal(samples[-1]['time'], end), 'response_comparison_window_not_covered')
            stimuli, spikes = ([number(v) for v in o[k]] for k in ('stimulus_times', 'spike_times'))
            require(bool(stimuli) and len(spikes) == o['spike_count']
                    and all(begin <= v <= end for v in stimuli + spikes)
                    and all(a < b for a, b in zip(stimuli, stimuli[1:]))
                    and all(a < b for a, b in zip(spikes, spikes[1:])),
                    'response_comparison_events')
            require(response not in ('TP', 'FP') or bool(spikes), 'response_comparison_missing_output')
            require(response != 'TN' or not spikes, 'response_comparison_silent_output_conflict')
            require(len(o['pattern_isi']) == len(stimuli) and
                    all(equal(b-a, number(isi)) for a, b, isi in
                        zip(stimuli, stimuli[1:], o['pattern_isi'][1:])),
                    'response_comparison_input_intervals')
            potentials = [s['lt_potential'] for s in samples]
            peak = max(range(len(potentials)), key=potentials.__getitem__)
            rows.append(dict(trial_id=o['trial_id'], sample_id=o['sample_id'],
                classification=response, pattern_isi=list(o['pattern_isi']),
                samples=len(samples), soma_channels=channels, frequency_hz=frequency,
                stimulus_times_from_first=[v-stimuli[0] for v in stimuli],
                spike_times_from_first=[v-stimuli[0] for v in spikes],
                spike_times_from_last=[v-stimuli[-1] for v in spikes],
                recorded_lt_maximum=potentials[peak],
                recorded_lt_maximum_time_from_last=samples[peak]['time']-stimuli[-1],
                source_observation=dict(declared['file'])))
            observations.append((declared, o))
        counts = {label: sum(row['classification'] == label for row in rows)
                  for label in ('TP', 'FP', 'FN', 'TN')}
        require({row['sample_id'] for row in rows} == set(source_by_sample),
                'response_comparison_incomplete_source_score_set')
        require(counts == cohort['source_counts'], 'response_comparison_source_counts_conflict')
        summaries.append(dict(id=name, title=cohort['title'], model_revision=cohort['model_revision'],
            threshold=threshold, counts=counts, source_audit=cohort['source_audit'], rows=rows))
        prepared.append((cohort, observations))
    return specification, prepared, summaries


def render(source, output):
    specification, prepared, summaries = read_sources(source)
    environment = plotting_runtime()
    import matplotlib.pyplot as plt
    output = Path(output)
    require(not output.exists(), 'response_comparison_fresh_output_required')
    output.mkdir(parents=True)
    figures = []
    with plt.rc_context({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'svg.fonttype': 'none', 'savefig.facecolor': 'white'}):
        for cohort, observations in prepared:
            selected = [(d, o) for d, o in observations if d['classification'] in ('TP', 'FP')]
            require(1 <= len(selected) <= 8, 'response_comparison_positive_selection')
            channels = len(selected[0][1]['samples'][0]['soma'])
            require(all(len(o['samples'][0]['soma']) == channels for _, o in selected),
                    'response_comparison_channel_mismatch')
            limits = []
            for channel in range(channels+1):
                values = [s['soma'][channel] if channel < channels else s['lt_potential']
                          for _, o in selected for s in o['samples']]
                if channel == channels:
                    values.append(cohort['threshold'])
                limits.append((padded_limits(values), padded_limits([0., max(values)])))
            for view in ('full', 'positive', 'last-input-detail'):
                height = 2.1*(channels+1)+1.8
                fig, axes = plt.subplots(channels+1, len(selected), squeeze=False,
                    figsize=(6.5*len(selected), height), dpi=150)
                fig.subplots_adjust(left=.08, right=.98, bottom=.75/height,
                                    top=1.-1.05/height, hspace=.65, wspace=.26)
                try:
                    fig.suptitle(cohort['title']+'\nСиний — потенциал; оранжевые линии — входы; '
                        'красный пунктир — выходы.\nПотенциалы — в условных единицах модели; '
                        'зелёный пунктир — фактический порог только пороговой зоны.', fontsize=12)
                    for column, (declared, o) in enumerate(selected):
                        anchor = o['stimulus_times'][-1] if view == 'last-input-detail' else o['stimulus_times'][0]
                        x = [(s['time']-anchor)*1000 for s in o['samples']]
                        intervals = '; '.join(format(v*1000, '.8g').replace('.', ',') for v in o['pattern_isi'][1:])
                        axes[0, column].set_title(declared['classification']+' · '+intervals+' мс', fontsize=11)
                        for channel in range(channels+1):
                            axis = axes[channel, column]
                            lt = channel == channels
                            values = [s['lt_potential'] if lt else s['soma'][channel] for s in o['samples']]
                            axis.plot(x, values, color='#1757a0', lw=1.3)
                            for value in o['stimulus_times']:
                                axis.axvline((value-anchor)*1000, color='#dc7908', lw=1.2, alpha=.85)
                            for value in o['spike_times']:
                                axis.axvline((value-anchor)*1000, color='#bc282d', ls='--', lw=1.1)
                            if lt:
                                axis.axhline(cohort['threshold'], color='#36823e', ls=':', lw=1)
                            axis.set_ylim(*limits[channel][0 if view == 'full' else 1])
                            axis.set_xlim(((-10., 20.) if view == 'last-input-detail' else (x[0], x[-1])))
                            axis.grid(alpha=.22)
                            axis.set_ylabel(('Пороговая зона' if lt else 'Сома '+str(channel+1))+
                                            '\nПотенциал, усл. ед.')
                            axis.set_xlabel('Время от '+('последнего' if view == 'last-input-detail' else 'первого')+' входа, мс')
                    for extension in ('png', 'svg'):
                        p = output/(cohort['id']+'-'+view+'.'+extension)
                        fig.savefig(p)
                        figures.append(dict(name=p.name, bytes=p.stat().st_size,
                            sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
                finally:
                    plt.close(fig)
    result = dict(kind='timelearner_recorded_response_descriptive_comparison', schema_version=1,
        source=dict(path=str(Path(source)), sha256=hashlib.sha256(Path(source).read_bytes()).hexdigest()),
        plotting_environment=environment, cohorts=summaries, figures=figures,
        events_source='actual recorded LT event histories, not threshold crossings inferred from samples',
        waveform_scope='after-children potential at the actually executed threshold; includes output feedback',
        classification_recomputed=False, new_native_execution=False, threshold_selected=False,
        training_certificate_created=False, scientific_verdict=None, visual_review_complete=False)
    (output/'comparison.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args=parser.parse_args()
    render(args.sources, args.output)


if __name__ == '__main__':
    main()
