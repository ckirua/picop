# Out-of-tree smoke: package-barrel + submodule cimport against an installed picop.
# Build: see README.md / scripts/smoke_barrel_cimport.sh

from picop cimport UUID, bytes_eq, list_len, str_eq, uuid4_bytes
from picop.cybytes cimport bytes_len


cpdef bint check_barrel():
    return (
        bytes_eq(b"ab", b"ab")
        and list_len([1, 2, 3]) == 3
        and str_eq("x", "x")
    )


cpdef Py_ssize_t check_submodule():
    return bytes_len(b"ok")


cpdef bint check_uuid():
    cdef bytes raw = uuid4_bytes()
    cdef UUID value = UUID(raw)
    return len(raw) == 16 and value.version == 4
