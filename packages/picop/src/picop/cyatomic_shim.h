#ifndef CYCEL_CYATOMIC_SHIM_H
#define CYCEL_CYATOMIC_SHIM_H

#include <stdatomic.h>
#include <stdint.h>

typedef _Atomic uint64_t atomic_uint64_t;

static inline void cy_atomic_init_uint64(atomic_uint64_t *obj, uint64_t value)
{
    atomic_init(obj, value);
}

static inline uint64_t cy_atomic_load_uint64_explicit(
    const atomic_uint64_t *obj,
    memory_order order)
{
    return atomic_load_explicit(obj, order);
}

static inline void cy_atomic_store_uint64_explicit(
    atomic_uint64_t *obj,
    uint64_t value,
    memory_order order)
{
    atomic_store_explicit(obj, value, order);
}

static inline uint64_t cy_atomic_fetch_add_uint64_explicit(
    atomic_uint64_t *obj,
    uint64_t value,
    memory_order order)
{
    return atomic_fetch_add_explicit(obj, value, order);
}

#endif
