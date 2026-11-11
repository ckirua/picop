# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
"""Tier B: critical-section helpers vs natural Cython and mutex baselines."""

import cython
from picop.cycriticalsection cimport (
    PicopCriticalSection, PicopCriticalSection2, critical_sections_enabled,
    cs_begin, cs_begin_mutex, cs_end, cs2_begin_mutex, cs2_end,
)
from picop.cylock cimport PyMutex, mutex_init, mutex_lock, mutex_unlock
include "_sink.pxi"


cpdef Py_ssize_t cypy_object_section(object d, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef PicopCriticalSection cs
    for k in range(n):
        cs_begin(&cs, d)
        d["value"] = k
        cs_end(&cs)
    return 1


cpdef Py_ssize_t baseline_object_section(object d, Py_ssize_t n):
    cdef Py_ssize_t k
    for k in range(n):
        with cython.critical_section(d):
            d["value"] = k
    return 1


cpdef Py_ssize_t cypy_mutex_counter(Py_ssize_t n):
    cdef Py_ssize_t k, counter = 0
    cdef PyMutex mu
    cdef PicopCriticalSection cs
    mutex_init(&mu)
    for k in range(n):
        cs_begin_mutex(&cs, &mu)
        counter += 1
        cs_end(&cs)
    tb_sink_ssize(counter)
    return 1


cpdef Py_ssize_t baseline_mutex_counter(Py_ssize_t n):
    cdef Py_ssize_t k, counter = 0
    cdef PyMutex mu
    mutex_init(&mu)
    for k in range(n):
        mutex_lock(&mu)
        counter += 1
        mutex_unlock(&mu)
    tb_sink_ssize(counter)
    return 1


cpdef Py_ssize_t cypy_two_mutex_swap(object a, object b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef PyMutex m1, m2
    cdef PicopCriticalSection2 cs
    mutex_init(&m1)
    mutex_init(&m2)
    for k in range(n):
        cs2_begin_mutex(&cs, &m1, &m2)
        a["value"], b["value"] = b["value"], a["value"]
        cs2_end(&cs)
    return 1


cpdef Py_ssize_t baseline_two_mutex_swap(object a, object b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef PyMutex m1, m2
    mutex_init(&m1)
    mutex_init(&m2)
    for k in range(n):
        mutex_lock(&m1)
        mutex_unlock(&m1)
        mutex_lock(&m2)
        mutex_unlock(&m2)
        a["value"], b["value"] = b["value"], a["value"]
    return 1


cpdef Py_ssize_t cypy_enabled_check(Py_ssize_t n):
    cdef Py_ssize_t k, total = 0
    for k in range(n):
        total += critical_sections_enabled()
    tb_sink_ssize(total)
    return 1


cpdef Py_ssize_t baseline_enabled_check(Py_ssize_t n):
    import sys
    cdef Py_ssize_t k, total = 0
    for k in range(n):
        total += sys._is_gil_enabled()
    tb_sink_ssize(total)
    return 1

