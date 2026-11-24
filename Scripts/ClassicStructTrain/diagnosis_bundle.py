"""Preserve verified discrepancy evidence with original paths and byte hashes."""
from pathlib import Path
import gzip
import hashlib
import json
import subprocess
import sys
from zipfile import ZipFile, ZIP_DEFLATED

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnosis_run import ROOT, WORK, CONFIG, DELIVERY, RUNTIME, relative, save, sha, load


def evidence_files():
    files = set()
    for directory in (WORK / "runs", WORK / "variants", WORK / "source-snapshots", WORK / "charts", CONFIG, DELIVERY):
        files.update(p for p in directory.rglob("*") if p.is_file() and p.suffix != ".lock")
    files.update(WORK.glob("*.json"))
    files.update(WORK.glob("*.patch"))
    files.update(p for p in Path(__file__).parent.glob("diagnosis_*") if p.is_file())
    for file in (WORK / "variants").glob("*.json"):
        binary = ROOT / load(file)["binary"]
        files.update([binary, binary.with_suffix(".ini")])
    for item in load(WORK / "locked-inference-cases.json"):
        files.update(ROOT / path for path in item["files"])
    return sorted(files)


def archive():
    destination = WORK / "Evidence"
    destination.mkdir(exist_ok=False)
    sdk = ROOT / "Libraries/Nmsdk-PulseLib"
    for metadata in (WORK / "variants").glob("*.json"):
        version = load(metadata)
        patch = subprocess.check_output(["git", "diff", "--binary", "--full-index", "8710978", version["pulselib_sha"]],
                                        cwd=sdk)
        (WORK / (metadata.stem + "-sdk.patch")).write_bytes(patch)

    index, unique = [], {}
    part, length, bundle = 0, 0, None
    try:
        for file in evidence_files():
            size = file.stat().st_size
            digest = sha(file)
            if digest not in unique:
                if bundle is None or length + size > 96 * 1024 * 1024:
                    if bundle is not None:
                        bundle.close()
                    part += 1
                    length = 0
                    bundle = ZipFile(destination / f"data-{part:03}.zip", "w", ZIP_DEFLATED, compresslevel=4)
                bundle.write(file, digest)
                unique[digest] = part
                length += size
            index.append({"path": relative(file), "sha256": digest, "bytes": size, "part": unique[digest]})
    finally:
        if bundle is not None:
            bundle.close()
    with gzip.open(destination / "index.json.gz", "wt", encoding="utf-8") as output:
        json.dump(index, output, ensure_ascii=False, separators=(",", ":"))
    archives = []
    for part_file in sorted(destination.glob("*.zip")):
        with ZipFile(part_file) as part_bundle:
            for digest in part_bundle.namelist():
                checksum = hashlib.sha256()
                with part_bundle.open(digest) as source:
                    while chunk := source.read(1024 * 1024):
                        checksum.update(chunk)
                assert checksum.hexdigest() == digest
        archives.append({"file": part_file.name, "bytes": part_file.stat().st_size, "sha256": sha(part_file)})
    save(destination / "verification.json", {
        "passed": True, "files": len(index), "unique_bytesets": len(unique), "archives": archives,
        "index_sha256": sha(destination / "index.json.gz"),
        "restore": "Read index.json.gz, select the corresponding data-###.zip, and extract the SHA256 member to the listed path.",
    })
    print(f"Verified {len(index)} files in {len(archives)} archives")


if __name__ == "__main__":
    archive()
