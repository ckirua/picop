#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
CONFIG="${SMH_Q_GATE_CONFIG:-bench/config_smoke.yaml}"
BASELINE="${SMH_Q_BASELINE:-artifacts/baseline.json}"

BUILD_PY="${SMH_Q_BUILD_PYTHON:-ON}"
if [[ "${SMH_Q_BUILD_CYTHON:-OFF}" == "ON" ]]; then
  cmake -S cpp -B cpp/build -DCMAKE_BUILD_TYPE=Release -DSMH_Q_BUILD_PYTHON=OFF
  cmake --build cpp/build -j"$(nproc)" --target smh_q_shared roundtrip stress producer consumer bench_sequential
  python3 -m pip install -q cython 2>/dev/null || true
  if [[ -f python/pyproject.toml ]]; then mv python/pyproject.toml python/pyproject.toml.bak; fi
  (cd python && python3 setup_cython.py build_ext --inplace)
  if [[ -f python/pyproject.toml.bak ]]; then mv python/pyproject.toml.bak python/pyproject.toml; fi
else
  PY_FLAG=OFF
  [[ "$BUILD_PY" == "ON" ]] && PY_FLAG=ON
  cmake -S cpp -B cpp/build -DCMAKE_BUILD_TYPE=Release -DSMH_Q_BUILD_PYTHON="$PY_FLAG"
  cmake --build cpp/build -j"$(nproc)"
  if [[ "$PY_FLAG" == "ON" ]]; then
    for _so in cpp/build/_native*.so; do
      if [[ -f "$_so" ]]; then
        cp -f "$_so" python/smh_q/_native.so
        cp -f "$_so" "python/smh_q/$(basename "$_so")"
      fi
    done
  fi
fi

echo "==> Running ctest"
ctest --test-dir cpp/build --output-on-failure
python3 -c "import sys; assert sys.version_info >= (3, 14)"
echo "==> Running harness ($CONFIG)"
SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
CANDIDATE="artifacts/bench_${SHA}.json"
python3 -m pip install -q pyyaml 2>/dev/null || true
export PYTHONPATH="$ROOT/python:${PYTHONPATH:-}"
export SMH_Q_BACKEND="${SMH_Q_BACKEND:-pybind11}"
python3 bench/harness.py --config "$CONFIG" --output "$CANDIDATE"
if [[ ! -f "$BASELINE" ]]; then
  echo "==> No baseline — writing $BASELINE"
  cp "$CANDIDATE" "$BASELINE"
  echo "GATE: PASS (baseline established)"
  exit 0
fi
python3 bench/compare.py "$BASELINE" "$CANDIDATE"
