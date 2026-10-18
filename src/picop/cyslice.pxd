# cyslice.pxd
# ``slice`` helpers. Public docs in ``cyslice.pyi``.
# Unpack/Adjust/GetIndices out-params: also exposed as tuple-returning cpdef where useful.

from cpython.object cimport PyObject_RichCompareBool, Py_EQ


cdef extern from "Python.h":
    bint PySlice_Check(object ob) noexcept
    slice PySlice_New(object start, object stop, object step)
    int PySlice_GetIndices(
        object sl, Py_ssize_t length,
        Py_ssize_t *start, Py_ssize_t *stop, Py_ssize_t *step,
    ) except? -1
    int PySlice_GetIndicesEx(
        object sl, Py_ssize_t length,
        Py_ssize_t *start, Py_ssize_t *stop, Py_ssize_t *step,
        Py_ssize_t *slicelength,
    ) except -1
    int PySlice_Unpack(
        object sl, Py_ssize_t *start, Py_ssize_t *stop, Py_ssize_t *step,
    ) except -1
    Py_ssize_t PySlice_AdjustIndices(
        Py_ssize_t length, Py_ssize_t *start, Py_ssize_t *stop, Py_ssize_t step,
    ) noexcept


cdef inline bint slcheck(object p) noexcept:
    return PySlice_Check(p)


cdef inline slice slnew(object start=None, object stop=None, object step=None):
    return PySlice_New(start, stop, step)


cdef inline tuple slindices_ex(object sl, Py_ssize_t length):
    # Clipped indices + slice length (preferred over GetIndices).
    cdef Py_ssize_t start, stop, step, slicelen
    PySlice_GetIndicesEx(sl, length, &start, &stop, &step, &slicelen)
    return (start, stop, step, slicelen)


cdef inline tuple slunpack(object sl):
    cdef Py_ssize_t start, stop, step
    PySlice_Unpack(sl, &start, &stop, &step)
    return (start, stop, step)


cdef inline int slget_indices(
    object sl, Py_ssize_t length,
    Py_ssize_t *start, Py_ssize_t *stop, Py_ssize_t *step,
) except? -1:
    # Older API — out-of-range is error (prefer slindices_ex).
    return PySlice_GetIndices(sl, length, start, stop, step)


cdef inline int slget_indices_ex(
    object sl, Py_ssize_t length,
    Py_ssize_t *start, Py_ssize_t *stop, Py_ssize_t *step,
    Py_ssize_t *slicelength,
) except -1:
    return PySlice_GetIndicesEx(sl, length, start, stop, step, slicelength)


cdef inline int slunpack_c(
    object sl, Py_ssize_t *start, Py_ssize_t *stop, Py_ssize_t *step,
) except -1:
    return PySlice_Unpack(sl, start, stop, step)


cdef inline Py_ssize_t sladjust_indices(
    Py_ssize_t length, Py_ssize_t *start, Py_ssize_t *stop, Py_ssize_t step,
) noexcept:
    return PySlice_AdjustIndices(length, start, stop, step)

# Wave 4 N1/N5 preferred names (0.3: soft letter/bare are cdef-only)

cdef inline Py_ssize_t slice_adjust_indices(Py_ssize_t length, Py_ssize_t *start, Py_ssize_t *stop, Py_ssize_t step) noexcept:
    return sladjust_indices(length, start, stop, step)

cpdef inline bint slice_check(object p) noexcept:
    return slcheck(p)


cdef inline bint sleq(slice a, slice b):
    # Identity short-circuit + richcompare (same semantics as ``slice.__eq__``).
    if a is b:
        return True
    return <bint>PyObject_RichCompareBool(a, b, Py_EQ)


cpdef inline bint slice_eq(slice a, slice b):
    return sleq(a, b)

cdef inline int slice_get_indices(object sl, Py_ssize_t length, Py_ssize_t *start, Py_ssize_t *stop, Py_ssize_t *step) except? -1:
    return slget_indices(sl, length, start, stop, step)

cdef inline int slice_get_indices_ex(object sl, Py_ssize_t length, Py_ssize_t *start, Py_ssize_t *stop, Py_ssize_t *step, Py_ssize_t *slicelength) except -1:
    return slget_indices_ex(sl, length, start, stop, step, slicelength)

cpdef inline tuple slice_indices_ex(object sl, Py_ssize_t length):
    return slindices_ex(sl, length)

cpdef inline slice slice_new(object start=None, object stop=None, object step=None):
    return slnew(start, stop, step)

cpdef inline tuple slice_unpack(object sl):
    return slunpack(sl)

cdef inline int slice_unpack_c(object sl, Py_ssize_t *start, Py_ssize_t *stop, Py_ssize_t *step) except -1:
    return slunpack_c(sl, start, stop, step)

