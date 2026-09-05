# cycall.pxd
# GIL-held CPython call helpers. Public convenience calls avoid argument tuples.
from cpython.object cimport PyObject
from libc.stddef cimport size_t

cdef extern from "Python.h":
    object PyObject_CallNoArgs(object callable)
    object PyObject_CallOneArg(object callable, object arg)
    PyObject *PyObject_Vectorcall(
        PyObject *callable, PyObject *const *args, size_t nargsf, PyObject *kwnames
    ) except NULL

cpdef object call_noargs(object callable)
cpdef object call_onearg(object callable, object arg)
cpdef object call_twoargs(object callable, object arg0, object arg1)
cdef object call_vector(object callable, PyObject *const *args, size_t nargs, PyObject *kwnames)
