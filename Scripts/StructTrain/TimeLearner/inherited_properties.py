"""Pinned shared Rdk property declarations and consumers, without runtime claims."""
import argparse
import hashlib
import json
from pathlib import Path
import re

from .native_evidence import require
from .property_drift import _source, _masked, _close, _methods, _single_method, _hash


CONSUMERS = {
    "Name": ("SetName", "GetFullName", "Copy"),
    "Id": ("SetId", "GetComponentId", "Copy"),
    "Activity": ("SetActivity", "Calculate", "Reset", "Default"),
    "TimeStep": ("SetTimeStep", "SetGlobalTimeStep", "Calculate", "Reset", "Default"),
    "MaxCalculationDuration": ("SetMaxCalculationDuration", "Calculate", "CheckDurationAndSkipComponentCalculation", "Default"),
    "CalculationDurationThreshold": ("SetCalculationDurationThreshold", "Calculate", "Default"),
    "Coord": ("SetCoord", "Copy"),
    "StepDuration": ("SetActivity", "Calculate", "GetStepDuration", "GetFullStepDuration"),
    "DebugSysEventsMask": ("SetDebugSysEventsMask", "Calculate", "LogDebugSysMessage", "Default"),
}


def catalog(pulselib, pulse_commit, rdk, rdk_commit):
    for revision in (pulse_commit, rdk_commit):
        require(re.fullmatch(r"[0-9a-f]{40}", revision) is not None, "full_inherited_source_commit_required")
    sources = []; hierarchy = []; headers = {}
    for name in ("NNeuronTimeLearner", "NNeuronTimeLearnerBranch", "UNet", "UItem", "UConnector", "UContainer", "UComponent", "UModule"):
        learner = name.startswith("NNeuron")
        header, reference = _source(pulselib if learner else rdk, pulse_commit if learner else rdk_commit,
                                    ("Core/" if learner else "Core/Engine/")+name+".h")
        sources.append(reference);headers[name] = header
        match = re.search(r"\bclass\s+(?:RDK_LIB_TYPE\s+)?"+name+r"\s*(?::\s*public\s+(\w+)\s*)?\{", _masked(header))
        require(match is not None, "inherited_source_class_declaration_missing:"+name)
        hierarchy.append({"class": name, "parent": match[1], "line": header.count("\n", 0, match.start())+1})
    parents = {row["class"]: row["parent"] for row in hierarchy}
    expected = {"NNeuronTimeLearner": "UNet", "NNeuronTimeLearnerBranch": "UNet", "UNet": "UItem",
                "UItem": "UConnector", "UConnector": "UContainer", "UContainer": "UComponent", "UComponent": "UModule", "UModule": None}
    require(parents == expected, "learner_inheritance_chain_changed")
    for name in ("UNet", "UItem", "UConnector", "UComponent", "UModule"):
        require(re.search(r"\bUProperty\s*<", _masked(headers[name])) is None,
                "additional_inherited_property_owner_requires_review:"+name)
    header = headers["UContainer"];masked = _masked(header)
    source, reference = _source(rdk, rdk_commit, "Core/Engine/UContainer.cpp");sources.append(reference)
    time_header, reference = _source(rdk, rdk_commit, "Core/Engine/UTime.h");sources.append(reference)
    require(re.search(r"typedef\s+unsigned\s+int\s+UTime\s*;", _masked(time_header)) is not None, "inherited_time_type_changed")
    methods = _methods(source, "UContainer");constructor = _single_method(methods, "UContainer")
    defaults = _single_method(methods, "Default");records = []
    for match in re.finditer(r"\bUProperty\s*<", masked):
        end = _close(masked, match.end()-1, "<", ">");arguments = [];start = match.end();depth = 0
        for position in range(start, end):
            char = masked[position];depth += (char == "<")-(char == ">")
            if char == "," and depth == 0:arguments.append(header[start:position].strip());start = position+1
        arguments.append(header[start:end].strip())
        require(len(arguments) == 3 and arguments[1] == "UContainer", "inherited_property_declaration_changed")
        name = re.match(r"\s*(\w+)\s*;", masked[end+1:])[1]
        require(name in CONSUMERS, "unreviewed_inherited_property:"+name)
        registration = re.search(r"\b"+name+r'\s*\(\s*"([^"\\]*)"\s*,\s*this([^)]*)\)', constructor["declaration"])
        require(registration is not None and registration[1] == name, "inherited_property_registration_changed:"+name)
        setter = re.search(r"&UContainer::(\w+)", registration[2]);setter = setter[1] if setter else None
        references = []
        for consumer in CONSUMERS[name]:
            require(bool(methods.get(consumer)), "inherited_property_consumer_missing:"+consumer)
            for method in methods[consumer]:
                references.append({"method": consumer, "line": method["line"], "body_sha256": _hash(method["body"])})
        mentions = {}
        for label, method in (("constructor", constructor), ("Default", defaults)):
            mentions[label] = [{"line": method["body_line"]+i, "source": line.strip()}
                               for i, line in enumerate(method["body"].splitlines())
                               if re.search(r"\b(?:"+name+("|"+setter if setter else "")+r")\b", _masked(line))]
        records.append({"owner": "UContainer", "applies_to": ["NNeuronTimeLearner", "NNeuronTimeLearnerBranch"],
                        "name": name, "type": arguments[0], "flags": arguments[2], "setter": setter,
                        "declaration_line": header.count("\n", 0, match.start())+1,
                        "lifecycle_source_mentions": mentions, "consumers": references})
    require({r["name"] for r in records} == set(CONSUMERS) and len(records) == 9, "inherited_property_set_changed")
    return {"kind": "timelearner_inherited_property_source_catalog", "schema_version": 1,
            "producer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "helper_sha256": hashlib.sha256(Path(__file__).with_name("property_drift.py").read_bytes()).hexdigest(),
            "pulse_commit": pulse_commit, "rdk_commit": rdk_commit, "sources": sources, "hierarchy": hierarchy,
            "shared_records": records, "shared_count": len(records), "runtime_test": False,
            "runtime_aliases_inventoried": False, "semantic_equivalence_attested": False,
            "lifecycle_mentions_are_evaluated_defaults": False, "scientific_verdict": None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pulselib", type=Path, required=True);parser.add_argument("--pulse-commit", required=True)
    parser.add_argument("--rdk", type=Path, required=True);parser.add_argument("--rdk-commit", required=True)
    parser.add_argument("--output", type=Path, required=True);args = parser.parse_args()
    result = catalog(args.pulselib, args.pulse_commit, args.rdk, args.rdk_commit)
    with args.output.open("xb") as stream:stream.write((json.dumps(result,ensure_ascii=False,indent=2)+"\n").encode())


if __name__ == "__main__":
    main()
