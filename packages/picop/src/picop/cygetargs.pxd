# cygetargs.pxd
# Argument-parsing C-API. cimport-only — varargs, for Cython call sites.
# No public cpdef (cannot wrap ``...`` safely from Python).

cdef extern from "Python.h":
    int PyArg_ParseTuple(object args, const char *format, ...) except 0
    int PyArg_ParseTupleAndKeywords(object args, object kw, const char *format, char *keywords[], ...) except 0
    int PyArg_Parse(object args, const char *format, ...) except 0
    int PyArg_UnpackTuple(object args, const char *name, Py_ssize_t min, Py_ssize_t max, ...) except 0
