# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from picop.cyfunction cimport (
    func_check,
    func_get_annotations,
    func_get_annotations_unchecked,
    func_get_code,
    func_get_code_unchecked,
    func_get_kw_defaults,
    func_get_kw_defaults_unchecked,
    func_new_with_qualname,
    func_set_kw_defaults,
)
from types import FunctionType
include "_sink.pxi"

def _qual_source():
    return 1

cdef object _QUAL_CODE = _qual_source.__code__
cdef object _QUAL_GLOBALS = _qual_source.__globals__

cpdef bint baseline_func_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), FunctionType)
        tb_sink_bint(r)
    return r

cpdef bint cypy_func_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = func_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

cpdef object baseline_func_get_code(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = None
    for k in range(n):
        r = tb_obj(p, k).__code__
    return r

cpdef object cypy_func_get_code(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = None
    for k in range(n):
        r = func_get_code(tb_obj(p, k))
    return r

cpdef object cypy_func_get_code_unchecked(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = None
    for k in range(n):
        r = func_get_code_unchecked(tb_obj(p, k))
    return r

cpdef object baseline_func_get_kw_defaults(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = None
    for k in range(n):
        r = tb_obj(p, k).__kwdefaults__
    return r

cpdef object cypy_func_get_kw_defaults(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = None
    for k in range(n):
        r = func_get_kw_defaults(tb_obj(p, k))
    return r

cpdef object cypy_func_get_kw_defaults_unchecked(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = None
    for k in range(n):
        r = func_get_kw_defaults_unchecked(tb_obj(p, k))
    return r

cpdef object baseline_func_get_annotations(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = None
    for k in range(n):
        r = getattr(tb_obj(p, k), "__annotations__", None)
    return r

cpdef object cypy_func_get_annotations(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = None
    for k in range(n):
        r = func_get_annotations(tb_obj(p, k))
    return r

cpdef object cypy_func_get_annotations_unchecked(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = None
    for k in range(n):
        r = func_get_annotations_unchecked(tb_obj(p, k))
    return r

cpdef object baseline_func_set_kw_defaults(object p, Py_ssize_t n, object value):
    cdef Py_ssize_t k
    for k in range(n):
        tb_obj(p, k).__kwdefaults__ = value
    return p

cpdef object cypy_func_set_kw_defaults(object p, Py_ssize_t n, object value):
    cdef Py_ssize_t k
    for k in range(n):
        func_set_kw_defaults(tb_obj(p, k), value)
    return p

cpdef object baseline_func_new_with_qualname(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = None
    for k in range(n):
        r = FunctionType(_QUAL_CODE, _QUAL_GLOBALS)
        r.__qualname__ = "Outer._qual_source"
    return r

cpdef object cypy_func_new_with_qualname(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = None
    for k in range(n):
        r = func_new_with_qualname(_QUAL_CODE, _QUAL_GLOBALS, "Outer._qual_source")
    return r
