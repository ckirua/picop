#!/usr/bin/env bash
# Smoke: out-of-tree extension with barrel and direct cimports against installed picop.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EXT="${ROOT}/examples/cimport_ext"

PYTHON="${PYTHON:-python3.15}"
"$PYTHON" -c "import picop; print('picop', picop.__version__)"

cd "${EXT}"
rm -f demo.c demo*.so demo*.pyd
"$PYTHON" setup.py build_ext --inplace
"$PYTHON" - <<'PY'
import sys
import sysconfig

free = bool(sysconfig.get_config_var("Py_GIL_DISABLED"))
assert not free or not sys._is_gil_enabled()
import demo
assert not free or not sys._is_gil_enabled()
assert demo.check_barrel()
assert demo.check_submodule() == 2
assert demo.check_uuid()
assert demo.check_ownership()
assert demo.check_containers()
assert demo.check_direct_uuid()
assert demo.check_memoryview_ownership()
assert not free or not sys._is_gil_enabled()
print("barrel/direct cimport behavior ok; GIL enabled:", sys._is_gil_enabled())
PY
