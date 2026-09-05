# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
"""GIL-held CPython call helpers."""

from cpython.object cimport PyObject


cpdef object call_noargs(object callable):
    """Call ``callable`` without constructing an argument tuple."""
    return PyObject_CallNoArgs(callable)


cpdef object call_onearg(object callable, object arg):
    """Call ``callable(arg)`` without constructing an argument tuple."""
    return PyObject_CallOneArg(callable, arg)


cpdef object call_twoargs(object callable, object arg0, object arg1):
    """Call ``callable(arg0, arg1)`` through the vectorcall protocol."""
    cdef PyObject *args[2]
    args[0] = <PyObject *>arg0
    args[1] = <PyObject *>arg1
    return <object>PyObject_Vectorcall(<PyObject *>callable, args, 2, NULL)


cdef object call_vector(object callable, PyObject *const *args, size_t nargs, PyObject *kwnames):
    return <object>PyObject_Vectorcall(<PyObject *>callable, args, nargs, kwnames)
