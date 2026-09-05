# cyversion.pxd
# Compile-time Python version constants. cimport-only.

from cpython.version cimport (
    PY_MAJOR_VERSION,
    PY_MICRO_VERSION,
    PY_MINOR_VERSION,
    PY_RELEASE_LEVEL,
    PY_RELEASE_SERIAL,
    PY_VERSION,
    PY_VERSION_HEX,
)
