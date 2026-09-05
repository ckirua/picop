# cyfileobject.pxd
# File-object helpers. Public docs in ``cyfileobject.pyi``.

cdef extern from "Python.h":
    object PyFile_FromFd(int fd, const char *name, const char *mode, int buffering, const char *encoding, const char *errors, const char *newline, int closefd)
    object PyFile_GetLine(object p, int n)
    int PyFile_WriteObject(object obj, object p, int flags) except -1
    int PyFile_WriteString(const char *s, object p) except -1
    int Py_PRINT_RAW


cpdef inline object file_from_fd(int fd, const char *name, const char *mode, int buffering=-1, const char *encoding=NULL, const char *errors=NULL, const char *newline=NULL, int closefd=1):
    return PyFile_FromFd(fd, name, mode, buffering, encoding, errors, newline, closefd)


cpdef inline object file_getline(object p, int n=-1):
    return PyFile_GetLine(p, n)


cpdef inline int file_write_object(object obj, object p, int flags=0) except -1:
    return PyFile_WriteObject(obj, p, flags)


cdef inline int file_write_string(const char *s, object p) except -1:
    return PyFile_WriteString(s, p)
# N2 preferred *_cstr (0.3: *_string cdef-only where soft)

cpdef inline int file_write_cstr(const char *s, object p) except -1:
    return file_write_string(s, p)
