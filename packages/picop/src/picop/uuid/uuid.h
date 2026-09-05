/*
 * cypy UUID generation helper adapted from asyncpg;
 * see the repository NOTICE and LICENSES/Apache-2.0.txt for UUID provenance.
 */

#pragma once

#include <limits.h>
#include <stdint.h>

#define UUID_SIZE 16

#ifndef UUID_RANDOM_BUFFER_SIZE
#define UUID_RANDOM_BUFFER_SIZE 65536
#endif

_Static_assert(
    UUID_RANDOM_BUFFER_SIZE % UUID_SIZE == 0,
    "UUID_RANDOM_BUFFER_SIZE must be a multiple of 16"
);
_Static_assert(
    UUID_RANDOM_BUFFER_SIZE <= INT_MAX,
    "UUID_RANDOM_BUFFER_SIZE must fit RAND_bytes' int length"
);

int c_uuid4(uint8_t uuid[UUID_SIZE]);
