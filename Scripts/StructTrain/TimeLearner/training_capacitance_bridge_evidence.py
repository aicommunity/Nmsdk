"""Audit actual native bridge snapshots; this is not a training certificate."""
import re

from .capacitance_evidence import audit_capacitance_state
from .model_identity import canonical_model_sha256
from .native_evidence import EvidenceError, number, require


PHASES = ('unbound', 'captured', 'ordinary_growth', 'joint_shrink',
          'rejections_preserve_model', 'joint_growth')


def _audit(record):
    require(type(record) is dict and set(record) == {
        'kind', 'schema_version', 'branch', 'normalization', 'phases', 'scientific_verdict'}
        and record['kind'] == 'native_training_capacitance_bridge'
        and type(record['schema_version']) is int and record['schema_version'] == 1,
        'unknown_training_capacitance_bridge_schema')
    require(type(record['branch']) is bool and type(record['normalization']) is int
            and record['normalization'] in (0, 1) and record['scientific_verdict'] is None,
            'invalid_training_capacitance_bridge_metadata')
    frames = record['phases']
    require(type(frames) is list and len(frames) == len(PHASES)
            and all(type(f) is dict for f in frames)
            and [f.get('phase') for f in frames] == list(PHASES),
            'incomplete_training_capacitance_bridge_phases')
    audits, prior_baseline, previous_scales = [], None, None
    inventory_fields = ('channels', 'channel_classes', 'channel_physics', 'channel_origins')
    for frame in frames:
        require(set(frame) == {'phase', 'native_state', 'controller_parameters', 'model', 'storage_images'},
                'unknown_training_capacitance_bridge_frame')
        identity = frame['model']
        require(type(identity) is dict and identity['valid'] is True and not identity['diagnostics']
                and identity['sha256'] == canonical_model_sha256(identity['model']),
                'invalid_training_capacitance_bridge_model')
        state, typed = frame['native_state'], frame['controller_parameters']
        if frame['phase'] == 'unbound':
            require(state == {} and typed is None, 'fabricated_unbound_training_capacitance')
            continue
        require(type(state) is dict and state and type(typed) is dict,
                'missing_training_capacitance_bridge_state')
        baseline = state['baseline']
        # Actual registry snapshots are captured separately by the native
        # producer, including images whose last physical consumer was removed.
        audits.append(audit_capacitance_state(state, baseline['model_spec'], identity, frame['storage_images']))
        origin = canonical_model_sha256({
            'kind': 'timelearner_training_capacitance_origin', 'schema_version': 1,
            'capture_model_revision': baseline['model_revision'], 'model_spec': baseline['model_spec'],
            'storage_images_sha256': baseline['storage_images_sha256']})
        require(set(typed) == {'origin', 'maximum_relative_change', 'membrane_scales'}
                and typed['origin'] == origin, 'training_capacitance_bridge_origin_mismatch')
        limit = number(typed['maximum_relative_change'])
        require(limit == number(state['maximum_relative_change']), 'training_capacitance_bridge_policy_mismatch')
        scales = dict(state['membrane_scales'])
        scales.update(state.get('dormant_membrane_scales', {}))
        for path in baseline['channels']:
            membrane = path.split('.', 1)[0]
            if re.fullmatch(r'Dendrite[1-9][0-9]*_[1-9][0-9]*', membrane):
                scales.setdefault(membrane, 1.)
        require(type(typed['membrane_scales']) is dict and typed['membrane_scales'] == scales,
                'training_capacitance_bridge_scale_mismatch')
        for value in typed['membrane_scales'].values():
            require(number(value) > 0 and 1-limit <= value <= 1+limit,
                    'invalid_training_capacitance_bridge_scale')
        if prior_baseline is not None:
            require({k: v for k, v in baseline.items() if k not in (*inventory_fields, 'sha256')}
                    == {k: v for k, v in prior_baseline.items() if k not in (*inventory_fields, 'sha256')},
                    'training_capacitance_bridge_baseline_recaptured')
            for field in inventory_fields:
                require(all(baseline[field].get(p) == v for p, v in prior_baseline[field].items()),
                        'training_capacitance_bridge_witness_lost')
            require(set(previous_scales) <= set(scales), 'training_capacitance_bridge_history_lost')
        prior_baseline, previous_scales = baseline, scales
    before, after = frames[3], frames[4]
    require(before['model'] == after['model'] and before['native_state'] == after['native_state']
            and before['controller_parameters'] == after['controller_parameters'],
            'training_capacitance_bridge_rejection_changed_model')
    require(frames[1]['native_state']['baseline']['sha256'] != frames[2]['native_state']['baseline']['sha256'],
            'training_capacitance_bridge_growth_not_witnessed')
    return {'kind': 'training_capacitance_bridge_audit', 'schema_version': 1, 'consistent': True,
            'bound_phases': len(audits), 'branch': record['branch'], 'normalization': record['normalization'],
            'effective_channels_by_phase': [a['effective_channels'] for a in audits],
            'native_import_verified': False, 'probe_observations_verified': False,
            'scientific_verdict': None}


def audit_training_capacitance_bridge(record):
    try:
        return _audit(record)
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, OverflowError) as error:
        raise EvidenceError('malformed_training_capacitance_bridge:'+str(error)) from error
