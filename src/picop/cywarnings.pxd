cdef extern from "Python.h":
    int PyErr_WarnEx(object category, const char *message, Py_ssize_t stacklevel) except -1
    int PyErr_WarnExplicitObject(object category, object message, object filename, int lineno, object module, object registry) except -1
cdef extern from *:
    """
    #include <Python.h>
    static PyObject *_picop_get_warnings_module(void) {
        PyObject *module = PyImport_AddModuleRef("warnings");
        if (module == NULL && !PyErr_Occurred()) {
            Py_INCREF(Py_None);
            return Py_None;
        }
        return module;
    }
    """
    object _picop_get_warnings_module()

cdef inline object get_warnings_module():
    return _picop_get_warnings_module()

cpdef bint warn_ex(object category, object message, Py_ssize_t stacklevel=*) except -1
cpdef bint warn_explicit(object category, object message, object filename, int lineno, object module=*, object registry=*) except -1
cpdef object warnings_module()
