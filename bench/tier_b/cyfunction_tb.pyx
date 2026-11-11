# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cpython.object cimport PyObject
from picop.cyfunction cimport (
    func_check,
    func_get_annotations,
    func_get_annotations_unchecked,
    func_get_code,
    func_get_code_unchecked,
    func_get_kw_defaults,
    func_get_kw_defaults_unchecked,
    func_add_watcher,
    func_clear_watcher,
    PyFunction_WatchEvent,
    PyFunctionObject,
    func_new_with_qualname,
    func_set_kw_defaults,
    PyFunction_EVENT_MODIFY_KWDEFAULTS,
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


cdef Py_ssize_t _watch_hits = 0

cdef int _watch_noop_cb(PyFunction_WatchEvent event, PyFunctionObject *func, PyObject *new_value) except -1:
    return 0

cdef int _watch_count_cb(PyFunction_WatchEvent event, PyFunctionObject *func, PyObject *new_value) except -1:
    global _watch_hits
    if event == PyFunction_EVENT_MODIFY_KWDEFAULTS:
        _watch_hits += 1
    return 0

cpdef object cypy_func_set_kw_defaults_watched(object p, Py_ssize_t n, object value):
    cdef Py_ssize_t k
    cdef int watcher = func_add_watcher(_watch_count_cb)
    for k in range(n):
        func_set_kw_defaults(tb_obj(p, k), value)
    func_clear_watcher(watcher)
    tb_sink_ssize(_watch_hits)
    return p

cpdef object cypy_func_set_kw_defaults_noop_cb(object p, Py_ssize_t n, object value):
    cdef Py_ssize_t k
    cdef int watcher = func_add_watcher(_watch_noop_cb)
    for k in range(n):
        func_set_kw_defaults(tb_obj(p, k), value)
    func_clear_watcher(watcher)
    return p

cpdef object cypy_func_new_with_qualname_watched(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef int watcher = func_add_watcher(_watch_noop_cb)
    cdef object r = None
    for k in range(n):
        r = func_new_with_qualname(_QUAL_CODE, _QUAL_GLOBALS, "Outer._qual_source")
    func_clear_watcher(watcher)
    return r
