# Changelog

## Unreleased

- Make CPython 3.15 primary while retaining 3.14 and genuine GIL-disabled 3.14t/3.15t operation. Build each interpreter ABI independently with pybind11 3.1 or newer.
- Pin native/ctypes handle lifetimes across operations and coordinate concurrent close calls. Native claim views own their mapping, including derived views retained after logical close.
- Validate native contiguous byte buffers and writable consume destinations; publish bytes directly without intermediate string/vector copies.
- Use acquire/release lock-free libatomic counters in the pure Python backend. Require Linux x86_64 and libatomic.so.1 for this backend; fail explicitly when unavailable.
- Package libsmh_q.so for installed ctypes use and expose live sequence queries through the C API.
- Report the legacy `cython` selector as its actual `pure_python` implementation; it is not a separate native backend or a no-GIL performance result.
- Preserve the SPSC protocol and shared-memory layout. Keep the committed 3.14 pybind11 performance baseline separate from four-runtime correctness and immutable-sdist release validation.
