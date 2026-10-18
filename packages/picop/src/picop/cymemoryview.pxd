# cymemoryview.pxd
# ``memoryview`` helpers. Public docs in ``cymemoryview.pyi``.
# FromMemory / FromBuffer / GET_* macros: cdef (pointers / lifetime).

import cython

from cpython.buffer cimport (
    Py_buffer, PyBUF_FULL_RO, PyBUF_READ, PyBUF_WRITE,
    PyBuffer_IsContiguous, PyBuffer_Release, PyObject_GetBuffer,
)
from cpython.object cimport PyObject, PyObject_RichCompareBool, Py_EQ
from libc.stddef cimport size_t
from libc.string cimport memcmp, strcmp


cdef extern from "Python.h":
    memoryview PyMemoryView_FromObject(object obj)
    memoryview PyMemoryView_FromMemory(char *mem, Py_ssize_t size, int flags)
    memoryview PyMemoryView_FromBuffer(Py_buffer *view)
    memoryview PyMemoryView_GetContiguous(object obj, int buffertype, char order)
    bint PyMemoryView_Check(object obj) noexcept
    Py_buffer *PyMemoryView_GET_BUFFER(object mview) noexcept
    PyObject* PyMemoryView_GET_BASE(object mview) noexcept


cdef inline bint mvcheck(object p) noexcept:
    return PyMemoryView_Check(p)


cdef inline bint mveq(memoryview a, memoryview b):
    # Acquire independent exports so metadata and data pointers stay valid.
    if a is b:
        return True
    cdef Py_buffer va
    cdef Py_buffer vb
    cdef int i
    cdef size_t nbytes
    if PyObject_GetBuffer(a, &va, PyBUF_FULL_RO) < 0:
        raise
    try:
        if PyObject_GetBuffer(b, &vb, PyBUF_FULL_RO) < 0:
            raise
        try:
            if va.ndim != vb.ndim or va.itemsize != vb.itemsize or va.len != vb.len:
                return False
            if va.format is NULL or vb.format is NULL:
                if va.format is not vb.format:
                    return <bint>PyObject_RichCompareBool(a, b, Py_EQ)
            elif strcmp(va.format, vb.format) != 0:
                return False
            if va.shape is not NULL and vb.shape is not NULL:
                for i in range(va.ndim):
                    if va.shape[i] != vb.shape[i]:
                        return False
            if not PyBuffer_IsContiguous(&va, b'C') or not PyBuffer_IsContiguous(&vb, b'C'):
                return <bint>PyObject_RichCompareBool(a, b, Py_EQ)
            nbytes = <size_t>va.len
            if nbytes == 0:
                return True
            return memcmp(va.buf, vb.buf, nbytes) == 0
        finally:
            PyBuffer_Release(&vb)
    finally:
        PyBuffer_Release(&va)

cdef inline bint mvne(memoryview a, memoryview b):
    return not mveq(a, b)


cdef inline memoryview mvfrom_object(object obj):
    return PyMemoryView_FromObject(obj)


cdef inline memoryview mvget_contiguous(object obj, int buffertype=PyBUF_READ, str order="C"):
    # order must be a single char 'C' / 'F' / 'A'.
    cdef bytes ob = order.encode("ascii")
    cdef char *op = ob
    return PyMemoryView_GetContiguous(obj, buffertype, op[0])


cdef inline memoryview mvfrom_memory(char *mem, Py_ssize_t size, int flags=PyBUF_READ):
    # Caller owns ``mem`` for the lifetime of the view.
    return PyMemoryView_FromMemory(mem, size, flags)


cdef inline memoryview mvfrom_buffer(Py_buffer *view):
    return PyMemoryView_FromBuffer(view)


cdef inline Py_buffer *mvget_buffer(memoryview mview) noexcept:
    # Caller retains a valid, unreleased view and synchronizes all pointer use.
    return PyMemoryView_GET_BUFFER(mview)


cdef inline object mvget_base(memoryview mview) noexcept:
    cdef PyObject* pointer
    cdef object owner
    with cython.critical_section(mview):
        pointer = PyMemoryView_GET_BASE(mview)
        if pointer is NULL:
            return None
        owner = <object>pointer
    return owner

# Wave 4 N1/N5 preferred names (0.3: soft letter/bare are cdef-only)

cpdef inline bint memoryview_check(object p) noexcept:
    return mvcheck(p)

cpdef inline bint memoryview_eq(memoryview a, memoryview b):
    return mveq(a, b)

cpdef inline bint memoryview_ne(memoryview a, memoryview b):
    return mvne(a, b)

cdef inline memoryview memoryview_from_buffer(Py_buffer *view):
    return mvfrom_buffer(view)

cdef inline memoryview memoryview_from_memory(char *mem, Py_ssize_t size, int flags=PyBUF_READ):
    return mvfrom_memory(mem, size, flags)

cpdef inline memoryview memoryview_from_object(object obj):
    return mvfrom_object(obj)

cdef inline object memoryview_get_base(memoryview mview) noexcept:
    return mvget_base(mview)

cpdef inline memoryview memoryview_get_contiguous(object obj, int buffertype=PyBUF_READ, str order="C"):
    return mvget_contiguous(obj, buffertype, order)


cpdef inline Py_ssize_t memoryview_nbytes(memoryview mview) noexcept:
    with cython.critical_section(mview):
        return PyMemoryView_GET_BUFFER(mview).len


cpdef inline Py_ssize_t memoryview_itemsize(memoryview mview) noexcept:
    with cython.critical_section(mview):
        return PyMemoryView_GET_BUFFER(mview).itemsize


cpdef inline int memoryview_ndim(memoryview mview) noexcept:
    with cython.critical_section(mview):
        return PyMemoryView_GET_BUFFER(mview).ndim


cpdef inline bint memoryview_readonly(memoryview mview) noexcept:
    with cython.critical_section(mview):
        return PyMemoryView_GET_BUFFER(mview).readonly != 0

