/*
 * cypy UUID generation helper adapted from asyncpg;
 * see the repository NOTICE and LICENSES/Apache-2.0.txt for UUID provenance.
 */

#pragma once

#include <limits.h>
#include <stddef.h>
#include <stdint.h>

#define UUID_SIZE 16

#ifndef UUID_RANDOM_BUFFER_SIZE
#define UUID_RANDOM_BUFFER_SIZE 65536
#endif

/* MSVC ignores `-std=c11` and its default C mode has no `_Static_assert`, so
   fall back to a negative-size typedef when the compiler does not advertise C11. */
#if defined(__STDC_VERSION__) && __STDC_VERSION__ >= 201112L && !defined(_MSC_VER)
#define PICOP_STATIC_ASSERT(condition, message) _Static_assert(condition, message)
#else
#define PICOP_STATIC_ASSERT_NAME_(line) picop_static_assert_line_##line
#define PICOP_STATIC_ASSERT_NAME(line) PICOP_STATIC_ASSERT_NAME_(line)
#define PICOP_STATIC_ASSERT(condition, message) \
    typedef char PICOP_STATIC_ASSERT_NAME(__LINE__)[(condition) ? 1 : -1]
#endif

PICOP_STATIC_ASSERT(
    UUID_RANDOM_BUFFER_SIZE >= UUID_SIZE,
    "UUID_RANDOM_BUFFER_SIZE must hold at least one UUID"
);

PICOP_STATIC_ASSERT(
    UUID_RANDOM_BUFFER_SIZE % UUID_SIZE == 0,
    "UUID_RANDOM_BUFFER_SIZE must be a multiple of 16"
);
PICOP_STATIC_ASSERT(
    UUID_RANDOM_BUFFER_SIZE <= INT_MAX,
    "UUID_RANDOM_BUFFER_SIZE must stay within int bounds for thread-local buffers"
);

/* Entropy provider (entropy.c): returns 1 on success, 0 on failure. */
int c_uuid_entropy(unsigned char *buffer, size_t nbytes);

/* Call once before generation; a nonzero result is a fork-hook error code. */
int c_uuid_init(void);
int c_uuid4(uint8_t uuid[UUID_SIZE]);
