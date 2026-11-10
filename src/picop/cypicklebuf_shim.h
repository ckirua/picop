#ifndef PICOP_CYPICKLEBUF_SHIM_H
#define PICOP_CYPICKLEBUF_SHIM_H

#include <Python.h>

#if PY_VERSION_HEX >= 0x030F0000
#  include <cpython/picklebufobject.h>

static inline PyObject *picop_pickle_buffer_from_object(PyObject *obj) {
    return PyPickleBuffer_FromObject(obj);
}
static inline int picop_pickle_buffer_release(PyObject *obj) {
    return PyPickleBuffer_Release(obj);
}
static inline int picop_pickle_buffer_check(PyObject *obj) {
    return PyPickleBuffer_Check(obj);
}
static inline const Py_buffer *picop_pickle_buffer_get_buffer(PyObject *obj) {
    return PyPickleBuffer_GetBuffer(obj);
}
static inline PyTypeObject *picop_pickle_buffer_type(void) {
    return &PyPickleBuffer_Type;
}
#else
static inline PyObject *picop_pickle_buffer_unavailable(void) {
    PyErr_SetString(PyExc_NotImplementedError,
                    "PickleBuffer C APIs require CPython 3.15 or newer");
    return NULL;
}
static inline PyObject *picop_pickle_buffer_from_object(PyObject *obj) {
    (void)obj;
    return picop_pickle_buffer_unavailable();
}
static inline int picop_pickle_buffer_release(PyObject *obj) {
    (void)obj;
    picop_pickle_buffer_unavailable();
    return -1;
}
static inline int picop_pickle_buffer_check(PyObject *obj) {
    (void)obj;
    picop_pickle_buffer_unavailable();
    return -1;
}
static inline const Py_buffer *picop_pickle_buffer_get_buffer(PyObject *obj) {
    (void)obj;
    picop_pickle_buffer_unavailable();
    return NULL;
}
static inline PyTypeObject *picop_pickle_buffer_type(void) {
    picop_pickle_buffer_unavailable();
    return NULL;
}
#endif

#endif
