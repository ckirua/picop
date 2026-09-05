# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
# Copyright (C) 2016-present the asyncpg authors and contributors
# Portions of this module are adapted from asyncpg's UUID implementation and
# remain under the Apache License, Version 2.0. See the repository NOTICE and
# LICENSES/Apache-2.0.txt files for attribution and license terms.

"""Cython implementation of UUID values and version 4 generation."""

import uuid

cimport cpython
cimport cython
from libc.stdint cimport int8_t, uint8_t
from libc.string cimport memcmp, memcpy


cdef extern from "hex.h":
    void uuid_to_str(const char* source, char* dest) noexcept nogil
    void uuid_to_hex(const char* source, char* dest) noexcept nogil


cdef extern from "uuid.h":
    int c_uuid4(unsigned char* dest) noexcept nogil


cdef object std_UUID = uuid.UUID
cdef object safe_unknown = uuid.SafeUUID.unknown
cdef object variant_ncs = uuid.RESERVED_NCS
cdef object variant_rfc = uuid.RFC_4122
cdef object variant_microsoft = uuid.RESERVED_MICROSOFT
cdef object variant_future = uuid.RESERVED_FUTURE


cdef char[256] _hextable
_hextable[:] = [
    -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
    -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
    -1,-1, 0,1,2,3,4,5,6,7,8,9,-1,-1,-1,-1,-1,-1,-1,10,11,12,13,14,15,-1,
    -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
    -1,-1,10,11,12,13,14,15,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
    -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
    -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
    -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
    -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
    -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
    -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1
]


cdef void uuid_bytes_from_str(str value, char* out) except *:
    cdef:
        const char* buf
        Py_ssize_t size
        unsigned char ch
        uint8_t acc = 0
        uint8_t part
        uint8_t acc_set = 0
        int i
        int j = 0

    buf = PyUnicode_AsUTF8AndSize(value, &size)
    if size > 36 or size < 32:
        raise ValueError(
            f"invalid UUID {value!r}: "
            f"length must be between 32..36 characters, got {size}"
        )

    for i in range(size):
        ch = <unsigned char>buf[i]
        if ch == <unsigned char>45:
            continue

        part = <uint8_t><int8_t>_hextable[ch]
        if part == <uint8_t>-1:
            if ch >= 0x20 and ch <= 0x7e:
                raise ValueError(
                    f"invalid UUID {value!r}: unexpected character {chr(ch)!r}"
                )
            raise ValueError(f"invalid UUID {value!r}: unexpected character")

        # Reject excess digits before writing so malformed text cannot overrun
        # the fixed 16-byte destination.
        if j == 16:
            raise ValueError(
                f"invalid UUID {value!r}: decodes to more than 16 bytes"
            )

        if acc_set:
            acc |= part
            out[j] = <char>acc
            acc_set = 0
            j += 1
        else:
            acc = <uint8_t>(part << 4)
            acc_set = 1

    if j != 16:
        raise ValueError(
            f"invalid UUID {value!r}: decodes to less than 16 bytes"
        )


cdef class __UUIDReplaceMe:
    pass

cdef UUID uuid_from_buf(const unsigned char* buf):
    cdef UUID value = UUID.__new__(UUID)
    memcpy(value._data, buf, 16)
    return value





@cython.final
@cython.no_gc_clear
cdef class UUID(__UUIDReplaceMe):
    """A fast C-backed UUID value."""

    def __cinit__(self):
        self._int = None
        self._hash = None

    def __init__(self, inp):
        cdef:
            char* buf
            Py_ssize_t size

        if cpython.PyBytes_Check(inp):
            cpython.PyBytes_AsStringAndSize(inp, &buf, &size)
            if size != 16:
                raise ValueError(f"16 bytes were expected, got {size}")
            memcpy(self._data, buf, 16)
        elif cpython.PyUnicode_Check(inp):
            uuid_bytes_from_str(inp, self._data)
        else:
            raise TypeError(f"a bytes or str object expected, got {inp!r}")

    @property
    def bytes(self):
        return cpython.PyBytes_FromStringAndSize(self._data, 16)

    @property
    def int(self):
        if self._int is None:
            self._int = int.from_bytes(self.bytes, "big") or 0
        return self._int

    @property
    def is_safe(self):
        return safe_unknown

    def __str__(self):
        cdef char[36] out
        uuid_to_str(self._data, out)
        return PyUnicode_FromKindAndData(
            PyUnicode_1BYTE_KIND,
            <const void*>out,
            36,
        )

    def __format__(self, format_spec):
        return format(str(self), format_spec)

    @property
    def hex(self):
        cdef char[32] out
        uuid_to_hex(self._data, out)
        return PyUnicode_FromKindAndData(
            PyUnicode_1BYTE_KIND,
            <const void*>out,
            32,
        )

    def __repr__(self):
        return f"UUID('{self}')"

    def __reduce__(self):
        return (type(self), (self.bytes,))

    def __eq__(self, other):
        if type(other) is UUID:
            return memcmp(self._data, (<UUID>other)._data, 16) == 0
        if isinstance(other, std_UUID):
            return self.int == other.int
        return NotImplemented

    def __ne__(self, other):
        if type(other) is UUID:
            return memcmp(self._data, (<UUID>other)._data, 16) != 0
        if isinstance(other, std_UUID):
            return self.int != other.int
        return NotImplemented

    def __lt__(self, other):
        if type(other) is UUID:
            return memcmp(self._data, (<UUID>other)._data, 16) < 0
        if isinstance(other, std_UUID):
            return self.int < other.int
        return NotImplemented

    def __gt__(self, other):
        if type(other) is UUID:
            return memcmp(self._data, (<UUID>other)._data, 16) > 0
        if isinstance(other, std_UUID):
            return self.int > other.int
        return NotImplemented

    def __le__(self, other):
        if type(other) is UUID:
            return memcmp(self._data, (<UUID>other)._data, 16) <= 0
        if isinstance(other, std_UUID):
            return self.int <= other.int
        return NotImplemented

    def __ge__(self, other):
        if type(other) is UUID:
            return memcmp(self._data, (<UUID>other)._data, 16) >= 0
        if isinstance(other, std_UUID):
            return self.int >= other.int
        return NotImplemented

    def __hash__(self):
        if self._hash is None:
            self._hash = hash(self.int)
        return self._hash

    def __int__(self):
        return self.int

    @property
    def bytes_le(self):
        value = self.bytes
        return (
            value[3::-1]
            + value[5:3:-1]
            + value[7:5:-1]
            + value[8:]
        )

    @property
    def fields(self):
        return (
            self.time_low,
            self.time_mid,
            self.time_hi_version,
            self.clock_seq_hi_variant,
            self.clock_seq_low,
            self.node,
        )

    @property
    def time_low(self):
        return self.int >> 96

    @property
    def time_mid(self):
        return (self.int >> 80) & 0xffff

    @property
    def time_hi_version(self):
        return (self.int >> 64) & 0xffff

    @property
    def clock_seq_hi_variant(self):
        return (self.int >> 56) & 0xff

    @property
    def clock_seq_low(self):
        return (self.int >> 48) & 0xff

    @property
    def time(self):
        return (
            ((self.time_hi_version & 0x0fff) << 48)
            | (self.time_mid << 32)
            | self.time_low
        )

    @property
    def clock_seq(self):
        return (
            ((self.clock_seq_hi_variant & 0x3f) << 8)
            | self.clock_seq_low
        )

    @property
    def node(self):
        return self.int & 0xffffffffffff

    @property
    def urn(self):
        return "urn:uuid:" + str(self)

    @property
    def variant(self):
        if not self.int & (0x8000 << 48):
            return variant_ncs
        if not self.int & (0x4000 << 48):
            return variant_rfc
        if not self.int & (0x2000 << 48):
            return variant_microsoft
        return variant_future

    @property
    def version(self):
        if self.variant == variant_rfc:
            return int((self.int >> 76) & 0x0f)
        return None


# In order for ``isinstance(UUID(...), uuid.UUID)`` to work, replace the
# layout-compatible extension base in the generated type's bases and MRO.
# Directly inheriting from both extension and stdlib UUID types causes an
# instance layout conflict.
assert UUID.__bases__[0] is __UUIDReplaceMe
assert UUID.__mro__[1] is __UUIDReplaceMe
cpython.Py_INCREF(std_UUID)
cpython.PyTuple_SET_ITEM(UUID.__bases__, 0, std_UUID)
cpython.Py_DECREF(__UUIDReplaceMe)
cpython.Py_INCREF(std_UUID)
cpython.PyTuple_SET_ITEM(UUID.__mro__, 1, std_UUID)
cpython.Py_DECREF(__UUIDReplaceMe)

cpdef bytes uuid4_bytes():
    """Return 16 random bytes with UUID v4 and RFC variant bits set."""
    cdef:
        unsigned char dest[16]
        int status

    status = c_uuid4(dest)
    if status != 1:
        raise RuntimeError("OpenSSL RAND_bytes failed")
    return cpython.PyBytes_FromStringAndSize(<const char*>dest, 16)


cpdef UUID uuid4():
    """Return a random version 4 UUID."""
    cdef:
        unsigned char dest[16]
        int status

    status = c_uuid4(dest)
    if status != 1:
        raise RuntimeError("OpenSSL RAND_bytes failed")
    return uuid_from_buf(dest)
