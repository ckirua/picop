# cython: freethreading_compatible=True
# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False, binding=True
# Copyright (C) 2016-present the asyncpg authors and contributors
# Portions of this module are adapted from asyncpg's UUID implementation and
# remain under the Apache License, Version 2.0. See the repository NOTICE and
# LICENSES/Apache-2.0.txt files for attribution and license terms.

"""Compiled UUID value methods and thread-local version 4 generation."""

import uuid

cimport cpython
from cpython.object cimport PyObject, PyTypeObject
from libc.string cimport memcmp

cdef extern from "hex.h":
    void uuid_to_str(const char* source, char* dest) noexcept nogil
    void uuid_to_hex(const char* source, char* dest) noexcept nogil

cdef extern from "uuid.h":
    int c_uuid_init() noexcept nogil
    int c_uuid4(unsigned char* dest) noexcept nogil

cdef extern from "_uuid_native.h":
    ctypedef struct PicopUUIDAPI:
        unsigned int version
        object (*from_buf)(PyTypeObject*, const unsigned char*)
        const unsigned char* (*data)(PyObject*) noexcept
        int (*parse)(PyObject*, unsigned char*) except -1
    unsigned int PICOP_UUID_API_VERSION
    const char* PICOP_UUID_CAPSULE

cdef extern from "Python.h":
    void* PyCapsule_GetPointer(object capsule, const char* name) except NULL

from . import _uuid_native as _native

# The external Cython type and Python export refer to the same native heap type.
globals()["UUID"] = _native.UUID
cdef const PicopUUIDAPI* _api = <const PicopUUIDAPI*>PyCapsule_GetPointer(
    _native._C_API, PICOP_UUID_CAPSULE,
)
if _api.version != PICOP_UUID_API_VERSION:
    raise ImportError("incompatible picop UUID native API")

if c_uuid_init() != 0:
    raise RuntimeError("UUID fork hook registration failed")

cdef object std_UUID = uuid.UUID
cdef object variant_ncs = uuid.RESERVED_NCS
cdef object variant_rfc = uuid.RFC_4122
cdef object variant_microsoft = uuid.RESERVED_MICROSOFT
cdef object variant_future = uuid.RESERVED_FUTURE


cdef inline const char* _data(UUID self) noexcept:
    # Immutable native storage, valid while the typed owning argument is alive.
    return <const char*>_api.data(<PyObject*>self)


cdef void uuid_bytes_from_str(str value, char* out) except *:
    _api.parse(<PyObject*>value, <unsigned char*>out)


cdef UUID uuid_from_buf(const unsigned char* buf):
    return <UUID>_api.from_buf(<PyTypeObject*>UUID, buf)


def _bytes(UUID self):
    return cpython.PyBytes_FromStringAndSize(_data(self), 16)


def _str(UUID self):
    cdef char out[36]
    uuid_to_str(_data(self), out)
    return PyUnicode_FromKindAndData(PyUnicode_1BYTE_KIND, <const void*>out, 36)


def _hex(UUID self):
    cdef char out[32]
    uuid_to_hex(_data(self), out)
    return PyUnicode_FromKindAndData(PyUnicode_1BYTE_KIND, <const void*>out, 32)


def _format(UUID self, format_spec):
    return format(str(self), format_spec)


def _repr(UUID self):
    return f"UUID('{self}')"


def _reduce(UUID self):
    return (type(self), (self.bytes,))


cdef object _compare(UUID self, object other, int op):
    cdef int order
    cdef object left, right
    if type(other) is UUID:
        order = memcmp(_data(self), _data(<UUID>other), 16)
        if op == 0:
            return order == 0
        if op == 1:
            return order != 0
        if op == 2:
            return order < 0
        if op == 3:
            return order > 0
        if op == 4:
            return order <= 0
        return order >= 0
    if isinstance(other, std_UUID):
        left, right = self.int, other.int
        if op == 0:
            return left == right
        if op == 1:
            return left != right
        if op == 2:
            return left < right
        if op == 3:
            return left > right
        if op == 4:
            return left <= right
        return left >= right
    return NotImplemented


def _eq(UUID self, other):
    return _compare(self, other, 0)


def _ne(UUID self, other):
    return _compare(self, other, 1)


def _lt(UUID self, other):
    return _compare(self, other, 2)


def _gt(UUID self, other):
    return _compare(self, other, 3)


def _le(UUID self, other):
    return _compare(self, other, 4)


def _ge(UUID self, other):
    return _compare(self, other, 5)


def _int_method(UUID self):
    return self.int


def _bytes_le(UUID self):
    value = self.bytes
    return value[3::-1] + value[5:3:-1] + value[7:5:-1] + value[8:]


def _fields(UUID self):
    return (self.time_low, self.time_mid, self.time_hi_version,
            self.clock_seq_hi_variant, self.clock_seq_low, self.node)


def _time_low(UUID self):
    return self.int >> 96


def _time_mid(UUID self):
    return (self.int >> 80) & 0xffff


def _time_hi_version(UUID self):
    return (self.int >> 64) & 0xffff


def _clock_seq_hi_variant(UUID self):
    return (self.int >> 56) & 0xff


def _clock_seq_low(UUID self):
    return (self.int >> 48) & 0xff


def _time(UUID self):
    # Preserve the original helper's arithmetic, including for newer versions.
    return ((self.time_hi_version & 0xfff) << 48) | (self.time_mid << 32) | self.time_low


def _clock_seq(UUID self):
    return ((self.clock_seq_hi_variant & 0x3f) << 8) | self.clock_seq_low


def _node(UUID self):
    return self.int & 0xffffffffffff


def _urn(UUID self):
    return "urn:uuid:" + str(self)


def _variant(UUID self):
    value = self.int
    if not value & (0x8000 << 48):
        return variant_ncs
    if not value & (0x4000 << 48):
        return variant_rfc
    if not value & (0x2000 << 48):
        return variant_microsoft
    return variant_future


def _version(UUID self):
    if self.variant == variant_rfc:
        return int((self.int >> 76) & 0x0f)
    return None


# Supported heap-type assignment updates the appropriate slots. The native type
# already has valid stdlib base behavior before these optimizations are attached.
UUID.__str__ = _str
UUID.__format__ = _format
UUID.__repr__ = _repr
UUID.__reduce__ = _reduce
UUID.__eq__ = _eq
UUID.__ne__ = _ne
UUID.__lt__ = _lt
UUID.__gt__ = _gt
UUID.__le__ = _le
UUID.__ge__ = _ge
UUID.__int__ = _int_method
UUID.bytes = property(_bytes)
UUID.hex = property(_hex)
UUID.bytes_le = property(_bytes_le)
UUID.fields = property(_fields)
UUID.time_low = property(_time_low)
UUID.time_mid = property(_time_mid)
UUID.time_hi_version = property(_time_hi_version)
UUID.clock_seq_hi_variant = property(_clock_seq_hi_variant)
UUID.clock_seq_low = property(_clock_seq_low)
UUID.time = property(_time)
UUID.clock_seq = property(_clock_seq)
UUID.node = property(_node)
UUID.urn = property(_urn)
UUID.variant = property(_variant)
UUID.version = property(_version)


cpdef bytes uuid4_bytes():
    """Return 16 random bytes with UUID v4 and RFC variant bits set."""
    cdef unsigned char dest[16]
    if c_uuid4(dest) != 1:
        raise RuntimeError("OpenSSL RAND_bytes failed")
    return cpython.PyBytes_FromStringAndSize(<const char*>dest, 16)


cpdef UUID uuid4():
    """Return a random version 4 UUID."""
    cdef unsigned char dest[16]
    if c_uuid4(dest) != 1:
        raise RuntimeError("OpenSSL RAND_bytes failed")
    return uuid_from_buf(dest)
