"""Explicit CLI entry point; commands have no import-time side effects."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def analyze(args: argparse.Namespace) -> dict:
    from .native_evidence import EvidenceError, audit_probe, load, require
    require(args.format == "domain" or not args.allow_legacy, "legacy_adapter_is_only_for_domains")
    require(args.format == "probe" or args.trace is None, "trace_option_is_only_for_probes")
    source = args.source.resolve(strict=True)
    if args.format == "domain":
        from .domain_evidence import audit_resistance_domain
        result = audit_resistance_domain(load(source), allow_legacy=args.allow_legacy)
    elif args.format == "learned-solo":
        from .learned_evidence import audit_learned_state, load_case
        result = audit_learned_state(*load_case(source))
    elif args.format == "stopped-solo":
        from .stopped_evidence import audit_stopped_state, load_case
        result = audit_stopped_state(*load_case(source))
    elif args.format == "recognition":
        from .recognition_evidence import audit_recognition_state, load_case
        result = audit_recognition_state(*load_case(source))
    elif args.format == "posttune-reconstruction":
        from .posttune_evidence import audit_reconstruction, load_case
        result = audit_reconstruction(*load_case(source))
    elif args.format == "probe":
        require(args.trace is not None, "primary_probe_trace_required")
        result = audit_probe(load(source), args.trace.resolve(strict=True))
    else:
        raise EvidenceError("unsupported_analysis_format")
    return {"kind": "timelearner_analysis", "schema_version": 1,
            "execution": "completed", "validity": "valid", "format": args.format,
            "analysis": result, "evaluation_verdict": None}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="TimeLearner reproducible experiment tools")
    commands = parser.add_subparsers(dest="command", required=True)
    inventory = commands.add_parser("inventory", help="inventory source properties and tracked historical tools")
    inventory.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    inventory.add_argument("--output", type=Path, required=True)
    analysis = commands.add_parser("analyze", help="audit original native evidence; no recognition verdict")
    analysis.add_argument("source", type=Path)
    analysis.add_argument("--format", choices=("domain", "probe", "learned-solo", "stopped-solo", "recognition", "posttune-reconstruction"), required=True)
    analysis.add_argument("--trace", type=Path, help="original primary CSV, required for probe")
    analysis.add_argument("--allow-legacy", action="store_true", help="descriptive domain schema-1 adapter only")
    analysis.add_argument("--output", type=Path, help="new output file; an existing file is never replaced")
    args = parser.parse_args(argv)
    if args.command == "inventory":
        from .inventory import write_inventory
        write_inventory(args.root.resolve(), args.output.resolve())
    elif args.command == "analyze":
        from .native_evidence import EvidenceError
        try:
            result = analyze(args)
            text = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
            if args.output is None:
                print(text, end="")
            else:
                with args.output.open("x", encoding="utf-8") as output:
                    output.write(text)
        except (EvidenceError, ValueError) as error:
            print(json.dumps({"kind": "timelearner_analysis", "schema_version": 1,
                              "execution": "completed", "validity": "invalid", "reason": str(error),
                              "evaluation_verdict": None}, ensure_ascii=False), file=sys.stderr)
            return 2
        except OSError as error:
            print(json.dumps({"kind": "timelearner_analysis", "schema_version": 1,
                              "execution": "process_error", "validity": "unknown", "reason": str(error),
                              "evaluation_verdict": None}, ensure_ascii=False), file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
