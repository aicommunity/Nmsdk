"""Side-effect-free admission of worker limits, reusable before queue waiting.

The same validator is used immediately before actual contained execution.
Limits are never clipped: invalid requests must be corrected explicitly.
"""
import argparse
import json
import math
from pathlib import Path
import sys

from .native_evidence import EvidenceError, require


MAXIMUM_WALL_SECONDS = 86400


def validate_limits(memory_bytes, tasks, maximum_wall_seconds, *, wall_reason='contained_limits_invalid'):
    require(type(maximum_wall_seconds) in (int, float) and math.isfinite(maximum_wall_seconds) and
            1 <= maximum_wall_seconds <= MAXIMUM_WALL_SECONDS, wall_reason)
    require(type(memory_bytes) is int and 0 < memory_bytes <= 2**63-1 and
            type(tasks) is int and 0 < tasks <= 2**31-1, 'contained_limits_invalid')
    return {'memory_bytes': memory_bytes, 'tasks': tasks, 'maximum_wall_seconds': maximum_wall_seconds}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--memory-bytes', type=int, required=True)
    parser.add_argument('--tasks', type=int, required=True)
    parser.add_argument('--wall-seconds', type=float, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    try:
        limits = validate_limits(args.memory_bytes, args.tasks, args.wall_seconds)
        result = {'kind': 'timelearner_contained_limits_preflight', 'schema_version': 1,
                  'validity': 'valid', 'limits': limits, 'worker_started': False,
                  'resources_reserved': False, 'scientific_verdict': None}
        if args.output is not None:
            with args.output.open('x', encoding='utf-8') as stream:
                json.dump(result, stream, indent=2, allow_nan=False);stream.write('\n')
        print(json.dumps(result, allow_nan=False));return 0
    except (EvidenceError, OSError, ValueError) as error:
        print(json.dumps({'validity': 'invalid', 'reason': str(error), 'worker_started': False,
                          'resources_reserved': False, 'scientific_verdict': None}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
