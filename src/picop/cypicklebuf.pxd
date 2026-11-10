# CPython 3.14 uses explicit NotImplementedError shims; APIs arrive in 3.15.
from cpython.buffer cimport Py_buffer

cpdef object pickle_buffer_from_object(object obj)
cpdef void pickle_buffer_release(object obj)
cpdef bint pickle_buffer_check(object obj)
cpdef object pickle_buffer_type()
cdef const Py_buffer* pickle_buffer_get_buffer(object obj) except? NULL
