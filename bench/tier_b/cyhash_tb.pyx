# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from picop.cyhash cimport hash_buffer, hash_buffer_raw, hash_generic, hash_pointer
include "_sink.pxi"

cpdef Py_ssize_t baseline_hash_buffer(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_hash_t r = 0
    for k in range(n):
        r = hash(bytes(tb_obj(p, k)))
        tb_sink_ssize(r)
    return r


cpdef Py_ssize_t cypy_hash_buffer(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_hash_t r = 0
    for k in range(n):
        r = hash_buffer(tb_obj(p, k))
        tb_sink_ssize(r)
    return r


cpdef Py_ssize_t baseline_hash_range(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_hash_t r = 0
    for k in range(n):
        r = hash(bytes(tb_obj(p, k)[8:56]))
        tb_sink_ssize(r)
    return r


cpdef Py_ssize_t cypy_hash_range(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_hash_t r = 0
    for k in range(n):
        r = hash_buffer(tb_obj(p, k), 8, 56)
        tb_sink_ssize(r)
    return r


cpdef Py_ssize_t baseline_hash_cached(object p, Py_ssize_t n):
    # The builtin route for an object CPython can hash: the hash is cached on the
    # object, so the loop never touches the buffer again.
    cdef Py_ssize_t k
    cdef Py_hash_t r = 0
    for k in range(n):
        r = hash(tb_obj(p, k))
        tb_sink_ssize(r)
    return r


cpdef Py_ssize_t baseline_hash_builtin(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_hash_t r = 0
    for k in range(n):
        r = hash(tb_obj(p, k))
        tb_sink_ssize(r)
    return r


cpdef Py_ssize_t cypy_hash_generic(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_hash_t r = 0
    for k in range(n):
        r = hash_generic(tb_obj(p, k))
        tb_sink_ssize(r)
    return r


cpdef Py_ssize_t cypy_hash_pointer(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_hash_t r = 0
    cdef object o
    for k in range(n):
        o = tb_obj(p, k)
        r = hash_pointer(<const void *>o)
        tb_sink_ssize(r)
    return r


cpdef Py_ssize_t cypy_hash_raw(bytes p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_hash_t r = 0
    cdef const char *ptr = p
    for k in range(n):
        r = hash_buffer_raw(ptr, 64)
        tb_sink_ssize(r)
    return r
