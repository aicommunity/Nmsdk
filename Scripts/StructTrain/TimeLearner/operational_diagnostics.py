"""Versioned, bounded-memory review of an owned process's captured streams.

This axis is separate from exit status, numerical validity and scientific
outcomes. Unknown stderr requires review; it is not declared a numerical error.
"""
import hashlib
from pathlib import Path
import re


_GLOG = re.compile(r'^([IWEF])(?:\d{8}|\d{4}) \d{2}:\d{2}:\d{2}\.\d+\s+\d+\s+[^\]\r\n]+:\d+\]')
_FAILURE = re.compile(r'^(?:Traceback \(most recent call last\):|(?:==\d+==)?ERROR: (?:AddressSanitizer|LeakSanitizer)|FATAL: ThreadSanitizer|SUMMARY: (?:AddressSanitizer|UndefinedBehaviorSanitizer)|.*:\d+:\d+: runtime error:)')


def inspect_streams(directory):
    """Read immutable stdout/stderr after closure; never scan shared runtime logs."""
    root = Path(directory)
    records, examples = [], []
    errors = warnings = unclassified = 0
    reasons = set()
    for name in ('stdout.log', 'stderr.log'):
        path = root/name
        if path.is_symlink() or not path.is_file():
            reasons.add('missing_or_aliased_stream:'+name)
            continue
        digest = hashlib.sha256(); size = 0
        before = path.stat()
        with path.open('rb') as stream:
            line = 0
            while True:
                raw = stream.readline(65537)
                if not raw: break
                line += 1; size += len(raw); digest.update(raw)
                try:
                    text = raw.decode('utf-8').rstrip('\r\n')
                except UnicodeDecodeError:
                    reasons.add('non_utf8_stream:'+name)
                    continue
                match = _GLOG.match(text)
                error = bool((match and match[1] in 'EF') or _FAILURE.match(text))
                warning = bool(match and match[1] == 'W')
                unknown = name == 'stderr.log' and bool(text.strip()) and not match and not error
                errors += error; warnings += warning; unclassified += unknown
                if len(raw) > 65536:
                    reasons.add('stream_line_limit:'+name)
                if (error or unknown) and len(examples) < 16:
                    examples.append({'stream': name, 'chunk': line, 'severity': 'error' if error else 'unclassified',
                                     'excerpt': text[:256]})
        after = path.stat()
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
                after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) or size != after.st_size:
            reasons.add('stream_changed_during_review:'+name)
        records.append({'path': name, 'bytes': size, 'sha256': digest.hexdigest()})
    # Contained runners retain the manager's original streams as well as the
    # portable copies. Rehashing a replacement copy must not hide its source.
    contained_match = None
    original = root/'contained'
    if original.exists() or original.is_symlink():
        contained_match = not original.is_symlink() and original.is_dir()
        for record in records:
            path = original/record['path']
            if path.is_symlink() or not path.is_file():
                contained_match = False
                continue
            before = path.stat(); digest = hashlib.sha256(); size = 0
            with path.open('rb') as stream:
                while raw := stream.read(65536):
                    size += len(raw); digest.update(raw)
            after = path.stat()
            contained_match = contained_match and (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) == (
                after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) and size == record['bytes'] and digest.hexdigest() == record['sha256']
        contained_match = contained_match and len(records) == 2
        if not contained_match: reasons.add('contained_stream_copy_mismatch')
    return {'kind': 'timelearner_operational_diagnostics', 'schema_version': 1,
            'policy': 'owned-streams-v1', 'status': 'error' if errors else 'needs_review' if reasons or unclassified else 'clear',
            'error_records': errors, 'warning_records': warnings, 'unclassified_stderr_chunks': unclassified,
            'reasons': sorted(reasons), 'examples': examples, 'streams': records,
            'contained_streams_match': contained_match,
            'scientific_verdict': None}


def permits_positive_audit(directory, recorded=None):
    """Recompute rather than trusting a stored clear flag, even after rehashing."""
    result = inspect_streams(directory)
    if recorded is not None and recorded != result:
        from .native_evidence import require
        require(False, 'operational_diagnostics_changed')
    return result['status'] == 'clear'
