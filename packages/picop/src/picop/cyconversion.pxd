# cyconversion.pxd
# OS string/double conversion. Public docs in ``cyconversion.pyi``.
# snprintf/vsnprintf/double_to_string: cimport (buffers).

cdef extern from "Python.h":
    double PyOS_string_to_double(const char *s, char **endptr, object overflow_exception) except? -1.0
    char *PyOS_double_to_string(double val, char format_code, int precision, int flags, int *ptype) except? NULL
    int PyOS_stricmp(const char *s1, const char *s2) noexcept
    int PyOS_strnicmp(const char *s1, const char *s2, Py_ssize_t size) noexcept
    enum:
        Py_DTSF_SIGN
        Py_DTSF_ADD_DOT_0
        Py_DTSF_ALT


cdef inline double conv_string_to_double(const char *s) except? -1.0:
    return PyOS_string_to_double(s, NULL, None)


cpdef inline int conv_stricmp(const char *s1, const char *s2) noexcept:
    return PyOS_stricmp(s1, s2)


cpdef inline int conv_strnicmp(const char *s1, const char *s2, Py_ssize_t size) noexcept:
    return PyOS_strnicmp(s1, s2, size)


cdef inline char *conv_double_to_string(double val, char format_code, int precision, int flags, int *ptype) except? NULL:
    # Caller must PyMem_Free the result.
    return PyOS_double_to_string(val, format_code, precision, flags, ptype)
# N2 preferred *_cstr (0.3: *_string cdef-only where soft)

cpdef inline double conv_cstr_to_double(const char *s) except? -1.0:
    return conv_string_to_double(s)
