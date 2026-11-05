# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
"""Tier B loops: idiomatic typed Cython calls vs ``picop.cycall`` helpers.

``call_vector`` / ``call_method_vector`` are ``cdef`` (Cython-side only), so the
vectorcall depth path can only be exercised from a compiled harness module.
"""

from cpython.object cimport PyObject

cdef extern from "Python.h":
    size_t PY_VECTORCALL_ARGUMENTS_OFFSET

from picop.cycall cimport (
    call_noargs,
    call_onearg,
    call_twoargs,
    call_vector,
    call_method_noargs,
    call_method_onearg,
    call_method_vector,
    vectorcall_nargs,
)

include "_sink.pxi"


# ---- baselines: idiomatic typed Cython calls ----

cpdef object baseline_call0(object func, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = tb_obj(func, k)()
        tb_sink_obj(r)
    return r


cpdef object baseline_call1(object func, object value, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = tb_obj(func, k)(value)
        tb_sink_obj(r)
    return r


cpdef object baseline_call2(object func, object a, object b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = tb_obj(func, k)(a, b)
        tb_sink_obj(r)
    return r


cpdef object baseline_call3(object func, object a, object b, object c, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = tb_obj(func, k)(a, b, c)
        tb_sink_obj(r)
    return r


cpdef object baseline_call_kw(object func, object a, object b, object kwnames, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = tb_obj(func, k)(a, offset=b)
        tb_sink_obj(r)
    return r


cpdef object baseline_method0(object obj, object name, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = tb_obj(obj, k).read()
        tb_sink_obj(r)
    return r


cpdef object baseline_method1(object obj, object name, object value, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = tb_obj(obj, k).read(value)
        tb_sink_obj(r)
    return r


# ---- picop.cycall side ----

cpdef object cypy_call_noargs(object func, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = call_noargs(tb_obj(func, k))
        tb_sink_obj(r)
    return r


cpdef object cypy_call_onearg(object func, object value, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = call_onearg(tb_obj(func, k), value)
        tb_sink_obj(r)
    return r


cpdef object cypy_call_twoargs(object func, object a, object b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = call_twoargs(tb_obj(func, k), a, b)
        tb_sink_obj(r)
    return r


cpdef object cypy_call_vector3(object func, object a, object b, object c, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    cdef PyObject *args[3]
    args[0] = <PyObject *>a
    args[1] = <PyObject *>b
    args[2] = <PyObject *>c
    for k in range(n):
        r = call_vector(tb_obj(func, k), args, 3, NULL)
        tb_sink_obj(r)
    return r


# Depth: marginal cost per vectorcall argument (same callable, varying nargsf).
cpdef object cypy_call_vector_n(object func, object a, object b, object c, object d, Py_ssize_t nargs, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    cdef PyObject *args[4]
    args[0] = <PyObject *>a
    args[1] = <PyObject *>b
    args[2] = <PyObject *>c
    args[3] = <PyObject *>d
    for k in range(n):
        r = call_vector(tb_obj(func, k), args, nargs, NULL)
        tb_sink_obj(r)
    return r


# Depth: zero-positional vectorcall (args may be NULL when nargsf is 0).
cpdef object cypy_call_vector_zero(object func, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = call_vector(tb_obj(func, k), NULL, 0, NULL)
        tb_sink_obj(r)
    return r


# Depth: reserved-slot vector (`args[-1]` scratch, nargsf carries the offset bit),
# the spelling CPython itself uses. Measured against the plain-count spelling.
cpdef object cypy_call_vector_plain2(object func, object a, object b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    cdef PyObject *args[2]
    args[0] = <PyObject *>a
    args[1] = <PyObject *>b
    for k in range(n):
        r = call_vector(tb_obj(func, k), args, 2, NULL)
        tb_sink_obj(r)
    return r


cpdef object cypy_call_vector_offset(object func, object a, object b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    cdef PyObject *slots[3]
    slots[0] = NULL  # reserved scratch slot read by callee argument shifting
    slots[1] = <PyObject *>a
    slots[2] = <PyObject *>b
    for k in range(n):
        r = call_vector(tb_obj(func, k), slots + 1, <size_t>(2 | PY_VECTORCALL_ARGUMENTS_OFFSET), NULL)
        tb_sink_obj(r)
    return r


# Depth: bound-method vectorcall with the offset bit — exercises the self-shifting
# path that reads args[-1].
cpdef object cypy_call_method_offset(object name, object self, object value):
    cdef PyObject *slots[3]
    slots[0] = NULL
    slots[1] = <PyObject *>self
    slots[2] = <PyObject *>value
    return call_method_vector(name, slots + 1, <size_t>(2 | PY_VECTORCALL_ARGUMENTS_OFFSET), NULL)


# Depth: keyword arguments through a caller-owned kwnames tuple.
cpdef object cypy_call_vector_kw(object func, object a, object b, object kwnames, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    cdef PyObject *args[2]
    args[0] = <PyObject *>a
    args[1] = <PyObject *>b  # keyword value follows the positional run
    for k in range(n):
        r = call_vector(tb_obj(func, k), args, 1, <PyObject *>kwnames)
        tb_sink_obj(r)
    return r


# Depth: kwnames is tested against NULL, not against emptiness — passing Py_None
# is undefined. Kept out of the timed loops; used by the probe section only.
cpdef object cypy_call_vector_none_kw(object func, object a):
    cdef PyObject *args[1]
    args[0] = <PyObject *>a
    return call_vector(func, args, 1, <PyObject *>None)


# Depth: cost of spelling nargsf through PyVectorcall_NARGS vs a plain count.
cpdef object cypy_nargs_macro(object func, object a, object b, Py_ssize_t nargs, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    cdef PyObject *args[2]
    args[0] = <PyObject *>a
    args[1] = <PyObject *>b
    for k in range(n):
        r = call_vector(tb_obj(func, k), args, <size_t>vectorcall_nargs(nargs), NULL)
        tb_sink_obj(r)
    return r


cpdef object baseline_nargs_literal(object func, object a, object b, Py_ssize_t nargs, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    cdef PyObject *args[2]
    args[0] = <PyObject *>a
    args[1] = <PyObject *>b
    for k in range(n):
        r = call_vector(tb_obj(func, k), args, <size_t>nargs, NULL)
        tb_sink_obj(r)
    return r


cpdef object cypy_call_method_noargs(object obj, object name, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = call_method_noargs(tb_obj(obj, k), name)
        tb_sink_obj(r)
    return r


cpdef object cypy_call_method_onearg(object obj, object name, object value, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = call_method_onearg(tb_obj(obj, k), name, value)
        tb_sink_obj(r)
    return r


cpdef object cypy_call_method_vector(object name, object obj, object value, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    cdef object target
    cdef PyObject *args[2]
    args[0] = <PyObject *>obj  # PyObject_VectorcallMethod counts the receiver as arg 0
    args[1] = <PyObject *>value
    for k in range(n):
        target = tb_obj(obj, k)
        args[0] = <PyObject *>target
        r = call_method_vector(name, args, 2, NULL)
        tb_sink_obj(r)
    return r
