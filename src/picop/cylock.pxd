# cylock.pxd
# CPython `PyMutex` primitives (cimport-only, CPython 3.14+).
# No Python API: a mutex is a one-byte value the extension author declares.
#
# Typical pattern:
#   cdef PyMutex mu
#   mutex_init(&mu)          # optional: zero-init means unlocked
#   mutex_lock(&mu)
#   ...  # mutate shared state
#   mutex_unlock(&mu)
#   assert not mutex_is_locked(&mu)

from libc.string cimport memset

cdef extern from "Python.h" nogil:
    # CPython documents the struct contents as private; the field is declared
    # only so Cython can size a stack-local `PyMutex`. Never read or write it.
    ctypedef struct PyMutex:
        unsigned char _bits

    void PyMutex_Lock(PyMutex *m)
    void PyMutex_Unlock(PyMutex *m)
    int PyMutex_IsLocked(PyMutex *m)


cdef inline void mutex_init(PyMutex *m) noexcept nogil:
    memset(m, 0, sizeof(PyMutex))


cdef inline void mutex_lock(PyMutex *m) noexcept nogil:
    PyMutex_Lock(m)


cdef inline void mutex_unlock(PyMutex *m) noexcept nogil:
    PyMutex_Unlock(m)


cdef inline bint mutex_is_locked(PyMutex *m) noexcept nogil:
    return PyMutex_IsLocked(m)
