# cython: freethreading_compatible=True
# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
"""CPython warning helpers."""


from .cywarnings cimport get_warnings_module

cpdef bint warn_ex(object category, object message, Py_ssize_t stacklevel=1) except -1:
    """Issue a warning using the active warnings filter."""
    if not isinstance(category, type) or not issubclass(category, Warning):
        raise TypeError("category must be a Warning subclass")
    cdef bytes encoded = str(message).encode()
    return PyErr_WarnEx(category, encoded, stacklevel)

cpdef bint warn_explicit(object category, object message, object filename, int lineno, object module=None, object registry=None) except -1:
    """Issue an explicitly located warning using the active warnings filter."""
    if not isinstance(category, type) or not issubclass(category, Warning):
        raise TypeError("category must be a Warning subclass")
    if module is None:
        module = filename
    return PyErr_WarnExplicitObject(category, message, filename, lineno, module, registry)

cpdef object warnings_module():
    """Return the initialized warnings module, or None if unavailable."""
    return get_warnings_module()
