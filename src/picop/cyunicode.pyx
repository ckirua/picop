# cython: freethreading_compatible=True
# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
"""
Fast :class:`str` UTF-8 and intern helpers.
"""


cdef class UnicodeWriter:
    def __cinit__(self):
        self._w = NULL

    def __init__(self, Py_ssize_t max_size=0):
        self._w = PyUnicodeWriter_Create(max_size)
        if self._w == NULL:
            raise MemoryError()

    cdef void _check_open(self) except *:
        if self._w == NULL:
            raise RuntimeError("UnicodeWriter already finished")

    cpdef write(self, object text):
        self._check_open()
        PyUnicodeWriter_WriteStr(self._w, text)

    cpdef write_char(self, Py_UCS4 ch):
        self._check_open()
        PyUnicodeWriter_WriteChar(self._w, ch)

    cpdef write_ascii(self, str text):
        self._check_open()
        cdef bytes ascii_text = text.encode("ascii")
        PyUnicodeWriter_WriteASCII(self._w, ascii_text, len(ascii_text))

    cpdef write_repr(self, object obj):
        self._check_open()
        PyUnicodeWriter_WriteRepr(self._w, obj)

    cpdef write_substring(self, str text, Py_ssize_t start=0, Py_ssize_t end=-1):
        self._check_open()
        if end < 0:
            end = len(text)
        PyUnicodeWriter_WriteSubstring(self._w, text, start, end)

    cpdef write_utf8(self, bytes data):
        self._check_open()
        PyUnicodeWriter_WriteUTF8(self._w, data, len(data))

    cpdef str finish(self):
        self._check_open()
        cdef PyUnicodeWriter *writer = self._w
        self._w = NULL
        return PyUnicodeWriter_Finish(writer)

    cpdef discard(self):
        self._check_open()
        PyUnicodeWriter_Discard(self._w)
        self._w = NULL

    def __enter__(self):
        self._check_open()
        return self

    def __exit__(self, object exc_type, object exc, object tb):
        if self._w != NULL:
            self.discard()
        return False
