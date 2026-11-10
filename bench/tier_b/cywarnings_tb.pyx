# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from picop.cywarnings cimport warn_ex
import warnings


cpdef Py_ssize_t baseline(object category, object message, Py_ssize_t n):
    cdef Py_ssize_t i
    for i in range(n):
        warnings.warn(message, category)
    return n

cpdef Py_ssize_t cypy(object category, object message, Py_ssize_t n):
    cdef Py_ssize_t i
    for i in range(n):
        warn_ex(category, message)
    return n
