#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PYTHON="${PYTHON:-python3}"
CONFIG="${SMH_Q_GATE_CONFIG:-bench/config_smoke.yaml}"
BASELINE="${SMH_Q_BASELINE:-artifacts/baseline.json}"
[[ -f "$BASELINE" ]] || { echo "Missing committed baseline: $BASELINE" >&2; exit 1; }
if [[ "${SMH_Q_BUILD_CYTHON:-OFF}" == "ON" ]]; then
  echo "The cython selector re-exports pure Python; it is not a native performance backend." >&2
  exit 1
fi
"$PYTHON" -c 'import sys; assert sys.version_info >= (3, 14)'
"$PYTHON" -m pip install -q 'pybind11>=3.1.0' pyyaml
ABI="$("$PYTHON" -c 'import sysconfig; print(sysconfig.get_config_var("SOABI"))')"
BUILD="$ROOT/build/$ABI"
STAGE="$BUILD/stage"
PYBIND11_DIR="$("$PYTHON" -m pybind11 --cmakedir)"
cmake -S native -B "$BUILD" -DCMAKE_BUILD_TYPE=Release \
  -DSMH_Q_BUILD_PYTHON=ON -DPython_EXECUTABLE="$PYTHON" -Dpybind11_DIR="$PYBIND11_DIR"
cmake --build "$BUILD" -j"$(nproc)"
mkdir -p "$STAGE/picoipc"
cp src/picoipc/*.py "$STAGE/picoipc/"
cmake --install "$BUILD" --prefix "$STAGE"
export SMH_Q_CPP_BUILD="$BUILD"
export SMH_Q_PYTHON_DIR="$STAGE"
export SMH_Q_LIB="$STAGE/picoipc/libsmh_q.so"
export PYTHONPATH="$STAGE"
export PICOIPC_BACKEND="${PICOIPC_BACKEND:-pybind11}"
echo "==> Running ctest"
ctest --test-dir "$BUILD" --output-on-failure
echo "==> Running harness ($CONFIG)"
SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
CANDIDATE="artifacts/bench_${SHA}.json"
"$PYTHON" bench/harness.py --config "$CONFIG" --output "$CANDIDATE"
"$PYTHON" bench/compare.py "$BASELINE" "$CANDIDATE"
