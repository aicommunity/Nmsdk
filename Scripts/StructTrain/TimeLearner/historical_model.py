"""Conservative identity of a historical serialized neuron and its inbound links.

This is an XML adapter, not a V2 ModelArchive or a dynamic checkpoint. Component
and input-edge order, every serialized neuron parameter, property attributes and
classes are retained. The external dataset/controller are specified separately.
"""
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from .model_identity import canonical_model_sha256
from .native_evidence import require


def property_value(node):
    children = list(node)
    if children:
        return {"tag": node.tag, "attributes": dict(node.attrib),
                "children": [property_value(c) for c in children]}
    kind = node.get("Type", "")
    text = node.text or ""
    if "string" in kind:
        value = {"kind": "string", "value": text}
    elif re.fullmatch(r"[bijlmxyt]|(?:MVector|MDMatrix|simplevector)(?:<.*>)?", kind):
        integer = kind in {"b", "i", "j", "l", "m", "x", "y", "t"} or bool(re.search(r"<[bijlmxyt]>", kind))
        tokens = text.split();values = []
        for token in tokens:
            if integer:
                require(re.fullmatch(r"[-+]?\d+", token) is not None, "invalid_historical_integer")
                values.append(str(int(token)))
            else:
                number = float(token.replace(",", "."))
                require(math.isfinite(number), "nonfinite_historical_model_parameter")
                values.append((0.0 if number == 0 else number).hex())
        value = {"kind": "integer" if integer else "binary64", "values": values}
    elif kind in {"d", "f"}:
        number = float(text.strip().replace(",", "."))
        require(math.isfinite(number), "nonfinite_historical_model_parameter")
        value = {"kind": "binary64", "values": [(0.0 if number == 0 else number).hex()]}
    else:
        # Unknown types stay conservative: do not silently equate spellings.
        value = {"kind": "uninterpreted", "text": text}
    return {"tag": node.tag, "attributes": dict(node.attrib), "value": value}


def serialized_neuron(path: Path, frequency_hz=2000):
    require(type(frequency_hz) in (int, float) and math.isfinite(frequency_hz) and frequency_hz > 0,
            "invalid_historical_model_frequency")
    root = ET.parse(path).getroot();model = root.find("./Model")
    require(model is not None, "historical_model_root_missing")
    neuron = model.find("./Components/NeuronTimeLearner/Components/Neuron")
    require(neuron is not None, "historical_serialized_neuron_missing")
    nodes = []
    def walk(node, prefix):
        props = node.findall("./Parameters/*")
        require(len({p.tag for p in props}) == len(props), "duplicate_historical_model_parameter")
        nodes.append({"path": prefix, "class": node.get("Class"),
                      "parameters": [property_value(p) for p in props]})
        for child in node.findall("./Components/*"):walk(child, prefix+"."+child.tag)
    prefix = "NeuronTimeLearner.Neuron";walk(neuron, prefix)
    edges = []
    def owner(text, container):
        text = (text or "").strip()
        if text.startswith("Model."):return text[6:]
        if not container or text.startswith("NeuronTimeLearner.") or text == "NeuronTimeLearner":return text
        return container+"."+text if text else container
    def links(node, container):
        for link in node.findall("./Links/*"):
            item = link.find("./Item")
            require(item is not None, "historical_link_source_missing")
            for connector in link.findall("./Connector"):
                dest = owner(connector.text, container)
                if dest == prefix or dest.startswith(prefix+"."):
                    edges.append({"source": owner(item.text, container), "source_attributes": dict(item.attrib),
                                  "destination": dest, "destination_attributes": dict(connector.attrib)})
        for child in node.findall("./Components/*"):
            links(child, child.tag if not container else container+"."+child.tag)
    links(model, "")
    require(bool(nodes) and bool(edges), "historical_neuron_or_inbound_links_empty")
    paths = {node["path"] for node in nodes}
    require(len(paths) == len(nodes), "duplicate_historical_component_path")
    global_paths = {""}
    def collect(node, prefix):
        for child in node.findall("./Components/*"):
            path = child.tag if not prefix else prefix+"."+child.tag
            require(path not in global_paths, "duplicate_historical_global_component_path")
            global_paths.add(path);collect(child, path)
    collect(model, "")
    for edge in edges:
        require(edge["destination"] in paths, "historical_link_destination_not_in_graph")
        require(edge["source"] in global_paths, "historical_link_source_not_in_graph")
    result = {"schema": "historical_serialized_neuron_v1", "frequency_hz": frequency_hz,
              "nodes_in_native_order": nodes, "inbound_edges_in_serialized_order": edges}
    return {"snapshot": result, "sha256": canonical_model_sha256(result),
            "nodes": len(nodes), "inbound_edges": len(edges),
            "scope": "serialized parameters/classes/ordered graph and inbound links; external protocol and dynamic state excluded"}
