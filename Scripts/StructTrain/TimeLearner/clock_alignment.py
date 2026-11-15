"""Compare relative native clocks with bounded binary64 cancellation error.

This is an arithmetic allowance on validated absolute timestamps, never a
training/synchrony tolerance. A quarter-tick resolution guard prevents a large
absolute origin from admitting a missing or shifted simulation step.
"""
import sys
from .native_evidence import number, require


def relative_clocks_equal(first, first_begin, second, second_begin, frequency_hz):
    a0,b0=number(first_begin),number(second_begin)
    frequency=number(frequency_hz)
    require(frequency>0, 'clock_alignment_invalid_frequency')
    if not first or len(first)!=len(second):return False
    before_a=before_b=None
    for raw_a,raw_b in zip(first,second):
        a,b=number(raw_a),number(raw_b)
        if before_a is not None and (a<=before_a or b<=before_b):return False
        # Each subtraction involves the absolute operands. Applying the same
        # roundoff convention only to the small differences loses that scale.
        arithmetic_bound=32*sys.float_info.epsilon*max(1.,abs(a),abs(a0),abs(b),abs(b0))
        if arithmetic_bound>=.25/frequency or abs((a-a0)-(b-b0))>arithmetic_bound:return False
        before_a,before_b=a,b
    return True


def specification_frequency(first, second):
    a=number(first['stimulus_profile']['frequency_hz'])
    b=number(second['stimulus_profile']['frequency_hz'])
    require(a==b and a>0, 'clock_alignment_frequency_changed')
    return a
