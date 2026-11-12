# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from picop.cydict cimport dict_get, dict_contains, dict_len, dict_check
include "_sink.pxi"

cpdef object baseline_dget(dict d, str key, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = (<dict>tb_obj(d, k)).get(key)
        tb_sink_obj(r)
    return r

cpdef object cypy_dget(dict d, str key, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = dict_get(<dict>tb_obj(d, k), key)
        tb_sink_obj(r)
    return r

cpdef bint baseline_dcontains(dict d, str key, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = key in <dict>tb_obj(d, k)
        tb_sink_bint(r)
    return r

cpdef bint cypy_dcontains(dict d, str key, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = dict_contains(<dict>tb_obj(d, k), key)
        tb_sink_bint(r)
    return r

cpdef Py_ssize_t baseline_dlen(dict d, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = len(<dict>tb_obj(d, k))
        tb_sink_ssize(r)
    return r

cpdef Py_ssize_t cypy_dlen(dict d, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = dict_len(<dict>tb_obj(d, k))
        tb_sink_ssize(r)
    return r

cpdef bint baseline_dcheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), dict)
        tb_sink_bint(r)
    return r

cpdef bint cypy_dcheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = dict_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

from picop.cydict cimport (
    dict_add_watcher,
    dict_clear_watcher,
    dict_watch,
    dict_unwatch,
    PyDict_WatchEvent,
    PyDict_EVENT_MODIFIED,
)

cdef Py_ssize_t _dict_watch_hits = 0

cdef int _dict_noop_cb(PyDict_WatchEvent event, PyObject *d, PyObject *key, PyObject *value) except -1:
    return 0

cdef int _dict_count_cb(PyDict_WatchEvent event, PyObject *d, PyObject *key, PyObject *value) except -1:
    global _dict_watch_hits
    if event == PyDict_EVENT_MODIFIED:
        _dict_watch_hits += 1
    return 0

cpdef object cypy_dict_set_plain(dict d, Py_ssize_t n, object value):
    cdef Py_ssize_t k
    for k in range(n):
        d["watch_key"] = value
    return d

cpdef object cypy_dict_set_noop_cb(dict d, Py_ssize_t n, object value):
    cdef Py_ssize_t k
    cdef int watcher = dict_add_watcher(_dict_noop_cb)
    dict_watch(d, watcher)
    for k in range(n):
        d["watch_key"] = value
    dict_unwatch(d, watcher)
    dict_clear_watcher(watcher)
    return d

cpdef object cypy_dict_set_count_cb(dict d, Py_ssize_t n, object value):
    cdef Py_ssize_t k
    cdef int watcher = dict_add_watcher(_dict_count_cb)
    dict_watch(d, watcher)
    global _dict_watch_hits
    _dict_watch_hits = 0
    for k in range(n):
        d["watch_key"] = value
    dict_unwatch(d, watcher)
    dict_clear_watcher(watcher)
    tb_sink_ssize(_dict_watch_hits)
    return d
