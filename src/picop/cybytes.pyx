# cython: freethreading_compatible=True
# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
"""
Fast :class:`bytes` accessors.
"""

cdef class BytesWriter:
    """Incremental ``bytes`` builder over CPython's internal writer."""

    def __init__(self, int max_size=0):
        if max_size < 0:
            raise ValueError("max_size must be >= 0")
        _PyBytesWriter_Init(&self._w)
        self._w.overallocate = 1
        self._pos = _PyBytesWriter_Alloc(&self._w, max_size)
        self._open = 1

    def __dealloc__(self):
        if self._open:
            _PyBytesWriter_Dealloc(&self._w)
            self._open = 0

    cdef void _check_open(self) except *:
        if not self._open:
            raise RuntimeError("BytesWriter is closed")

    cpdef void write(self, object data):
        self._check_open()
        cdef Py_ssize_t n
        if PyBytes_CheckExact(data):
            n = PyBytes_GET_SIZE(data)
            self._pos = _PyBytesWriter_Prepare(&self._w, self._pos, n)
            memcpy(self._pos, PyBytes_AS_STRING(data), <size_t>n)
        elif PyByteArray_Check(data):
            n = PyByteArray_GET_SIZE(data)
            self._pos = _PyBytesWriter_Prepare(&self._w, self._pos, n)
            memcpy(self._pos, PyByteArray_AS_STRING(data), <size_t>n)
        else:
            raise TypeError("BytesWriter.write expects bytes or bytearray")
        self._pos += n

    cpdef void write_char(self, int ch):
        self._check_open()
        if not 0 <= ch <= 255:
            raise ValueError("write_char expects 0 <= ch <= 255")
        cdef unsigned char b = ch
        self._pos = _PyBytesWriter_Prepare(&self._w, self._pos, 1)
        memcpy(self._pos, &b, 1)
        self._pos += 1

    cpdef bytes finish(self):
        self._check_open()
        result = <bytes>_PyBytesWriter_Finish(&self._w, self._pos)
        self._open = 0
        return result

    cpdef void discard(self):
        self._check_open()
        _PyBytesWriter_Dealloc(&self._w)
        self._open = 0

    def __enter__(self):
        return self

    def __exit__(self, exc, value, tb):
        if self._open:
            _PyBytesWriter_Dealloc(&self._w)
            self._open = 0
        return False
