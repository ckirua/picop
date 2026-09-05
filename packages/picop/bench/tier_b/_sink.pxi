# Shared anti-DCE / anti-LICM helpers for Tier B cdef loops.

from cpython.object cimport PyObject

cdef extern from *:
    """
    static volatile Py_ssize_t cypy_tier_b_sink;

    /* New reference — Cython treats `object` returns as owned. */
    static PyObject* cypy_tb_opaque(PyObject* o, Py_ssize_t k) {
        cypy_tier_b_sink ^= k;
        Py_INCREF(o);
        return o;
    }
    """
    Py_ssize_t cypy_tier_b_sink
    object cypy_tb_opaque(object o, Py_ssize_t k)


cdef inline void tb_sink_obj(object o) noexcept:
    cypy_tier_b_sink = <Py_ssize_t><void*><PyObject*>o


cdef inline void tb_sink_ssize(Py_ssize_t v) noexcept:
    cypy_tier_b_sink = v


cdef inline void tb_sink_bint(bint v) noexcept:
    cypy_tier_b_sink = <Py_ssize_t>v


cdef inline tuple tb_tuple(object o, Py_ssize_t k):
    return <tuple>cypy_tb_opaque(o, k)


cdef inline object tb_obj(object o, Py_ssize_t k):
    return cypy_tb_opaque(o, k)
