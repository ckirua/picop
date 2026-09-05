# cyarray.pxd
# Wrappers over Cython ``cpython.array`` (stdlib ``array.array`` buffer helpers).
# Public docs live in ``cyarray.pyi``. Pointer/resize paths: prefer cdef.

from cpython.array cimport (
    array,
    clone as _ay_clone,
    copy as _ay_copy,
    extend as _ay_extend,
    extend_buffer as _ay_extend_buffer,
    resize as _ay_resize,
    resize_smart as _ay_resize_smart,
    zero as _ay_zero,
)
from cpython.object cimport Py_SIZE
from libc.stddef cimport size_t
from libc.string cimport memcmp


cdef inline bint aycheck(object p):
    return isinstance(p, array)


cdef inline bint aycheck_exact(object p):
    return type(p) is array


cdef inline Py_ssize_t aylen(array a) noexcept:
    return Py_SIZE(a)


cdef inline bint ayeq(array a, array b) noexcept:
    # Identity / typecode / len short-circuit + memcmp on item buffer.
    if a is b:
        return True
    if a.ob_descr.typecode_char != b.ob_descr.typecode_char:
        return False
    cdef Py_ssize_t n = Py_SIZE(a)
    if n != Py_SIZE(b):
        return False
    if n == 0:
        return True
    cdef size_t nbytes = <size_t>n * <size_t>a.ob_descr.itemsize
    return memcmp(a.data.as_chars, b.data.as_chars, nbytes) == 0


cdef inline bint ayne(array a, array b) noexcept:
    return not ayeq(a, b)


cdef inline array aycopy(array a):
    return _ay_copy(a)


cdef inline array ayclone(array template, Py_ssize_t length, bint zero=True):
    return _ay_clone(template, length, zero)


cdef inline int ayextend(array self, array other) except -1:
    return _ay_extend(self, other)


cdef inline int ayzero(array a) except -1:
    _ay_zero(a)
    return 0


cdef inline int ayresize(array a, Py_ssize_t n) except -1:
    return _ay_resize(a, n)


cdef inline int ayresize_smart(array a, Py_ssize_t n) except -1:
    return _ay_resize_smart(a, n)


cdef inline int ayextend_buffer(array self, char *stuff, Py_ssize_t n) except -1:
    # Append n elements from raw buffer (same typecode).
    return _ay_extend_buffer(self, stuff, n)

# Wave 4 N1/N5 preferred names (0.3: soft letter/bare are cdef-only)

cpdef inline bint array_check(object p):
    return aycheck(p)

cpdef inline bint array_check_exact(object p):
    return aycheck_exact(p)

cpdef inline array array_clone(array template, Py_ssize_t length, bint zero=True):
    return ayclone(template, length, zero)

cpdef inline array array_copy(array a):
    return aycopy(a)

cpdef inline int array_extend(array self, array other) except -1:
    return ayextend(self, other)

cdef inline int array_extend_buffer(array self, char *stuff, Py_ssize_t n) except -1:
    return ayextend_buffer(self, stuff, n)

cpdef inline Py_ssize_t array_len(array a) noexcept:
    return aylen(a)

cpdef inline bint array_eq(array a, array b) noexcept:
    return ayeq(a, b)

cpdef inline bint array_ne(array a, array b) noexcept:
    return ayne(a, b)

cpdef inline int array_resize(array a, Py_ssize_t n) except -1:
    return ayresize(a, n)

cpdef inline int array_resize_smart(array a, Py_ssize_t n) except -1:
    return ayresize_smart(a, n)

cpdef inline int array_zero(array a) except -1:
    return ayzero(a)

