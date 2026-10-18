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
    # wrapper broke package-barrel ``from cypy cimport`` via ``__init__.pxd``.
    return PyThread_get_thread_ident()


cdef inline PyThreadState *eval_save_thread() nogil:
    return PyEval_SaveThread()


cdef inline void eval_restore_thread(PyThreadState *tstate) nogil:
    PyEval_RestoreThread(tstate)
