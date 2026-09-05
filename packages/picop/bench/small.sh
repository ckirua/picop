#!/usr/bin/env bash
# Run cypy benchmarks and save combined output under results/.
#
# Usage (from repo root):
#   ./bench/small.sh
#
# Override:
#   PYTHON=/path/to/python3.14 CPY_BENCH_N=200000 ./bench/small.sh

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
RESULTS_DIR="$HERE/results"
mkdir -p "$RESULTS_DIR"

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
  if command -v python3 >/dev/null 2>&1; then
    candidates+=("$(command -v python3)")
  fi
  for candidate in "${candidates[@]}"; do
    [[ -n "$candidate" && -x "$candidate" ]] || continue
    if "$candidate" -c "import cypy" >/dev/null 2>&1; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

if ! PYTHON="$(pick_python)"; then
  echo "error: no python with cypy installed (activate .venv or set PYTHON=...)" >&2
  exit 1
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$RESULTS_DIR/cypy-bench_${STAMP}.txt"
LATEST="$RESULTS_DIR/latest.txt"

git_rev=""
if command -v git >/dev/null 2>&1 && git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git_rev="$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || true)"
fi

run_all() {
  echo "cypy benchmarks (tier A = vs plain Python unless noted)"
  echo "timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "python: $($PYTHON --version 2>&1)"
  if [[ -n "$git_rev" ]]; then
    echo "git: $git_rev"
  fi
  echo "config: n=${CPY_BENCH_N:-80000} runs=${CPY_BENCH_RUNS:-5} warmup=${CPY_BENCH_WARMUP:-0}"
  echo "  ratio < 1.0 → cypy wins  |  ≥5% gate → ratio ≤ 0.95"
  echo "========================================"
  echo

  local bench failed=0
  for bench in "$HERE"/*_bench.py; do
    [[ -f "$bench" ]] || continue
    echo ">>> $(basename "$bench")"
    echo "----------------------------------------"
    if (cd "$HERE" && "$PYTHON" "$bench"); then
      :
    else
      echo "FAILED: $(basename "$bench")"
      failed=1
    fi
    echo
  done

  echo "========================================"
  if [[ "$failed" -eq 0 ]]; then
    echo "all benchmarks completed"
  else
    echo "one or more benchmarks failed"
  fi

  return "$failed"
}

set +e
run_all | tee "$OUT" | tee "$LATEST"
status=${PIPESTATUS[0]}
set -e

echo
echo "Results saved to bench/results/"

exit "$status"
