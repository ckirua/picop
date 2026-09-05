#!/usr/bin/env bash
# Build (if needed) and run a Tier B module harness.
#
# Usage (from repo root):
#   ./bench/tier_b/run.sh cytuple
#   ./bench/tier_b/run.sh --build-only
#   ./bench/tier_b/run.sh --all

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"

pick_python() {
  local candidate candidates=()
  if [[ -n "${PYTHON:-}" ]]; then
    candidates+=("$PYTHON")
  fi
  if [[ -n "${VIRTUAL_ENV:-}" && -x "${VIRTUAL_ENV}/bin/python" ]]; then
    candidates+=("${VIRTUAL_ENV}/bin/python")
  fi
  if [[ -x "$ROOT/.venv/bin/python" ]]; then
    candidates+=("$ROOT/.venv/bin/python")
  fi
  if command -v python3.14 >/dev/null 2>&1; then
    candidates+=("$(command -v python3.14)")
  fi
  for candidate in "${candidates[@]}"; do
    [[ -n "$candidate" && -x "$candidate" ]] || continue
    if "$candidate" -c "import cypy, Cython" >/dev/null 2>&1; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

if ! PYTHON="$(pick_python)"; then
  echo "error: need python with cypy + Cython (activate .venv)" >&2
  exit 1
fi

cd "$ROOT"

if [[ "${1:-}" == "--build-only" ]]; then
  shift
  exec "$PYTHON" -m bench.tier_b.build "$@"
fi

if [[ "${1:-}" == "--all" ]]; then
  "$PYTHON" -m bench.tier_b.build
  failed=0
  for py in "$HERE"/*.py; do
    base="$(basename "$py" .py)"
    case "$base" in
      __init__|build|_tb_util|_gen_*) continue ;;
    esac
    echo ">>> tier_b $base"
    if ! "$PYTHON" -m "bench.tier_b.$base"; then
      failed=1
    fi
  done
  exit "$failed"
fi

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <module>|--all|--build-only [modules...]" >&2
  exit 2
fi

mod="$1"
if [[ "$mod" == "cyeq_inventory" ]]; then
  "$PYTHON" -m bench.tier_b.build cyeq_containers cyeq_buffers cyeq_scalars cyeq_misc
  exec "$PYTHON" -m bench.tier_b.cyeq_inventory
fi
"$PYTHON" -m bench.tier_b.build "$mod"
exec "$PYTHON" -m "bench.tier_b.$mod"
