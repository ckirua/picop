#!/usr/bin/env bash
# Run correctness/performance smoke harnesses for each implemented Python backend.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PYTHON="${PYTHON:-python3}"
CONFIG="${SMH_Q_GATE_CONFIG:-bench/config_smoke.yaml}"
OUT_DIR="artifacts/backend_compare"
mkdir -p "$OUT_DIR"
"$PYTHON" -m pip install -q 'pybind11>=3.1.0' pyyaml

ABI="$("$PYTHON" -c 'import sysconfig; print(sysconfig.get_config_var("SOABI"))')"
BUILD="${SMH_Q_BUILD_DIR:-$ROOT/build/$ABI}"
STAGE="$BUILD/stage"
PYBIND11_DIR="$("$PYTHON" -m pybind11 --cmakedir)"
cmake -S native -B "$BUILD" -DCMAKE_BUILD_TYPE=Release \
  -DSMH_Q_BUILD_PYTHON=ON -DPython_EXECUTABLE="$("$PYTHON" -c 'import sys; print(sys.executable)')" \
  -Dpybind11_DIR="$PYBIND11_DIR"
cmake --build "$BUILD" -j"$(nproc)"
mkdir -p "$STAGE/picoipc"
cp src/picoipc/*.py "$STAGE/picoipc/"
cmake --install "$BUILD" --prefix "$STAGE"
export PYTHONPATH="$STAGE"
export SMH_Q_CPP_BUILD="$BUILD"
export SMH_Q_PYTHON_DIR="$STAGE"
export SMH_Q_LIB="$STAGE/picoipc/libsmh_q.so"

BACKENDS=(pure ctypes pybind11)
for backend in "${BACKENDS[@]}"; do
  export PICOIPC_BACKEND="$backend"
  outfile="${OUT_DIR}/${backend}.json"
  echo "==> Backend: ${PICOIPC_BACKEND} ($PYTHON)"
  set +e
  "$PYTHON" -c 'import os, picoipc; actual = picoipc.impl_name(); expected = os.environ["PICOIPC_BACKEND"]; expected = {"pure": "pure_python"}.get(expected, expected); print("actual backend:", actual); assert actual == expected'
  rc=$?
  if [[ $rc -eq 0 ]]; then
    "$PYTHON" bench/harness.py --config "$CONFIG" --output "$outfile"
    rc=$?
  fi
  set -e
  if [[ $rc -ne 0 ]]; then
    echo "    harness/backend check failed (exit $rc)"
    echo '{}' > "$outfile.failed"
    rm -f "$outfile"
  else
    rm -f "$outfile.failed"
  fi
done

"$PYTHON" - "$OUT_DIR" "${BACKENDS[@]}" <<'PYINNER'
import json
import sys
from pathlib import Path

out_dir = Path(sys.argv[1])
backends = sys.argv[2:]
rows = []
pure_rate = None
for backend in backends:
    path = out_dir / f"{backend}.json"
    failed = path.with_suffix(".json.failed").exists() or not path.exists()
    if failed:
        rows.append({"backend": backend, "impl": "FAIL", "msgs_per_sec": None,
                     "correctness": "FAIL", "wall_s": None, "note": "harness/backend failed"})
        continue
    data = json.loads(path.read_text())
    impl = data.get("impl", "?")
    rate = data.get("sequential_msgs_per_sec_64b")
    correctness = "PASS" if data.get("correctness_pass", data.get("correctness_ok")) else "FAIL"
    wall_s = data.get("wall_s")
    rows.append({"backend": backend, "impl": impl, "msgs_per_sec": rate,
                 "correctness": correctness, "wall_s": wall_s, "note": ""})
    if backend == "pure" and rate:
        pure_rate = rate

print("\n=== picoipc backend comparison (smoke harness) ===\n")
hdr = f"{'Backend':<10} {'Impl':<14} {'msgs/s (64B)':>16} {'vs pure':>10} {'correct':>9} {'wall_s':>8}  Note"
print(hdr)
print("-" * len(hdr))
for row in rows:
    rate = row["msgs_per_sec"]
    rate_str = f"{rate:,.0f}" if rate else "n/a"
    vs_pure = f"{rate / pure_rate:.2f}x" if rate and pure_rate else "n/a"
    wall = row["wall_s"]
    wall_str = f"{wall:.3f}" if wall is not None else "n/a"
    print(f"{row['backend']:<10} {row['impl']:<14} {rate_str:>16} {vs_pure:>10} "
          f"{row['correctness']:>9} {wall_str:>8}  {row['note']}")
if pure_rate:
    print(f"\npure baseline: {pure_rate:,.0f} msgs/s (64B sequential)")
PYINNER
