#!/usr/bin/env bash
# Summarize agentic SLO-related audit event counts from a JSONL audit log.
set -euo pipefail

AUDIT_FILE="${1:-}"
if [[ -z "${AUDIT_FILE}" || ! -f "${AUDIT_FILE}" ]]; then
  echo "Usage: $0 <audit.jsonl>" >&2
  exit 1
fi

python3 - "${AUDIT_FILE}" <<'PY'
import json
import sys

path = sys.argv[1]
counts = {}
with open(path, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        event = row.get("event_type") or row.get("type") or ""
        if event in {
            "task_completed",
            "task_failed",
            "task_plan_hint",
            "task_plan_fallback_to_agent",
            "false_execution_prevented",
            "escalation_to_hitl",
            "intent_ambiguity_blocked",
            "ask_user_issued",
            "ask_user_answered",
            "unified_turn_started",
            "unified_turn_completed",
        }:
            counts[event] = counts.get(event, 0) + 1

print("LLM agentic SLO snapshot:")
for key in sorted(counts):
    print(f"  {key}: {counts[key]}")
if not counts:
    print("  (no SLO events found)")
PY
