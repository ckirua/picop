# cyatomic.pxd
# C11 stdatomic.h wrappers for lock-free / SPSC ring-buffer work in Cython.
# cimport-only — no Python API. All helpers are nogil.
#
# Typical SPSC index pattern:
#   producer: atomic_store_release(tail, new_tail)
#   consumer: atomic_load_acquire(head)
#   capacity check: atomic_load_relaxed(other_index)

from libc.stddef cimport size_t
from libc.stdint cimport uint64_t

cdef extern from "<stdatomic.h>" nogil:
    ctypedef enum memory_order:
        memory_order_relaxed
        memory_order_acquire
        memory_order_release
        memory_order_acq_rel
        memory_order_seq_cst

    ctypedef struct atomic_size_t:
        pass

    void atomic_init(atomic_size_t *obj, size_t value)

    size_t atomic_load_explicit(const atomic_size_t *obj, memory_order order)
    void atomic_store_explicit(atomic_size_t *obj, size_t value, memory_order order)
    size_t atomic_fetch_add_explicit(atomic_size_t *obj, size_t value, memory_order order)
    bint atomic_compare_exchange_weak_explicit(
        atomic_size_t *obj,
        size_t *expected,
        size_t desired,
        memory_order succ,
        memory_order fail,
    )

cdef extern from "cyatomic_shim.h" nogil:
    ctypedef struct atomic_uint64_t "atomic_uint64_t":
        pass

    void cy_atomic_init_uint64(atomic_uint64_t *obj, uint64_t value)
    uint64_t cy_atomic_load_uint64_explicit(
        const atomic_uint64_t *obj,
        memory_order order,
    )
    void cy_atomic_store_uint64_explicit(
        atomic_uint64_t *obj,
        uint64_t value,
        memory_order order,
    )
    uint64_t cy_atomic_fetch_add_uint64_explicit(
        atomic_uint64_t *obj,
        uint64_t value,
        memory_order order,
    )


cdef inline size_t atomic_load_relaxed(atomic_size_t *obj) nogil:
    return atomic_load_explicit(obj, memory_order_relaxed)


cdef inline size_t atomic_load_acquire(atomic_size_t *obj) nogil:
    return atomic_load_explicit(obj, memory_order_acquire)


cdef inline void atomic_store_relaxed(atomic_size_t *obj, size_t value) nogil:
    atomic_store_explicit(obj, value, memory_order_relaxed)


cdef inline void atomic_store_release(atomic_size_t *obj, size_t value) nogil:
    atomic_store_explicit(obj, value, memory_order_release)


cdef inline size_t atomic_fetch_add_relaxed(atomic_size_t *obj, size_t value) nogil:
    return atomic_fetch_add_explicit(obj, value, memory_order_relaxed)


cdef inline bint atomic_cas_weak_relaxed(
    atomic_size_t *obj,
    size_t *expected,
    size_t desired,
) nogil:
    return atomic_compare_exchange_weak_explicit(
        obj,
        expected,
        desired,
        memory_order_relaxed,
        memory_order_relaxed,
    )


cdef inline void atomic_uint64_init(atomic_uint64_t *obj, uint64_t value) nogil:
    cy_atomic_init_uint64(obj, value)


cdef inline uint64_t atomic_uint64_load_relaxed(atomic_uint64_t *obj) nogil:
    return cy_atomic_load_uint64_explicit(obj, memory_order_relaxed)


cdef inline uint64_t atomic_uint64_load_acquire(atomic_uint64_t *obj) nogil:
    return cy_atomic_load_uint64_explicit(obj, memory_order_acquire)


cdef inline void atomic_uint64_store_relaxed(atomic_uint64_t *obj, uint64_t value) nogil:
    cy_atomic_store_uint64_explicit(obj, value, memory_order_relaxed)


cdef inline void atomic_uint64_store_release(atomic_uint64_t *obj, uint64_t value) nogil:
    cy_atomic_store_uint64_explicit(obj, value, memory_order_release)


cdef inline uint64_t atomic_uint64_fetch_add_relaxed(atomic_uint64_t *obj, uint64_t value) nogil:
    return cy_atomic_fetch_add_uint64_explicit(obj, value, memory_order_relaxed)
