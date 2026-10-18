# cymem.pxd
# Python heap / pymalloc helpers (cimport-only). Public docs: none (no cpdef).
# Prefer these over libc malloc for extension arenas tracked by Python.

from libc.stddef cimport size_t
from cpython.mem cimport (
    PyMem_Calloc,
    PyMem_Free,
    PyMem_Malloc,
    PyMem_RawFree,
    PyMem_RawMalloc,
    PyMem_RawRealloc,
    PyMem_Realloc,
    PyObject_Calloc,
    PyObject_Free,
    PyObject_Malloc,
    PyObject_Realloc,
)


cdef inline void *mem_malloc(size_t n):
    return PyMem_Malloc(n)


cdef inline void *mem_calloc(size_t nelem, size_t elsize):
    return PyMem_Calloc(nelem, elsize)


cdef inline void *mem_realloc(void *p, size_t n):
    return PyMem_Realloc(p, n)


cdef inline void mem_free(void *p):
    PyMem_Free(p)


cdef inline void *mem_raw_malloc(size_t n) nogil:
    return PyMem_RawMalloc(n)


cdef inline void *mem_raw_realloc(void *p, size_t n) nogil:
    return PyMem_RawRealloc(p, n)


cdef inline void mem_raw_free(void *p) nogil:
    PyMem_RawFree(p)


cdef inline void *obj_malloc(size_t n):
    return PyObject_Malloc(n)


cdef inline void *obj_calloc(size_t nelem, size_t elsize):
    return PyObject_Calloc(nelem, elsize)


cdef inline void *obj_realloc(void *p, size_t n):
    return PyObject_Realloc(p, n)


cdef inline void obj_free(void *p):
    PyObject_Free(p)
