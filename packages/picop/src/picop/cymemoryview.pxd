# cymemoryview.pxd
# ``memoryview`` helpers. Public docs in ``cymemoryview.pyi``.
# FromMemory / FromBuffer / GET_* macros: cdef (pointers / lifetime).

from cpython.buffer cimport Py_buffer, PyBUF_READ, PyBUF_WRITE, PyBuffer_IsContiguous
from cpython.object cimport PyObject_RichCompareBool, Py_EQ
from libc.stddef cimport size_t
from libc.string cimport memcmp, strcmp


cdef extern from "Python.h":
    memoryview PyMemoryView_FromObject(object obj)
    memoryview PyMemoryView_FromMemory(char *mem, Py_ssize_t size, int flags)
    memoryview PyMemoryView_FromBuffer(Py_buffer *view)
    memoryview PyMemoryView_GetContiguous(object obj, int buffertype, char order)
    bint PyMemoryView_Check(object obj) noexcept
    Py_buffer *PyMemoryView_GET_BUFFER(object mview) noexcept
    object PyMemoryView_GET_BASE(object mview) noexcept


cdef inline bint mvcheck(object p) noexcept:
    return PyMemoryView_Check(p)


cdef inline bint mveq(memoryview a, memoryview b):
    # Contiguous same-layout fast path; else richcompare (correct for strides).
    if a is b:
        return True
    cdef Py_buffer *pa = PyMemoryView_GET_BUFFER(a)
    cdef Py_buffer *pb = PyMemoryView_GET_BUFFER(b)
    cdef int i
    cdef size_t nbytes
    if pa.ndim != pb.ndim or pa.itemsize != pb.itemsize or pa.len != pb.len:
        return False
    if pa.format is NULL or pb.format is NULL:
        if pa.format is not pb.format:
            return <bint>PyObject_RichCompareBool(a, b, Py_EQ)
    elif strcmp(pa.format, pb.format) != 0:
        return False
    if pa.shape is not NULL and pb.shape is not NULL:
        for i in range(pa.ndim):
            if pa.shape[i] != pb.shape[i]:
                return False
    if not PyBuffer_IsContiguous(pa, b'C') or not PyBuffer_IsContiguous(pb, b'C'):
        return <bint>PyObject_RichCompareBool(a, b, Py_EQ)
    nbytes = <size_t>pa.len
    if nbytes == 0:
        return True
    return memcmp(pa.buf, pb.buf, nbytes) == 0


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
    # Private exporter buffer; mview must be a memoryview.
    return PyMemoryView_GET_BUFFER(mview)


cdef inline object mvget_base(memoryview mview) noexcept:
    # Exporting object, or None if FromMemory/FromBuffer.
    return PyMemoryView_GET_BASE(mview)

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

