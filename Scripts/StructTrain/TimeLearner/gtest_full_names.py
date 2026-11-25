"""Exact GoogleTest names, including typed and value-parameterized cases.

The single dot separates suite from case; slashes belong to GoogleTest's
instantiation/type/parameter names. They must never be globally replaced.
This module selects tests and audits identity, not scientific observations.
"""
import re

from .native_evidence import require


PART = r'[A-Za-z_][A-Za-z0-9_]*(?:/[A-Za-z0-9_]+)*'
MAXIMUM_FILTER_BYTES = 60*1024


def full_name(suite, case):
    require(type(suite) is str and type(case) is str and
            re.fullmatch(PART, suite) and re.fullmatch(PART, case),
            'invalid_gtest_full_name')
    return suite+'.'+case


def validate_names(names):
    require(type(names) is list and bool(names) and
            all(type(n) is str and n.count('.') == 1 for n in names),
            'invalid_gtest_full_name_inventory')
    for name in names:
        suite, case = name.split('.')
        require(full_name(suite, case) == name, 'invalid_gtest_full_name')
    require(len(names) == len(set(names)), 'duplicate_gtest_full_name')
    return names


def parse_listing(text):
    """Read saved --gtest_list_tests output; reject unknown nonempty lines."""
    require(type(text) is str and 0 < len(text.encode('utf-8')) <= 4*1024**2,
            'invalid_gtest_listing_size')
    suite, names, suites, suite_cases = None, [], set(), 0
    for line in text.splitlines():
        if not line.strip():
            continue
        content = line.split(' #', 1)[0].rstrip()
        if not line.startswith((' ', '\t')):
            require(content.endswith('.') and re.fullmatch(PART, content[:-1]),
                    'unknown_gtest_listing_line')
            require(suite is None or suite_cases > 0, 'empty_gtest_listing_suite')
            suite = content[:-1]
            require(suite not in suites, 'duplicate_gtest_listing_suite')
            suites.add(suite)
            suite_cases = 0
        else:
            require(suite is not None and line.startswith('  ') and
                    re.fullmatch(PART, content.strip()), 'unknown_gtest_listing_case')
            names.append(full_name(suite, content.strip()))
            suite_cases += 1
    require(suite is not None and suite_cases > 0, 'empty_gtest_listing_suite')
    return validate_names(names)


def filter_argument(names):
    validate_names(names)
    argument = '--gtest_filter='+':'.join(names)
    require(len(argument.encode('utf-8')) <= MAXIMUM_FILTER_BYTES,
            'gtest_filter_argument_budget')
    return argument


def partition(names, maximum_cases=32):
    """Finite complete leaves, preserving exact names, order and coverage."""
    validate_names(names)
    require(type(maximum_cases) is int and 1 <= maximum_cases <= 256,
            'invalid_gtest_partition_size')
    leaves, current = [], []
    for name in names:
        filter_argument([name])
        if current and (len(current) == maximum_cases or
                        len(('--gtest_filter='+':'.join([*current, name])).encode('utf-8')) > MAXIMUM_FILTER_BYTES):
            leaves.append(current)
            current = []
        current.append(name)
    if current:
        leaves.append(current)
    require([n for leaf in leaves for n in leaf] == names, 'gtest_partition_lost_cases')
    return leaves
