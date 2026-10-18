# cyiterator.pxd
# Iterator protocol helpers. Public docs in ``cyiterator.pyi``.

cdef extern from "Python.h":
    bint PyIter_Check(object o) noexcept
    object PyIter_Next(object o)


cpdef inline bint iter_check(object o) noexcept:
    return PyIter_Check(o)


cdef inline bint itereq(object a, object b) noexcept:
    # Iterator equality is identity (CPython uses ``object.__eq__`` for
    # typical iterators). Soft ``itereq``. Callers should pass iterator
    # objects. Not on ``hot``.
    return a is b


cpdef inline bint iter_eq(object a, object b) noexcept:
    return itereq(a, b)


cpdef inline object iter_next(object o):
    # Returns None at end without raising StopIteration (C-API convention).
    return PyIter_Next(o)
