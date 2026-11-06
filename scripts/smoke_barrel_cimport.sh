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
assert demo.check_sentinels()
assert demo.check_locks()
import threading
import time

holder = threading.Thread(target=demo.hold_shared, args=(0.3,))
holder.start()
time.sleep(0.1)
assert demo.shared_is_locked(), "mutex state not visible across threads"
holder.join()
assert not demo.shared_is_locked()

def _frame_probe():
    values = [1, 2]
    return demo.check_frames(sys._getframe())

assert _frame_probe()
assert demo.check_code()
assert demo.check_traceback()
assert demo.check_direct_uuid()
assert demo.check_memoryview_ownership()
assert not free or not sys._is_gil_enabled()
print("barrel/direct cimport behavior ok; GIL enabled:", sys._is_gil_enabled())
PY
