# cython: freethreading_compatible=True
# Out-of-tree smoke: package-barrel + submodule cimport against an installed picop.
# Build: see README.md / scripts/smoke_barrel_cimport.sh

from picop cimport UUID, bytes_eq, list_len, str_eq, uuid4_bytes
from picop.cybytes cimport bytes_len
from picop.cybytes cimport bytes_concat, bytes_concat_and_del, bytes_resize
from picop.cylist cimport list_get, list_get_checked
from picop.cydict cimport dict_get, dict_get_with_error
from picop.cyobject cimport obj_call
from picop.uuid._uuid cimport UUID as DirectUUID, uuid_from_buf
from picop.cymemoryview cimport memoryview_get_base, memoryview_from_memory
from picop.cysentinel cimport sentinel_check, sentinel_check_exact, sentinel_new, sentinel_type

from cpython.object cimport PyObject
from picop.cytraceback cimport tb_check, tb_lineno, tb_next_borrow
import sys
from picop.cycode cimport PyCodeObject
from picop.cyframe cimport (
    frame_back,
    frame_check,
    frame_code,
    frame_lineno,
    frame_var,
    frame_var_cstr,
)
from picop.cycode cimport (
    code_addr2_location,
    code_check,
    code_firstlineno,
    code_name,
    code_num_free,
)
import gc
import weakref


class _Exporter(bytearray):
    pass


cpdef bint check_barrel():
    return (
        bytes_eq(b"ab", b"ab")
        and list_len([1, 2, 3]) == 3
        and str_eq("x", "x")
        and obj_call(str, (42,)) == "42"
    )


cpdef Py_ssize_t check_submodule():
    return bytes_len(b"ok")


cpdef bint check_uuid():
    cdef bytes raw = uuid4_bytes()
    cdef UUID value = UUID(raw)
    return len(raw) == 16 and value.version == 4


cpdef bint check_ownership():
    cdef bytes left = bytes(bytearray(b"left"))
    cdef bytes right = bytes(bytearray(b"right"))
    assert bytes_concat(left, right) == b"leftright"
    assert bytes_concat_and_del(left, right) == b"leftright"
    assert left == b"left" and right == b"right"
    assert bytes_resize(left, 2) == b"le"
    assert left == b"left"
    try:
        bytes_concat(left, object())
    except TypeError:
        pass
    else:
        raise AssertionError("concat must propagate buffer errors")
    return True


cpdef bint check_sentinels():
    try:
        marker = sentinel_new("marker", module="demo", repr="<marker>")
    except NotImplementedError:
        return not sentinel_check(object()) and not sentinel_check_exact(object())
    return (
        sentinel_check(marker)
        and sentinel_check_exact(marker)
        and repr(marker) == "<marker>"
        and sentinel_type() is type(marker)
    )


cpdef bint check_frames(object caller):
    # ``cdef`` locals live in the C frame, not in ``co_varnames``, and
    # ``PyFrame_GetVar`` only sees fast locals, so the caller passes a
    # Python frame with Python-level locals.
    assert frame_check(caller)
    assert frame_lineno(caller) > 0
    assert frame_code(caller) is caller.f_code
    assert frame_var(caller, "values") is not None
    assert frame_var_cstr(caller, b"values") is not None
    cdef object back = frame_back(caller)
    assert back is None or frame_check(back)
    return True

cpdef bint check_traceback():
    try:
        raise ValueError("probe")
    except ValueError:
        tb = sys.exc_info()[2]
    assert tb_check(tb)
    assert tb_lineno(tb) > 0
    cdef PyObject *nxt = tb_next_borrow(tb)
    assert nxt == NULL
    return True


def inner():
    return None


cpdef bint check_code():
    cdef object f = inner
    cdef object code = f.__code__
    cdef tuple location = code_addr2_location(<PyCodeObject *>code, 0)
    assert code_check(f.__code__)
    assert code_name(inner.__code__) == "inner"
    assert code_firstlineno(inner.__code__) > 0
    assert code_num_free(<PyCodeObject *>code) >= 0
    assert len(location) == 4
    assert isinstance(location[0], int)
    assert isinstance(location[1], int)
    assert isinstance(location[2], int)
    assert isinstance(location[3], int)
    return True
cpdef bint check_containers():
    cdef list values = [object()]
    assert list_get(values, 0) is values[0]
    assert list_get_checked(values, 0) is values[0]
    try:
        list_get_checked(values, 1)
    except IndexError:
        pass
    else:
        raise AssertionError("checked list access must reject OOB")
    assert dict_get({"none": None}, "none") is None
    assert dict_get_with_error({}, "missing") is None
    try:
        dict_get_with_error({}, [])
    except TypeError:
        pass
    else:
        raise AssertionError("propagating dictionary lookup swallowed an error")
    return True


cpdef bint check_direct_uuid():
    cdef unsigned char raw[16]
    cdef int i
    for i in range(16):
        raw[i] = i
    cdef bytes expected = bytes(range(16))
    cdef DirectUUID direct = uuid_from_buf(raw)
    cdef UUID barrel = UUID(expected)
    return direct == barrel and bytes_eq(direct.bytes, expected)


cpdef bint check_memoryview_ownership():
    cdef char storage[1]
    cdef memoryview view
    storage[0] = 0
    view = memoryview_from_memory(storage, 1)
    assert memoryview_get_base(view) is None
    view.release()

    exporter = _Exporter(b"payload")
    ref = weakref.ref(exporter)
    view = memoryview(exporter)
    owner = memoryview_get_base(view)
    view.release()
    del view, exporter
    gc.collect()
    assert owner == b"payload"
    assert ref() is owner
    del owner
    gc.collect()
    assert ref() is None
    return True
