#ifndef PICOP_CYCRITICALSECTION_SHIM_H
#define PICOP_CYCRITICALSECTION_SHIM_H

#include <Python.h>

/* CPython's `PyCriticalSection` layout is explicitly private and its body is
   only visible in free-threaded builds, so an extension cannot stack-allocate
   one portably. Callers stack-allocate one of these aligned buffers instead;
   the wrappers below reinterpret it and never touch its fields.
   64 / 128 bytes are far larger than the real structs (16 / 24 bytes on
   64-bit), and `uintptr_t` guarantees the pointer alignment CPython needs. */
typedef struct {
    uintptr_t _data[8];
} PicopCriticalSection;

typedef struct {
    uintptr_t _data[16];
} PicopCriticalSection2;

#ifdef Py_GIL_DISABLED
/* Compile-time proof that the buffers are big enough for the private structs. */
static char picop_cs_size_ok[sizeof(PyCriticalSection) <= sizeof(PicopCriticalSection)];
static char picop_cs2_size_ok[sizeof(PyCriticalSection2) <= sizeof(PicopCriticalSection2)];
#endif

static inline int picop_critical_sections_enabled(void) {
#ifdef Py_GIL_DISABLED
    return 1;
#else
    return 0;
#endif
}

static inline void picop_cs_begin(PicopCriticalSection *buf, PyObject *op) {
#ifdef Py_GIL_DISABLED
    PyCriticalSection *c = (PyCriticalSection *)buf;
    PyCriticalSection_Begin(c, op);
#else
    (void)buf;
    (void)op;
#endif
}

static inline void picop_cs_begin_mutex(PicopCriticalSection *buf, PyMutex *mutex) {
#ifdef Py_GIL_DISABLED
    PyCriticalSection *c = (PyCriticalSection *)buf;
    PyCriticalSection_BeginMutex(c, mutex);
#else
    (void)buf;
    (void)mutex;
#endif
}

static inline void picop_cs_end(PicopCriticalSection *buf) {
#ifdef Py_GIL_DISABLED
    PyCriticalSection_End((PyCriticalSection *)buf);
#else
    (void)buf;
#endif
}

static inline void picop_cs2_begin(PicopCriticalSection2 *buf, PyObject *a, PyObject *b) {
#ifdef Py_GIL_DISABLED
    PyCriticalSection2 *c = (PyCriticalSection2 *)buf;
    PyCriticalSection2_Begin(c, a, b);
#else
    (void)buf;
    (void)a;
    (void)b;
#endif
}

static inline void picop_cs2_begin_mutex(PicopCriticalSection2 *buf, PyMutex *m1, PyMutex *m2) {
#ifdef Py_GIL_DISABLED
    PyCriticalSection2 *c = (PyCriticalSection2 *)buf;
    PyCriticalSection2_BeginMutex(c, m1, m2);
#else
    (void)buf;
    (void)m1;
    (void)m2;
#endif
}

static inline void picop_cs2_end(PicopCriticalSection2 *buf) {
#ifdef Py_GIL_DISABLED
    PyCriticalSection2_End((PyCriticalSection2 *)buf);
#else
    (void)buf;
#endif
}

#endif
