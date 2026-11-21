"""Read the recorded physical reset/preserve control; never certify training.

The four fixtures retain complete recognition observations, but their envelope
contains model digests rather than the complete physical models. Observation
consistency and the measured reset effect are checked here. Physical graph,
scheduler and child readback remain the responsibility of the original native
test and its independently retained execution evidence.
"""
from pathlib import Path

from .native_evidence import equal, load, number, require
from .recognition_trial_evidence import _TrialModel, _audit_recognition_observation
from .runtime import file_record


FIELDS = {'kind', 'schema_version', 'frequency_hz', 'model_data_sha256',
          'model_revision', 'observations', 'preserved_first_sample_difference',
          'new_training_performed', 'production_continuous_wrapper_verified',
          'scientific_verdict'}


def analyze_fixture(value, *, branch, frequency):
    require(type(branch) is bool and type(frequency) is int and frequency in (2000, 20000),
            'continuity_fixture_scope')
    require(type(value) is dict and set(value) == FIELDS and
            value['kind'] == 'timelearner_physical_dynamics_continuity_fixture' and
            type(value['schema_version']) is int and value['schema_version'] == 1 and
            number(value['frequency_hz']) == frequency and
            value['new_training_performed'] is False and
            value['production_continuous_wrapper_verified'] is False and
            value['scientific_verdict'] is None, 'continuity_fixture_schema')
    for name in ('model_revision', 'model_data_sha256'):
        digest = value[name]
        require(type(digest) is str and len(digest) == 64 and
                all(c in '0123456789abcdef' for c in digest), 'continuity_fixture_model_digest')
    # Explicitly scoped to the native fixture's known ordinary LTZone. This is
    # a protocol projection, not a physical-model or storage-image audit.
    model = _TrialModel(value['model_revision'], 2, branch, frequency,
                        '$.LTZone', ('NPulseLTZoneThreshold',))
    pairs = value['observations']
    require(type(pairs) is list and len(pairs) == 2, 'continuity_fixture_pair_count')
    samples = frequency*91//1000 + 5
    for index, pair in enumerate(pairs):
        require(type(pair) is dict and set(pair) == {'reset', 'preserve'}, 'continuity_fixture_pair')
        for role in ('reset', 'preserve'):
            o = pair[role]
            audit = _audit_recognition_observation(o, model)
            policy = ('preserve_neuron_dynamics' if index == 1 and role == 'preserve'
                      else 'reset_per_trial')
            require(o['schema_version'] == 2 and o['reset_policy'] == policy and
                    o['run_id'] == role and o['trial_id'] == role+'/'+str(index) and
                    o['sample_id'] == 'target' and o['label'] == 'target' and
                    o['pattern_isi'] == [.01, .08] and audit['valid_observation'] and
                    audit['complete'] and not o['censored'] and len(o['samples']) == samples,
                    'continuity_fixture_trial_contract')
        require(pair['reset']['begin'] == pair['preserve']['begin'] and
                pair['reset']['end'] == pair['preserve']['end'], 'continuity_fixture_unmatched_clocks')
    first, second = pairs
    require(first['reset']['samples'] == first['preserve']['samples'],
            'continuity_fixture_first_responses_differ')
    baseline = first['reset']['samples'][0]['soma']
    tail = first['reset']['samples'][-1]['soma']
    restored = second['reset']['samples'][0]['soma']
    retained = second['preserve']['samples'][0]['soma']
    require(restored == baseline and
            equal(second['reset']['begin'], first['reset']['end']+1/frequency),
            'continuity_fixture_reset_or_boundary_changed')
    tail_delta = max(abs(a-b) for a,b in zip(tail, baseline))
    preserve_delta = max(abs(a-b) for a,b in zip(retained, baseline))
    require(tail_delta > 1e-6 and preserve_delta > 1e-6 and
            equal(number(value['preserved_first_sample_difference']), preserve_delta),
            'continuity_fixture_residual_not_confirmed')
    return dict(kind='timelearner_physical_continuity_readback', schema_version=1,
        topology='Branch' if branch else 'Classic', frequency_hz=frequency,
        model_revision=value['model_revision'], model_data_sha256=value['model_data_sha256'],
        complete_observations=4, samples_per_observation=samples,
        first_responses_equal=True, baseline=baseline, reset_second_baseline=restored,
        preserved_second_baseline=retained, first_tail_difference=tail_delta,
        preserved_first_sample_difference=preserve_delta,
        recorded_events=[dict(trial_id=o['trial_id'], reset_policy=o['reset_policy'],
            stimulus_times=o['stimulus_times'], spike_times=o['spike_times'],
            spike_count=o['spike_count'],
            spikes_before_first_stimulus=sum(t < o['stimulus_times'][0] for t in o['spike_times']))
            for pair in pairs for o in pair.values()],
        recorded_observation_protocol_verified=True, effective_model_audited=False,
        original_scheduler_execution_reverified=False, new_native_execution=False,
        production_continuous_wrapper_verified=False, scientific_verdict=None)


def read_fixture(path):
    path = Path(path)
    parts = path.stem.split('-')
    require(len(parts) == 4 and parts[:2] == ['physical', 'continuity'] and
            parts[2] in ('Classic', 'Branch') and parts[3] in ('2000', '20000'),
            'continuity_fixture_filename')
    value = load(path)
    result = analyze_fixture(value, branch=parts[2] == 'Branch', frequency=int(parts[3]))
    return value, dict(result, source=file_record(path))


def render_fixture(path, output):
    value, result = read_fixture(path)
    from .plotting import padded_limits, plotting_runtime
    runtime = plotting_runtime()
    output = Path(output)
    require(not output.exists(), 'continuity_report_fresh_output_required')
    output.mkdir(parents=True)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    pairs = value['observations']; channels = len(result['baseline'])
    colors = ('#245dc1', '#853faa')
    with plt.rc_context({'font.size': 13, 'axes.titlesize': 13, 'axes.labelsize': 12}):
        fig, axes = plt.subplots(3, 1, figsize=(8.2, 9.2), constrained_layout=True)
        title = 'Общий кабель' if result['topology'] == 'Branch' else 'Независимые пути'
        fig.suptitle('Сброс и сохранение физической динамики\n'+title+
                     '; '+str(result['frequency_hz'])+' Гц; M=2\n'+
                     'Две короткие пробы, без обучения и оценки классификации', fontsize=13)
        all_values = [x for pair in pairs for o in pair.values() for s in o['samples'] for x in s['soma']]
        limits = padded_limits(all_values)
        for index, ax in enumerate(axes[:2]):
            for role, color, style in (('reset', colors[0], '-'), ('preserve', colors[1], '--')):
                o = pairs[index][role]; times = [s['time']-o['begin'] for s in o['samples']]
                for channel in range(channels):
                    name = (('Экземпляр 1' if role == 'reset' else 'Экземпляр 2') if index == 0
                            else ('Сброс' if role == 'reset' else 'Сохранение'))+'; сома '+str(channel+1)
                    ax.plot(times, [s['soma'][channel] for s in o['samples']], color=color,
                            linestyle=style, linewidth=1.5, alpha=1-channel*.25, label=name)
                for j,t in enumerate(o['spike_times']):
                    ax.axvline(t-o['begin'], color=color, linestyle=':', linewidth=1,
                        alpha=.6, label=('Выходные события; '+('экз. 1' if role == 'reset' else 'экз. 2')) if j == 0 else None)
            for t in pairs[index]['reset']['stimulus_times']:
                ax.axvline(t-pairs[index]['reset']['begin'], color='#df7900', linewidth=1.1,
                           label='Входной импульс' if t == pairs[index]['reset']['stimulus_times'][0] else None)
            ax.set_title('Первая проба: оба экземпляра сброшены' if index == 0 else
                         'Вторая проба: различная политика сброса')
            ax.set_ylim(*limits); ax.set_ylabel('Потенциал сомы,\nусловные единицы'); ax.grid(alpha=.25)
            ax.legend(fontsize=9, loc='lower right', ncol=2)
        left, right = pairs[1]['reset'], pairs[1]['preserve']
        times = [s['time']-left['begin'] for s in left['samples']]
        for channel in range(channels):
            axes[2].plot(times, [a['soma'][channel]-b['soma'][channel]
                for a,b in zip(right['samples'], left['samples'])], linewidth=1.5,
                color=('#245dc1', '#008c80')[channel], label='Сома '+str(channel+1))
        for t in left['stimulus_times']: axes[2].axvline(t-left['begin'], color='#df7900', linewidth=1.1)
        for o,color in ((left,colors[0]),(right,colors[1])):
            for t in o['spike_times']: axes[2].axvline(t-o['begin'], color=color, linestyle=':', linewidth=1, alpha=.6)
        axes[2].set_title('Вторая проба: сохранение минус сброс');axes[2].set_ylabel('Разность потенциалов,\nусловные единицы')
        axes[2].legend(fontsize=10,loc='lower right');axes[2].grid(alpha=.25)
        for ax in axes:
            ax.set_xlim(0, left['end']-left['begin']);ax.set_xlabel('Время от начала пробы, с')
        for suffix in ('png', 'svg'): fig.savefig(output/('continuity.'+suffix), dpi=180)
        plt.close(fig)
    from .native_calibration_worker import _write
    manifest = dict(result, plotting_runtime=runtime, full_samples_rendered=True,
        observation_scope='two_short_closed_trials_not_full_pattern_recognition',
        input_markers='actual stimulus times; vertical markers are not potential amplitudes',
        output_markers='actual recorded LT event times; dotted blue and purple by physical owner',
        artifacts=[file_record(output/('continuity.'+s)) for s in ('png', 'svg')])
    _write(output/'manifest.json', manifest)
    return manifest
