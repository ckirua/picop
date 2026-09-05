/*
 * Thread-local entropy buffering adapted from asyncpg's UUID generator. This
 * implementation replaces the original process-global atomic buffer with
 * private per-thread storage and uses OpenSSL as cypy's entropy source.
 * asyncpg provenance for cypy.uuid is recorded in the repository NOTICE;
 * applicable Apache terms are in LICENSES/Apache-2.0.txt.
 */

#include "uuid.h"

#include <stdalign.h>
#include <stddef.h>
#include <string.h>

#ifndef _WIN32
#include <pthread.h>
#endif

#include <openssl/rand.h>

alignas(64) static _Thread_local unsigned char
    random_buffer[UUID_RANDOM_BUFFER_SIZE];
static _Thread_local size_t random_buffer_pos = UUID_RANDOM_BUFFER_SIZE;

#ifndef _WIN32
static void
uuid_random_after_fork(void)
{
    random_buffer_pos = UUID_RANDOM_BUFFER_SIZE;
}

__attribute__((constructor)) static void
uuid_random_register_atfork(void)
{
    (void)pthread_atfork(NULL, NULL, uuid_random_after_fork);
}
#endif

int
c_uuid4(uint8_t uuid[UUID_SIZE])
{
    size_t pos = random_buffer_pos;

    if (pos == UUID_RANDOM_BUFFER_SIZE) {
        if (RAND_bytes(random_buffer, (int)UUID_RANDOM_BUFFER_SIZE) != 1) {
            return 0;
        }
        pos = 0;
    }

    memcpy(uuid, random_buffer + pos, UUID_SIZE);
    random_buffer_pos = pos + UUID_SIZE;

    uuid[6] = (uint8_t)((uuid[6] & 0x0fU) | 0x40U);
    uuid[8] = (uint8_t)((uuid[8] & 0x3fU) | 0x80U);
    return 1;
}
