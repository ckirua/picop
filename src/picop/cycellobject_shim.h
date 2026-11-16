#ifndef PICOP_CYCELLOBJECT_SHIM_H
#define PICOP_CYCELLOBJECT_SHIM_H
#include <Python.h>

/* Swap a cell's contents in one critical section.
   Returns the previous contents as a NEW reference (None for an empty cell).
   `value` is owned by the caller's Cython frame, so we incref before the cell
   takes ownership — the same accounting as PyCell_Set. */
static inline PyObject *cy_cell_swap(PyObject *cell, PyObject *value)
{
    PyCellObject *c = (PyCellObject *)cell;
    PyObject *old;
    Py_INCREF(value);
    Py_BEGIN_CRITICAL_SECTION(cell);
    old = c->ob_ref;
    c->ob_ref = value;
    Py_END_CRITICAL_SECTION();
    if (old == NULL) {
        Py_INCREF(Py_None);
        return Py_None;
    }
    return old;
}

static inline PyObject *cy_cell_empty(void)
{
    return PyCell_New(NULL);
}
#endif
