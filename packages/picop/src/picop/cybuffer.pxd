# cybuffer.pxd
# Buffer protocol helpers. Public docs in ``cybuffer.pyi``.
# ``Py_buffer*`` / Fill* / contiguous utils: cdef (caller-managed views).

from cpython.buffer cimport (
    Py_buffer,
    PyBUF_FULL_RO,
    PyBuffer_FillContiguousStrides,
    PyBuffer_FillInfo,
    PyBuffer_FromContiguous,
    PyBuffer_GetPointer,
    PyBuffer_IsContiguous,
    PyBuffer_Release,
    PyBuffer_SizeFromFormat,
    PyBuffer_ToContiguous,
    PyObject_CheckBuffer,
    PyObject_CopyData,
    PyObject_GetBuffer,
)
from cpython.object cimport PyObject_RichCompareBool, Py_EQ
from libc.stddef cimport size_t
from libc.string cimport memcmp, strcmp


cpdef inline bint buf_check(object obj) noexcept:
    return PyObject_CheckBuffer(obj)


cpdef inline int buf_copy_data(object dest, object src) except -1:
    return PyObject_CopyData(dest, src)


cdef inline bint buceq(object a, object b):
    # Abstract buffer-protocol equality (not a concrete bytes/bytearray type).
    # Contiguous same-layout → memcmp; else memoryview richcompare fallback.
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
                    return <bint>PyObject_RichCompareBool(memoryview(a), memoryview(b), Py_EQ)
            elif strcmp(va.format, vb.format) != 0:
                return False
            if va.shape is not NULL and vb.shape is not NULL:
                for i in range(va.ndim):
                    if va.shape[i] != vb.shape[i]:
                        return False
            if not PyBuffer_IsContiguous(&va, b'C') or not PyBuffer_IsContiguous(&vb, b'C'):
                return <bint>PyObject_RichCompareBool(memoryview(a), memoryview(b), Py_EQ)
            nbytes = <size_t>va.len
            if nbytes == 0:
                return True
            return memcmp(va.buf, vb.buf, nbytes) == 0
        finally:
            PyBuffer_Release(&vb)
    finally:
        PyBuffer_Release(&va)


cpdef inline bint buf_eq(object a, object b):
    return buceq(a, b)


cdef inline int buf_get(object obj, Py_buffer *view, int flags) except -1:
    return PyObject_GetBuffer(obj, view, flags)


cdef inline void buf_release(Py_buffer *view) noexcept:
    PyBuffer_Release(view)


cdef inline void *buf_get_pointer(Py_buffer *view, Py_ssize_t *indices) noexcept:
    return PyBuffer_GetPointer(view, indices)


cdef inline Py_ssize_t buf_size_from_format(const char *fmt) except -1:
    return PyBuffer_SizeFromFormat(fmt)


cdef inline int buf_to_contiguous(
    void *buf, Py_buffer *view, Py_ssize_t length, char fort
) except -1:
    return PyBuffer_ToContiguous(buf, view, length, fort)


cdef inline int buf_from_contiguous(
    Py_buffer *view, void *buf, Py_ssize_t length, char fort
) except -1:
    return PyBuffer_FromContiguous(view, buf, length, fort)


cdef inline bint buf_is_contiguous(Py_buffer *view, char fort) noexcept:
    return PyBuffer_IsContiguous(view, fort)


cdef inline void buf_fill_contiguous_strides(
    int ndims,
    Py_ssize_t *shape,
    Py_ssize_t *strides,
    Py_ssize_t itemsize,
    char fort,
) noexcept:
    PyBuffer_FillContiguousStrides(ndims, shape, strides, itemsize, fort)


cdef inline int buf_fill_info(
    Py_buffer *view,
    object exporter,
    void *buf,
    Py_ssize_t length,
    int readonly,
    int flags,
) except -1:
    return PyBuffer_FillInfo(view, exporter, buf, length, readonly, flags)
