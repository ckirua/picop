# Agent guidance (picoipc)

`picoipc` owns low-latency local IPC primitives. The current backend is the Linux POSIX shared-memory SPSC ring implemented by the bundled `smh_q` C++ engine.

- Keep queue semantics explicit: SPSC, MPSC, and MPMC are different contracts, not interchangeable modes.
- Do not add network brokers, durable messaging, or generic `asyncio` queue wrappers here.
- Preserve the shared-memory wire layout across C++, ctypes, pure Python, and pybind11 implementations unless a versioned protocol change is intended.
- Keep Linux-specific code isolated to this package; `picop` remains independently installable.
- Run `./bench/run_gate.sh` from this directory for the correctness and performance gate.
