#ifndef CYCEL_CYTUPLE_SHIM_H
#define CYCEL_CYTUPLE_SHIM_H

#include <Python.h>

/*
 * PyTuple_FromArray() is public only on CPython 3.15+. On older versions the
 * same semantics are spelled out directly: allocate a fresh tuple and INCREF
 * each array element (the caller keeps its own references). Negative sizes
 * raise ValueError instead of invoking undefined behaviour.
 */
static inline PyObject *cy_tuple_from_array(PyObject *const *array, Py_ssize_t size)
{
    if (size < 0) {
        PyErr_SetString(PyExc_ValueError, "size must be >= 0");
        return NULL;
    }
#if PY_VERSION_HEX >= 0x030F0000
    return PyTuple_FromArray(array, size);
#else
    PyObject *t = PyTuple_New(size);
    if (t == NULL) {
        return NULL;
    }
    for (Py_ssize_t i = 0; i < size; i++) {
        Py_INCREF(array[i]);
        PyTuple_SET_ITEM(t, i, array[i]);
    }
    return t;
#endif
}

#endif /* CYCEL_CYTUPLE_SHIM_H */
