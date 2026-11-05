#ifndef CYCEL_CYTRACEBACK_SHIM_H
#define CYCEL_CYTRACEBACK_SHIM_H

#include <Python.h>

static inline PyObject *cy_tb_next(PyObject *tb)
{
    PyTracebackObject *t = (PyTracebackObject *)tb;
    return t->tb_next ? Py_NewRef(t->tb_next) : Py_NewRef(Py_None);
}

static inline PyObject *cy_tb_next_raw(PyObject *tb)
{
    PyTracebackObject *t = (PyTracebackObject *)tb;
    return (PyObject *)t->tb_next;
}

static inline PyObject *cy_tb_frame(PyObject *tb)
{
    PyTracebackObject *t = (PyTracebackObject *)tb;
    return Py_NewRef(t->tb_frame);
}

static inline int cy_tb_lineno(PyObject *tb)
{
    PyTracebackObject *t = (PyTracebackObject *)tb;
    if (t->tb_lineno >= 0) {
        return t->tb_lineno;
    }
    if (t->tb_lasti >= 0) {
        /* PyFrame_GetCode returns a new reference; release it after the lookup. */
        PyCodeObject *code = PyFrame_GetCode(t->tb_frame);
        int lineno = PyCode_Addr2Line(code, t->tb_lasti);
        Py_DECREF(code);
        return lineno;
    }
    return PyFrame_GetLineNumber(t->tb_frame);
}

static inline int cy_tb_lasti(PyObject *tb)
{
    PyTracebackObject *t = (PyTracebackObject *)tb;
    return t->tb_lasti;
}

static inline Py_ssize_t cy_tb_depth(PyObject *tb)
{
    PyTracebackObject *t = (PyTracebackObject *)tb;
    Py_ssize_t n = 0;
    while (t) {
        ++n;
        t = t->tb_next;
    }
    return n;
}

#endif /* CYCEL_CYTRACEBACK_SHIM_H */
