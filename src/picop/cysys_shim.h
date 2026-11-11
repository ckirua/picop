#ifndef PICOP_CYSYS_SHIM_H
#define PICOP_CYSYS_SHIM_H

#include <Python.h>
#include <sysmodule.h>
#if PY_VERSION_HEX >= 0x030F0000
static inline PyObject *picop_sys_get_attr(PyObject *name) { return PySys_GetAttr(name); }
static inline PyObject *picop_sys_get_attr_string(const char *name) { return PySys_GetAttrString(name); }
static inline int picop_sys_get_optional_attr(PyObject *name, PyObject **result) { return PySys_GetOptionalAttr(name, result); }
static inline int picop_sys_get_optional_attr_string(const char *name, PyObject **result) { return PySys_GetOptionalAttrString(name, result); }
#else
static inline PyObject *picop_sys_api_unavailable(void) {
    PyErr_SetString(PyExc_NotImplementedError, "PySys attribute APIs require CPython 3.15 or newer");
    return NULL;
}
static inline PyObject *picop_sys_get_attr(PyObject *name) { (void)name; return picop_sys_api_unavailable(); }
static inline PyObject *picop_sys_get_attr_string(const char *name) { (void)name; return picop_sys_api_unavailable(); }
static inline int picop_sys_get_optional_attr(PyObject *name, PyObject **result) { (void)name; (void)result; picop_sys_api_unavailable(); return -1; }
static inline int picop_sys_get_optional_attr_string(const char *name, PyObject **result) { (void)name; (void)result; picop_sys_api_unavailable(); return -1; }
#endif
#endif
