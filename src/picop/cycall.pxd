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
    object PyObject_CallMethodNoArgs(object self, object name)
    object PyObject_CallMethodOneArg(object self, object name, object arg)
    PyObject *PyObject_VectorcallMethod(
        PyObject *name, PyObject *const *args, size_t nargsf, PyObject *kwnames
    ) except NULL
    # Macro: strips PY_VECTORCALL_ARGUMENTS_OFFSET from nargsf.
    Py_ssize_t PyVectorcall_NARGS(size_t nargsf) noexcept

cpdef object call_noargs(object callable)
cpdef object call_onearg(object callable, object arg)
cpdef object call_twoargs(object callable, object arg0, object arg1)

# Borrowed argument vectors / keyword-name tuples are caller-owned and must stay
# live for the whole call. ``nargsf`` is forwarded to CPython unchanged: a plain
# positional count, or the count OR'd with PY_VECTORCALL_ARGUMENTS_OFFSET when
# args[-1] is a real reserved scratch slot. ``kwnames`` must be NULL or a tuple -
# Py_None is undefined behaviour (measured: SIGSEGV). For call_method_vector,
# args[0] is the receiver and is counted in nargsf.
cdef object call_vector(object callable, PyObject *const *args, size_t nargsf, PyObject *kwnames)
cdef object call_method_noargs(object self, object name)
cdef object call_method_onearg(object self, object name, object arg)
cdef object call_method_vector(object name, PyObject *const *args, size_t nargsf, PyObject *kwnames)
cdef Py_ssize_t vectorcall_nargs(size_t nargsf) noexcept
