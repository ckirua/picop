#!/usr/bin/env bash
# Run smoke harness for every Python backend and print a comparison table.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
CONFIG="${SMH_Q_GATE_CONFIG:-bench/config_smoke.yaml}"
OUT_DIR="artifacts/backend_compare"
mkdir -p "$OUT_DIR"

export PYTHONPATH="${ROOT}/python:${PYTHONPATH:-}"

BUILD_PY="${SMH_Q_BUILD_PYTHON:-ON}"
if [[ "${SMH_Q_BUILD_CYTHON:-OFF}" == "ON" ]]; then
  cmake -S cpp -B cpp/build -DCMAKE_BUILD_TYPE=Release -DSMH_Q_BUILD_PYTHON=OFF
  cmake --build cpp/build -j"$(nproc)" --target smh_q_shared roundtrip stress producer consumer bench_sequential
  python3 -m pip install -q cython 2>/dev/null || true
  if [[ -f pyproject.toml ]]; then mv pyproject.toml pyproject.toml.bak; fi
  (cd python && python3 setup_cython.py build_ext --inplace) 2>/dev/null || true
  if [[ -f pyproject.toml.bak ]]; then mv pyproject.toml.bak pyproject.toml; fi
else
  PY_FLAG=OFF
  [[ "$BUILD_PY" == "ON" ]] && PY_FLAG=ON
  cmake -S cpp -B cpp/build -DCMAKE_BUILD_TYPE=Release -DSMH_Q_BUILD_PYTHON="$PY_FLAG"
  cmake --build cpp/build -j"$(nproc)"
  if [[ "$PY_FLAG" == "ON" ]]; then
    for _so in cpp/build/_native*.so; do
      if [[ -f "$_so" ]]; then
        cp -f "$_so" python/picoipc/_native.so
        cp -f "$_so" "python/picoipc/$(basename "$_so")"
      fi
    done
  fi
fi

BACKENDS=(pure ctypes pybind11 cython)

for backend in "${BACKENDS[@]}"; do
  export PICOIPC_BACKEND="$backend"
  outfile="${OUT_DIR}/${backend}.json"
  echo "==> Backend: ${PICOIPC_BACKEND}"
  set +e
  python3 bench/harness.py --config "$CONFIG" --output "$outfile"
  rc=$?
  set -e
  if [[ $rc -ne 0 ]]; then
    echo "    harness failed (exit $rc)"
    echo '{}' > "$outfile.failed"
    rm -f "$outfile"
  else
    rm -f "$outfile.failed"
  fi
done

python3 - "$OUT_DIR" "${BACKENDS[@]}" <<'PYINNER'
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
        rows.append({
            "backend": backend,
            "impl": "FAIL",
            "msgs_per_sec": None,
            "correctness": "FAIL",
            "wall_s": None,
            "note": "stub (no _cython_ring extension)" if backend == "cython" else "harness failed",
        })
        continue

    data = json.loads(path.read_text())
    impl = data.get("impl", "?")
    rate = data.get("sequential_msgs_per_sec_64b")
    correctness = "PASS" if data.get("correctness_pass", data.get("correctness_ok")) else "FAIL"
    wall_s = data.get("wall_s")
    note = ""
    if backend == "cython" and impl != "cython":
        note = "stub (no extension; fell back to " + impl + ")"
    elif impl != backend and backend not in ("pure", "pure_python") and impl != "pure_python":
        if backend == "pure" and impl == "pure_python":
            pass
        else:
            note = f"requested {backend}, got {impl}"

    rows.append({
        "backend": backend,
        "impl": impl,
        "msgs_per_sec": rate,
        "correctness": correctness,
        "wall_s": wall_s,
        "note": note,
    })
    if backend in ("pure", "pure_python") and rate:
        pure_rate = rate
    if pure_rate is None and impl in ("pure", "pure_python") and rate:
        pure_rate = rate

print()
print("=== picoipc backend comparison (smoke harness) ===")
print("config: bench/config_smoke.yaml")
print()
hdr = f"{'Backend':<10} {'Impl':<14} {'msgs/s (64B)':>16} {'vs pure':>10} {'correct':>9} {'wall_s':>8}  Note"
print(hdr)
print("-" * len(hdr))

for row in rows:
    rate = row["msgs_per_sec"]
    rate_str = f"{rate:,.0f}" if rate else "n/a"
    if rate and pure_rate and pure_rate > 0:
        speedup = rate / pure_rate
        vs_pure = f"{speedup:.2f}x"
    else:
        vs_pure = "n/a"
    wall = row["wall_s"]
    wall_str = f"{wall:.3f}" if wall is not None else "n/a"
    note = row["note"]
    print(
        f"{row['backend']:<10} {row['impl']:<14} {rate_str:>16} {vs_pure:>10} "
        f"{row['correctness']:>9} {wall_str:>8}  {note}"
    )

print()
if pure_rate:
    print(f"pure baseline: {pure_rate:,.0f} msgs/s (64B sequential)")
PYINNER
