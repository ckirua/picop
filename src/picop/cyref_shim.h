/* cyref_shim.h — immortal helper (Order 078).

Version branching happens here so Cython sees one uniform API on every
supported CPython. Mirrors 3.15 `PyUnstable_SetImmortal`: returns 1 when
the object is immortal after the call, 0 when it cannot be pinned
(not uniquely referenced, or a str). On 3.14 the same effect is emulated
by pinning `ob_refcnt` at the immortal threshold. */
#ifndef CYREF_SHIM_H
#define CYREF_SHIM_H

#include <Python.h>

static inline int cy_ref_set_immortal(PyObject *o) {
    if (o == NULL) {
        return 0;
    }
#if PY_VERSION_HEX >= 0x030F0000
    return PyUnstable_SetImmortal(o);
#elif !defined(Py_GIL_DISABLED)
    /* 3.14 GIL emulation: a refcount at the immortal threshold is treated
       as immortal by Py_INCREF/Py_DECREF fast paths (32-bit refcount with
       the sign bit set on 64-bit builds). */
    if (PyUnicode_Check(o)) {
        return 0;
    }
    if (Py_REFCNT(o) >= (Py_ssize_t)_Py_IMMORTAL_MINIMUM_REFCNT) {
        return 1;
    }
    if (Py_REFCNT(o) != 1) {
        return 0;
    }
    o->ob_refcnt = _Py_IMMORTAL_INITIAL_REFCNT;
    return 1;
#else
    /* 3.14 free-threaded builds encode immortality in the shared refcount
       words; pinning there is not safe without internal APIs. Refuse. */
    return 0;
#endif
}

#endif /* CYREF_SHIM_H */
