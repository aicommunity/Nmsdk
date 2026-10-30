#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  Scripts/doc-audit/commit-phase.sh \
    --phase "phase-1-p0" \
    --scope "hardware|basic|cvbasic|motion|pulse|rdk|bin|nmsdk|all" \
    --summary "short imperative summary" \
    [--body-file /abs/path/body.txt] \
    [--dry-run]

Commits documentation changes in submodules first, then root (gitlink bump).
Messages are English conventional commits: docs(<scope>): <summary>
EOF
}

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

phase=""
scope=""
summary=""
body_file=""
dry_run=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --phase) phase="${2:-}"; shift 2;;
    --scope) scope="${2:-}"; shift 2;;
    --summary) summary="${2:-}"; shift 2;;
    --body-file) body_file="${2:-}"; shift 2;;
    --dry-run) dry_run=1; shift;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2;;
  esac
done

if [[ -z "$phase" || -z "$scope" || -z "$summary" ]]; then
  usage
  exit 2
fi

declare -A SCOPE_DIR=(
  [rdk]="$ROOT_DIR/Rdk"
  [bin]="$ROOT_DIR/Bin"
  [pulse]="$ROOT_DIR/Libraries/Nmsdk-PulseLib"
  [motion]="$ROOT_DIR/Libraries/Nmsdk-MotionControlLib"
  [basic]="$ROOT_DIR/Libraries/Rdk-BasicLib"
  [cvbasic]="$ROOT_DIR/Libraries/Rdk-CvBasicLib"
  [hardware]="$ROOT_DIR/Libraries/Rdk-HardwareLib"
  [nmsdk]="$ROOT_DIR"
)

DOC_GLOBS=(
  "*.md"
  "Docs/Audit"
  "Docs/ClDescLexicon.json"
  "Scripts/doc-audit"
)

stage_docs_in_repo() {
  local repo="$1"
  git -C "$repo" add -A -- '*.md' 2>/dev/null || true
  if [[ "$repo" == "$ROOT_DIR" ]]; then
    git -C "$repo" add Docs/Audit Scripts/doc-audit Docs/ClDescLexicon.json 2>/dev/null || true
    git -C "$repo" add Rdk Bin Libraries 2>/dev/null || true
  else
    git -C "$repo" add Docs 2>/dev/null || true
    if [[ "$repo" == *"/Bin" ]]; then
      git -C "$repo" add 'Configs/**/README.md' 2>/dev/null || true
    fi
  fi
}

build_message() {
  local sc="$1"
  local msg="docs(${sc}): ${summary}"
  if [[ -n "$body_file" && -f "$body_file" ]]; then
    msg+=$'\n\n'"$(cat "$body_file")"
  fi
  msg+=$'\n\n'"Phase: ${phase}"
  printf '%s' "$msg"
}

commit_repo() {
  local repo="$1"
  local sc="$2"
  if [[ ! -d "$repo/.git" ]] && ! git -C "$repo" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    return 0
  fi
  if [[ -n "$(git -C "$repo" status --porcelain)" ]]; then
    if [[ "$dry_run" -eq 1 ]]; then
      echo "[dry-run] would commit in $repo"
      git -C "$repo" status --short
      return 0
    fi
    stage_docs_in_repo "$repo"
    if git -C "$repo" diff --cached --quiet; then
      echo "No staged doc changes in $repo (skipped)"
      return 0
    fi
    local msg
    msg="$(build_message "$sc")"
    git -C "$repo" commit -m "$msg"
    echo "Committed in $repo @ $(git -C "$repo" rev-parse --short HEAD)"
  fi
}

ORDER=(rdk bin pulse motion basic cvbasic hardware nmsdk)

if [[ "$scope" == "all" ]]; then
  scopes=("${ORDER[@]}")
else
  scopes=("$scope")
fi

for sc in "${scopes[@]}"; do
  dir="${SCOPE_DIR[$sc]:-}"
  if [[ -z "$dir" ]]; then
    echo "Unknown scope: $sc" >&2
    exit 2
  fi
  if [[ "$sc" == "nmsdk" ]]; then
    # commit submodules with changes first when doing all
    if [[ "$scope" == "all" ]]; then
      for sub in rdk bin pulse motion basic cvbasic hardware; do
        commit_repo "${SCOPE_DIR[$sub]}" "$sub"
      done
    fi
    commit_repo "$ROOT_DIR" "nmsdk"
  else
    commit_repo "$dir" "$sc"
  fi
done

echo "commit-phase done (dry_run=$dry_run)"
