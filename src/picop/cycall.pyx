# cython: freethreading_compatible=True
# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
"""CPython call helpers requiring an attached thread state."""

from cpython.object cimport PyObject


cpdef object call_noargs(object callable):
    """Call ``callable`` without constructing an argument tuple."""
    return PyObject_CallNoArgs(callable)


cpdef object call_onearg(object callable, object arg):
    """Call ``callable(arg)`` without constructing an argument tuple."""
    return PyObject_CallOneArg(callable, arg)


cpdef object call_twoargs(object callable, object arg0, object arg1):
    """Call ``callable(arg0, arg1)`` through the vectorcall protocol."""
    cdef PyObject *args[2]
    args[0] = <PyObject *>arg0
    args[1] = <PyObject *>arg1
    # ``PyObject_Vectorcall`` returns a new reference; the ``<object>`` cast
    # would incref it again, so convert and release the raw pointer.
    cdef PyObject *result = PyObject_Vectorcall(<PyObject *>callable, args, 2, NULL)
    cdef object out = <object>result
    Py_DECREF(result)
    return out


cdef object call_vector(object callable, PyObject *const *args, size_t nargsf, PyObject *kwnames):
    """Vectorcall with a caller-owned argument vector.

    ``args`` and ``kwnames`` are borrowed for the duration of the call. ``nargsf``
    is passed straight to CPython, so the PY_VECTORCALL_ARGUMENTS_OFFSET bit is
    allowed when ``args[-1]`` is a live reserved slot. ``kwnames`` must be NULL or
    a tuple; ``Py_None`` is undefined (measured SIGSEGV).
    """
    cdef PyObject *result = PyObject_Vectorcall(<PyObject *>callable, args, nargsf, kwnames)
    cdef object out = <object>result
    Py_DECREF(result)
    return out


cdef object call_method_noargs(object self, object name):
    """Call ``self.name()`` without an argument tuple."""
    return PyObject_CallMethodNoArgs(self, name)


cdef object call_method_onearg(object self, object name, object arg):
    """Call ``self.name(arg)`` without an argument tuple."""
    return PyObject_CallMethodOneArg(self, name, arg)


cdef object call_method_vector(object name, PyObject *const *args, size_t nargsf, PyObject *kwnames):
    """Vectorcall a looked-up method; ``args[0]`` is the receiver and counts in ``nargsf``."""
    cdef PyObject *result = PyObject_VectorcallMethod(<PyObject *>name, args, nargsf, kwnames)
    cdef object out = <object>result
    Py_DECREF(result)
    return out


cdef Py_ssize_t vectorcall_nargs(size_t nargsf) noexcept:
    """Strip the PY_VECTORCALL_ARGUMENTS_OFFSET bit from ``nargsf``."""
    return PyVectorcall_NARGS(nargsf)
