/* cysentinel_shim.h — version-gated sentinel primitives.
 *
 * ``sentinel`` is new in CPython 3.15. The shim keeps the module
 * compilable on the supported 3.14 line.
 */
#ifndef CYCEL_CYSENTINEL_SHIM_H
#define CYCEL_CYSENTINEL_SHIM_H

#include <Python.h>

#if PY_VERSION_HEX >= 0x030F0000

static inline PyObject *cy_sentinel_type(void)
{
    Py_INCREF(&PySentinel_Type);
    return (PyObject *)&PySentinel_Type;
}

static inline int cy_sentinel_check(PyObject *obj)
{
    return PySentinel_Check(obj);
}

static inline int cy_sentinel_check_exact(PyObject *obj)
{
    return PySentinel_CheckExact(obj);
}

static inline PyObject *cy_sentinel_new(const char *name, const char *module,
                                        const char *repr)
{
    return PySentinel_New(name, module, repr);
}


#else /* CPython < 3.15: no sentinel type */

static inline PyObject *cy_sentinel_type(void)
{
    PyErr_SetString(PyExc_NotImplementedError,
                    "sentinel requires CPython 3.15 or newer");
    return NULL;
}

static inline int cy_sentinel_check(PyObject *obj)
{
    (void)obj;
    return 0;
}

static inline int cy_sentinel_check_exact(PyObject *obj)
{
    (void)obj;
    return 0;
}

static inline PyObject *cy_sentinel_new(const char *name, const char *module,
                                        const char *repr)
{
    (void)name;
    (void)module;
    (void)repr;
    PyErr_SetString(PyExc_NotImplementedError,
                    "sentinel requires CPython 3.15 or newer");
    return NULL;
}

#endif /* PY_VERSION_HEX */

#endif /* CYCEL_CYSENTINEL_SHIM_H */
