#!/usr/bin/env bash
# Compare a regular Python build with its free-threaded counterpart (Python 3.15 by default).
# Set SMH_Q_FREETHREADING=1 to run only the free-threaded interpreter.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
CONFIG="${SMH_Q_GATE_CONFIG:-bench/config_full.yaml}"
BACKEND="${PICOIPC_BACKEND:-pybind11}"
PYTHON_REGULAR="${SMH_Q_PYTHON_GIL:-python3.15}"
PYTHON_NOGIL="${SMH_Q_PYTHON_NOGIL:-python3.15t}"
# The t lane must prove an unforced disabled-GIL import.
unset PYTHON_GIL

prepare_runtime() {
  local base_python="$1"
  local label="$2"
  local is_nogil="$3"
  local soabi venv python build stage executable
  soabi="$("$base_python" -c 'import sysconfig; print(sysconfig.get_config_var("SOABI"))')"
  venv="$ROOT/.venv-freethreading/$soabi"
  python="$venv/bin/python"
  build="$ROOT/build/$soabi"
  stage="$build/stage"
  if [[ ! -x "$python" ]]; then
    mkdir -p "$(dirname "$venv")"
    "$base_python" -m venv "$venv"
  fi
  "$python" -m pip install --quiet --upgrade 'pybind11>=3.1.0' pyyaml
  executable="$("$python" -c 'import sys; print(sys.executable)')"
  cmake -S native -B "$build" -DCMAKE_BUILD_TYPE=Release \
    -DSMH_Q_BUILD_PYTHON=ON -DPython_EXECUTABLE="$executable" \
    -Dpybind11_DIR="$("$python" -m pybind11 --cmakedir)"
  cmake --build "$build" -j"$(nproc)"
  mkdir -p "$stage/picoipc"
  cp src/picoipc/*.py "$stage/picoipc/"
  cmake --install "$build" --prefix "$stage"
  export PYTHONPATH="$stage"
  export SMH_Q_CPP_BUILD="$build"
  export SMH_Q_PYTHON_DIR="$stage"
  export SMH_Q_LIB="$stage/picoipc/libsmh_q.so"
  export PICOIPC_BACKEND="$BACKEND"
  if [[ "$is_nogil" == "1" ]]; then
    "$python" - <<'PY'
import os
import sys
assert not sys._is_gil_enabled(), 'free-threaded interpreter started with the GIL enabled'
import picoipc
expected = {'pure': 'pure_python'}.get(os.environ['PICOIPC_BACKEND'], os.environ['PICOIPC_BACKEND'])
assert picoipc.impl_name() == expected, (picoipc.impl_name(), expected)
assert not sys._is_gil_enabled(), 'GIL became enabled after package/backend import'
print('actual backend:', picoipc.impl_name(), 'GIL enabled:', sys._is_gil_enabled())
PY
  else
    "$python" -c 'import picoipc, os; expected = {"pure": "pure_python"}.get(os.environ["PICOIPC_BACKEND"], os.environ["PICOIPC_BACKEND"]); assert picoipc.impl_name() == expected; print("actual backend:", picoipc.impl_name())'
  fi
  mkdir -p "$ROOT/artifacts"
  "$python" bench/harness.py --config "$CONFIG" --output "$ROOT/artifacts/bench_${soabi}_${label}.json"
}

if [[ "${SMH_Q_FREETHREADING:-}" == "1" ]]; then
  prepare_runtime "$PYTHON_NOGIL" nogil 1
else
  prepare_runtime "$PYTHON_REGULAR" gil 0
  prepare_runtime "$PYTHON_NOGIL" nogil 1
fi
