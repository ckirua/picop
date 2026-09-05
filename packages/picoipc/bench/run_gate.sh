#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
CONFIG="${SMH_Q_GATE_CONFIG:-bench/config_smoke.yaml}"
BASELINE="${SMH_Q_BASELINE:-artifacts/baseline.json}"

BUILD_PY="${SMH_Q_BUILD_PYTHON:-ON}"
if [[ "${SMH_Q_BUILD_CYTHON:-OFF}" == "ON" ]]; then
  cmake -S native -B build/native -DCMAKE_BUILD_TYPE=Release -DSMH_Q_BUILD_PYTHON=OFF
  cmake --build build/native -j"$(nproc)" --target smh_q_shared roundtrip stress producer consumer bench_sequential
  python3 -m pip install -q cython 2>/dev/null || true
  if [[ -f pyproject.toml ]]; then mv pyproject.toml pyproject.toml.bak; fi
  (cd src && python3 setup_cython.py build_ext --inplace)
  if [[ -f pyproject.toml.bak ]]; then mv pyproject.toml.bak pyproject.toml; fi
else
  PY_FLAG=OFF
  [[ "$BUILD_PY" == "ON" ]] && PY_FLAG=ON
  cmake -S native -B build/native -DCMAKE_BUILD_TYPE=Release -DSMH_Q_BUILD_PYTHON="$PY_FLAG"
  cmake --build build/native -j"$(nproc)"
  if [[ "$PY_FLAG" == "ON" ]]; then
    for _so in build/native/_native*.so; do
      if [[ -f "$_so" ]]; then
        cp -f "$_so" src/picoipc/_native.so
        cp -f "$_so" "src/picoipc/$(basename "$_so")"
      fi
    done
  fi
fi

echo "==> Running ctest"
ctest --test-dir build/native --output-on-failure
python3 -c "import sys; assert sys.version_info >= (3, 14)"
echo "==> Running harness ($CONFIG)"
SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
CANDIDATE="artifacts/bench_${SHA}.json"
python3 -m pip install -q pyyaml 2>/dev/null || true
export PYTHONPATH="$ROOT/src:${PYTHONPATH:-}"
export PICOIPC_BACKEND="${PICOIPC_BACKEND:-pybind11}"
python3 bench/harness.py --config "$CONFIG" --output "$CANDIDATE"
if [[ ! -f "$BASELINE" ]]; then
  echo "==> No baseline — writing $BASELINE"
  cp "$CANDIDATE" "$BASELINE"
  echo "GATE: PASS (baseline established)"
  exit 0
fi
python3 bench/compare.py "$BASELINE" "$CANDIDATE"
