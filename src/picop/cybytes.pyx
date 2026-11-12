# cython: freethreading_compatible=True
# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
"""
Fast :class:`bytes` accessors.
"""

cdef class BytesWriter:
    """Incremental ``bytes`` builder over CPython's writer.

    ``max_size`` is a capacity hint: it pre-allocates on CPython 3.8-3.14
    (internal ``_PyBytesWriter``) and is ignored on 3.15+ (the public
    ``PyBytesWriter`` has no capacity reservation; writes overallocate).
    """

    def __init__(self, int max_size=0):
        if max_size < 0:
            raise ValueError("max_size must be >= 0")
        self._w = cy_bytes_writer_create(max_size)
        self._open = 1

    def __dealloc__(self):
        if self._open:
            cy_bytes_writer_discard(self._w)
            self._open = 0

    cdef void _check_open(self) except *:
        if not self._open:
            raise RuntimeError("BytesWriter is closed")

    cpdef void write(self, object data):
        self._check_open()
        if PyBytes_CheckExact(data):
            cy_bytes_writer_write(self._w, PyBytes_AS_STRING(data), PyBytes_GET_SIZE(data))
        elif PyByteArray_Check(data):
            cy_bytes_writer_write(self._w, PyByteArray_AS_STRING(data), PyByteArray_GET_SIZE(data))
        else:
            raise TypeError("BytesWriter.write expects bytes or bytearray")

    cpdef void write_char(self, int ch):
        self._check_open()
        if not 0 <= ch <= 255:
            raise ValueError("write_char expects 0 <= ch <= 255")
        cdef unsigned char b = ch
        cy_bytes_writer_write(self._w, <const char *>&b, 1)

    cpdef bytes finish(self):
        self._check_open()
        result = <bytes>cy_bytes_writer_finish(self._w)
        self._open = 0
        return result

    cpdef void discard(self):
        self._check_open()
        cy_bytes_writer_discard(self._w)
        self._open = 0

    def __enter__(self):
        return self

    def __exit__(self, exc, value, tb):
        if self._open:
            cy_bytes_writer_discard(self._w)
            self._open = 0
        return False
