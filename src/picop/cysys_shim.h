#ifndef PICOP_CYSYS_SHIM_H
#define PICOP_CYSYS_SHIM_H

#include <Python.h>
#include <sysmodule.h>
#if PY_VERSION_HEX >= 0x030F0000
static inline PyObject *picop_sys_get_attr(PyObject *name) { return PySys_GetAttr(name); }
static inline PyObject *picop_sys_get_attr_string(const char *name) { return PySys_GetAttrString(name); }
static inline int picop_sys_get_optional_attr(PyObject *name, PyObject **result) { return PySys_GetOptionalAttr(name, result); }
static inline int picop_sys_get_optional_attr_string(const char *name, PyObject **result) { return PySys_GetOptionalAttrString(name, result); }
/* import.h lazy-import controls (CPython 3.15+); PyImport_LAZY_NORMAL == 0. */
static inline int picop_lazy_imports_supported(void) { return 1; }
static inline int picop_lazy_mode_set(int mode) { return PyImport_SetLazyImportsMode((PyImport_LazyImportsMode)mode); }
static inline int picop_lazy_mode_get(void) { return (int)PyImport_GetLazyImportsMode(); }
static inline int picop_lazy_filter_set(PyObject *filter) { return PyImport_SetLazyImportsFilter(filter); }
static inline PyObject *picop_lazy_filter_get(void) { return PyImport_GetLazyImportsFilter(); }
#else
static inline PyObject *picop_sys_api_unavailable(void) {
    PyErr_SetString(PyExc_NotImplementedError, "PySys attribute APIs require CPython 3.15 or newer");
    return NULL;
}
static inline PyObject *picop_sys_get_attr(PyObject *name) { (void)name; return picop_sys_api_unavailable(); }
static inline PyObject *picop_sys_get_attr_string(const char *name) { (void)name; return picop_sys_api_unavailable(); }
static inline int picop_sys_get_optional_attr(PyObject *name, PyObject **result) { (void)name; (void)result; picop_sys_api_unavailable(); return -1; }
static inline int picop_sys_get_optional_attr_string(const char *name, PyObject **result) { (void)name; (void)result; picop_sys_api_unavailable(); return -1; }
static inline int picop_lazy_imports_supported(void) { return 0; }
static inline int picop_lazy_mode_set(int mode) { (void)mode; PyErr_SetString(PyExc_NotImplementedError, "Lazy import controls require CPython 3.15 or newer"); return -1; }
static inline int picop_lazy_mode_get(void) { PyErr_SetString(PyExc_NotImplementedError, "Lazy import controls require CPython 3.15 or newer"); return -1; }
static inline int picop_lazy_filter_set(PyObject *filter) { (void)filter; PyErr_SetString(PyExc_NotImplementedError, "Lazy import controls require CPython 3.15 or newer"); return -1; }
static inline PyObject *picop_lazy_filter_get(void) { PyErr_SetString(PyExc_NotImplementedError, "Lazy import controls require CPython 3.15 or newer"); return NULL; }
#endif
#endif
