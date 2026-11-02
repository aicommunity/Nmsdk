"""Pinned Git evidence for declared learner properties; never a runtime verdict.

Catalog membership and identical source slices do not prove effective child
physics, semantic equivalence of changed consumers, or complete mode coverage.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

from .native_evidence import require


TOKENS = re.compile(r'//[^\r\n]*|/\*.*?\*/|(?:u8|[LuU])?R"(?P<delimiter>[^()\s\\]{0,16})\(.*?\)(?P=delimiter)"|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', re.S)


def _masked(text):
    return TOKENS.sub(lambda m: re.sub(r"[^\r\n]", " ", m.group()), text)


def _close(text, start, left, right):
    require(text[start] == left, "property_source_opening_token_missing")
    depth = 1
    for index in range(start+1, len(text)):
        depth += (text[index] == left) - (text[index] == right)
        if depth == 0:
            return index
    require(False, "property_source_unclosed_token")


def _hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _git(repo, *arguments):
    return subprocess.check_output(["git", "-C", str(repo), *arguments])


def _source(repo, commit, path):
    raw = _git(repo, "show", commit+":"+path)
    return raw.decode("utf-8-sig"), {"commit": commit, "path": path,
            "blob": _git(repo, "rev-parse", commit+":"+path).decode().strip(),
            "sha256": hashlib.sha256(raw).hexdigest()}


def _methods(text, component):
    masked = _masked(text)
    result = {}
    pattern = re.compile(r"(?m)^[^\n;{}]*\b"+component+r"::(?P<name>~?\w+)\s*\(")
    for match in pattern.finditer(masked):
        end = _close(masked, match.end()-1, "(", ")")
        begin = masked.find("{", end+1)
        require(begin >= 0, "property_source_method_body_missing")
        finish = _close(masked, begin, "{", "}")
        name = match["name"]
        result.setdefault(name, []).append({"line": text.count("\n", 0, match.start())+1,
                        "start_offset": match.start(),
                        "body_line": text.count("\n", 0, begin)+1,
                        "body": text[begin:finish+1],
                        "declaration": text[match.start():begin]})
    return result


def _single_method(methods, name):
    require(len(methods.get(name, [])) == 1, "property_source_ambiguous_or_missing_method:"+name)
    return methods[name][0]


def catalog(repo, commit):
    require(re.fullmatch(r"[0-9a-f]{40}", commit) is not None, "full_property_source_commit_required")
    result = []; sources = []
    for component in ("NNeuronTimeLearner", "NNeuronTimeLearnerBranch"):
        header, header_ref = _source(repo, commit, "Core/"+component+".h")
        source, source_ref = _source(repo, commit, "Core/"+component+".cpp")
        sources.extend([header_ref, source_ref])
        methods = _methods(source, component)
        require(component in methods and "ADefault" in methods, "property_source_owner_lifecycle_missing")
        constructor_method = _single_method(methods, component)
        constructor = constructor_method["declaration"]
        default = _single_method(methods, "ADefault"); default_masked = _masked(default["body"])
        masked = _masked(header)
        for match in re.finditer(r"\bUProperty\s*<", masked):
            end = _close(masked, match.end()-1, "<", ">")
            content = header[match.end():end]
            arguments = []; depth = 0; start = 0
            for position, char in enumerate(content):
                depth += (char == "<") - (char == ">")
                if char == "," and depth == 0:
                    arguments.append(content[start:position].strip());start = position+1
            arguments.append(content[start:].strip())
            require(len(arguments) == 3 and arguments[1] == component, "property_source_declaration_shape_changed")
            name_match = re.match(r"\s*(\w+)\s*;", masked[end+1:])
            require(name_match is not None, "property_source_declaration_name_missing")
            name = name_match[1]
            registration = re.search(r"\b"+name+r'\s*\(\s*"(?P<label>[^"\\]*)"\s*,\s*this(?P<rest>[^)]*)\)', constructor)
            require(registration is not None, "property_source_registration_missing:"+component+"."+name)
            setter = re.search(r"&"+component+r"::(\w+)", registration["rest"])
            setter_name = setter[1] if setter else None
            require(setter_name is None or setter_name in methods, "property_source_setter_body_missing:"+str(setter_name))
            mentions = []
            for use in re.finditer(r"\b"+name+r"\b", default_masked):
                line_start = default_masked.rfind("\n", 0, use.start())+1
                line_end = default_masked.find("\n", use.end())
                if line_end < 0:line_end = len(default_masked)
                entry = {"line": default["body_line"]+default_masked.count("\n", 0, use.start()),
                         "source": default["body"][line_start:line_end].strip()}
                if entry not in mentions:mentions.append(entry)
            setter_body = _single_method(methods, setter_name) if setter_name else None
            result.append({"component": component, "name": name, "type": arguments[0], "flags": arguments[2],
                           "declaration_line": header.count("\n", 0, match.start())+1,
                           "registration_line": source.count("\n", 0, constructor_method["start_offset"]+registration.start())+1,
                           "registered_name": registration["label"], "setter": setter_name,
                           "setter_line": setter_body["line"] if setter_body else None,
                           "setter_source_sha256": _hash(setter_body["body"]) if setter_body else None,
                           "default_mentions": mentions})
    keys = {(r["component"], r["name"]) for r in result}
    require(len(keys) == len(result), "duplicate_property_source_declaration")
    return {"source": commit, "sources": sources, "properties": result}


def compare(repo, before, after):
    old, new = catalog(repo, before), catalog(repo, after)
    a = {(r["component"], r["name"]): r for r in old["properties"]}
    b = {(r["component"], r["name"]): r for r in new["properties"]}
    rows = []
    fields = ("type", "flags", "registered_name", "setter", "setter_source_sha256")
    for key in sorted(a.keys() | b.keys()):
        changed = [field for field in fields if a.get(key, {}).get(field) != b.get(key, {}).get(field)]
        defaults = lambda record: [v["source"] for v in record.get("default_mentions", [])]
        if defaults(a.get(key, {})) != defaults(b.get(key, {})):changed.append("default_source_mentions")
        rows.append({"component": key[0], "name": key[1], "present_before": key in a,
                     "present_after": key in b, "changed_source_fields": changed})
    return {"kind": "timelearner_declared_property_source_drift", "schema_version": 1,
            "producer": {"analyzer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                         "source_kind": "immutable_git_blobs", "runtime_test": False},
            "before": old, "after": new, "records": rows,
            "runtime_property_matrix_complete": False, "semantic_equivalence_attested": False,
            "limitations": ["Declared UProperty members only; inherited Rdk properties are outside this catalog.",
                            "Default mentions are source evidence, not evaluated runtime defaults.",
                            "Changed helper/consumer/lifecycle semantics require a separate manual review.",
                            "Identical setter slices do not prove effective application in any physical mode."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pulselib", type=Path, required=True)
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    evidence = compare(args.pulselib, args.before, args.after)
    with args.output.open("xb") as stream:
        stream.write((json.dumps(evidence, ensure_ascii=False, indent=2)+"\n").encode("utf-8"))


if __name__ == "__main__":
    main()
