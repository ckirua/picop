/* cyfrozendict_shim.h — version-gated frozendict primitives.
 *
 * ``frozendict`` is new in CPython 3.15.  The shim keeps the module
 * compilable on the supported 3.14 line: checks answer ``False`` and the
 * constructors raise ``NotImplementedError`` instead of failing to link.
 */
#ifndef CYCEL_CYFROZENDICT_SHIM_H
#define CYCEL_CYFROZENDICT_SHIM_H

#include <Python.h>

#if PY_VERSION_HEX >= 0x030F0000

static inline int cy_frozendict_check(PyObject *obj)
{
    return PyFrozenDict_Check(obj);
}

static inline int cy_frozendict_check_exact(PyObject *obj)
{
    return PyFrozenDict_CheckExact(obj);
}

static inline int cy_anydict_check(PyObject *obj)
{
    return PyAnyDict_Check(obj);
}

static inline int cy_anydict_check_exact(PyObject *obj)
{
    return PyAnyDict_CheckExact(obj);
}

static inline PyObject *cy_frozendict_new(PyObject *iterable)
{
    return PyFrozenDict_New(iterable);
}

static inline PyObject *cy_frozendict_new_empty(void)
{
    return PyFrozenDict_New(NULL);
}

static inline Py_ssize_t cy_anydict_len(PyObject *obj)
{
    return PyDict_GET_SIZE(obj);
}

#else /* CPython < 3.15: no frozendict type */

static inline int cy_frozendict_check(PyObject *obj)
{
    (void)obj;
    return 0;
}

static inline int cy_frozendict_check_exact(PyObject *obj)
{
    (void)obj;
    return 0;
}

static inline int cy_anydict_check(PyObject *obj)
{
    return PyDict_Check(obj);
}

static inline int cy_anydict_check_exact(PyObject *obj)
{
    return PyDict_CheckExact(obj);
}

static inline PyObject *cy_frozendict_new(PyObject *iterable)
{
    (void)iterable;
    PyErr_SetString(PyExc_NotImplementedError,
                    "frozendict requires CPython 3.15 or newer");
    return NULL;
}

static inline PyObject *cy_frozendict_new_empty(void)
{
    PyErr_SetString(PyExc_NotImplementedError,
                    "frozendict requires CPython 3.15 or newer");
    return NULL;
}

static inline Py_ssize_t cy_anydict_len(PyObject *obj)
{
    return PyDict_GET_SIZE(obj);
}

#endif /* PY_VERSION_HEX */

#endif /* CYCEL_CYFROZENDICT_SHIM_H */
