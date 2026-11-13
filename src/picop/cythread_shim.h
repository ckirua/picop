/* cythread_shim.h — interpreter guard/view helpers (Order 077).

Version branching happens here so Cython sees one uniform API on 3.8-3.15.
Guard/view structs are incomplete types and thread-state tokens are
`typedef void`; every handle is a void* that is never dereferenced. */
#ifndef CYTHREAD_SHIM_H
#define CYTHREAD_SHIM_H

#include <Python.h>
#include <stdint.h>

#if PY_VERSION_HEX >= 0x030F0000

static inline int cy_interpreter_guards_enabled(void) { return 1; }

static inline void *cy_guard_from_current(void) {
    return (void *)PyInterpreterGuard_FromCurrent();
}

static inline void *cy_guard_from_view(void *view) {
    return (void *)PyInterpreterGuard_FromView((PyInterpreterView *)view);
}

static inline void cy_guard_close(void *guard) {
    if (guard != NULL) PyInterpreterGuard_Close((PyInterpreterGuard *)guard);
}

static inline void *cy_view_from_current(void) {
    return (void *)PyInterpreterView_FromCurrent();
}

static inline void *cy_view_from_main(void) {
    return (void *)PyInterpreterView_FromMain();
}

static inline void cy_view_close(void *view) {
    if (view != NULL) PyInterpreterView_Close((PyInterpreterView *)view);
}

static inline void *cy_threadstate_ensure(void *guard) {
    return (void *)PyThreadState_Ensure((PyInterpreterGuard *)guard);
}

static inline void *cy_threadstate_ensure_from_view(void *view) {
    return (void *)PyThreadState_EnsureFromView((PyInterpreterView *)view);
}

static inline void cy_threadstate_release(void *token) {
    PyThreadState_Release((PyThreadStateToken *)token);
}

#else  /* < 3.15: guards/views unavailable; ensure/release fall back to GILState */

static inline int cy_interpreter_guards_enabled(void) { return 0; }

static inline void *cy_guard_from_current(void) {
    PyErr_SetString(PyExc_RuntimeError, "interpreter guards require CPython 3.15+");
    return NULL;
}

static inline void *cy_guard_from_view(void *view) { (void)view; return NULL; }
static inline void cy_guard_close(void *guard) { (void)guard; }

static inline void *cy_view_from_current(void) {
    PyErr_SetString(PyExc_RuntimeError, "interpreter views require CPython 3.15+");
    return NULL;
}

static inline void *cy_view_from_main(void) { return NULL; }
static inline void cy_view_close(void *view) { (void)view; }

static inline void *cy_threadstate_ensure(void *guard) {
    (void)guard;
    return (void *)(uintptr_t)PyGILState_Ensure();
}

static inline void *cy_threadstate_ensure_from_view(void *view) {
    (void)view;
    return (void *)(uintptr_t)PyGILState_Ensure();
}

static inline void cy_threadstate_release(void *token) {
    PyGILState_Release((PyGILState_STATE)(uintptr_t)token);
}

#endif

#endif /* CYTHREAD_SHIM_H */
