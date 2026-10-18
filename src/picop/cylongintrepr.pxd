# cylongintrepr.pxd
# Internals of CPython ``int`` (digit layout). cimport-only — no public surface.
# Unsafe: ``_PyLong_New`` leaves digits uninitialized; fill before expose.
# Python 3.14+: digits live at ``PyLongObject.long_value.ob_digit`` (Cython's
# ``cpython.longintrepr`` still models the pre-3.12 flat ``ob_digit`` field).

from cpython.longintrepr cimport (
    PyLong_BASE,
    PyLong_MASK,
    PyLong_SHIFT,
    _PyLong_New,
    digit,
    py_long,
    sdigit,
)

cdef extern from *:
    """
    static inline digit *cypy_longrepr_digits(void *o) {
        return ((PyLongObject *)o)->long_value.ob_digit;
    }
    """
    digit *cypy_longrepr_digits(void *o) noexcept


cdef inline py_long longrepr_new(Py_ssize_t size):
    # Size in digits; uninitialized ob_digit — fill before Python exposure.
    return _PyLong_New(size)


cdef inline digit *longrepr_digits(py_long o) noexcept:
    return cypy_longrepr_digits(<void *>o)
