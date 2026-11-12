#ifndef CYCEL_CYBYTES_SHIM_H
#define CYCEL_CYBYTES_SHIM_H

#include <stddef.h>
#include <string.h>

/*
 * memmem() is a GNU extension: MSVC and MinGW do not provide it, so the
 * bytes/bytearray search helpers use this portable equivalent. The scan
 * mirrors glibc's strategy (memchr for the first byte, then memcmp).
 */
static inline void *cy_memmem(const void *haystack, size_t haystacklen,
                              const void *needle, size_t needlelen)
{
    const unsigned char *h = (const unsigned char *)haystack;
    const unsigned char *n = (const unsigned char *)needle;

    if (needlelen == 0) {
        return (void *)haystack;
    }
    if (haystacklen < needlelen) {
        return NULL;
    }

    const unsigned char *end = h + haystacklen - needlelen;
    const unsigned char *p = h;
    while (p <= end) {
        p = (const unsigned char *)memchr(p, n[0], (size_t)(end - p) + 1);
        if (p == NULL) {
            return NULL;
        }
        if (needlelen == 1 || memcmp(p + 1, n + 1, needlelen - 1) == 0) {
            return (void *)p;
        }
        ++p;
    }
    return NULL;
}

/*
 * Mirror of CPython's internal _PyBytesWriter (internal/pycore_bytesobject.h
 * cannot be included by extension modules: it requires Py_BUILD_CORE).
 * Field-for-field identical to the interpreter's struct. These functions are
 * non-static in the interpreter (exported for _pickle), so the linker
 * resolves them directly.
 */
typedef struct CyBytesWriter {
    PyObject *buffer;
    Py_ssize_t allocated;
    Py_ssize_t min_size;
    int use_bytearray;
    int overallocate;
    int use_small_buffer;
    char small_buffer[512];
} CyBytesWriter;

extern void _PyBytesWriter_Init(CyBytesWriter *writer);
extern void *_PyBytesWriter_Alloc(CyBytesWriter *writer, Py_ssize_t size);
extern void *_PyBytesWriter_Prepare(CyBytesWriter *writer, void *str, Py_ssize_t size);
extern PyObject *_PyBytesWriter_Finish(CyBytesWriter *writer, void *str);
extern void _PyBytesWriter_Dealloc(CyBytesWriter *writer);

#endif
