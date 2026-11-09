# cyhash.pxd
# Buffer / pointer hashing helpers. Public docs in ``cyhash.pyi``.
# Raw-pointer helpers are cdef (trusted-caller memory, see docs/SAFETY.md).

from cpython.buffer cimport Py_buffer, PyBUF_SIMPLE, PyObject_GetBuffer, PyBuffer_Release
from cpython.object cimport PyObject


cdef extern from "Python.h":
    Py_hash_t Py_HashBuffer(const void *ptr, Py_ssize_t length) noexcept
    Py_hash_t Py_HashPointer(const void *ptr) noexcept
    Py_hash_t PyObject_GenericHash(PyObject *obj) noexcept


cdef inline Py_hash_t hbraw(const void *ptr, Py_ssize_t length) noexcept:
    return Py_HashBuffer(ptr, length)


cdef inline Py_hash_t hbobject(object data, Py_ssize_t start, Py_ssize_t end):
    cdef Py_buffer buf
    if PyObject_GetBuffer(data, &buf, PyBUF_SIMPLE) < 0:
        raise
    try:
        if end < 0:
            end = buf.len
        if start < 0 or end > buf.len or end < start:
            raise ValueError("hash_buffer() range out of bounds")
        return Py_HashBuffer(<const void *>buf.buf + start, end - start)
    finally:
        PyBuffer_Release(&buf)


cpdef inline Py_hash_t hash_buffer(object data, Py_ssize_t start=0, Py_ssize_t end=-1):
    return hbobject(data, start, end)


cdef inline Py_hash_t hash_buffer_raw(const void *ptr, Py_ssize_t length) noexcept:
    # Caller owns ``ptr`` and guarantees ``length`` readable bytes.
    return hbraw(ptr, length)


cdef inline Py_hash_t hash_pointer(const void *ptr) noexcept:
    return Py_HashPointer(ptr)


cdef inline Py_hash_t hash_generic(object obj) noexcept:
    # Identity hash: ignores a type's own ``__hash__``.
    return PyObject_GenericHash(<PyObject *>obj)
