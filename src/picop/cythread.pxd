# cythread.pxd
# GIL release + lock slice of ``cpython.pythread`` (cimport-only).
# TSS / start_new_thread left deferred.

from cpython.pystate cimport PyThreadState
from cpython.pythread cimport (
    NOWAIT_LOCK,
    PY_LOCK_ACQUIRED,
    PY_LOCK_FAILURE,
    PY_LOCK_INTR,
    PyThread_acquire_lock,
    PyThread_allocate_lock,
    PyThread_free_lock,
    PyThread_get_thread_ident,
    PyThread_release_lock,
    PyThread_type_lock,
    WAIT_LOCK,
)

cdef extern from "Python.h":
    PyThreadState *PyEval_SaveThread() nogil
    void PyEval_RestoreThread(PyThreadState *tstate) nogil


cdef inline PyThread_type_lock thread_allocate_lock():
    return PyThread_allocate_lock()


cdef inline void thread_free_lock(PyThread_type_lock lock):
    PyThread_free_lock(lock)


cdef inline int thread_acquire(PyThread_type_lock lock, int mode) nogil:
    return PyThread_acquire_lock(lock, mode)


cdef inline void thread_release(PyThread_type_lock lock) nogil:
    PyThread_release_lock(lock)


cdef inline long thread_get_ident():
    # Not nogil: Cython's ``PyThread_get_thread_ident`` is GIL-marked; a nogil
    # wrapper broke package-barrel cimports via ``__init__.pxd``.
    return PyThread_get_thread_ident()


cdef inline PyThreadState *eval_save_thread() nogil:
    return PyEval_SaveThread()


cdef inline void eval_restore_thread(PyThreadState *tstate) nogil:
    PyEval_RestoreThread(tstate)
# Order 077: PEP 788 interpreter guards / views (CPython 3.15+).
# Uniform void* handles; the shim branches on PY_VERSION_HEX so the API
# exists on 3.8-3.14 too (guard/view acquire raise, ensure falls back to
# PyGILState). Tokens are opaque — never pass them to PyThreadState APIs.
cdef extern from "cythread_shim.h":
    int guards_enabled "cy_interpreter_guards_enabled"() noexcept
    void *guard_from_current "cy_guard_from_current"() except NULL
    void *guard_from_view "cy_guard_from_view"(void *view)
    void guard_close "cy_guard_close"(void *guard) noexcept
    void *view_from_current "cy_view_from_current"() except NULL
    void *view_from_main "cy_view_from_main"()
    void view_close "cy_view_close"(void *view) noexcept
    void *threadstate_ensure "cy_threadstate_ensure"(void *guard) except NULL
    void *threadstate_ensure_from_view "cy_threadstate_ensure_from_view"(void *view) except NULL
    void threadstate_release "cy_threadstate_release"(void *token) noexcept

cpdef guards_supported()
cpdef interpreter_guard()
