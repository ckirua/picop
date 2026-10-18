# cymarshal.pxd
# Marshal helpers. Public docs in ``cymarshal.pyi``.
# FILE* APIs rejected as public.

cdef extern from "marshal.h":
    object PyMarshal_WriteObjectToString(object value, int version)
    object PyMarshal_ReadObjectFromString(const char *data, Py_ssize_t len)


cdef extern from "Python.h":
    int PyBytes_AsStringAndSize(object obj, char **buffer, Py_ssize_t *length) except -1


cpdef inline object marshal_dumps(object value, int version=4):
    return PyMarshal_WriteObjectToString(value, version)


cpdef inline object marshal_loads(object data):
    cdef char *buf
    cdef Py_ssize_t n
    PyBytes_AsStringAndSize(data, &buf, &n)
    return PyMarshal_ReadObjectFromString(buf, n)
