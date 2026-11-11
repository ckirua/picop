# cycriticalsection.pxd
# CPython `critical_section.h` critical sections (CPython 3.12+; real locking
# only in free-threaded builds). Cimport only: a critical section is a
# stack-local C struct and cannot cross the Python boundary.
#
# Cython's own `with cython.critical_section(obj):` already covers the common
# "lock one/two objects around a block" case. These wrappers cover what that
# syntax cannot express: a section guarded by your own `PyMutex` (see
# `picop.cylock`), or guards that must be entered and released across
# non-block control flow.
#
# Pattern:
#   cdef PyMutex mu
#   cdef PicopCriticalSection cs
#   cs_begin_mutex(&cs, &mu)
#   ...  # mutate shared state
#   cs_end(&cs)
#
# In a GIL build every wrapper is a no-op (CPython's own macros are no-ops
# there), so the same code compiles and runs on both interpreter flavours.
# `critical_sections_enabled()` reports which one you are on.
#
# The section structs are the shim's aligned buffers, not CPython's private
# structs: the wrapper casts them internally, so an extension never needs the
# (private, release-changing) field layout.

from libc.stdint cimport uintptr_t

from .cylock cimport PyMutex

cdef extern from "cycriticalsection_shim.h" nogil:
    ctypedef struct PicopCriticalSection:
        uintptr_t _data[8]

    ctypedef struct PicopCriticalSection2:
        uintptr_t _data[16]

    int critical_sections_enabled "picop_critical_sections_enabled"()

    void cs_begin "picop_cs_begin" (PicopCriticalSection *buf, object obj)
    void cs_begin_mutex "picop_cs_begin_mutex" (PicopCriticalSection *buf, PyMutex *mutex)
    void cs_end "picop_cs_end" (PicopCriticalSection *buf)

    void cs2_begin "picop_cs2_begin" (PicopCriticalSection2 *buf, object a, object b)
    void cs2_begin_mutex "picop_cs2_begin_mutex" (PicopCriticalSection2 *buf, PyMutex *m1, PyMutex *m2)
    void cs2_end "picop_cs2_end" (PicopCriticalSection2 *buf)
