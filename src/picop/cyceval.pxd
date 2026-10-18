# cyceval.pxd
# Eval / GIL init helpers. cimport-only (process-wide).
# PyEval_ThreadsInitialized was removed; treat threads as always initialized on
# modern CPython (3.14+ / this package's floor).

cdef extern from "Python.h":
    void PyEval_InitThreads() noexcept


cdef inline void eval_init_threads() noexcept:
    # No-op on modern CPython once runtime started; kept for Completeness.
    PyEval_InitThreads()


cdef inline bint eval_threads_initialized() noexcept:
    return True
