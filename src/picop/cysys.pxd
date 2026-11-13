from cpython.object cimport PyObject

cdef object sys_get_object(str name)
cdef object sys_get_xoptions()
cpdef object sys_get_attr(object name)
cpdef bint lazy_imports_supported()
cpdef str lazy_import_mode()
cpdef void set_lazy_import_mode(str mode)
cdef object lazy_import_filter_get()
cdef int lazy_import_filter_set(object filter) except -1
cdef object sys_get_attr_string(str name)
cdef int sys_set_object_cstr(const char* name, object value) except -1
cdef int sys_get_optional_attr(object name, PyObject** result) except -1
cdef int sys_get_optional_attr_string(const char* name, PyObject** result) except -1
cdef void sys_write_stdout_cstr(const char* text) noexcept
cdef void sys_write_stderr_cstr(const char* text) noexcept
cdef void sys_format_stdout_cstr(const char* text) noexcept
cdef void sys_format_stderr_cstr(const char* text) noexcept
