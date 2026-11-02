"""Locate published source-path claims; a textual reference is not runtime attestation."""
import argparse
from collections import Counter
import gzip
import hashlib
import io
import json
import lzma
from pathlib import Path
import re
import subprocess
import tarfile

from .native_evidence import require


LIMIT = 64*1024*1024
TEXT = {".json", ".md", ".log", ".txt", ".ini", ".xml", ".py", ".sh", ".ps1", ".cpp", ".h", ".cmake"}
PREFIX = "Reports/StructTrain/TimeLearner/"


def audit(repository, revision, needle):
    repository = Path(repository).resolve(strict=True)
    def git(*args):return subprocess.check_output(["git", "-C", str(repository), *args])
    require(re.fullmatch(r"[0-9a-f]{40}", revision) is not None, "full_source_audit_revision_required")
    require(type(needle) is str and needle and "\n" not in needle and "\0" not in needle, "invalid_source_audit_needle")
    require(Path(git("rev-parse", "--show-toplevel").decode().strip()).resolve() == repository, "source_audit_repository_alias")
    require(git("cat-file", "-t", revision).strip() == b"commit", "source_audit_revision_not_commit")
    matches = [];unknown = [];stats = Counter();reports = {}

    def inspect(raw, path, blob, member=None):
        label = member or path
        if label.endswith(".gz"):
            try:
                with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:raw = stream.read(LIMIT+1)
            except (OSError,EOFError) as error:
                unknown.append({"git_path":path,"blob":blob,"member":member,
                                "reason":"gzip_unreadable","detail":type(error).__name__});return
            label = label[:-3]
        if Path(label).suffix.lower() not in TEXT:return
        stats["text_files_considered"] += 1
        record = {"git_path": path, "blob": blob, "member": member}
        if len(raw)>LIMIT:
            unknown.append({**record,"reason":"text_size_limit"});return
        if raw.startswith(b"version https://git-lfs.github.com/spec/"):
            unknown.append({**record,"reason":"lfs_payload_not_in_git_blob"});return
        try:
            if raw.startswith((b"\xff\xfe",b"\xfe\xff")):text = raw.decode("utf-16")
            else:
                require(b"\0" not in raw,"unrecognized_text_encoding")
                text = raw.decode("utf-8-sig")
        except (UnicodeError, ValueError) as error:
            unknown.append({**record,"reason":"text_encoding_unreadable","detail":type(error).__name__});return
        stats["text_files_inspected"] += 1
        lines = []
        for ordinal,line in enumerate(text.splitlines(),1):
            if needle not in line:continue
            category = "metadata_reference"
            if Path(label).suffix == ".md":category = "report_reference"
            elif "NMSDK_RESOURCE_ROOT" in line:category = "configured_resource_root_reference"
            elif re.search(r'"(?:source_root|source_directory|source_path)"\s*:',line):category = "declared_source_path_reference"
            elif Path(label).suffix == ".py" and re.search(r"\b(?:source|repo)\s*=",line):category = "source_binding_in_code"
            elif Path(label).suffix in (".log",".txt"):category = "log_source_path_reference"
            lines.append({"line":ordinal,"category":category,"line_sha256":hashlib.sha256(line.encode()).hexdigest()})
        if not lines:return
        report = path[len(PREFIX):].split("/",1)[0]
        counts = Counter(row["category"] for row in lines)
        matches.append({**record,"report":report,"content_sha256":hashlib.sha256(raw).hexdigest(),"references":lines})
        reports.setdefault(report,Counter()).update(counts)

    listing = git("ls-tree","-r","-z",revision,"--",PREFIX)
    process = subprocess.Popen(["git","-C",str(repository),"cat-file","--batch"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    try:
        for record in listing.split(b"\0"):
            if not record:continue
            metadata,path = record.split(b"\t",1);mode,kind,blob = metadata.decode().split();path = path.decode()
            if kind!="blob" or mode not in ("100644","100755"):continue
            if not (Path(path).suffix.lower() in TEXT or path.endswith((".tar.xz",".json.gz"))):continue
            process.stdin.write((blob+"\n").encode());process.stdin.flush()
            header = process.stdout.readline().decode().split()
            require(len(header)==3 and header[0]==blob and header[1]=="blob","source_audit_git_batch_header")
            size = int(header[2])
            if size>LIMIT:
                remaining = size
                while remaining:
                    block = process.stdout.read(min(remaining,1024*1024))
                    require(bool(block),"source_audit_git_batch_truncated");remaining -= len(block)
                require(process.stdout.read(1)==b"\n","source_audit_git_batch_truncated")
                unknown.append({"git_path":path,"blob":blob,"member":None,"reason":"git_blob_size_limit"})
                stats["oversized_git_blobs_drained"] += 1
                continue
            raw = process.stdout.read(size)
            require(len(raw)==size and process.stdout.read(1)==b"\n","source_audit_git_batch_truncated")
            stats["git_blobs_read"] += 1
            if path.endswith(".tar.xz"):
                stats["archives_read"] += 1
                try:
                    with tarfile.open(fileobj=io.BytesIO(raw),mode="r|xz") as archive:
                        for member in archive:
                            if not member.isfile():continue
                            name = member.name
                            if not (Path(name).suffix.lower() in TEXT or name.endswith(".json.gz")):continue
                            if member.size>LIMIT:
                                unknown.append({"git_path":path,"blob":blob,"member":name,"reason":"text_size_limit"});continue
                            inspect(archive.extractfile(member).read(),path,blob,name)
                except (tarfile.TarError,lzma.LZMAError,EOFError,OSError) as error:
                    unknown.append({"git_path":path,"blob":blob,"member":None,"reason":"archive_unreadable","detail":type(error).__name__})
            else:inspect(raw,path,blob)
    finally:
        process.stdin.close();process.stdout.close();process.wait()
    require(process.returncode==0,"source_audit_git_batch_failed")
    return {"kind":"published_source_reference_audit","schema_version":1,"root_revision":revision,"needle":needle,
            "producer_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"scope_prefix":PREFIX,
            "statistics":dict(stats),"report_references":{k:dict(v) for k,v in sorted(reports.items())},
            "matches":matches,"uninspected_metadata":unknown,"absence_proves_unaffected":False,
            "runtime_source_attested":False,"scientific_result_validity_changed":False,
            "limitations":["Textual path claims only; source references do not establish actual resource reads.",
                "Reports without a matching source name may still have used the affected worktree.",
                "CSV/image contents, nested archives and non-text payloads are outside this scan.",
                "Escaped/computed source names may not occur literally; unreadable/large metadata remains unknown.",
                "No source checkout, archived script execution, source metadata repair or result rewriting."],"scientific_verdict":None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,required=True);parser.add_argument("--revision",required=True)
    parser.add_argument("--needle",required=True);parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args();result = audit(args.root,args.revision,args.needle)
    with args.output.open("xb") as stream:stream.write((json.dumps(result,indent=2,ensure_ascii=False)+"\n").encode())


if __name__ == "__main__":main()
