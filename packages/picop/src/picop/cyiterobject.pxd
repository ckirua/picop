# cyiterobject.pxd
# Sequence / callable iterator constructors. Public docs in ``cyiterobject.pyi``.

cdef extern from "Python.h":
    bint PySeqIter_Check(object op) noexcept
    object PySeqIter_New(object seq)
    bint PyCallIter_Check(object op) noexcept
    object PyCallIter_New(object callable, object sentinel)


cpdef inline bint seqiter_check(object op) noexcept:
    return PySeqIter_Check(op)


cpdef inline object seqiter_new(object seq):
    return PySeqIter_New(seq)


cpdef inline bint calliter_check(object op) noexcept:
    return PyCallIter_Check(op)


cpdef inline object calliter_new(object callable, object sentinel):
    return PyCallIter_New(callable, sentinel)
