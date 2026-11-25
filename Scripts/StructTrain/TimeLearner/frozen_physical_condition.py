"""Condition fingerprints for frozen physical trial matrices and their cases.

The default serialization preserves the original Linux followup declarations.
This module has no worker, platform or component-scheduler side effects.
"""
from .native_evidence import number, require

GIB = 1024**3


def condition(job, design, runtime, wall_seconds, *, index=None, memory_bytes=8*GIB):
    from .condition import ConditionSpec, artifact
    from .runtime import runtime_content_identity
    import math
    require(type(memory_bytes) is int and 32*1024**2 <= memory_bytes <= 64*GIB,
            'frozen_physical_condition_memory_budget')
    selected = job['trials'] if index is None else [job['trials'][index]]
    model = job['source_model_data']; frequency = model['configuration']['model']['frequency_hz']
    trials = [{k:v for k,v in t.items() if k not in ('run_id', 'trial_id')} for t in selected]
    presentation = design if index is None else dict(protocol_id=design['protocol_id'],
        reset_policy='reset_per_trial', time_frame='relative_to_actual_first_input')
    payloads = dict(algorithm=dict(operation='physical-model-evaluate', implementation_id=job['implementation_id'],
        native_runtime_content=runtime_content_identity(runtime)), model_spec=model['configuration']['model'],
        storage_profiles=dict(effective_graph_sha256=model['model_revision']),
        initial_state=dict(frozen_recognition_graph=model['model_revision'], dynamic_checkpoint=False),
        training_plan=dict(performed=False), input_data=dict(trials=trials), presentation_protocol=presentation,
        # DATA1/2 carry their native threshold in model metadata. DATA3 adds
        # a top-level candidate field; it is not part of the base DATA wire.
        calibration_spec=dict(performed=False,
                              fixed_threshold=number(model['neuron']['metadata']['calibration']['threshold']),
                              selected_on_previous_eight_pattern_matrix=True),
        evaluation_spec=dict(criterion=job['criterion'], coverage_policy=job['coverage_policy'],
                             new_positive_class_assessed=False),
        execution_policy=dict(maximum_model_ticks=sum(math.ceil(t['duration']*frequency)+4 for t in selected),
                              native_memory_bytes=memory_bytes, native_wall_seconds=wall_seconds),
        randomness_spec=dict(random_factors=[], independent_stochastic_repetitions=False))
    artifacts = {k:artifact(k,v) for k,v in payloads.items()}
    spec = ConditionSpec(controller_version=2, amplitude_goal='captured_per_input',
                         **{k:v['sha256'] for k,v in artifacts.items()})
    require(ConditionSpec.loads(spec.dumps()) == spec, 'linux_frozen_followups_condition_roundtrip')
    spec.resolve({v['sha256']:v for v in artifacts.values()})
    result = dict(condition=spec.to_object(), condition_fingerprint=spec.fingerprint,
                  artifacts={v['sha256']:v for v in artifacts.values()},
                  descriptor_integrity_only=True, scientific_verdict=None)
    if index is None:
        result.update(condition_scope='matrix', case_conditions={t['sample_id']:condition(
            job, design, runtime, wall_seconds, index=i, memory_bytes=memory_bytes)
            for i,t in enumerate(job['trials'])})
    return result
