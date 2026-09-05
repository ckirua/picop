cimport cython


cdef extern from "Python.h":
    int PyUnicode_1BYTE_KIND
    const char* PyUnicode_AsUTF8AndSize(
        object unicode,
        Py_ssize_t* size,
    ) except NULL
    object PyUnicode_FromKindAndData(
        int kind,
        const void* buffer,
        Py_ssize_t size,
    )


cdef class __UUIDReplaceMe:
    pass


@cython.final
@cython.no_gc_clear
cdef class UUID(__UUIDReplaceMe):
    cdef char[16] _data
    cdef object _int
    cdef object _hash


cdef UUID uuid_from_buf(const unsigned char* buf)
cdef void uuid_bytes_from_str(str value, char* out) except *

cpdef bytes uuid4_bytes()
cpdef UUID uuid4()
