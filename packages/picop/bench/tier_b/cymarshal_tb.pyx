# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cymarshal cimport marshal_dumps
include "_sink.pxi"

cpdef object baseline_marshal_dumps(object value, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    import marshal as _marshal
    dumps = _marshal.dumps
    for k in range(n):
        r = dumps(tb_obj(value, k))
        tb_sink_obj(r)
    return r

cpdef object cypy_marshal_dumps(object value, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = marshal_dumps(tb_obj(value, k))
        tb_sink_obj(r)
    return r
