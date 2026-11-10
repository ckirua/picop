# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from picop.cymethod cimport (
    cfunction_check,
    cfunction_check_exact,
    cfunction_get_self,
    cfunction_get_self_unchecked,
    classmethod_new,
    method_check,
    method_get_function,
    method_get_self,
    method_new,
    staticmethod_new,
)
from types import BuiltinFunctionType, MethodType
include "_sink.pxi"

cpdef bint baseline_method_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), MethodType)
        tb_sink_bint(r)
    return r

cpdef bint cypy_method_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = method_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

cpdef bint baseline_cfunction_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), BuiltinFunctionType)
        tb_sink_bint(r)
    return r

cpdef bint cypy_cfunction_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = cfunction_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

cpdef bint baseline_cfunction_check_exact(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = type(tb_obj(p, k)) is BuiltinFunctionType
        tb_sink_bint(r)
    return r

cpdef bint cypy_cfunction_check_exact(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = cfunction_check_exact(tb_obj(p, k))
        tb_sink_bint(r)
    return r

cpdef object baseline_cfunction_get_self(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = None
    for k in range(n):
        r = tb_obj(p, k).__self__
    return r

cpdef object cypy_cfunction_get_self(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = None
    for k in range(n):
        r = cfunction_get_self(tb_obj(p, k))
    return r

cpdef object cypy_cfunction_get_self_unchecked(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = None
    for k in range(n):
        r = cfunction_get_self_unchecked(tb_obj(p, k))
    return r

cpdef object baseline_classmethod_new(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = None
    for k in range(n):
        r = classmethod(tb_obj(p, k))
    return r

cpdef object cypy_classmethod_new(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = None
    for k in range(n):
        r = classmethod_new(tb_obj(p, k))
    return r

cpdef object baseline_staticmethod_new(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = None
    for k in range(n):
        r = staticmethod(tb_obj(p, k))
    return r

cpdef object cypy_staticmethod_new(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = None
    for k in range(n):
        r = staticmethod_new(tb_obj(p, k))
    return r
