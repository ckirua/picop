#ifndef CYCEL_CYCODE_SHIM_H
#define CYCEL_CYCODE_SHIM_H

#include <Python.h>

static inline PyObject *cy_code_name(PyCodeObject *code)
{
    return Py_NewRef(code->co_name);
}

static inline PyObject *cy_code_qualname(PyCodeObject *code)
{
    return Py_NewRef(code->co_qualname);
}

static inline PyObject *cy_code_filename(PyCodeObject *code)
{
    return Py_NewRef(code->co_filename);
}

static inline int cy_code_firstlineno(PyCodeObject *code)
{
    return code->co_firstlineno;
}

static inline int cy_code_argcount(PyCodeObject *code)
{
    return code->co_argcount;
}

static inline int cy_code_posonlyargcount(PyCodeObject *code)
{
    return code->co_posonlyargcount;
}

static inline int cy_code_kwonlyargcount(PyCodeObject *code)
{
    return code->co_kwonlyargcount;
}

static inline PyObject *cy_code_consts(PyCodeObject *code)
{
    return Py_NewRef(code->co_consts);
}

static inline PyObject *cy_code_names(PyCodeObject *code)
{
    return Py_NewRef(code->co_names);
}

#endif /* CYCEL_CYCODE_SHIM_H */
