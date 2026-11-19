"""Explicit schema9 terminal policy, separate from its unchanged math view.

Execution, condition identity and manifests retain the ORIGINAL declaration.
Splitting this envelope is not validation of the underlying configuration or
evidence of an executed restoration. The caller validates the returned base.
"""
from copy import deepcopy

from .native_evidence import count, number, require


def validate_terminal_policy(value):
    require(type(value) is dict and set(value)=={'schema_version','maximum_wall_seconds'},
            'native_terminal_policy_fields')
    require(count(value['schema_version'])==1 and number(value['maximum_wall_seconds'])>0,
            'native_terminal_policy_schema_or_budget')
    return value


def split_terminal_configuration(configuration):
    """Validate wrapper only; return a private base and the declared policy."""
    require(type(configuration) is dict,'terminal_configuration_object')
    if configuration.get('schema_version')!=9:
        require(not {'terminal_base_schema_version','terminal_selection'}.intersection(configuration),
                'unversioned_terminal_configuration')
        return configuration,None
    require(configuration.get('kind')=='timelearner_native_cold_configuration',
            'terminal_configuration_kind')
    require(count(configuration['schema_version'])==9,'terminal_configuration_schema')
    base=count(configuration.get('terminal_base_schema_version'))
    require(1<=base<=8,'terminal_configuration_base_schema')
    policy=validate_terminal_policy(configuration.get('terminal_selection'))
    projected=deepcopy(configuration)
    projected.pop('terminal_base_schema_version');projected.pop('terminal_selection')
    projected['schema_version']=base
    return projected,deepcopy(policy)


def underlying_configuration_schema(configuration):
    base,_=split_terminal_configuration(configuration)
    return count(base.get('schema_version'))
