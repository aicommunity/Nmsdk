#!/usr/bin/env bash
# Archive only NMSDK / NeuroModelerConsole text journals (PLAN Tim 2026-10-24).
# tar+zstd per source directory; verify; delete journals only after OK.
# Never touches models/configs/results.csv; never active run journals.
# Usage:
#   archive_nmsdk_journals.sh [--dry-run] <dir> [<dir> ...]
set -euo pipefail

HOSTTAG="$(hostname | tr -c 'A-Za-z0-9._-' '_')"
DATE_UTC="$(date -u +%Y%m%d)"
DATA_ROOT="${DATA_OFFLOAD_ROOT:-/media/user/Data}"
ARCH_ROOT="${DATA_ROOT}/TLAgent-offload/journals/${HOSTTAG}/${DATE_UTC}"
MIN_DATA_FREE_PCT="${MIN_DATA_FREE_PCT:-5}"
DRY=0
REGISTRY="${RUN_REGISTRY_TSV:-}"

die() { echo "ERROR: $*" >&2; exit 2; }

free_pct() {
  python3 - "$1" <<'PY'
import shutil, sys
u = shutil.disk_usage(sys.argv[1])
print(f"{100.0 * u.free / u.total:.2f}")
PY
}

data_ok() {
  [[ -d "$DATA_ROOT" ]] || die "Data root missing: $DATA_ROOT"
  local pct
  pct="$(free_pct "$DATA_ROOT")"
  echo "CHECK Data free_pct=${pct} min=${MIN_DATA_FREE_PCT}"
  python3 - "$pct" "$MIN_DATA_FREE_PCT" <<'PY'
import sys
pct, mn = float(sys.argv[1]), float(sys.argv[2])
if pct < mn:
    print(f"BLOCK_ARCHIVE free_pct={pct:.2f} < {mn:.0f}%")
    sys.exit(3)
print("OK_ARCHIVE_ALLOWED")
PY
}

# Journals only — never StatisticLog binaries, never results.csv / xml / json payloads.
is_journal() {
  local f="$1" base
  base="$(basename "$f")"
  case "$base" in
    *.log|*.LOG|*Audit.log|*Audit.LOG|TimeLearnerTrainingAudit.log|run_posttune*.log|gate*.log|monitor*.log)
      return 0 ;;
  esac
  # plain-text console redirects often *.out for launch wrappers — include only if name suggests journal
  case "$base" in
    *console*.out|*posttune*.out|*gate*.out) return 0 ;;
  esac
  return 1
}

active_paths() {
  # Absolute paths of live Console -c Project.ini → workdir parents
  pgrep -af 'NeuroModelerConsole' 2>/dev/null | while read -r line; do
    if [[ "$line" =~ -c[[:space:]]+([^[:space:]]+/Project\.ini) ]]; then
      dirname "$(dirname "${BASH_REMATCH[1]}")"
    fi
  done
  # live posttune work dirs mentioned in cmdline
  pgrep -af 'posttune_verify|c1_dose_response|r0_branch' 2>/dev/null | while read -r line; do
    echo "$line" | grep -oE '/[^ ]+/runs/[^ ]+' || true
  done
}

path_is_active() {
  local src="$1" a
  while IFS= read -r a; do
    [[ -z "$a" ]] && continue
    case "$src" in
      "$a"|"$a"/*) return 0 ;;
    esac
    case "$a" in
      "$src"|"$src"/*) return 0 ;;
    esac
  done < <(active_paths)
  return 1
}

collect_journals() {
  local root="$1"
  find "$root" -type f \( \
      -name '*.log' -o -name '*.LOG' -o -name '*Audit.log' -o -name 'TimeLearnerTrainingAudit.log' \
      -o -name 'run_posttune*.log' -o -name '*console*.out' -o -name '*posttune*.out' \
    \) 2>/dev/null | while read -r f; do
    is_journal "$f" && printf '%s\n' "$f"
  done
}

archive_one_dir() {
  local src="$1"
  [[ -d "$src" ]] || { echo "SKIP missing $src"; return 0; }
  src="$(cd "$src" && pwd)"
  if path_is_active "$src"; then
    echo "SKIP_ACTIVE $src"
    return 0
  fi
  mapfile -t files < <(collect_journals "$src")
  if [[ ${#files[@]} -eq 0 ]]; then
    echo "SKIP_NO_JOURNALS $src"
    return 0
  fi
  # filter already-archived companions (*.tar.zst next to them) — only uncompressed
  local list=()
  local f
  for f in "${files[@]}"; do
    [[ -f "$f" ]] || continue
    # skip if this exact file already has .tar.zst sibling set from prior batch name — keep simple: skip *.zst
    case "$f" in *.zst|*.tar|*.tar.zst) continue ;; esac
    list+=("$f")
  done
  [[ ${#list[@]} -gt 0 ]] || { echo "SKIP_NONE $src"; return 0; }

  local base dst staging listfile archive
  base="$(basename "$src")"
  dst="$ARCH_ROOT/${base}_journals"
  staging="$(mktemp -d /tmp/nmsdk_jarch.XXXXXX)"
  listfile="$staging/filelist.txt"
  archive="$dst.tar.zst"
  mkdir -p "$ARCH_ROOT"

  # Build relative paths from src for tar
  : >"$listfile"
  for f in "${list[@]}"; do
    realpath --relative-to="$src" "$f" >>"$listfile"
  done
  local n
  n="$(wc -l <"$listfile")"
  echo "ARCHIVE $src n_journals=$n -> $archive dry=$DRY"

  if [[ "$DRY" == "1" ]]; then
    head -5 "$listfile"
    rm -rf "$staging"
    return 0
  fi

  # Re-check free space before write
  data_ok || { rm -rf "$staging"; return 3; }

  nice -n 19 ionice -c3 tar -C "$src" -cf - -T "$listfile" \
    | nice -n 19 ionice -c3 zstd -T0 -19 -o "$archive"

  # Integrity: zstd test + file list compare
  nice -n 19 ionice -c3 zstd -t "$archive"
  local tar_list
  tar_list="$staging/tar_list.txt"
  nice -n 19 ionice -c3 zstd -dc "$archive" | tar -tf - | sed 's#^\./##' | sort >"$tar_list"
  sort -o "$listfile" "$listfile"
  if ! cmp -s "$listfile" "$tar_list"; then
    echo "VERIFY_FAIL list mismatch $archive" >&2
    rm -rf "$staging"
    return 1
  fi
  echo "VERIFY_OK $archive files=$n"

  # Delete only archived journals
  while IFS= read -r rel; do
    rm -f "$src/$rel"
  done <"$listfile"

  # Registry note
  if [[ -n "$REGISTRY" && -f "$REGISTRY" ]]; then
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
      "jarch_${base}_${DATE_UTC}" "$HOSTTAG" "journals" "archive" "offloaded" \
      "$src" "$archive" "$(stat -c%s "$archive" 2>/dev/null || echo 0)" "" \
      "$(date -u +%Y-%m-%dT%H:%MZ)" "journals_only tar.zst n=$n" >>"$REGISTRY"
  fi

  rm -rf "$staging"
  echo "DELETED_JOURNALS $src count=$n"
}

# --- main ---
ARGS=()
for a in "$@"; do
  case "$a" in
    --dry-run) DRY=1 ;;
    *) ARGS+=("$a") ;;
  esac
done
[[ ${#ARGS[@]} -gt 0 ]] || die "usage: $0 [--dry-run] <dir>..."

data_ok || {
  echo "STOP: Data free < ${MIN_DATA_FREE_PCT}% — update CAMPAIGN_STATUS_LATEST.md"
  exit 3
}

mkdir -p "$ARCH_ROOT"
ec=0
for d in "${ARGS[@]}"; do
  archive_one_dir "$d" || ec=$?
  # stop batch if free dropped below threshold mid-run
  if ! data_ok; then
    echo "STOP_MID: Data free < ${MIN_DATA_FREE_PCT}% after archiving some dirs"
    exit 3
  fi
done
exit "$ec"
