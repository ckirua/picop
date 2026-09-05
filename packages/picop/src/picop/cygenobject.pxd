# cygenobject.pxd
# Generator helpers. Public docs in ``cygenobject.pyi``.
# Gen_New* steal a frame reference — cdef only.

from cpython.pystate cimport PyFrameObject


cdef extern from "Python.h":
    bint PyGen_Check(object ob) noexcept
    bint PyGen_CheckExact(object ob) noexcept
    object PyGen_New(PyFrameObject *frame)
    object PyGen_NewWithQualName(PyFrameObject *frame, object name, object qualname)


cpdef inline bint gen_check(object ob) noexcept:
    return PyGen_Check(ob)


cpdef inline bint gen_check_exact(object ob) noexcept:
    return PyGen_CheckExact(ob)


cdef inline bint geneq(object a, object b) noexcept:
    # Generator equality is identity (CPython uses ``object.__eq__``). Soft
    # ``geneq``. Callers should pass generator objects. Not on ``hot``.
    return a is b


cpdef inline bint gen_eq(object a, object b) noexcept:
    return geneq(a, b)


cdef inline object gen_new(PyFrameObject *frame):
    # Steals reference to frame.
    return PyGen_New(frame)


cdef inline object gen_new_with_qualname(PyFrameObject *frame, object name, object qualname):
    # Steals reference to frame.
    return PyGen_NewWithQualName(frame, name, qualname)
