# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from libc.stdint cimport uint32_t
from picop.cylong cimport (
    PyLongLayout,
    PyLongWriter,
    long_check,
    long_as_int32,
    long_as_uint32,
    long_as_long,
    long_native_layout,
    long_writer_create,
    long_writer_finish,
    long_writer_discard,
)
include "_sink.pxi"

cdef inline void _store_digit(void *digits, Py_ssize_t index, Py_ssize_t ndigits,
                              uint32_t value, const PyLongLayout *layout) noexcept:
    cdef unsigned char *bytes = <unsigned char *>digits
    cdef Py_ssize_t offset
    cdef int byte_index
    cdef int digit_bytes = layout.digit_size
    cdef int shift
    cdef unsigned char byte_value
    offset = (index if layout.digits_order == -1 else ndigits - 1 - index) * digit_bytes
    for byte_index in range(digit_bytes):
        shift = byte_index * 8 if layout.digit_endianness == -1 else (digit_bytes - 1 - byte_index) * 8
        byte_value = <unsigned char>((value >> shift) & 0xff)
        bytes[offset + byte_index] = byte_value

cdef inline uint32_t _digit_mask(const PyLongLayout *layout) noexcept:
    return (<uint32_t>1 << layout.bits_per_digit) - 1

cpdef object baseline_writer(object opaque, Py_ssize_t n, Py_ssize_t ndigits, bint negative):
    cdef Py_ssize_t k, j
    cdef object result = 0
    cdef uint32_t limb
    cdef const PyLongLayout *layout = long_native_layout()
    cdef uint32_t mask = _digit_mask(layout)
    cdef uint32_t source[256]
    if not 1 <= ndigits <= 256:
        raise ValueError("ndigits must be between 1 and 256")
    for j in range(ndigits):
        source[j] = (<uint32_t>j * <uint32_t>2654435761) & mask
    if ndigits:
        source[ndigits - 1] |= 1
    for k in range(n):
        result = 0
        for j in range(ndigits - 1, -1, -1):
            limb = source[j]
            result = (result << layout.bits_per_digit) | limb
        if negative:
            result = -result
        result = tb_obj(result, k)
        tb_sink_obj(result)
    return result

cpdef object cypy_writer(object opaque, Py_ssize_t n, Py_ssize_t ndigits, bint negative):
    cdef Py_ssize_t k, j
    cdef uint32_t mask = _digit_mask(long_native_layout())
    cdef uint32_t source[256]
    cdef void *digits
    cdef PyLongWriter *writer
    cdef PyLongWriter *finishing_writer
    cdef object result
    cdef const PyLongLayout *layout = long_native_layout()
    if not 1 <= ndigits <= 256:
        raise ValueError("ndigits must be between 1 and 256")
    for j in range(ndigits):
        source[j] = (<uint32_t>j * <uint32_t>2654435761) & mask
    if ndigits:
        source[ndigits - 1] |= 1
    for k in range(n):
        writer = long_writer_create(negative, ndigits, &digits)
        try:
            for j in range(ndigits):
                _store_digit(digits, j, ndigits, source[j], layout)
            finishing_writer = writer
            writer = NULL
            result = long_writer_finish(finishing_writer)
        except:
            if writer != NULL:
                long_writer_discard(writer)
                writer = NULL
            raise
        result = tb_obj(result, k)
        tb_sink_obj(result)
    return result

cpdef bint writer_depth_probes():
    cdef const PyLongLayout *layout = long_native_layout()
    cdef uint32_t mask = _digit_mask(layout)
    cdef void *digits
    cdef PyLongWriter *writer
    cdef object value
    cdef object base = 1
    cdef bint caught = False
    cdef int j
    assert layout.bits_per_digit > 0 and layout.digit_size in (2, 4)
    assert layout.digits_order in (-1, 1)
    assert layout.digit_endianness in (-1, 1)
    writer = long_writer_create(0, 1, &digits)
    _store_digit(digits, 0, 1, 7, layout)
    assert long_writer_finish(writer) == 7
    writer = long_writer_create(1, 1, &digits)
    _store_digit(digits, 0, 1, 7, layout)
    assert long_writer_finish(writer) == -7
    writer = long_writer_create(0, 1, &digits)
    _store_digit(digits, 0, 1, 0, layout)
    assert long_writer_finish(writer) == 0
    writer = long_writer_create(1, 1, &digits)
    _store_digit(digits, 0, 1, 0, layout)
    assert long_writer_finish(writer) == 0
    writer = long_writer_create(1, 3, &digits)
    for j in range(3):
        _store_digit(digits, j, 3, 0, layout)
    _store_digit(digits, 0, 3, 5, layout)
    assert long_writer_finish(writer) == -5
    writer = long_writer_create(0, 1, &digits)
    _store_digit(digits, 0, 1, mask, layout)
    assert long_writer_finish(writer) == mask
    writer = long_writer_create(0, 3, &digits)
    _store_digit(digits, 0, 3, 1, layout)
    _store_digit(digits, 1, 3, 2, layout)
    _store_digit(digits, 2, 3, 3, layout)
    base <<= layout.bits_per_digit
    assert long_writer_finish(writer) == 3 * base * base + 2 * base + 1
    caught = False
    try:
        long_writer_create(0, 0, &digits)
    except ValueError:
        caught = True
    assert caught
    caught = False
    try:
        long_writer_create(0, 1, NULL)
    except ValueError:
        caught = True
    assert caught
    long_writer_discard(NULL)
    writer = long_writer_create(0, 1, &digits)
    try:
        raise RuntimeError("fill failed")
    except RuntimeError:
        long_writer_discard(writer)
    return True

cpdef bint baseline_long_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), int)
        tb_sink_bint(r)
    return r

cpdef bint cypy_long_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = long_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r


cpdef int baseline_long_as_int32(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef int r = 0
    for k in range(n):
        r = <int>int(tb_obj(p, k))
        tb_sink_ssize(r)
    return r

cpdef int cypy_long_as_int32(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef int r = 0
    for k in range(n):
        r = long_as_int32(tb_obj(p, k))
        tb_sink_ssize(r)
    return r

cpdef bint depth_probes():
    cdef bint caught
    cdef object value
    caught = False
    try:
        long_as_int32(2**32)
    except OverflowError:
        caught = True
    assert caught
    try:
        long_as_uint32(-1)
    except ValueError:
        caught = True
    assert caught
    assert long_as_int32(True) == 1
    caught = False
    try:
        long_as_int32("not an int")
    except TypeError:
        caught = True
    assert caught
    value = 42
    assert long_as_int32(value) == long_as_long(value)
    return True
