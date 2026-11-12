#ifndef CYCEL_CYBYTES_SHIM_H
#define CYCEL_CYBYTES_SHIM_H

#include <stddef.h>
#include <stdlib.h>
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
 * Incremental bytes writer.
 *
 * CPython 3.15+ exports a real public API (cpython/bytesobject.h:
 * PyBytesWriter_Create / WriteBytes / Finish / Discard) with an opaque
 * struct; we use it directly.
 *
 * CPython 3.8-3.14 has no public writer API. The internal _PyBytesWriter
 * (internal/pycore_bytesobject.h) cannot be included by extension modules
 * (it requires Py_BUILD_CORE), but its functions are non-static in the
 * interpreter (exported for _pickle), so the linker resolves them against
 * this field-for-field mirror of the struct.
 *
 * Both paths expose the same uniform wrapper API:
 *   cy_bytes_writer_create(size) -> writer (NULL on error, exception set)
 *   cy_bytes_writer_write(writer, data, size) -> 0 / -1 (exception set)
 *   cy_bytes_writer_finish(writer) -> bytes (NULL on error)
 *   cy_bytes_writer_discard(writer)
 */
#if PY_VERSION_HEX < 0x030F0000
typedef struct CyInternalBytesWriter {
    PyObject *buffer;
    Py_ssize_t allocated;
    Py_ssize_t min_size;
    int use_bytearray;
    int overallocate;
    int use_small_buffer;
    char small_buffer[512];
} CyInternalBytesWriter;
#endif

typedef struct CyBytesWriter {
#if PY_VERSION_HEX >= 0x030F0000
    PyBytesWriter *pub;
#else
    CyInternalBytesWriter internal;
    char *pos;
#endif
} CyBytesWriter;

#if PY_VERSION_HEX >= 0x030F0000

static inline CyBytesWriter *cy_bytes_writer_create(Py_ssize_t size) {
    CyBytesWriter *w = (CyBytesWriter *)malloc(sizeof(CyBytesWriter));
    if (w == NULL) {
        PyErr_NoMemory();
        return NULL;
    }
    w->pub = PyBytesWriter_Create(size);
    if (w->pub == NULL) {
        free(w);
        return NULL;
    }
    return w;
}

static inline int cy_bytes_writer_write(CyBytesWriter *w, const char *data,
                                        Py_ssize_t size) {
    return PyBytesWriter_WriteBytes(w->pub, data, size);
}

static inline PyObject *cy_bytes_writer_finish(CyBytesWriter *w) {
    PyObject *result = PyBytesWriter_Finish(w->pub);
    free(w);
    return result;
}

static inline void cy_bytes_writer_discard(CyBytesWriter *w) {
    PyBytesWriter_Discard(w->pub);
    free(w);
}

#else

extern void _PyBytesWriter_Init(CyInternalBytesWriter *writer);
extern void *_PyBytesWriter_Prepare(CyInternalBytesWriter *writer, void *str, Py_ssize_t size);
extern PyObject *_PyBytesWriter_Finish(CyInternalBytesWriter *writer, void *str);
extern void _PyBytesWriter_Dealloc(CyInternalBytesWriter *writer);

static inline CyBytesWriter *cy_bytes_writer_create(Py_ssize_t size) {
    CyBytesWriter *w = (CyBytesWriter *)malloc(sizeof(CyBytesWriter));
    if (w == NULL) {
        PyErr_NoMemory();
        return NULL;
    }
    memset(w, 0, sizeof(CyBytesWriter));
    _PyBytesWriter_Init(&w->internal);
    /* Replicate _PyBytesWriter_Alloc(): it is not exported under its own
       name in all builds, but Prepare from the small buffer is equivalent. */
    w->internal.use_small_buffer = 1;
    w->internal.overallocate = 1;
    w->internal.allocated = 512;
    if (size > 0) {
        w->pos = (char *)_PyBytesWriter_Prepare(&w->internal, w->internal.small_buffer, size);
        if (w->pos == NULL) {
            free(w);
            return NULL;
        }
    } else {
        w->pos = w->internal.small_buffer;
    }
    return w;
}

static inline int cy_bytes_writer_write(CyBytesWriter *w, const char *data,
                                        Py_ssize_t size) {
    w->pos = (char *)_PyBytesWriter_Prepare(&w->internal, w->pos, size);
    if (w->pos == NULL) {
        return -1;
    }
    memcpy(w->pos, data, (size_t)size);
    w->pos += size;
    return 0;
}

static inline PyObject *cy_bytes_writer_finish(CyBytesWriter *w) {
    PyObject *result = _PyBytesWriter_Finish(&w->internal, w->pos);
    free(w);
    return result;
}

static inline void cy_bytes_writer_discard(CyBytesWriter *w) {
    _PyBytesWriter_Dealloc(&w->internal);
    free(w);
}

#endif

#endif
