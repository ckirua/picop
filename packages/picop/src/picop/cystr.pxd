# cystr.pxd
# High-level ``str`` helpers (custom surface over ``cpython.unicode``).
# UTF-8 / intern: ``cyunicode``. Public docs: ``cystr.pyi``.

from cpython.unicode cimport (
    PyUnicode_1BYTE_KIND,
    PyUnicode_Check,
    PyUnicode_CheckExact,
    PyUnicode_Compare,
    PyUnicode_Concat,
    PyUnicode_DATA,
    PyUnicode_Find,
    PyUnicode_GET_LENGTH,
    PyUnicode_KIND,
    PyUnicode_READ,
    PyUnicode_Tailmatch,
)
from libc.stddef cimport size_t
from libc.string cimport memchr, memcmp

cdef extern from "string.h":
    void* memmem(const void *haystack, size_t haystacklen,
                 const void *needle, size_t needlelen) nogil

cdef extern from *:
    ctypedef unsigned int Py_UCS4

cdef str EMPTY_STR


cdef inline bint ucheck(object obj) noexcept:
    return PyUnicode_Check(obj)


cdef inline bint ucheck_exact(object obj) noexcept:
    return PyUnicode_CheckExact(obj)


cdef inline bint is_str(object obj) noexcept:
    # Exact ``str`` (same as ucheck_exact for built-in str).
    return type(obj) is str


cdef inline bint is_not_str(object obj) noexcept:
    return type(obj) is not str


cdef inline str as_str_or_empty(object obj):
    if type(obj) is str:
        return <str>obj
    return EMPTY_STR


cdef inline str none_to_empty(object obj):
    if obj is None:
        return EMPTY_STR
    if type(obj) is str:
        return <str>obj
    return EMPTY_STR


cpdef inline str str_or_none(object obj):
    if type(obj) is str:
        return <str>obj
    return None


cpdef inline str str_or_empty(object obj):
    if type(obj) is str:
        return <str>obj if obj else ""
    return ""


cdef inline Py_ssize_t strlen(str s) noexcept:
    return PyUnicode_GET_LENGTH(s)


cdef inline bint is_empty(str s) noexcept:
    return PyUnicode_GET_LENGTH(s) == 0


cdef inline bint not_empty(str s) noexcept:
    return PyUnicode_GET_LENGTH(s) != 0


cdef inline bint streq(str a, str b) noexcept:
    if a is b:
        return True
    cdef Py_ssize_t la = PyUnicode_GET_LENGTH(a)
    if la != PyUnicode_GET_LENGTH(b):
        return False
    if la == 0:
        return True
    cdef int kind_a = PyUnicode_KIND(a)
    cdef int kind_b = PyUnicode_KIND(b)
    if kind_a == PyUnicode_1BYTE_KIND and kind_b == PyUnicode_1BYTE_KIND:
        return memcmp(PyUnicode_DATA(a), PyUnicode_DATA(b), la) == 0
    return PyUnicode_Compare(a, b) == 0


cdef inline bint strneq(str a, str b) noexcept:
    return not streq(a, b)


cdef inline int scmp(str a, str b) noexcept:
    # Three-way compare → -1 / 0 / 1 (``PyUnicode_Compare``, identity short-circuit).
    if a is b:
        return 0
    cdef int r = PyUnicode_Compare(a, b)
    if r < 0:
        return -1
    if r > 0:
        return 1
    return 0


cdef inline bint slt(str a, str b) noexcept:
    return scmp(a, b) < 0


cdef inline bint sle(str a, str b) noexcept:
    return scmp(a, b) <= 0


cdef inline bint sgt(str a, str b) noexcept:
    return scmp(a, b) > 0


cdef inline bint sge(str a, str b) noexcept:
    return scmp(a, b) >= 0


cdef inline bint startswith(str s, str prefix) noexcept:
    cdef Py_ssize_t sn = PyUnicode_GET_LENGTH(s)
    cdef Py_ssize_t pn = PyUnicode_GET_LENGTH(prefix)
    if pn == 0:
        return True
    if pn > sn:
        return False
    if PyUnicode_KIND(s) == PyUnicode_1BYTE_KIND and \
       PyUnicode_KIND(prefix) == PyUnicode_1BYTE_KIND:
        return memcmp(PyUnicode_DATA(s), PyUnicode_DATA(prefix), pn) == 0
    return PyUnicode_Tailmatch(s, prefix, 0, sn, -1)


cdef inline bint endswith(str s, str suffix) noexcept:
    cdef Py_ssize_t sn = PyUnicode_GET_LENGTH(s)
    cdef Py_ssize_t pn = PyUnicode_GET_LENGTH(suffix)
    if pn == 0:
        return True
    if pn > sn:
        return False
    if PyUnicode_KIND(s) == PyUnicode_1BYTE_KIND and \
       PyUnicode_KIND(suffix) == PyUnicode_1BYTE_KIND:
        return memcmp(
            <unsigned char*>PyUnicode_DATA(s) + (sn - pn),
            PyUnicode_DATA(suffix),
            pn,
        ) == 0
    return PyUnicode_Tailmatch(s, suffix, 0, sn, 1)


cpdef inline Py_ssize_t find(str s, str sub):
    return PyUnicode_Find(s, sub, 0, PyUnicode_GET_LENGTH(s), 1)


cdef inline bint contains(str haystack, str needle) noexcept:
    cdef Py_ssize_t hlen = PyUnicode_GET_LENGTH(haystack)
    cdef Py_ssize_t nlen = PyUnicode_GET_LENGTH(needle)
    cdef char *hp
    cdef char *np
    if nlen == 0:
        return True
    if nlen > hlen:
        return False
    if PyUnicode_KIND(haystack) == PyUnicode_1BYTE_KIND and \
       PyUnicode_KIND(needle) == PyUnicode_1BYTE_KIND:
        hp = <char*>PyUnicode_DATA(haystack)
        np = <char*>PyUnicode_DATA(needle)
        if nlen == 1:
            if hlen == 1:
                return hp[0] == np[0]
            return memchr(hp, <unsigned char>np[0], hlen) is not NULL
        if nlen == 2:
            return memmem(hp, <size_t>hlen, np, 2) is not NULL
    return PyUnicode_Find(haystack, needle, 0, hlen, 1) >= 0


cdef inline Py_UCS4 char_at(str s, Py_ssize_t i) noexcept:
    return PyUnicode_READ(PyUnicode_KIND(s), PyUnicode_DATA(s), i)


cdef inline Py_UCS4 first_char(str s) noexcept:
    return PyUnicode_READ(PyUnicode_KIND(s), PyUnicode_DATA(s), 0)


cdef inline Py_UCS4 last_char(str s) noexcept:
    cdef Py_ssize_t n = PyUnicode_GET_LENGTH(s)
    return PyUnicode_READ(PyUnicode_KIND(s), PyUnicode_DATA(s), n - 1)


cdef inline str concat(str a, str b):
    return <str>PyUnicode_Concat(a, b)


cdef inline str concat3(str a, str b, str c):
    cdef str tmp = <str>PyUnicode_Concat(a, b)
    return <str>PyUnicode_Concat(tmp, c)


cdef inline str concat4(str a, str b, str c, str d):
    cdef str ab = <str>PyUnicode_Concat(a, b)
    cdef str abc = <str>PyUnicode_Concat(ab, c)
    return <str>PyUnicode_Concat(abc, d)


cpdef inline bint is_ascii(str s) noexcept:
    cdef Py_ssize_t n = PyUnicode_GET_LENGTH(s)
    if n == 0:
        return True
    cdef int kind = PyUnicode_KIND(s)
    cdef void* data = PyUnicode_DATA(s)
    cdef Py_ssize_t i
    cdef unsigned char ch
    if kind == PyUnicode_1BYTE_KIND:
        for i in range(n):
            ch = (<unsigned char*>data)[i]
            if ch > 127:
                return False
        return True
    cdef Py_UCS4 ch4
    for i in range(n):
        ch4 = PyUnicode_READ(kind, data, i)
        if ch4 > 127:
            return False
    return True


cdef inline bint is_blank(str s) noexcept:
    cdef Py_ssize_t n = PyUnicode_GET_LENGTH(s)
    cdef int kind = PyUnicode_KIND(s)
    cdef void* data = PyUnicode_DATA(s)
    cdef Py_ssize_t i
    cdef unsigned char ch
    if kind == PyUnicode_1BYTE_KIND:
        for i in range(n):
            ch = (<unsigned char*>data)[i]
            if ch != 32 and ch != 9 and ch != 10 and ch != 11 and ch != 12 and ch != 13:
                return False
        return True
    cdef Py_UCS4 ch4
    for i in range(n):
        ch4 = PyUnicode_READ(kind, data, i)
        if ch4 != 32 and ch4 != 9 and ch4 != 10 and ch4 != 11 and ch4 != 12 and ch4 != 13:
            return False
    return True


cdef inline bint all_digits(str s) noexcept:
    cdef Py_ssize_t n = PyUnicode_GET_LENGTH(s)
    if n == 0:
        return False
    cdef int kind = PyUnicode_KIND(s)
    cdef void* data = PyUnicode_DATA(s)
    cdef Py_ssize_t i
    cdef unsigned char ch
    if kind == PyUnicode_1BYTE_KIND:
        for i in range(n):
            ch = (<unsigned char*>data)[i]
            if ch < 48 or ch > 57:
                return False
        return True
    cdef Py_UCS4 ch4
    for i in range(n):
        ch4 = PyUnicode_READ(kind, data, i)
        if ch4 < 48 or ch4 > 57:
            return False
    return True


cdef inline bint all_alpha_ascii(str s) noexcept:
    cdef Py_ssize_t n = PyUnicode_GET_LENGTH(s)
    if n == 0:
        return False
    cdef int kind = PyUnicode_KIND(s)
    cdef void* data = PyUnicode_DATA(s)
    cdef Py_ssize_t i
    cdef unsigned char ch
    if kind == PyUnicode_1BYTE_KIND:
        for i in range(n):
            ch = (<unsigned char*>data)[i]
            if not ((65 <= ch <= 90) or (97 <= ch <= 122)):
                return False
        return True
    cdef Py_UCS4 ch4
    for i in range(n):
        ch4 = PyUnicode_READ(kind, data, i)
        if not ((65 <= ch4 <= 90) or (97 <= ch4 <= 122)):
            return False
    return True


cdef inline bint all_alnum_ascii(str s) noexcept:
    cdef Py_ssize_t n = PyUnicode_GET_LENGTH(s)
    if n == 0:
        return False
    cdef int kind = PyUnicode_KIND(s)
    cdef void* data = PyUnicode_DATA(s)
    cdef Py_ssize_t i
    cdef unsigned char ch
    if kind == PyUnicode_1BYTE_KIND:
        for i in range(n):
            ch = (<unsigned char*>data)[i]
            if not ((48 <= ch <= 57) or (65 <= ch <= 90) or (97 <= ch <= 122)):
                return False
        return True
    cdef Py_UCS4 ch4
    for i in range(n):
        ch4 = PyUnicode_READ(kind, data, i)
        if not ((48 <= ch4 <= 57) or (65 <= ch4 <= 90) or (97 <= ch4 <= 122)):
            return False
    return True

# Wave 4 N1/N5 preferred names (0.3: soft letter/bare are cdef-only)

cpdef inline bint str_all_alnum_ascii(str s) noexcept:
    return all_alnum_ascii(s)

cpdef inline bint str_all_alpha_ascii(str s) noexcept:
    return all_alpha_ascii(s)

cpdef inline bint str_all_digits(str s) noexcept:
    return all_digits(s)

cpdef inline str str_as_or_empty(object obj):
    return as_str_or_empty(obj)

cpdef inline Py_UCS4 str_char_at(str s, Py_ssize_t i) noexcept:
    return char_at(s, i)

cpdef inline str str_concat(str a, str b):
    return concat(a, b)

cpdef inline str str_concat3(str a, str b, str c):
    return concat3(a, b, c)

cpdef inline str str_concat4(str a, str b, str c, str d):
    return concat4(a, b, c, d)

cpdef inline bint str_contains(str haystack, str needle) noexcept:
    return contains(haystack, needle)

cpdef inline bint str_endswith(str s, str suffix) noexcept:
    return endswith(s, suffix)

cpdef inline Py_ssize_t str_find(str s, str sub):
    return find(s, sub)

cpdef inline Py_UCS4 str_first_char(str s) noexcept:
    return first_char(s)

cpdef inline bint str_is_ascii(str s) noexcept:
    return is_ascii(s)

cpdef inline bint str_is_blank(str s) noexcept:
    return is_blank(s)

cpdef inline bint str_is_empty(str s) noexcept:
    return is_empty(s)

cpdef inline bint str_is_not(object obj) noexcept:
    return is_not_str(obj)

cpdef inline bint str_is(object obj) noexcept:
    return is_str(obj)

cpdef inline Py_UCS4 str_last_char(str s) noexcept:
    return last_char(s)

cpdef inline str str_none_to_empty(object obj):
    return none_to_empty(obj)

cpdef inline bint str_not_empty(str s) noexcept:
    return not_empty(s)

cpdef inline bint str_startswith(str s, str prefix) noexcept:
    return startswith(s, prefix)

cpdef inline bint str_eq(str a, str b) noexcept:
    return streq(a, b)

cpdef inline int str_cmp(str a, str b) noexcept:
    return scmp(a, b)

cpdef inline bint str_lt(str a, str b) noexcept:
    return slt(a, b)

cpdef inline bint str_le(str a, str b) noexcept:
    return sle(a, b)

cpdef inline bint str_gt(str a, str b) noexcept:
    return sgt(a, b)

cpdef inline bint str_ge(str a, str b) noexcept:
    return sge(a, b)

cpdef inline Py_ssize_t str_len(str s) noexcept:
    return strlen(s)

cpdef inline bint str_ne(str a, str b) noexcept:
    return strneq(a, b)

cpdef inline bint str_check(object obj) noexcept:
    return ucheck(obj)

cpdef inline bint str_check_exact(object obj) noexcept:
    return ucheck_exact(obj)

