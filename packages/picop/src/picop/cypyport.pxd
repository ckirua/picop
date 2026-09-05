# cypyport.pxd
# Portability typedefs / ssize limits. cimport-only re-exports.

from cpython.pyport cimport (
    PY_SSIZE_T_MAX,
    PY_SSIZE_T_MIN,
    int32_t,
    int64_t,
    uint32_t,
    uint64_t,
)
