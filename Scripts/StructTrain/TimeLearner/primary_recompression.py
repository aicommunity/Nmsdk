"""Recompress a lossless primary container; never rewrite its model documents."""
import hashlib
import lzma
from pathlib import Path
import shutil

from .native_calibration_worker import _digest, _signed, _write
from .native_evidence import load, require
from .portable_primary import _bundle_version, _sha
from .source_envelope_bundle import KIND, _record


def _snapshot(root):
    result = {}
    for path in root.rglob('*'):
        require(not path.is_symlink(), 'primary_recompression_symlink')
        if path.is_file():
            result[path.relative_to(root).as_posix()] = _record(path)
    return result


def recompress(source, output):
    """Keep the exact uncompressed tar stream, recipes and original file hashes.

    Only derived archive/index metadata changes. The caller owns the source and
    output namespaces and supplies process/disk limits through the normal worker.
    """
    source = Path(source).resolve(strict=True)
    output = Path(output).resolve()
    require(not output.exists() and not output.is_relative_to(source) and
            not source.is_relative_to(output), 'primary_recompression_separate_output')
    before = _snapshot(source)
    index = load(source/'bundle.json');_digest(index)
    require(index['kind'] == KIND and index['schema_version'] == 1,
            'primary_recompression_source_kind')
    literal = index['literals_bundle']
    require(literal['path'] == 'literals/bundle.json' and
            before[literal['path']] == literal['record'], 'primary_recompression_literal_binding')
    bundle = load(source/literal['path']);_bundle_version(bundle)
    archive = source/'literals/primary.tar.xz'
    require(before['literals/primary.tar.xz'] == dict(bytes=bundle['archive_bytes'],
            sha256=bundle['archive_sha256']), 'primary_recompression_source_archive_changed')
    expected = {'bundle.json', 'literals/bundle.json', 'literals/primary.tar.xz'}
    for row in index['recipes'].values():
        require(row['path'] in before and before[row['path']] == row['record'],
                'primary_recompression_recipe_changed')
        expected.add(row['path'])
    require(set(before) == expected, 'primary_recompression_source_namespace')
    output.mkdir();(output/'literals').mkdir()
    for relative in sorted(expected-{'bundle.json', 'literals/bundle.json', 'literals/primary.tar.xz'}):
        destination = output/relative;destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source/relative, destination)
        require(_record(destination) == before[relative], 'primary_recompression_copy_changed')
    target = output/'literals/primary.tar.xz'
    maximum = bundle['expanded_bytes']+4096*len(bundle['members'])+1024**2
    original_hash = hashlib.sha256();size = 0
    with lzma.open(archive, 'rb') as reader, lzma.LZMAFile(target, 'wb', filters=[
            dict(id=lzma.FILTER_LZMA2, preset=9 | lzma.PRESET_EXTREME, dict_size=128*1024**2)]) as writer:
        while data := reader.read(1024**2):
            size += len(data)
            require(size <= maximum, 'primary_recompression_tar_budget')
            original_hash.update(data);writer.write(data)
    restored_hash = hashlib.sha256();restored_size = 0
    with lzma.open(target, 'rb') as reader:
        while data := reader.read(1024**2):
            restored_size += len(data)
            require(restored_size <= maximum, 'primary_recompression_tar_budget')
            restored_hash.update(data)
    require((size, original_hash.digest()) == (restored_size, restored_hash.digest()),
            'primary_recompression_tar_stream_changed')
    updated_bundle = {**bundle, 'archive_bytes': target.stat().st_size, 'archive_sha256': _sha(target),
                      'compression': {**bundle['compression'], 'dictionary_bytes': 128*1024**2}}
    _bundle_version(updated_bundle)
    _write(output/literal['path'], updated_bundle)
    updated_index = {k: v for k, v in index.items() if k != 'sha256'}
    updated_index['literals_bundle'] = dict(path=literal['path'], record=_record(output/literal['path']))
    _write(output/'bundle.json', _signed(updated_index))
    require(before == _snapshot(source), 'primary_recompression_source_changed')
    return dict(kind='timelearner_primary_container_recompression', schema_version=1,
        source_index=before['bundle.json'], output_index=_record(output/'bundle.json'),
        original_archive_bytes=bundle['archive_bytes'], archive_bytes=updated_bundle['archive_bytes'],
        uncompressed_tar_bytes=size, uncompressed_tar_sha256=original_hash.hexdigest(),
        tar_stream_identical=True, original_member_inventory_unchanged=True,
        recipe_bytes_unchanged=True, source_changed=False, native_execution_attested=False,
        scientific_verdict=None)
