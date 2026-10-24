#!/usr/bin/env bash
# Archive only NMSDK / NeuroModelerConsole text journals (Tim 2026-10-24).
# tar+zstd per source directory; verify; delete journals only after OK.
# Never touches models/configs/results.csv; never active run journals.
#
# Usage:
#   archive_nmsdk_journals.sh [--dry-run] <dir> [<dir> ...]
#   archive_nmsdk_journals.sh [--dry-run] --from-list <file>
#
# Env:
#   DATA_OFFLOAD_ROOT   default /media/user/Data
#   DATA_OFFLOAD_HOST   optional user@host when Data is remote (Elder→M40)
#   MIN_DATA_FREE_PCT   default 5
#   ZSTD_LEVEL          default 3 (text logs; -19 too slow for multi-GB Dynamics)
#   RUN_REGISTRY_TSV    append jarch_* rows when set
set -euo pipefail

HOSTTAG="$(hostname | tr -c 'A-Za-z0-9._-' '_')"
DATE_UTC="$(date -u +%Y%m%d)"
DATA_ROOT="${DATA_OFFLOAD_ROOT:-/media/user/Data}"
DATA_HOST="${DATA_OFFLOAD_HOST:-}"
ARCH_REL="TLAgent-offload/journals/${HOSTTAG}/${DATE_UTC}"
MIN_DATA_FREE_PCT="${MIN_DATA_FREE_PCT:-5}"
ZSTD_LEVEL="${ZSTD_LEVEL:-3}"
DRY=0
REGISTRY="${RUN_REGISTRY_TSV:-}"

die() { echo "ERROR: $*" >&2; exit 2; }

remote_sh() {
  if [[ -n "$DATA_HOST" ]]; then
    ssh -o BatchMode=yes -o ConnectTimeout=30 "$DATA_HOST" "$@"
  else
    bash -c "$1"
  fi
}

free_pct() {
  if [[ -n "$DATA_HOST" ]]; then
    remote_sh "python3 -c \"import shutil;u=shutil.disk_usage('${DATA_ROOT}');print(f'{100*u.free/u.total:.2f}')\""
  else
    python3 - "$DATA_ROOT" <<'PY'
import shutil, sys
u = shutil.disk_usage(sys.argv[1])
print(f"{100.0 * u.free / u.total:.2f}")
PY
  fi
}

data_ok() {
  if [[ -z "$DATA_HOST" ]]; then
    [[ -d "$DATA_ROOT" ]] || die "Data root missing: $DATA_ROOT (set DATA_OFFLOAD_HOST if remote)"
  else
    remote_sh "test -d '${DATA_ROOT}'" || die "Remote Data missing: $DATA_HOST:$DATA_ROOT"
  fi
  local pct
  pct="$(free_pct)"
  echo "CHECK Data free_pct=${pct} min=${MIN_DATA_FREE_PCT} host=${DATA_HOST:-local}"
  python3 - "$pct" "$MIN_DATA_FREE_PCT" <<'PY'
import sys
pct, mn = float(sys.argv[1]), float(sys.argv[2])
if pct < mn:
    print(f"BLOCK_ARCHIVE free_pct={pct:.2f} < {mn:.0f}%")
    sys.exit(3)
print("OK_ARCHIVE_ALLOWED")
PY
}

is_journal() {
  local f="$1" base
  base="$(basename "$f")"
  case "$base" in
    *.log|*.LOG|*Audit.log|*Audit.LOG|TimeLearnerTrainingAudit.log|TimeLearnerTrainingDynamics.log|run_posttune*.log|gate*.log|monitor*.log)
      return 0 ;;
  esac
  case "$base" in
    *console*.out|*posttune*.out|*gate*.out) return 0 ;;
  esac
  return 1
}

active_paths() {
  pgrep -af 'NeuroModelerConsole' 2>/dev/null | while read -r line; do
    if [[ "$line" =~ -c[[:space:]]+([^[:space:]]+/Project\.ini) ]]; then
      dirname "$(dirname "${BASH_REMATCH[1]}")"
    fi
  done
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
      -o -name 'TimeLearnerTrainingDynamics.log' -o -name 'run_posttune*.log' \
      -o -name '*console*.out' -o -name '*posttune*.out' \
    \) 2>/dev/null | while read -r f; do
    is_journal "$f" && printf '%s\n' "$f"
  done
}

ensure_arch_root() {
  if [[ -n "$DATA_HOST" ]]; then
    remote_sh "mkdir -p '${DATA_ROOT}/${ARCH_REL}'"
  else
    mkdir -p "${DATA_ROOT}/${ARCH_REL}"
  fi
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
  local list=()
  local f
  for f in "${files[@]}"; do
    [[ -f "$f" ]] || continue
    case "$f" in *.zst|*.tar|*.tar.zst) continue ;; esac
    list+=("$f")
  done
  [[ ${#list[@]} -gt 0 ]] || { echo "SKIP_NONE $src"; return 0; }

  local base archive_name staging listfile archive_local archive_remote n
  base="$(basename "$src")"
  archive_name="${base}_journals.tar.zst"
  staging="$(mktemp -d /tmp/nmsdk_jarch.XXXXXX)"
  listfile="$staging/filelist.txt"
  archive_local="$staging/$archive_name"
  archive_remote="${DATA_ROOT}/${ARCH_REL}/${archive_name}"

  : >"$listfile"
  for f in "${list[@]}"; do
    realpath --relative-to="$src" "$f" >>"$listfile"
  done
  n="$(wc -l <"$listfile")"
  echo "ARCHIVE $src n_journals=$n -> ${DATA_HOST:+$DATA_HOST:}$archive_remote dry=$DRY"

  if [[ "$DRY" == "1" ]]; then
    head -5 "$listfile"
    rm -rf "$staging"
    return 0
  fi

  data_ok || { rm -rf "$staging"; return 3; }
  ensure_arch_root

  nice -n 19 ionice -c3 tar -C "$src" -cf - -T "$listfile" \
    | nice -n 19 ionice -c3 zstd -T0 "-${ZSTD_LEVEL}" -o "$archive_local"

  nice -n 19 ionice -c3 zstd -t "$archive_local"
  local tar_list
  tar_list="$staging/tar_list.txt"
  nice -n 19 ionice -c3 zstd -dc "$archive_local" | tar -tf - | sed 's#^\./##' | sort >"$tar_list"
  sort -o "$listfile" "$listfile"
  if ! cmp -s "$listfile" "$tar_list"; then
    echo "VERIFY_FAIL list mismatch local $archive_local" >&2
    rm -rf "$staging"
    return 1
  fi

  # Place on Data (local or remote)
  if [[ -n "$DATA_HOST" ]]; then
    nice -n 19 ionice -c3 rsync -a "$archive_local" "${DATA_HOST}:${archive_remote}"
    remote_sh "nice -n 19 ionice -c3 zstd -t '${archive_remote}'"
    remote_sh "nice -n 19 ionice -c3 zstd -dc '${archive_remote}' | tar -tf - | sed 's#^\\./##' | sort" >"$staging/remote_list.txt"
    if ! cmp -s "$listfile" "$staging/remote_list.txt"; then
      echo "VERIFY_FAIL remote list mismatch $archive_remote" >&2
      rm -rf "$staging"
      return 1
    fi
  else
    nice -n 19 ionice -c3 mv -f "$archive_local" "$archive_remote"
    nice -n 19 ionice -c3 zstd -t "$archive_remote"
    nice -n 19 ionice -c3 zstd -dc "$archive_remote" | tar -tf - | sed 's#^\./##' | sort >"$staging/placed_list.txt"
    if ! cmp -s "$listfile" "$staging/placed_list.txt"; then
      echo "VERIFY_FAIL placed list mismatch $archive_remote" >&2
      rm -rf "$staging"
      return 1
    fi
  fi
  echo "VERIFY_OK $archive_remote files=$n"

  while IFS= read -r rel; do
    rm -f "$src/$rel"
  done <"$listfile"

  local asize=0
  if [[ -n "$DATA_HOST" ]]; then
    asize="$(remote_sh "stat -c%s '${archive_remote}' 2>/dev/null || echo 0")"
  else
    asize="$(stat -c%s "$archive_remote" 2>/dev/null || echo 0)"
  fi

  if [[ -n "$REGISTRY" && -f "$REGISTRY" ]]; then
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
      "jarch_${base}_${DATE_UTC}" "$HOSTTAG" "journals" "archive" "offloaded" \
      "$src" "$archive_remote" "$asize" "" \
      "$(date -u +%Y-%m-%dT%H:%MZ)" "journals_only tar.zst n=$n zstd=${ZSTD_LEVEL}" >>"$REGISTRY"
  fi

  rm -rf "$staging"
  echo "DELETED_JOURNALS $src count=$n archive_bytes=$asize"
}

# --- main ---
ARGS=()
FROM_LIST=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY=1; shift ;;
    --from-list)
      FROM_LIST="${2:-}"
      [[ -n "$FROM_LIST" ]] || die "--from-list needs file"
      shift 2
      ;;
    *) ARGS+=("$1"); shift ;;
  esac
done
if [[ -n "$FROM_LIST" ]]; then
  [[ -f "$FROM_LIST" ]] || die "list file missing: $FROM_LIST"
  while IFS= read -r line; do
    [[ -z "$line" || "$line" =~ ^# ]] && continue
    ARGS+=("$line")
  done <"$FROM_LIST"
fi
[[ ${#ARGS[@]} -gt 0 ]] || die "usage: $0 [--dry-run] [--from-list FILE] <dir>..."

data_ok || {
  echo "STOP: Data free < ${MIN_DATA_FREE_PCT}% — update CAMPAIGN_STATUS_LATEST.md"
  exit 3
}

ensure_arch_root
ec=0
for d in "${ARGS[@]}"; do
  archive_one_dir "$d" || ec=$?
  if ! data_ok; then
    echo "STOP_MID: Data free < ${MIN_DATA_FREE_PCT}% after archiving some dirs"
    exit 3
  fi
done
exit "$ec"
