/*
 * Operating-system CSPRNG for the UUID generator: BCrypt on Windows,
 * /dev/urandom elsewhere. Keeping the provider in its own translation unit
 * lets the entropy contract tests link a failing implementation instead of
 * the real one (see tests/test_uuid_entropy.py).
 */

#include "uuid.h"

#ifdef _WIN32
/* bcrypt.h's prototypes use ULONG/BCRYPT_* types that come from the Windows
   base headers; MSVC rejects bcrypt.h on its own. */
#include <windows.h>
#include <bcrypt.h>
#else
#include <fcntl.h>
#include <unistd.h>
#endif

int
c_uuid_entropy(unsigned char *buffer, size_t nbytes)
{
#ifdef _WIN32
    return BCryptGenRandom(NULL, buffer, (ULONG)nbytes,
                           BCRYPT_USE_SYSTEM_PREFERRED_RNG) == 0;
#else
    int fd = open("/dev/urandom", O_RDONLY);
    size_t got = 0;

    if (fd < 0) {
        return 0;
    }
    while (got < nbytes) {
        ssize_t n = read(fd, buffer + got, nbytes - got);
        if (n <= 0) {
            close(fd);
            return 0;
        }
        got += (size_t)n;
    }
    close(fd);
    return 1;
#endif
}
