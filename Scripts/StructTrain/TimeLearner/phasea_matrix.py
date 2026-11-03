"""Recover historical Phase A stimuli from exact Git data, never its verdict.

CSV ISIs omit the first stimulus delay. XML supplies all four values; its
MatrixClasses supplies labels. Cross-check both before preparing native probes.
This does not reproduce the historical scheduler or import response metrics.
"""
import csv
import hashlib
import io
import math
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

from .model_identity import canonical_model_sha256 as sha
from .native_evidence import EvidenceError, number, require

REVISION = '1c1464e248f8744e858bd66df0be99e39969fd65'
PREFIX = 'Configs/SpikeSamples/StructTrain/SelectivityPhaseA/EXP00_baseline/Test/'
PARAMETERS = PREFIX+'Parameters_00.xml'
OBSERVATIONS = PREFIX+'SelectivityLog/results.csv'


def _source(path, raw):
    return {'path': path, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
            'blob_sha1': hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()}


def extract(parameters, observations, revision):
    require(type(revision) is str and re.fullmatch('[0-9a-f]{40}', revision), 'phasea_matrix_exact_revision_required')
    try:
        root = ET.fromstring(parameters)
        datasets = root.findall('.//DatasetMatrix/Parameters')
        require(len(datasets) == 1, 'phasea_matrix_dataset_not_unique')
        data = datasets[0]
        def field(name):
            values = data.findall(name)
            require(len(values) == 1 and values[0].text is not None, 'phasea_matrix_property_missing:'+name)
            return values[0]
        require(field('NumSamples').text.strip() == '8' and field('NumFeatures').text.strip() == '1' and
                field('MaxSpikesPerFeature').text.strip() == '4', 'phasea_matrix_unsupported_dimensions')
        def matrix(name, kind, rows, columns):
            node = field(name)
            require(node.get('Type') == kind and node.get('Rows') == str(rows) and node.get('Cols') == str(columns),
                    'phasea_matrix_property_shape:'+name)
            tokens = node.text.split()
            require(len(tokens) == rows*columns, 'phasea_matrix_truncated_property:'+name)
            values = [float(v) for v in tokens]
            require(all(math.isfinite(v) for v in values), 'phasea_matrix_nonfinite_property:'+name)
            return values
        values = matrix('MatrixData', 'MDMatrix<d>', 32, 1)
        classes = matrix('MatrixClasses', 'MDMatrix<i>', 1, 8)
        require(all(v in (0., 1.) for v in classes) and classes.count(1.) == 1, 'phasea_matrix_invalid_labels')
        patterns = [values[i:i+4] for i in range(0, 32, 4)]
        require(all(p[0] >= 0 and all(v > 0 for v in p[1:]) for p in patterns), 'phasea_matrix_invalid_isi')
        targets = root.findall('.//TrainingPattern')
        require(len(targets) == 1 and targets[0].get('Rows') == '4' and targets[0].get('Cols') == '1',
                'phasea_matrix_training_target_missing')
        require([float(v) for v in targets[0].text.split()] == patterns[classes.index(1.)],
                'phasea_matrix_training_target_changed')
        reader = csv.DictReader(io.StringIO(observations.decode('utf-8-sig')))
        columns = reader.fieldnames
        require(columns is not None and len(columns) == len(set(columns)) and
                {'trial', 'target_class', 'stim_count', 'isi0', 'isi1', 'isi2', 'isi3'} <= set(columns),
                'phasea_matrix_csv_schema')
        rows = list(reader)
        require(len(rows) == 8 and all(None not in row and all(v is not None for v in row.values()) for row in rows),
                'phasea_matrix_csv_incomplete')
        by_id = {}
        for row in rows:
            require(row['trial'] in [str(i) for i in range(8)] and row['trial'] not in by_id,
                    'phasea_matrix_csv_duplicate_or_unknown_id')
            by_id[row['trial']] = row
        for i, pattern in enumerate(patterns):
            row = by_id[str(i)]
            require(row['target_class'] == str(int(classes[i])) and row['stim_count'] == '4' and
                    [float(row['isi'+str(k)]) for k in range(3)] == pattern[1:] and not row['isi3'].strip(),
                    'phasea_matrix_csv_xml_disagreement')
        presentation = {key: field(key).text.strip() for key in
                        ('Delay', 'AdvanceSampleAfterBurst', 'LoopSamples', 'StateGeneration')}
        require(math.isfinite(float(presentation['Delay'])) and float(presentation['Delay']) >= 0 and
                all(presentation[k] in ('0', '1') for k in ('AdvanceSampleAfterBurst', 'LoopSamples')) and
                presentation['StateGeneration'].isdigit(), 'phasea_matrix_invalid_historical_properties')
    except (ET.ParseError, UnicodeError, ValueError, TypeError, AttributeError, KeyError) as error:
        if isinstance(error, EvidenceError):
            raise
        raise EvidenceError('phasea_matrix_malformed_source:'+str(error)) from error
    records = [{'sample_id': 'phasea-row-'+str(i), 'source_trial_id': str(i),
                'label': 'target' if classes[i] else 'foil', 'pattern_isi': p, 'pattern_hash': sha(p)}
               for i, p in enumerate(patterns)]
    require(len({r['pattern_hash'] for r in records}) == 8, 'phasea_matrix_duplicate_pattern')
    return {'kind': 'timelearner_phasea_pattern_matrix', 'schema_version': 1, 'repository': 'Bin',
            'revision': revision, 'sources': [_source(PARAMETERS, parameters), _source(OBSERVATIONS, observations)],
            'patterns': records, 'pattern_matrix_sha256': sha(records),
            'historical_dataset_properties': presentation, 'historical_presentation_reproduced': False,
            'response_metrics_imported': False, 'scientific_verdict': None}


def from_git(repository, revision=REVISION):
    require(type(revision) is str and re.fullmatch('[0-9a-f]{40}', revision), 'phasea_matrix_exact_revision_required')
    try:
        raw = [subprocess.check_output(['git', '-C', str(Path(repository).resolve(strict=True)),
                                       'show', revision+':'+path], stderr=subprocess.PIPE)
               for path in (PARAMETERS, OBSERVATIONS)]
    except subprocess.CalledProcessError as error:
        raise EvidenceError('phasea_matrix_git_source_unavailable') from error
    return extract(*raw, revision)


def trial_design(matrix, target, run_id, *, frequency=2000, duration=2., reset_policy='reset_per_trial', rotations=8):
    require(type(matrix) is dict and set(matrix) == {'kind', 'schema_version', 'repository', 'revision', 'sources',
            'patterns', 'pattern_matrix_sha256', 'historical_dataset_properties', 'historical_presentation_reproduced',
            'response_metrics_imported', 'scientific_verdict'} and
            matrix['kind'] == 'timelearner_phasea_pattern_matrix' and type(matrix['schema_version']) is int and
            matrix['schema_version'] == 1 and matrix['pattern_matrix_sha256'] == sha(matrix['patterns']) and
            matrix['historical_presentation_reproduced'] is False and matrix['response_metrics_imported'] is False and
            matrix['scientific_verdict'] is None, 'phasea_matrix_invalid_artifact')
    require(matrix['repository'] == 'Bin' and type(matrix['revision']) is str and
            re.fullmatch('[0-9a-f]{40}', matrix['revision']) and type(matrix['sources']) is list and
            len(matrix['sources']) == 2 and all(type(r) is dict and set(r) == {'path', 'bytes', 'sha256', 'blob_sha1'}
            and type(r['bytes']) is int and r['bytes'] > 0 and type(r['sha256']) is str and
            re.fullmatch('[0-9a-f]{64}', r['sha256']) and type(r['blob_sha1']) is str and
            re.fullmatch('[0-9a-f]{40}', r['blob_sha1']) for r in matrix['sources']) and
            {r['path'] for r in matrix['sources']} == {PARAMETERS, OBSERVATIONS}, 'phasea_matrix_source_binding_invalid')
    patterns = matrix['patterns']
    require(type(patterns) is list and all(type(p) is dict and set(p) ==
            {'sample_id', 'source_trial_id', 'label', 'pattern_isi', 'pattern_hash'} for p in patterns),
            'phasea_matrix_unknown_pattern_fields')
    require({p['source_trial_id'] for p in patterns} == {str(i) for i in range(8)} and
            all(p['sample_id'] == 'phasea-row-'+p['source_trial_id'] for p in patterns) and
            len(patterns) == len({p['sample_id'] for p in patterns}) == len({p['pattern_hash'] for p in patterns}) == 8 and
            sum(p['label'] == 'target' for p in patterns) == 1 and
            all(p['label'] in ('target', 'foil') and len(p['pattern_isi']) == 4 and
                p['pattern_hash'] == sha(p['pattern_isi']) for p in patterns), 'phasea_matrix_invalid_pattern_inventory')
    require(next(p['pattern_isi'] for p in patterns if p['label'] == 'target') == target,
            'phasea_matrix_learned_target_mismatch')
    require(type(run_id) is str and bool(run_id) and type(frequency) is int and frequency > 0 and
            type(rotations) is int and rotations in (1, 8) and
            reset_policy in ('reset_per_trial', 'preserve_neuron_dynamics') and
            all(number(duration) > sum(number(v) for v in p['pattern_isi']) and
                p['pattern_isi'][0] >= 0 and all(v > 0 for v in p['pattern_isi'][1:]) for p in patterns),
            'phasea_matrix_native_protocol_invalid')
    require(math.isfinite(duration*frequency) and duration*frequency <= 10000000-5,
            'phasea_matrix_native_sample_budget_exceeded')
    trials = []
    for rotation in range(rotations):
        for position, pattern in enumerate(patterns[rotation:]+patterns[:rotation]):
            trials.append({'run_id': run_id, 'trial_id': f'{run_id}/rotation-{rotation}/{position}',
                           **{k: pattern[k] for k in ('sample_id', 'label', 'pattern_hash')},
                           'pattern_isi': list(pattern['pattern_isi']),
                           'duration': duration, 'maximum_samples': math.ceil(duration*frequency)+5,
                           'reset_policy': reset_policy, 'record_threshold_potential': True})
    return trials
