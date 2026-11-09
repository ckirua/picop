#!/usr/bin/env bash
# Smoke: out-of-tree extension with barrel and direct cimports against installed picop.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EXT="${ROOT}/examples/cimport_ext"

PYTHON="${PYTHON:-python3.15}"
# Resolve relative interpreter paths against the repo, since the build runs inside the extension dir.
if [[ "${PYTHON}" != /* ]]; then
  PYTHON="${ROOT}/${PYTHON}"
fi
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
assert demo.check_lock_contention(), "mutex-protected counter lost updates"

def _frame_probe():
    values = [1, 2]
    return demo.check_frames(sys._getframe())

assert _frame_probe()
assert demo.check_code()
monitoring = sys.monitoring
tool_id = 4
code = demo.check_monitoring.__code__
seen = []

def monitoring_callback(*args):
    if args[0] is code:
        seen.append(args)

monitoring.use_tool_id(tool_id, "picop smoke")
monitoring.register_callback(tool_id, monitoring.events.LINE, monitoring_callback)
monitoring.register_callback(tool_id, monitoring.events.PY_RETURN, monitoring_callback)
events = monitoring.events.LINE | monitoring.events.PY_RETURN
monitoring.set_events(tool_id, events)
try:
    active, fired_line, fired_return, instrumented = demo.check_monitoring(code)
    assert active, "monitoring scope did not observe active LINE tool"
    assert fired_line == 0 and fired_return == 0
    assert instrumented
    assert len(seen) == 2, seen
finally:
    monitoring.set_events(tool_id, 0)
    monitoring.free_tool_id(tool_id)

active, fired_line, fired_return, instrumented = demo.check_monitoring(code)
assert active == 0, active
assert len(seen) == 2, seen
print("cymonitoring scope and fire callbacks ok")

assert demo.check_traceback()
assert demo.check_direct_uuid()
assert demo.check_memoryview_ownership()
assert demo.check_hashing()
assert demo.check_errors()
assert demo.check_memory()
assert demo.check_thread_locks()
assert demo.check_atomics()
assert demo.check_long_repr()
assert demo.check_refs()
assert demo.check_arg_unpack((1, 2), {"n": 3})
assert demo.check_ceval()
assert demo.check_pystate()
assert demo.check_lifecycle()
assert demo.check_port_and_version()
assert not free or not sys._is_gil_enabled()
print("barrel/direct cimport behavior ok; GIL enabled:", sys._is_gil_enabled())
PY
