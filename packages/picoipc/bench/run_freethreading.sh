#!/usr/bin/env bash
# Compare python3.14 (GIL) vs python3.14t (free-threaded) on config_full.yaml.
# Set SMH_Q_FREETHREADING=1 to run the no-GIL interpreter only.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG="${SMH_Q_GATE_CONFIG:-bench/config_full.yaml}"
export PYTHONPATH="${ROOT}/python:${PYTHONPATH:-}"
export PICOIPC_BACKEND="${PICOIPC_BACKEND:-pybind11}"

python3.14 -m pip install -q --break-system-packages pyyaml 2>/dev/null || true
python3.14t -m pip install -q --break-system-packages pyyaml 2>/dev/null || true

if [[ "${SMH_Q_FREETHREADING:-}" == "1" ]]; then
  exec python3.14t "${ROOT}/bench/harness.py" --config "$CONFIG" "$@"
fi

python3.14 "${ROOT}/bench/harness.py" --config "$CONFIG" --output "${ROOT}/artifacts/bench_py314_gil.json"
python3.14t "${ROOT}/bench/harness.py" --config "$CONFIG" --output "${ROOT}/artifacts/bench_py314_nogil.json"
