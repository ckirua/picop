# cython: freethreading_compatible=True
# Out-of-tree smoke: package-barrel + submodule cimport against an installed picop.
# Build: see README.md / scripts/smoke_barrel_cimport.sh

from picop cimport (
    PyMonitoringState,
    monitoring_scope,
    monitoring_exit_scope,
    monitoring_active,
    monitoring_is_instrumented,
    fire_line,
    fire_py_return,
    PY_MONITORING_EVENT_LINE,
)
from picop cimport UUID, bytes_eq, list_len, str_eq, uuid4_bytes
from picop cimport mutex_is_locked as barrel_mutex_is_locked
from picop.cybytes cimport bytes_len
from picop.cybytes cimport bytes_concat, bytes_concat_and_del, bytes_resize
from picop.cylist cimport list_get, list_get_checked
from picop.cydict cimport dict_get, dict_get_with_error
from picop.cyobject cimport obj_call
from picop.uuid._uuid cimport UUID as DirectUUID, uuid_from_buf
from picop.cymemoryview cimport memoryview_get_base, memoryview_from_memory
from picop.cysentinel cimport sentinel_check, sentinel_check_exact, sentinel_new, sentinel_type
from picop.cyfunction cimport func_check, func_get_code, func_new_with_qualname
from picop.cymethod cimport cfunction_check, cfunction_get_self, classmethod_new, staticmethod_new
from picop.cylock cimport PyMutex, mutex_init, mutex_is_locked, mutex_lock, mutex_unlock

from cpython.object cimport PyObject
from libc.stddef cimport size_t
from libc.stdint cimport uint64_t
from picop.cytraceback cimport tb_check, tb_lineno, tb_next_borrow
import sys
import threading
import time
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
from picop.cyatomic cimport (
    atomic_cas_weak_relaxed,
    atomic_fetch_add_relaxed,
    atomic_init,
    atomic_load_acquire,
    atomic_size_t,
    atomic_store_release,
    atomic_uint64_fetch_add_relaxed,
    atomic_uint64_load_acquire,
    atomic_uint64_init,
    atomic_uint64_store_release,
    atomic_uint64_t,
)
from picop.cyceval cimport eval_init_threads, eval_threads_initialized
from picop.cyerr cimport (
    err_clear,
    err_exception_matches,
    err_fetch,
    err_get_raised,
    err_no_memory,
    err_occurred,
    err_restore,
    err_set_string,
)
from picop.cygetargs cimport (
    PyArg_ParseTuple,
    PyArg_ParseTupleAndKeywords,
    PyArg_UnpackTuple,
)
from picop.cylongintrepr cimport (
    PyLong_BASE,
    PyLong_MASK,
    PyLong_SHIFT,
    digit,
    longrepr_digits,
    longrepr_new,
    py_long,
)
from picop.cymem cimport (
    mem_calloc,
    mem_free,
    mem_malloc,
    mem_raw_free,
    mem_raw_malloc,
    mem_realloc,
    obj_calloc,
    obj_free,
    obj_malloc,
    obj_realloc,
)
from picop.cypylifecycle cimport life_get_version, life_is_initialized
from picop.cypystate cimport (
    PyGILState_STATE,
    PyThreadState,
    pystate_get,
    pystate_get_dict,
    pystate_gil_ensure,
    pystate_gil_release,
)
from picop.cyref cimport (
    ref_decref,
    ref_incref,
    ref_is_uniquely_referenced,
    ref_refcnt,
    ref_xdecref,
)
from picop.cypyport cimport PY_SSIZE_T_MAX, int64_t
from picop.cythread cimport (
    NOWAIT_LOCK,
    PY_LOCK_ACQUIRED,
    PyThread_type_lock,
    eval_restore_thread,
    eval_save_thread,
    thread_acquire,
    thread_allocate_lock,
    thread_free_lock,
    thread_get_ident,
    thread_release,
)
from picop.cyversion cimport PY_MINOR_VERSION, PY_VERSION_HEX
from picop.cyhash cimport hash_buffer, hash_buffer_raw, hash_generic, hash_pointer
import gc
import weakref


class _Exporter(bytearray):
    pass


# Code objects compiled by Cython carry frame-cache assumptions and cannot be
# re-wrapped into a plain PyFunction; build the demo function from CPython code.
_DEMO_NS = {}
exec(compile("def _demo_increment(value):\n    return value + 1", "<demo>", "exec"), _DEMO_NS)
_DEMO_CODE = _DEMO_NS["_demo_increment"].__code__


def _demo_source(cls_or_self, value):
    return value + 1


def _demo_one(value):
    return value + 1


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

cpdef bint check_functions_and_methods():
    made = func_new_with_qualname(_DEMO_CODE, globals(), "demo.increment")
    holder = type("Holder", (), {"doubled": classmethod_new(_demo_source), "plain": staticmethod_new(_demo_one)})
    return (
        func_check(made)
        and func_get_code(made) is _DEMO_CODE
        and made(2) == 3
        and made.__qualname__ == "demo.increment"
        and cfunction_check(len)
        and cfunction_get_self(len) is len.__self__
        and not cfunction_check(made)
        and holder.doubled(1) == 2
        and holder().plain(1) == 2
    )


cpdef bint check_locks():
    cdef PyMutex mu
    mutex_init(&mu)
    if mutex_is_locked(&mu):
        return False
    with nogil:
        mutex_lock(&mu)
        locked = barrel_mutex_is_locked(&mu)
        mutex_unlock(&mu)
    return locked and not mutex_is_locked(&mu)


cdef PyMutex shared_lock


cpdef bint shared_is_locked():
    return mutex_is_locked(&shared_lock)


cpdef void hold_shared(double seconds):
    # Held across a sleep so another thread can observe the locked state.
    with nogil:
        mutex_lock(&shared_lock)
    time.sleep(seconds)
    with nogil:
        mutex_unlock(&shared_lock)


cdef PyMutex contention_lock
cdef list contention_counter = [0]


cpdef void contention_bump(int iterations):
    # ``counter[0] += 1`` is a read-modify-write: without the mutex it is a
    # lost-update race on a free-threaded build.
    for _ in range(iterations):
        with nogil:
            mutex_lock(&contention_lock)
        contention_counter[0] += 1
        with nogil:
            mutex_unlock(&contention_lock)


cpdef bint check_lock_contention():
    mutex_init(&contention_lock)
    contention_counter[0] = 0
    cdef int workers = 8
    cdef int per_worker = 5000
    pool = [threading.Thread(target=contention_bump, args=(per_worker,)) for _ in range(workers)]
    for worker in pool:
        worker.start()
    for worker in pool:
        worker.join()
    return contention_counter[0] == workers * per_worker


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


cpdef bint check_errors():
    err_set_string(ValueError, "picop smoke")
    cdef bint occurred = err_occurred()
    cdef bint matches = err_exception_matches(ValueError)
    err_clear()

    err_set_string(ValueError, "round trip")
    cdef PyObject *ptype = NULL
    cdef PyObject *pvalue = NULL
    cdef PyObject *ptraceback = NULL
    err_fetch(&ptype, &pvalue, &ptraceback)
    cdef bint fetched = ptype is not NULL and pvalue is not NULL
    err_restore(ptype, pvalue, ptraceback)
    cdef bint restored = err_occurred()
    err_clear()

    err_set_string(ValueError, "raised")
    cdef object raised = <object>err_get_raised()
    err_clear()

    err_no_memory()
    cdef bint nomem_set = err_occurred()
    err_clear()

    return (
        occurred
        and matches
        and not err_occurred()
        and fetched
        and restored
        and isinstance(raised, ValueError)
        and nomem_set
    )


cpdef bint check_memory():
    cdef void *block = mem_malloc(8)
    cdef void *zeroed = mem_calloc(4, 2)
    cdef void *raw = mem_raw_malloc(16)
    cdef void *obj = obj_calloc(2, 4)
    block = mem_realloc(block, 32)
    obj = obj_realloc(obj, 16)
    mem_free(block)
    mem_free(zeroed)
    mem_raw_free(raw)
    obj_free(obj)
    return block != NULL and zeroed != NULL and raw != NULL and obj != NULL


cpdef bint check_thread_locks():
    cdef PyThread_type_lock lock = thread_allocate_lock()
    if lock == NULL:
        return False
    cdef int acquired = thread_acquire(lock, NOWAIT_LOCK)
    thread_release(lock)
    cdef long ident = thread_get_ident()
    cdef PyThreadState *saved = eval_save_thread()
    eval_restore_thread(saved)
    thread_free_lock(lock)
    return acquired == PY_LOCK_ACQUIRED and ident != 0 and thread_get_ident() == ident


cpdef bint check_atomics():
    cdef atomic_size_t counter
    cdef atomic_uint64_t big
    cdef size_t expected
    cdef size_t loaded
    cdef size_t final
    cdef uint64_t loaded_big
    cdef bint swapped

    with nogil:
        atomic_init(&counter, 1)
        atomic_store_release(&counter, 7)
        loaded = atomic_load_acquire(&counter)
        atomic_fetch_add_relaxed(&counter, 3)
        expected = 10
        swapped = atomic_cas_weak_relaxed(&counter, &expected, 20)
        final = atomic_load_acquire(&counter)
        atomic_uint64_init(&big, 0)
        atomic_uint64_store_release(&big, 18446744073709551615ULL)
        loaded_big = atomic_uint64_load_acquire(&big)
        loaded_big = atomic_uint64_fetch_add_relaxed(&big, 1ULL)

    return (
        loaded == 7
        and swapped
        and final == 20
        and loaded_big == 18446744073709551615ULL
    )


cpdef bint check_long_repr():
    cdef object value = (1 << PyLong_SHIFT) | 0x1234
    cdef digit *digits = longrepr_digits(value)
    if digits[0] != (0x1234 & PyLong_MASK) or digits[1] != 1:
        return False

    cdef py_long built = longrepr_new(2)
    digits = longrepr_digits(built)
    digits[0] = 5
    digits[1] = 1
    return <object>built == PyLong_BASE + 5


cpdef bint check_refs():
    cdef object value = [1, 2]
    cdef Py_ssize_t before = ref_refcnt(value)
    ref_incref(value)
    ref_decref(value)
    ref_xdecref(NULL)
    return ref_refcnt(value) == before and ref_is_uniquely_referenced(value)


cpdef bint check_arg_unpack(object args, object kwargs):
    cdef PyObject *first = NULL
    cdef PyObject *second = NULL
    cdef int ok = PyArg_UnpackTuple(args, "pair", 2, 2, &first, &second)

    cdef int number = 0
    cdef char *keywords[2]
    keywords[0] = "n"
    keywords[1] = NULL
    cdef int kw_ok = PyArg_ParseTupleAndKeywords((), kwargs, "i", keywords, &number)

    cdef int parsed = 0
    PyArg_ParseTuple((7,), "i", &parsed)

    cdef bint bad_rejected = False
    try:
        PyArg_ParseTuple(("x",), "i", &parsed)
    except TypeError:
        bad_rejected = True

    return (
        ok == 1
        and <object>first == 1
        and <object>second == 2
        and kw_ok == 1
        and number == 3
        and parsed == 7
        and bad_rejected
    )


cpdef bint check_ceval():
    eval_init_threads()
    return eval_threads_initialized()


cpdef bint check_pystate():
    cdef PyThreadState *tstate = pystate_get()
    cdef object state_dict = pystate_get_dict()
    state_dict["picop_smoke"] = 7
    cdef PyGILState_STATE gil = pystate_gil_ensure()
    pystate_gil_release(gil)
    return tstate is not NULL and state_dict is not None and state_dict["picop_smoke"] == 7


cpdef bint check_lifecycle():
    cdef bytes version = life_get_version()
    cdef str short = sys.version.split(" ")[0]
    return life_is_initialized() and version.decode().startswith(short)


cpdef bint check_port_and_version():
    cdef int64_t max_ssize = PY_SSIZE_T_MAX
    return PY_VERSION_HEX >= 0x030E0000 and PY_MINOR_VERSION >= 14 and max_ssize > 0


cpdef bint check_hashing():
    cdef bytes payload = b"cyhash barrel smoke"
    cdef bytearray mutable = bytearray(payload)
    cdef memoryview view = memoryview(payload)
    assert hash_buffer(view) == hash(payload)
    assert hash_buffer(mutable) == hash(payload)
    assert hash_buffer(view, 5, 12) == hash(payload[5:12])
    cdef Py_hash_t raw = hash_buffer_raw(<const char *>payload, <Py_ssize_t>len(payload))
    assert raw == hash(payload)
    cdef object target = payload
    cdef Py_hash_t generic = hash_generic(target)
    assert generic == hash_pointer(<PyObject *>target), "PyObject_GenericHash is the identity hash"
    assert generic != -1
    return True

cpdef tuple check_monitoring(object code):
    cdef PyMonitoringState states[19]
    cdef unsigned long long version = 0
    cdef int active
    cdef int fired_line
    cdef int fired_return
    cdef int instrumented
    monitoring_scope(states, <uint64_t *>&version)
    active = monitoring_active(states, PY_MONITORING_EVENT_LINE)
    fired_line = fire_line(states, <PyObject *>code, 0, 1)
    fired_return = fire_py_return(states, <PyObject *>code, 0, <PyObject *>None)
    monitoring_exit_scope()
    instrumented = monitoring_is_instrumented(PY_MONITORING_EVENT_LINE)
    return (active, fired_line, fired_return, instrumented)
