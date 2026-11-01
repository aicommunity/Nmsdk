#!/usr/bin/env bash
# PLAN 2026-10-25 §H2/H3: warn + offload completed runs; never kill active consoles.
# Usage:
#   disk_watch_offload.sh check
#   disk_watch_offload.sh offload-dry-run <src_dir> ...
#   disk_watch_offload.sh offload <src_dir> ...
set -euo pipefail

HOSTTAG="$(hostname | tr -c 'A-Za-z0-9._-' '_')"
DATE_UTC="$(date -u +%Y%m%d)"
DATA_ROOT="${DATA_OFFLOAD_ROOT:-/media/user/Data}"
OFFLOAD_ROOT="${DATA_ROOT}/TLAgent-offload/${HOSTTAG}/${DATE_UTC}"
MIN_DATA_FREE_PCT="${MIN_DATA_FREE_PCT:-5}"
WARN_HOME_AVAIL_G="${WARN_HOME_AVAIL_G:-80}"

die() { echo "ERROR: $*" >&2; exit 2; }

free_pct() {
  python3 - "$1" <<'PY'
import shutil, sys
u = shutil.disk_usage(sys.argv[1])
print(f"{100.0 * u.free / u.total:.2f}")
PY
}

avail_g() {
  df -BG "$1" 2>/dev/null | awk 'NR==2{gsub(/G/,"",$4); print $4}'
}

data_offload_allowed() {
  # return 0 if allowed, 3 if blocked
  if [[ ! -d "$DATA_ROOT" ]]; then
    echo "WARN no Data mount at $DATA_ROOT"
    return 0
  fi
  local pct
  pct="$(free_pct "$DATA_ROOT")"
  echo "CHECK Data=$DATA_ROOT free_pct=${pct} min=${MIN_DATA_FREE_PCT}"
  python3 - "$pct" "$MIN_DATA_FREE_PCT" <<'PY'
import sys
pct, mn = float(sys.argv[1]), float(sys.argv[2])
if pct < mn:
    print(f"BLOCK_OFFLOAD Data free_pct={pct:.2f} < {mn:.0f}% — update CAMPAIGN_STATUS; do not rsync")
    sys.exit(3)
print("OK_OFFLOAD_ALLOWED")
PY
}

cmd_check() {
  local home_path="${HOME_RUN_FS:-/home/user}"
  local ag
  ag="$(avail_g "$home_path" || echo 0)"
  echo "CHECK host=$HOSTTAG home_avail_G=${ag} warn_below=${WARN_HOME_AVAIL_G}"
  if [[ "${ag:-0}" -lt "$WARN_HOME_AVAIL_G" ]]; then
    echo "WARN_HOME_DISK avail=${ag}G < ${WARN_HOME_AVAIL_G}G — schedule offload of done runs; do NOT kill consoles"
  fi
  data_offload_allowed || true
}

verify_tree() {
  python3 - "$1" "$2" <<'PY'
import sys
from pathlib import Path

def stats(root: Path):
    n, b = 0, 0
    for p in root.rglob("*"):
        if p.is_file():
            n += 1
            b += p.stat().st_size
    return n, b

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
ns, bs = stats(src)
nd, bd = stats(dst)
print(f"verify src_files={ns} src_bytes={bs} dst_files={nd} dst_bytes={bd}")
if ns != nd or bs != bd:
    sys.exit(1)
PY
}

cmd_offload() {
  local dry="${1:-0}"
  shift || true
  [[ $# -gt 0 ]] || die "offload needs src dirs"
  if ! data_offload_allowed; then
    echo "BLOCKED: Data free_pct too low — refuse offload"
    exit 3
  fi
  mkdir -p "$OFFLOAD_ROOT"
  local src base dst
  for src in "$@"; do
    [[ -d "$src" ]] || { echo "SKIP missing $src"; continue; }
    if pgrep -af "NeuroModelerConsole.*$(basename "$src")" >/dev/null 2>&1; then
      echo "SKIP_ACTIVE $src"
      continue
    fi
    base="$(basename "$src")"
    dst="$OFFLOAD_ROOT/$base"
    echo "RSYNC $src -> $dst dry=$dry"
    if [[ "$dry" == "1" ]]; then
      rsync -a --dry-run "$src"/ "$dst"/
      continue
    fi
    rsync -a --info=stats2 "$src"/ "$dst"/
    verify_tree "$src" "$dst"
    rm -rf "$src"
    echo "OFFLOADED_OK $src -> $dst"
  done
}

case "${1:-check}" in
  check) cmd_check ;;
  offload-dry-run) shift; cmd_offload 1 "$@" ;;
  offload) shift; cmd_offload 0 "$@" ;;
  *) die "usage: $0 check|offload-dry-run|offload <dirs...>" ;;
esac
