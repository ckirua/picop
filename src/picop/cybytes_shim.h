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
 *   cy_bytes_writer_size(writer) -> logical size
 *   cy_bytes_writer_data(writer) -> buffer base
 *   cy_bytes_writer_grow(writer, extra) -> newly reserved region
 *   cy_bytes_writer_finish_with_size(writer, size) -> bytes (NULL on error)
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
    Py_ssize_t written;   /* logical size; the buffer base is pos - written */
#endif
} CyBytesWriter;


#if PY_VERSION_HEX >= 0x030F0000

static inline CyBytesWriter *cy_bytes_writer_create(Py_ssize_t size) {
    CyBytesWriter *w = (CyBytesWriter *)malloc(sizeof(CyBytesWriter));
    if (w == NULL) {
        PyErr_NoMemory();
        return NULL;
    }
    /* 3.15's public writer has no pure reservation call: Create(size)
       allocates the buffer but also sets the logical size to size, and
       Resize sets the size too (it never shrinks the allocation). Creating
       with the hint and rewinding to zero via Resize(0) turns the hint into
       reserved capacity: writes then fill from offset 0 and Finish()
       truncates to the bytes actually written. */
    if (size > 0) {
        w->pub = PyBytesWriter_Create(size);
        if (w->pub == NULL || PyBytesWriter_Resize(w->pub, 0) < 0) {
            PyBytesWriter_Discard(w->pub);
            free(w);
            return NULL;
        }
    }
    else {
        w->pub = PyBytesWriter_Create(0);
        if (w->pub == NULL) {
            free(w);
            return NULL;
        }
    }
    return w;
}

static inline int cy_bytes_writer_write(CyBytesWriter *w, const char *data,
                                        Py_ssize_t size) {
    return PyBytesWriter_WriteBytes(w->pub, data, size);
}

static inline Py_ssize_t cy_bytes_writer_size(const CyBytesWriter *w) {
    return PyBytesWriter_GetSize(w->pub);
}

static inline char *cy_bytes_writer_data(const CyBytesWriter *w) {
    return (char *)PyBytesWriter_GetData(w->pub);
}

/* Grow the logical size by extra (may be negative) and return a pointer to the
   start of the newly reserved region. Any pointer captured before a later
   grow/write is invalid: the buffer may be reallocated. */
static inline char *cy_bytes_writer_grow(CyBytesWriter *w, Py_ssize_t extra) {
    return (char *)PyBytesWriter_GrowAndUpdatePointer(
        w->pub, extra,
        PyBytesWriter_GetData(w->pub) + PyBytesWriter_GetSize(w->pub));
}

/* CPython's FinishWithSize discards the writer on a bad size; validate first so
   a rejected call leaves the writer usable. */
static inline PyObject *cy_bytes_writer_finish_with_size(CyBytesWriter *w,
                                                         Py_ssize_t size) {
    Py_ssize_t used = PyBytesWriter_GetSize(w->pub);
    if (size < 0 || size > used) {
        PyErr_Format(PyExc_ValueError, "size must be between 0 and %zd", used);
        return NULL;
    }
    PyObject *result = PyBytesWriter_FinishWithSize(w->pub, size);
    free(w);
    return result;
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
    w->written += size;
    return 0;
}

static inline Py_ssize_t cy_bytes_writer_size(const CyBytesWriter *w) { return w->written; }
static inline char *cy_bytes_writer_data(const CyBytesWriter *w) { return w->pos - w->written; }

static inline char *cy_bytes_writer_grow(CyBytesWriter *w, Py_ssize_t extra) {
    if (extra < 0) {
        if (w->written + extra < 0) {
            PyErr_SetString(PyExc_ValueError, "grow would make the writer size negative");
            return NULL;
        }
        w->pos += extra;
        w->written += extra;
        return w->pos;
    }
    char *str = (char *)_PyBytesWriter_Prepare(&w->internal, w->pos, extra);
    if (str == NULL) {
        return NULL;
    }
    w->pos = str + extra;
    w->written += extra;
    return str;
}

static inline PyObject *cy_bytes_writer_finish_with_size(CyBytesWriter *w,
                                                         Py_ssize_t size) {
    if (size < 0 || size > w->written) {
        PyErr_Format(PyExc_ValueError, "size must be between 0 and %zd", w->written);
        return NULL;
    }
    PyObject *result = _PyBytesWriter_Finish(&w->internal, (w->pos - w->written) + size);
    free(w);
    return result;
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
