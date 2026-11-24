"""Lossless, bounded file indirection for complete native learned-state jobs.

Training/history evidence is never removed. Source bytes and the ordinary
resolved job digest remain authoritative; this envelope is only an I/O format.
"""
import hashlib
import os
from pathlib import Path, PurePosixPath

from .model_identity import canonical_model_sha256 as sha
from .native_evidence import require

TRANSPORT = 'checked-file-source-v1'
KIND = 'timelearner_checked_file_source_job'
MAXIMUM_SOURCE_BYTES = 1024*1024**2
SOURCE_FIELDS = {'timelearner_native_diagnostic_evaluation_job':'source_stopped',
                 'timelearner_native_recognition_export_job':'source_solo',
                 'timelearner_native_evaluation_job':'source_recognition',
                 'timelearner_native_physical_model_export_job':'source_state',
                 'timelearner_native_physical_model_conversion_job':'source_model_data',
                 'timelearner_native_physical_threshold_candidate_job':'source_model_data',
                 'timelearner_native_physical_model_evaluation_job':'source_model_data'}


def _record(path):
    require(not path.is_symlink() and path.is_file(), 'job_source_file_required')
    path_before=path.stat()
    with path.open('rb') as stream:
        before=os.fstat(stream.fileno())
        require(0 < before.st_size <= MAXIMUM_SOURCE_BYTES, 'job_source_declared_size')
        digest=hashlib.sha256();size=0
        for chunk in iter(lambda:stream.read(1024**2),b''):
            size+=len(chunk)
            require(size<=before.st_size, 'job_source_size_changed')
            digest.update(chunk)
        after=os.fstat(stream.fileno())
    current=path.stat()
    keys=('st_dev','st_ino','st_size','st_mtime_ns','st_ctime_ns')
    # Windows stat and fstat expose different file-id widths. Compare each API
    # to itself; retain all metadata checks and the exact content digest.
    require(not path.is_symlink() and size==before.st_size==current.st_size and
            all(getattr(before,k)==getattr(after,k) for k in keys) and
            all(getattr(path_before,k)==getattr(current,k) for k in keys),
            'job_source_bytes_changed')
    if os.name!='nt':
        require((before.st_dev,before.st_ino)==(current.st_dev,current.st_ino),'job_source_bytes_changed')
    return {'bytes':size,'sha256':digest.hexdigest()}


def make_envelope(job, source_path, input_root):
    require(type(job) is dict and job.get('kind') in SOURCE_FIELDS, 'job_source_unsupported_operation')
    field=SOURCE_FIELDS[job['kind']]
    require(type(job.get(field)) is dict and type(job[field].get('sha256')) is str,
            'job_source_package_required')
    root=Path(input_root).resolve(strict=True);path=Path(source_path)
    require(path.is_absolute() and not path.is_symlink(), 'job_source_file_required')
    path=path.absolute()
    require(path.is_relative_to(root), 'job_source_path_escape')
    relative=path.relative_to(root).as_posix();parts=PurePosixPath(relative)
    require(not parts.is_absolute() and '..' not in parts.parts and '.' not in parts.parts and
            '\\' not in relative and ':' not in relative, 'job_source_path_escape')
    current=root
    for part in parts.parts:
        current=current/part
        require(not current.is_symlink(), 'job_source_symlink')
    body={k:v for k,v in job.items() if k!=field}
    source={'field':field,'path':relative,**_record(path),'package_sha256':job[field]['sha256']}
    envelope={'kind':KIND,'schema_version':1,'job':body,'source':source}
    return {**envelope,'sha256':sha(envelope)}


def verify_envelope(envelope, job, source_path, input_root):
    require(envelope==make_envelope(job,source_path,input_root), 'job_source_transport_changed')
    return {'transport':TRANSPORT,'source_bytes':envelope['source']['bytes'],
            'source_sha256':envelope['source']['sha256'],'resolved_job_sha256':job['sha256']}
