#ifndef PICOP_CYPICKLEBUF_SHIM_H
#define PICOP_CYPICKLEBUF_SHIM_H

#include <Python.h>

/* PyPickleBuffer_FromObject / Release / Check / GetBuffer are public C-API
   in every supported interpreter (declared in cpython/picklebufobject.h since
   3.8, exported by 3.14 and 3.15), so there is no version branch here. */
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

#endif
