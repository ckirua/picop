#ifndef CYCEL_CYFRAME_SHIM_H
#define CYCEL_CYFRAME_SHIM_H

#include <Python.h>

/*
 * ``PyFrame_GetCode``/``GetBack``/``GetGenerator``/``GetVar``/``PyFrame_New``
 * all return a *new* reference.  Declaring them as ``PyObject *`` and casting
 * with ``<object>`` increfs an already-owned reference, leaking one per call.
 * The shim keeps the C signatures honest; the ``object`` externs in
 * ``cyframe.pxd`` let Cython take the reference instead.
 */

static inline PyObject *cy_frame_code(PyFrameObject *frame)
{
    return (PyObject *)PyFrame_GetCode(frame);
}

static inline PyObject *cy_frame_back(PyFrameObject *frame)
{
    PyFrameObject *back = PyFrame_GetBack(frame);
    return back ? (PyObject *)back : Py_NewRef(Py_None);
}

static inline PyObject *cy_frame_generator(PyFrameObject *frame)
{
    PyObject *generator = PyFrame_GetGenerator(frame);
    return generator ? generator : Py_NewRef(Py_None);
}

static inline PyObject *cy_frame_var(PyFrameObject *frame, PyObject *name)
{
    /* Sets NameError when the variable is missing; ``except NULL`` propagates it. */
    return PyFrame_GetVar(frame, name);
}

static inline PyObject *cy_frame_var_cstr(PyFrameObject *frame, const char *name)
{
    return PyFrame_GetVarString(frame, name);
}

static inline PyObject *cy_frame_new(PyThreadState *tstate, PyCodeObject *code,
                                     PyObject *globals, PyObject *locals)
{
    return (PyObject *)PyFrame_New(tstate, code, globals, locals);
}

#endif
